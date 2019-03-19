from unittest import TestCase
import json
from user_timeline_statistics import UserTimelineStatistics
from twitter import Status


class TestUserTimelineStatistics(TestCase):

    @classmethod
    def setUpClass(cls):
        with open("sample_test_data.json", "r") as file:
            timeline = json.load(file)
            cls.timeline = [Status.NewFromJsonDict(status) for status in timeline]
        cls.stats = UserTimelineStatistics()

    def test_replies_count(self):
        # sprawdza działanie w/w metody w przypadku podania poprawych danych i zbioru pustego
        self.assertEqual(self.stats.replies_count(self.timeline), 8)
        self.assertEqual(self.stats.replies_count([]), 0)

    def test_replies_count_with_errors(self):
        # sprawdza działanie w/w metody w przypadku podania błędnych danych
        self.assertRaises(TypeError, self.stats.replies_count, 43)
        self.assertRaises(TypeError, self.stats.replies_count, True)
        self.assertRaises(TypeError, self.stats.replies_count, "ananas")
        self.assertRaises(TypeError, self.stats.replies_count, [21, False, "szpinak"])

    def test_replies_percentage(self):
        # sprawdza działanie w/w metody w przypadku podania poprawych danych i zbioru pustego
        self.assertAlmostEqual(self.stats.replies_percentage(self.timeline), 8/20*100)
        self.assertRaises(ValueError, self.stats.replies_percentage, [])

    def test_replies_percentage_with_errors(self):
        # sprawdza działanie w/w metody w przypadku podania błędnych danych
        self.assertRaises(TypeError, self.stats.replies_percentage, 23)
        self.assertRaises(TypeError, self.stats.replies_percentage, False)
        self.assertRaises(TypeError, self.stats.replies_percentage, "rzepa")
        self.assertRaises(TypeError, self.stats.replies_percentage, [True, 39, "marchew"])
