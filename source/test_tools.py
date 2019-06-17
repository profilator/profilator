from unittest import TestCase
from tools import Tools


class TestTools(TestCase):

    def test_clean_links_one_link(self):
        text = "Ananas banana kołysał https://youtu.be/6kS65TbKjeU?t=49 fajne"
        result = "Ananas banana kołysał fajne"
        self.assertEqual(Tools.clean_links(text), result)

    def test_clean_links_one_link_not_equal(self):
        text = "Ananas banana kołysał https://youtu.be/6kS65TbKjeU?t=49 fajne"
        result = "Ananas banana kołysał fajnen"
        self.assertNotEqual(Tools.clean_links(text), result)

    def test_clean_links_one_link_with_slash(self):
        text = "Ananas banana kołysał https://youtu.be/6kS65TbKjeU?t=49/ fajne"
        result = "Ananas banana kołysał fajne"
        self.assertEqual(Tools.clean_links(text), result)

    def test_clean_links_two_links(self):
        text = "Ananas https://t.co/5mCBmQ52w8 banana kołysał https://youtu.be/_uJQZ8QmoKo fajne"
        result = "Ananas banana kołysał fajne"
        self.assertEqual(Tools.clean_links(text), result)

    def test_clean_links_end_link(self):
        text = "Ananas banana kołysał fajne https://t.co/jlzzctiGeC"
        result = "Ananas banana kołysał fajne"
        self.assertEqual(Tools.clean_links(text), result)

    def test_clean_links_start_link(self):
        text = "https://youtu.be/6kS65TbKjeU?t=49 Ananas banana kołysał fajne"
        result = "Ananas banana kołysał fajne"
        self.assertEqual(Tools.clean_links(text), result)

    def test_clean_links_new_line(self):
        text = "Ananas banana kołysał fajne\nhttps://youtu.be/6kS65TbKjeU?t=49"
        result = "Ananas banana kołysał fajne"
        self.assertEqual(Tools.clean_links(text), result)
