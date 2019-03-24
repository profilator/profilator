from twitter import Status
from collections.abc import Iterable
import collections as col
import numpy as np
from sklearn.cluster import KMeans
from sklearn import metrics


class UserTimelineStatistics(object):
    # tutaj wrzucamy metody służące do zbierania podstawowych statystyk użytkownika

    def replies_count(self, timeline):
        # zwraca ile spośród wpisów użytkownika to odpowiedzi
        replies = 0
        for status in timeline:
            if not isinstance(status, Status):
                raise TypeError("Expected Status class instance, got %s" % type(status))
            if "in_reply_to_status_id" in status.AsDict():
                replies += 1
        return replies

    def replies_percentage(self, timeline):
        # zwraca procent odpowiedzi spośród wszystkich statusów w timeline
        if not isinstance(timeline, Iterable):
            raise TypeError("Expected an iterable of Status objects, got %s" % type(timeline))
        if len(timeline) == 0:
            raise ValueError("An iterable must not be empty")
        replies = self.replies_count(timeline)
        return replies / len(timeline) * 100

    def day_counter(self, timeline):
        # zwraca słownik zawierający ilość postów, które dodano w określonych dniach tygodnia
        days = col.Counter()
        for k in timeline:
            days[k.created_at[:3]] += 1
        return days

    def most_active_day(self, timeline):
        # zwraca dzień, w którym pojawiło się najwięcej postów
        # mad - most active day
        days = self.day_counter(timeline)
        # d to zmienna pomocnicza przechowująca obecną największą liczbę dni, w których pojawiała się aktywność
        d = 0
        for day_of_week, number_of_days in days.items():
            if(number_of_days > d):
                d = number_of_days
                mad = day_of_week
        return mad

    def average_favourites(self, timeline):
        # zwraca średnią ilość ulubionych pod postami użytkownika
        total_likes = 0
        posts = 0
        if not isinstance(timeline, Iterable):
            raise TypeError("Expected an iterable of Status objects, got %s" % type(timeline))

        for post in timeline:
            if post.favorite_count:
                if isinstance(post.favorite_count, int):
                    total_likes += post.favorite_count
                else:
                    raise TypeError("Expected an integer, got %s" % type(post.favorite_count))
            posts += 1
        if total_likes == 0:
            return 0
        else:
            return posts / total_likes

    def hours_count(timeline, n = None):
        # Zwraca listę zawierajacą godziny, o jakich były dodawane posty oraz liczby postów dodanych o każdej godzinie, posortwoaną wg liczby postów.
        # Drugi argument to liczba elementów, jakie mają zostać zwrócone. Domyślnie zwraca całą listę.
        hour_hist = col.Counter()
        for post in timeline:
            if not isinstance(post, Status):
                raise TypeError("Expected Status class instance, got %s" % type(post))
            else:
                hour_hist[int(post.created_at[11:13])] += 1
        return hour_hist.most_common(n)

    def avg_hour(timeline):
        # Zwraca średnią z godzin, o jakich były dodawane posty.
        sum = 0; n = 0
        if not isinstance(timeline, Iterable):
            raise TypeError("Expected an iterable of Status objects, got %s" % type(timeline))
        if len(timeline) == 0:
            raise ValueError("An iterable must not be empty")

        for post in timeline:
            sum += int(post.created_at[11:13])
            n += 1
        return sum/n;

    def KMeans_clusters(timeline):
        # Zwraca liczbę klastrów, dla której przy użyciu algorymu KMeans współczynnik Silhouette jest największy
        hour_list = [] # lista godzin dodawania tweetów
        for post in timeline:
            if not isinstance(post, Status):
                raise TypeError("Expected Status class instance, got %s" % type(post))
            minutes = int(post.created_at[11:13])*60 + int(post.created_at[14:16]) # godzina dodania tweeta przeliczona na liczbę minut, jaka upłynęła od północy
            hour_list.append(minutes)
        hour_list = np.reshape(hour_list, (-1, 1)) # zamiana listy na tablicę dwuwymiarową

        max_score = 0
        for k in range(2, 20): # pętla, w której obliczany jest silhouette score dla każdej liczby klastrów z zakresu
            model = KMeans(n_clusters=k).fit(hour_list)
            clusters = model.predict(hour_list)
            score = metrics.silhouette_score(hour_list, clusters);
            if score>max_score: # wyznaczanie maksymalnego silhouette score
                max_score = score
                max = k
        return max
