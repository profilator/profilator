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
        # zwraca procent odpowiedzi z pośród wszystkich statusów w timeline
        replies = self.replies_count(timeline)
        return replies / len(timeline)
