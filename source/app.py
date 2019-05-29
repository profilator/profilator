from flask import Flask, render_template, request, redirect, url_for
from bokeh.embed import components
from bokeh.transform import cumsum
from bokeh.plotting import figure, ColumnDataSource
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import NumeralTickFormatter
from bokeh.palettes import Category10
from user_timeline_statistics import UserTimelineStatistics
from tools import Tools
from twitter import Api
from twitter import Status
from twitter.error import TwitterError
from math import pi
import numpy as np
from numpy import histogram
import pandas as pd
import json
import os
from os import path
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import *
from sklearn.cluster import KMeans
from sklearn import metrics
import string
import re


app = Flask(__name__)

with open("token/tokens.json", "r") as file:
    tokens = json.load(file)


api = Api(consumer_key=tokens["consumer_key"],
          consumer_secret=tokens["consumer_secret"],
          access_token_key=tokens["access_token_key"],
          access_token_secret=tokens["access_token_secret"],
          tweet_mode="extended")

account = UserTimelineStatistics()
human_format = Tools.human_format


def create_replies_graph(t):
    # tworzy wykres kołowy przedstawiający ilość odpowiedzi
    stats = UserTimelineStatistics()
    replies = stats.replies_count(t)

    x = {
        "posts": len(t) - replies,
        "replies": replies,
    }

    data = pd.Series(x).reset_index(name="value").rename(columns={"index": "tweet_type"})
    data["angle"] = data["value"] / data["value"].sum() * 2 * pi
    data["color"] = ["#00c4a6", "#007fc4"]

    p = figure(plot_height=300, plot_width=450, title="Replies Count", toolbar_location=None,
               tools="hover", tooltips="@tweet_type: @value", x_range=(-0.5, 1.0))
    p.wedge(x=0, y=1, radius=0.4, start_angle=cumsum("angle", include_zero=True),
            end_angle=cumsum("angle"), line_color="white", fill_color='color',
            legend="tweet_type", source=data)
    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    return p


def create_favorites_graph(t, bins):
    # tworzy histogram polubień
    hist, bin_edges = histogram([post.favorite_count for post in t], bins=bins)
    bin_edges = [round(i) for i in bin_edges]
    m = max(hist)
    colors = ["#00c4a6" if v != m else "#007fc4" for v in hist]

    source = ColumnDataSource(data=dict(
        left=bin_edges[:-1],
        right=bin_edges[1:],
        top=hist,
        bottom=[0 for x in range(len(hist))],
        colors=colors
    ))

    tooltips = [
        ("Favorites range", "<@left{0,0}; @right{0,0})"),
        ("Tweets", "@top")
    ]

    p = figure(plot_height=300, plot_width=450, title="Favorites", toolbar_location="right",
               x_axis_label="Favorites count", y_axis_label="Number of tweets", tooltips=tooltips)
    p.quad("left", "right", "top", "bottom", fill_color="colors", source=source)
    p.xaxis.ticker = bin_edges

    if bin_edges[-1] >= 10000:
        p.xaxis.major_label_orientation = pi/4
        p.xaxis.formatter = NumeralTickFormatter(format="0,0")

    return p


def create_posts_in_days_graph(t):
    # tworzy wykres słupkowy pokazujący ilość opublikowanych postów w poszczególnych dniach tygodnia

    days = account.day_counter(t)

    # ta lista pełni rolę pojemnika - każda cyfra odpowiada kolejnemu dniowi tygodnia zaczynając od poniedziałku
    lista = [1,2,3,4,5,6,7]

    # ta lista wykorzystywana jest zarówno przez tooltips jak i pętlę przygotowującą etykiety
    week = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

    # pseudosegregująca pętla - zamienia rekord tabeli 'lista' na liczbę postów w zależności,
    # jaki dzień tygodnia zawiera klucz słownika 'Days'
    for d, posts in days.items():
        if d == 'Mon':
            lista[0] = posts
        elif d == 'Tue':
            lista[1] = posts
        elif d == 'Wed':
            lista[2] = posts
        elif d == 'Thu':
            lista[3] = posts
        elif d == 'Fri':
            lista[4] = posts
        elif d == 'Sat':
            lista[5] = posts
        elif d == 'Sun':
            lista[6] = posts

    tooltips = [
        ("Day of week", "@week2"),
        ("Number of posts", "@lista2")
    ]
            
    m = max(lista)
    colors = ["#00c4a6" if v != m else "#007fc4" for v in lista]

    p = figure(plot_height=300, plot_width=450, title="Published posts in the days of week", toolbar_location="right",
               x_axis_label="Day of week", y_axis_label="Number of tweets", tooltips=tooltips)
    p.vbar(x=[i for i in range(1, 8)], width=0.5, bottom=0, top=lista, fill_color=colors)
    labels = {}

    # pętla przygotowywuje słownik wykorzystywany do etykiety wykresu
    # - co prawda zawsze będzie 7 punktów wykresu, ale nie ma problemu z tickami
    n = 1
    for d in week:
        labels[n] = d
        n += 1
    p.xaxis.major_label_overrides = labels

    return p


def create_length_graph(t, bins):
    # tworzy histogram dlugosci postow
    hist, bin_edges = histogram([len(post.full_text) for post in t], bins=bins)
    bin_edges = [round(i) for i in bin_edges]
    m = max(hist)
    colors = ["#00c4a6" if v != m else "#007fc4" for v in hist]

    source = ColumnDataSource(data=dict(
        left=bin_edges[:-1],
        right=bin_edges[1:],
        top=hist,
        bottom=[0 for x in range(len(hist))],
        colors=colors
    ))

    tooltips = [
        ("Tweet length", "<@left{0,0}; @right{0,0})"),
        ("Tweets", "@top")
    ]

    p = figure(plot_height=300, plot_width=450, title="Tweets Length",
               toolbar_location="right", x_axis_label="Tweet length", y_axis_label="Number of tweets",
               tooltips=tooltips)
    p.quad("left", "right", "top", "bottom", fill_color="colors", source=source)
    p.xaxis.ticker = bin_edges

    if bin_edges[-1] >= 10000:
        p.xaxis.major_label_orientation = pi/4
        p.xaxis.formatter = NumeralTickFormatter(format="0,0")

    return p


def create_posts_in_hours_graph(t):
    # tworzy wykres słupkowy pokazujący ilość opublikowanych postów w poszczególnych godzinach

    hours = account.hours_count(t)
    top = []
    x = []

    for hour, posts in hours.items():
        top.append(posts)
        x.append(hour)

    tooltips = [
        ("Hour", "@x"),
        ("Tweets", "@top")
    ]

    m = max(top)
    colors = ["#00c4a6" if v != m else "#007fc4" for v in top]

    p = figure(plot_height=300, plot_width=450, title="Published posts in hours of a day (UTC +0)",
               toolbar_location="right", x_axis_label="Hours", y_axis_label="Number of tweets", tooltips=tooltips)
    p.vbar(x=x, width=0.5, bottom=0, top=top, color="#007fc4", fill_color=colors)
    return p


# Preprocessing and tokenizing
def preprocessing(line):
    line = line.lower()
    line = re.sub(r"[{}]".format(string.punctuation), " ", line)
    return line

def KMeans_clusters(X, n=10):
    """
    Optymalizacja liczby klastrów

    Wyznacza liczbę klastrów, dla której użycie algorytmu KMeans daje największy współczynnik Silhouette Score.

    Parameters
    ----------
    X : lista lub macierz
        Zbiór, który ma być sklasteryzowany
    n : int
        Maksymalna liczba klastrów, jaka ma być testowana. Domyślnie 10

    Returns
    -------
    int
        Liczba klastrów z największym Silhouette Score

    """
    max_score = 0
    for k in range(2, n + 1):
        model = KMeans(n_clusters=k).fit(X)
        clusters = model.predict(X)
        score = metrics.silhouette_score(X, clusters)
        if score > max_score:
            max_score = score
            max = k
    return max

def create_tfidf_graph(t):
    post_list = []  # lista zawierająca treści tweetów
    for post in t:
        if not isinstance(post, Status):
            raise TypeError("Expected Status class instance, got %s" % type(post))
        text = post.full_text
        post_list.append(text)

    tfidf_vectorizer = TfidfVectorizer(preprocessor=preprocessing)
    tfidf = tfidf_vectorizer.fit_transform(post_list)

    mf = LocallyLinearEmbedding()
    df = pd.DataFrame(mf.fit_transform(tfidf.toarray()))

    n = KMeans_clusters(tfidf, 9)
    if n > 5:
        n = n // 2  # jeśli optymalna liczba klastrów wychodzi wieksza niż 5, zmniejsza ją o połowę

    # Klasteryzacja
    kmeans = KMeans(n_clusters=n).fit(tfidf)
    clusters = kmeans.predict(tfidf)
    df["class"] = clusters

    colors = np.hstack([Category10[10]] * 20)
    source = ColumnDataSource(data=dict(
        x=df[0],
        y=df[1],
        color=colors[clusters].tolist(),
        desc=post_list,
    ))
    tooltips = [
        ("text", "@desc"),
    ]

    p = figure(title="Tweets grouped by content", tooltips=tooltips)
    p.scatter(x='x', y='y', color='color', source=source)
    return p


def wordcloud(timeline, pid):
    text = ""
    for tweet in timeline:
        text = text + " " + tweet.full_text
    wc = WordCloud(width=1920, height=1080, max_words=50, background_color="white").generate(text)
    wc.to_file("static/temp/" + pid + ".png")
    

@app.route("/")
def index():
    html = render_template(
        "index.html",
        error=request.args.get("error")
    )
    return encode_utf8(html)


@app.route("/report")
def report():
    nickname = request.args.get('nickname')

    try:
        user = api.GetUser(screen_name=nickname)
    except TwitterError:
        return redirect(url_for('index', error="Error: User not found"))

    timeline = api.GetUserTimeline(screen_name=nickname, count=200, trim_user=True)

    replies_script, replies_div = components(create_replies_graph(timeline))
    favorites_script, favorites_div = components(create_favorites_graph(timeline, 10))
    posts_in_days_script, posts_in_days_div = components(create_posts_in_days_graph(timeline))
    length_script, length_div = components(create_length_graph(timeline, 10))
    posts_in_hours_script, posts_in_hours_div = components(create_posts_in_hours_graph(timeline))
    tfidf_script, tfidf_div = components(create_tfidf_graph(timeline))
    wordcloud(timeline, user.id_str)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    try:
        following_tooltip = len(api.GetFriendIDs(user.id))
        following = human_format(following_tooltip)
    except TwitterError:
        following = "???"
        following_tooltip = "Reached api limit"

    tweets = user.statuses_count
    followers = user.followers_count
    likes = user.favourites_count

    # render template
    html = render_template(
        "report.html",
        nickname=nickname,
        tweets=human_format(tweets),
        following=following,
        followers=human_format(followers),
        likes=human_format(likes),
        tweets_tooltip=tweets,
        following_tooltip=following_tooltip,
        followers_tooltip=followers,
        likes_tooltip=likes,
        replies_script=replies_script,
        replies_div=replies_div,
        favorites_script=favorites_script,
        favorites_div=favorites_div,
        posts_in_days_script=posts_in_days_script,
        posts_in_days_div=posts_in_days_div,
        posts_in_hours_script=posts_in_hours_script,
        posts_in_hours_div=posts_in_hours_div,
        js_resources=js_resources,
        css_resources=css_resources,
        length_script=length_script,
        length_div=length_div,
        tfidf_script=tfidf_script,
        tfidf_div=tfidf_div,
        pid="temp/" + user.id_str + ".png"
    )

    return encode_utf8(html)


if __name__ == "__main__":
    app.run(debug=True)

