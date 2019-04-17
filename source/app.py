from flask import Flask, render_template
from bokeh.embed import components
from bokeh.transform import cumsum
from bokeh.plotting import figure, ColumnDataSource
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from source.user_timeline_statistics import UserTimelineStatistics
from twitter import Api
from math import pi
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

timeline = api.GetUserTimeline(screen_name="AndrzejDuda", count=200, trim_user=True)


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
    data["color"] = ["#6d91e8", "#8e57c1"]

    p = figure(plot_height=350, title="Replies Count", toolbar_location=None,
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
    m = max(hist)
    colors = ["#6d91e8" if v != m else "#8e57c1" for v in hist]

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

    p = figure(plot_height=350, title="Favorites", toolbar_location="right",
               x_axis_label="Favorites count", y_axis_label="Number of tweets", tooltips=tooltips)
    p.quad("left", "right", "top", "bottom", fill_color="colors", source=source)
    return p


@app.route("/")
def index():
    html = render_template(
        "index.html"
    )
    return encode_utf8(html)


@app.route("/report")
def report():
    replies_script, replies_div = components(create_replies_graph(timeline))
    favorites_script, favorites_div = components(create_favorites_graph(timeline, 10))

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        "report.html",
        replies_script=replies_script,
        replies_div=replies_div,
        favorites_script=favorites_script,
        favorites_div=favorites_div,
        js_resources=js_resources,
        css_resources=css_resources,
    )

    return encode_utf8(html)


if __name__ == "__main__":
    app.run(debug=True)
