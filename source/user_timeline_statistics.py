from twitter import Api


class UserTimelineStatistics(object):
    # tutaj wrzucamy metody służące do zbierania podstawowych statystyk użytkownika

    def replies_count(self, timeline):
        replies = 0
        # zwraca ile spośród wpisów użytkownika to odpowiedzi
        for status in timeline:
            if "in_reply_to_status_id" in status.asDict():
                replies += 1
        return replies

    def replies_percentage(self, timeline):
        # zwraca procent odpowiedzi spośród wszystkich statusów w timeline
        replies = self.replies_count(timeline)
        return replies / len(timeline) * 100

    def day_counter(self, timeline):
        # zwraca słownik zawierający ilość postów, które dodano w określonych dniach tygodnia
        import collections as col
        # nie jestem pewien, czy ten import powinien być poza definicją metody
        days = col.Counter()
        for k in timeline:
            days[k.created_at[:3]] += 1
        return days
    
    def most_active_day(self, timeline):
        # zwraca dzień, w którym pojawiło się najwięcej postów
        days = day_counter(timeline)
        d = 0
        for i, v in days.items():
            if(v > d):
                d = v
                mad = i
        return mad

    def average_favourites(self, timeline):
        # zwraca średnią ilość ulubionych pod postami użytkownika
        total_likes = 0
        posts = 0
        for post in timeline:
            total_likes += post["favorite_count"]
            posts += 1
        return posts / total_likes
