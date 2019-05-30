from unittest import TestCase
from tools import Tools


class TestTools(TestCase):

    def test_clean_string_one_link(self):
        text = "Ananas banana kołysał https://youtu.be/6kS65TbKjeU?t=49 fajne"
        result = "Ananas banana kołysał fajne"
        self.assertEqual(Tools.clean_string(text), result)

    def test_clean_string_two(self):
        text = "Ananas https://t.co/5mCBmQ52w8 banana kołysał https://youtu.be/_uJQZ8QmoKo fajne"
        result = "Ananas banana kołysał fajne"
        self.assertEqual(Tools.clean_string(text), result)

    def test_clean_string_end_link(self):
        text = "Ananas banana kołysał fajne https://youtu.be/6kS65TbKjeU?t=49"
        result = "Ananas banana kołysał fajne"
        self.assertEqual(Tools.clean_string(text), result)

    def test_clean_string_start_link(self):
        text = "https://youtu.be/6kS65TbKjeU?t=49 Ananas banana kołysał fajne"
        result = "Ananas banana kołysał fajne"
        self.assertEqual(Tools.clean_string(text), result)

