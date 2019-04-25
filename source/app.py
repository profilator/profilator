from flask import Flask, render_template, request, redirect, url_for
from bokeh.embed import components
from bokeh.transform import cumsum
from bokeh.plotting import figure, ColumnDataSource
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import NumeralTickFormatter
from user_timeline_statistics import UserTimelineStatistics
from twitter import Api
from twitter.error import TwitterError
from math import pi, floor, log10
from numpy import histogram
import pandas as pd
import json

app = Flask(__name__)

with open("token/tokens.json", "r") as file:
    tokens = json.load(file)


api = Api(consumer_key=tokens["consumer_key"],
          consumer_secret=tokens["consumer_secret"],
          access_token_key=tokens["access_token_key"],
          access_token_secret=tokens["access_token_secret"])

account = UserTimelineStatistics()


def human_format(num, ends=["", "K", "M", "B", "T"]):
    # divides by 3 to separate into thousands (...000)
    if num <= 0:
        return num
    index = int(floor(log10(num))/3)
    number = round(num/(10**(log10(num)-log10(num) % 3)), index)
    if number.is_integer():
        number = int(number)
    return str(number) + ends[index]


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
    lista = []

    for d, posty in days.items():
        lista.append(posty)

    m = max(lista)
    colors = ["#00c4a6" if v != m else "#007fc4" for v in lista]

    p = figure(plot_height=300, plot_width=450, title="Published posts in the days of week", toolbar_location="right",
               x_axis_label="Day of week", y_axis_label="Number of tweets")
    p.vbar(x=[i for i in range(1, 8)], width=0.5, bottom=0, top=lista, fill_color=colors)
    return p


def create_length_graph(t, bins):
    # tworzy histogram dlugosci postow
    hist, bin_edges = histogram([len(post.text) for post in t], bins=bins)
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

    p = figure(plot_height=300, plot_width=450, title="Tweets Length [Yet wrong outcome]",
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

    p = figure(plot_height=300, plot_width=450, title="Published posts in hours of a day [Yet wrong outcome]",
               toolbar_location="right", x_axis_label="Hours", y_axis_label="Number of tweets", tooltips=tooltips)
    p.vbar(x=x, width=0.5, bottom=0, top=top, color="#007fc4", fill_color=colors)
    return p


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

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    try:
        following=human_format(len(api.GetFriendIDs(user.id)))
    except TwitterError:
        following = "???"

    # render template
    html = render_template(
        "report.html",
        nickname=nickname,
        tweets=human_format(user.statuses_count),
        following=following,
        followers=human_format(user.followers_count),
        likes=human_format(user.favourites_count),
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
    )

    return encode_utf8(html)


if __name__ == "__main__":
    app.run(debug=True)

