from flask import Flask, render_template
from bokeh.embed import components
from bokeh.transform import cumsum
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from source.user_timeline_statistics import UserTimelineStatistics
from twitter import Api
from math import pi
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


@app.route("/")
def index():
    return "Hello, World!"


@app.route("/bokeh")
def bokeh():

    stats = UserTimelineStatistics()
    replies = stats.replies_count(timeline)

    x = {
        "replies": replies,
        "posts": len(timeline) - replies
    }

    data = pd.Series(x).reset_index(name="value").rename(columns={"index": "tweet_type"})
    data["angle"] = data["value"]/data["value"].sum() * 2 * pi
    data["color"] = ["#8e57c1", "#6d91e8"]

    p=figure(plot_height=350, title="Replies Count", toolbar_location=None,
             tools="hover", tooltips="@tweet_type: @value", x_range=(-0.5, 1.0))
    p.wedge(x=0, y=1, radius=0.4, start_angle=cumsum("angle", include_zero=True),
            end_angle=cumsum("angle"), line_color="white", fill_color='color',
            legend="tweet_type", source=data)
    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    script, div = components(p)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    html = render_template(
        "index.html",
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return encode_utf8(html)


if __name__ == "__main__":
    app.run(debug=True)