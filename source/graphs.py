import re
import string
from math import pi
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.palettes import Category10
from numpy import histogram
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import LocallyLinearEmbedding
from twitter import Status
from wordcloud import WordCloud
from user_timeline_statistics import UserTimelineStatistics

account = UserTimelineStatistics()


def create_replies_graph(t):
    # tworzy wykres kołowy przedstawiający ilość odpowiedzi
    replies = account.replies_count(t)
    retweets = account.retweets_count(t)

    x = {
        "tweets": len(t) - replies - retweets,
        "replies": replies,
        "retweets": retweets
    }

    data = pd.Series(x).reset_index(name="value").rename(columns={"index": "tweet_type"})
    data["angle"] = data["value"] / data["value"].sum() * 2 * pi
    data["color"] = ["#00c4a6", "#007fc4", "#49b6f9"]

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

    # zmienna przechowująca element listy zawierający największą wartość
    m = max(lista)

    # kolory, jakimi zostaną wypełnione poszczególne "słupki" wykresu
    colors = ["#00c4a6" if v != m else "#007fc4" for v in lista]

    source = ColumnDataSource(data=dict(
        x = [i for i in range(1, 8)],
        width = [0.5,0.5,0.5,0.5,0.5,0.5,0.5],
        bottom =[0,0,0,0,0,0,0],
        top=lista,
        fill_color=colors

    ))

    tooltips = [
        ("Number of posts", "@top")
    ]

    p = figure(plot_height=300, plot_width=450, title="Published posts in the days of week", toolbar_location="right",
               x_axis_label="Day of week", y_axis_label="Number of tweets", tooltips=tooltips)
    p.vbar(x="x", width="width", bottom="bottom", top="top", fill_color="fill_color", source=source)
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
    """Tworzy wykres słupkowy pokazujący ilość opublikowanych postów w poszczególnych godzinach."""

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


def preprocessing(line):
    """Preprocessing and tokenizing"""
    line = line.lower()
    line = re.sub(r"[{}]".format(string.punctuation), " ", line)
    return line


def KMeans_clusters(X, n=10):
    """
    Optymalizacja liczby klastrów

    Wyznacza liczbę klastrów z podanego przedziału, dla której użycie algorytmu KMeans daje największy współczynnik
    Silhouette Score.

    Parameters
    ----------
    X : tablica lub macierz rzadka, kształt = [n_samples, n_features]
        Zbiór, który ma być sklasteryzowany
    n : int
        Maksymalna liczba klastrów, jaka ma być testowana. Domyślnie 10.
        Musi być mniejsza niż liczba elementów w zbiorze X. Nie może być mniejsza niż 2.

    Returns
    -------
    int
        Liczba klastrów z największym Silhouette Score

    """
    max_score = 0
    max = 1
    for k in range(2, n + 1):
        model = KMeans(n_clusters=k).fit(X)
        clusters = model.predict(X)
        score = metrics.silhouette_score(X, clusters)
        if score > max_score:
            max_score = score
            max = k
    return max


def create_tfidf_graph(t):
    """Tworzy wykres przedstawiający posty sklasteryzowane wg TF-IDF."""
    if len(t) < 3:  # manifold nie działa, kiedy postów jest mniej niż 3
        p = figure(title="Too small number of tweets")
        return p

    post_list = []  # lista zawierająca treści tweetów
    for post in t:
        if not isinstance(post, Status):
            raise TypeError("Expected Status class instance, got %s" % type(post))
        text = post.full_text
        post_list.append(text)

    tfidf_vectorizer = TfidfVectorizer(preprocessor=preprocessing)
    tfidf = tfidf_vectorizer.fit_transform(post_list)

    mf = LocallyLinearEmbedding(n_neighbors=min(5, len(t)-1))
    df = pd.DataFrame(mf.fit_transform(tfidf.toarray()))

    # Jeśli postów, jest mniej niż dziewięć, maksymlna liczba klastrów wynosi len(t)-1
    n = KMeans_clusters(tfidf, min(9, len(t)-1))
    if n > 5:
        n = n // 2  # jeśli optymalna liczba klastrów wychodzi większa niż 5, zmniejsza ją o połowę

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
    tooltips = """
    <div style="width:250px;">
    @desc
    </div>
    """

    p = figure(title="Tweets grouped by content", tooltips=tooltips)
    p.scatter(x='x', y='y', color='color', source=source)
    return p


def wordcloud(timeline, pid):
    text = ""
    for tweet in timeline:
        text = text + " " + tweet.full_text
    wc = WordCloud(width=1920, height=1080, max_words=50, background_color="white").generate(text)
    wc.to_file("static/temp/" + pid + ".png")
