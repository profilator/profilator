from flask import Flask, render_template, request, redirect, url_for
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from user_timeline_statistics import UserTimelineStatistics
from tools import Tools
from twitter import Api
from twitter.error import TwitterError
import json

from graphs import *

app = Flask(__name__)

with open("token/tokens.json", "r") as file:
    tokens = json.load(file)


api = Api(consumer_key=tokens["consumer_key"],
          consumer_secret=tokens["consumer_secret"],
          access_token_key=tokens["access_token_key"],
          access_token_secret=tokens["access_token_secret"],
          tweet_mode="extended")

account = UserTimelineStatistics()


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

    timeline = api.GetUserTimeline(screen_name=nickname, count=200, trim_user=True, include_rts=False)

    # for i, tweet in enumerate(timeline):
        # timeline[i].full_text = Tools.clean_string(tweet.full_text)

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
        following = Tools.human_format(following_tooltip)
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
        tweets=Tools.human_format(tweets),
        following=following,
        followers=Tools.human_format(followers),
        likes=Tools.human_format(likes),
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

