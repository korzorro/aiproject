from datetime import timedelta

MAX_TIME_SPAN = timedelta(days=14)

class Task:

    def __init__(self, name=None, deadline=None, duration=None, min_dur=None,
                 max_dur=None, max_dur_daily=None, recurrence=None, range=None):
        self.name = name
        self.deadline = deadline
        self.duration = duration
        self.min_dur = min_dur
        self.max_dur = max_dur
        self.max_dur_daily = max_dur_daily
        self.recurrence = recurrence
        self.range = range

    def __hash__(self):
        return hash(self.name)


class Event:

    def __init__(self, name=None, start=None, duration=None):
        self.name = name
        self.start = start
        self.duration = duration
    
    def ends_before(self, event):
        return self.start + self.duration <= event.start
    
    def meets(self, event):
        return self.start + self.duration == event.start or \
            event.start + event.duration == self.start
    
    def overlaps(self, event):
        return not (event.ends_before(self) or self.ends_before(event))
    
    def __hash__(self):
        return hash(self.name)


class Recurrence:

    def __init__(self, interval=None, occurrences=None):
        self.interval = interval
        self.occurrences = occurrences

    def times(self):
        return MAX_TIME_SPAN.days / self.interval.days
    
    def __hash__(self):
        return hash(self.occurrences)
