from twitter import Api
import json


with open('token/tokens.json', "r") as file:
    tokens = json.load(file)


api = Api(consumer_key=tokens["consumer_key"],
          consumer_secret=tokens["consumer_secret"],
          access_token_key=tokens["access_token_key"],
          access_token_secret=tokens["access_token_secret"])

timeline = api.GetUserTimeline(screen_name="AndrzejDuda", count=10, trim_user=True)


# metody dostępne dla Api możecie znaleźć w dokumentacji na stronie:
# https://python-twitter.readthedocs.io/en/latest/twitter.html#module-twitter.api
# najbardziej przydatne będa dla was metody zaczynające się od Get, zwłaszcza metoda "GetUserTimeline"
