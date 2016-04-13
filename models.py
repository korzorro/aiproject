from datetime import timedelta

MAX_TIME_SPAN = timedelta(days=14)


class Task:

    def __init__(self, name=None, deadline=None, duration=None, min_dur=None,
                 max_dur=None, max_dur_daily=None, recurrence=None, time_range=None):
        self.name = name
        self.deadline = deadline
        self.duration = duration
        self.min_dur = min_dur
        self.max_dur = max_dur
        self.max_dur_daily = max_dur_daily
        self.recurrence = recurrence
        if time_range:
            self.time_range_lower = time_range[0]
            self.time_range_upper = time_range[1]
        else:
            self.time_range_lower = None
            self.time_range_upper = None

    def __hash__(self):
        return hash(self.name)


class Event:

    def __init__(self, name=None, start=None, duration=None, recurrence=None):
        self.name = name
        self.start = start
        self.duration = duration
        self.recurrence = recurrence
        
    def ends_before(self, event):
        return self.start + self.duration <= event.start
    
    def meets(self, event):
        return self.start + self.duration == event.start or \
            event.start + event.duration == self.start
    
    def overlaps(self, event):
        return not (event.ends_before(self) or self.ends_before(event))

    @property
    def end(self):
        return self.start + self.duration

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


def within_interval(start, end, target):
    return target >= start and target < end


def divide_timedelta(a, b):
    if b == timedelta():
        print('Error: Divide by 0 time')
        exit()
    count = 0
    while a > timedelta():
        a -= b
        count += 1
    return count

