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
    def clean_string(string):
        # get rid of links, hashtags and mensions in strings.
        new_string = re.sub(r"(\s|^)(http://|https://)(\w+\.)+\w+(/\S+)*/?(\s|$)", " ", string)
        return new_string.strip()
