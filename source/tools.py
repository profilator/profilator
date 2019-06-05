from math import floor, log10
import re


class Tools(object):

    @staticmethod
    def human_format(num, ends=("", "K", "M", "B", "T")):
        # divides by 3 to separate into thousands (...000)
        if num <= 0:
            return num
        i = int(floor(log10(num))/3)
        number = round(num/(10**(log10(num)-log10(num) % 3)), i)
        if number.is_integer():
            number = int(number)
        return str(number) + ends[i]

    @staticmethod
    def clean_links(string):
        # get rid of links, hashtags and mensions in strings.
        new_string = re.sub(r"((\s|^)http[s]?://(\w+\.)+\w+(/\S+)*/?(\s|$))", " ", string)
        return new_string.strip()

    @staticmethod
    def cut_tweets(timeline):
        new_timeline = timeline.copy()
        i = 0
        for post in timeline:
            post_dict = post.AsDict()
            if "in_reply_to_status_id" not in post_dict and "retweeted_status" not in post_dict:
                del new_timeline[i]
            else:
                i += 1
        return new_timeline
