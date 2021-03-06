from math import floor, log10
import re
from guess_language import guess_language

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
    def human_format_date(date):
        day=date[8]+date[9]
        month=date[4]+date[5]+date[6]
        if month=="Jan": month="01"
        elif month=="Feb": month="02"
        elif month=="Mar": month="03"
        elif month=="Apr": month="04"
        elif month=="May": month="05"
        elif month=="Jun": month="06"
        elif month=="Jul": month="07"
        elif month=="Aug": month="08"
        elif month=="Sep": month="09"
        elif month=="Oct": month="10"
        elif month=="Nov": month="11"
        elif month=="Dec": month="12"
        year=date[26]+date[27]+date[28]+date[29]
        return day+"."+month+"."+year

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
		
    @staticmethod
    def language(timeline):
        text = ""
        for tweet in timeline:
            text = text + " " + tweet.full_text
        return guess_language(text)