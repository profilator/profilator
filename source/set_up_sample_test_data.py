from twitter import Api
import json


def set_up_sample_test_data():
    with open('token/tokens.json', "r") as file:
        tokens = json.load(file)

    api = Api(consumer_key=tokens["consumer_key"],
              consumer_secret=tokens["consumer_secret"],
              access_token_key=tokens["access_token_key"],
              access_token_secret=tokens["access_token_secret"],
              tweet_mode="extended")
    timeline = api.GetUserTimeline(screen_name="Pontifex", count=200, trim_user=True)
    json_timeline = [post.AsDict() for post in timeline]
    with open("test.json", "w") as file:
        json.dump(json_timeline, file, indent=4)


if __name__ == "__main__":
    set_up_sample_test_data()
