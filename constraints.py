from itertools import combinations
from datetime import timedelta, datetime

now = datetime.now()
NOW = now.replace(minute=int(round(float(now.minute)/15))*15 % 60)

def is_complete(events):
    for event in events:
        if not event.start:
            return False
    return True


def inrange(events, tasks):
    for task in filter(lambda t: t.range, tasks):
        if not starts_ends_within_range(
                filter(lambda e: event.name == task.name and event.start, events),
                task):
            return False
    return True


def starts_ends_within_range(events, task):
    for event in events:
        if task.range[0] < task.range[1]:
            if event.start.time < task.range[0]:
                return False
            if event.start.time + event.duration > task.range[1]:
                return False
        else:
            if event.start.time > task.range[0]:
                return False
            if event.start.time + event.duration < task.range[1]:
                return False
    return True


def cooldown(events):
    for event1, event2 in combinations(events, 2):
        if event1.name == event2.name and event1.start and event2.start:
            if abs(event1.start - event2.start) < event1.duration*2:
                return False
    return True


def max_daily(events, tasks):
    for task in filter(lambda t: t.max_dur_daily, tasks):
        if max_daily_exceeded(filter(lambda e: e.name == task.name and e.start, events), task):
            return False
    return True


def max_daily_exceeded(events, task):
    today = NOW.replace(hour=0, minute=0, second=0)
    events = list(events)
    if len(events) == 0:
        return False
    last_event = list(sorted(events, key=lambda e: e.start, reverse=True))[0]
    while today < last_event.start:
        total_duration = timedelta()
        for event in filter(lambda e: e.start >= today and e.start < today + timedelta(days=1), events):
            total_duration += event.duration
        if total_duration > task.max_dur_daily:
            return True
        today += timedelta(days=1)
    return False


def recurrence(events, tasks):
    if not is_complete(events):
        return True
    for task in filter(lambda t: t.recurrence, tasks):
        if not recurrence_met(filter(lambda e: e.start and e.name == task.name, events), task):
            return False
    return True


def recurrence_met(events, task):
    today = NOW.replace(hour=0, minute=0, second=0)
    events = list(events)
    if len(events) == 0:
        return False
    last_event = list(sorted(events, key=lambda e: e.start, reverse=True))[0]
    while today < last_event.start:
        total_duration = timedelta()
        for event in filter(lambda e: e.start >= today and e.start < today + task.recurrence.interval, events):
            total_duration += event.duration
        if total_duration < task.duration:
            return False
        today += task.recurrence.interval
    return True


def durations_met(events, tasks):
    for task in tasks:
        if not duration_met(
                task,
                filter(lambda e: e.name == task.name, events)):
            return False
    return True


def duration_met(task, events):
    duration = timedelta()
    for event in events:
        duration += event.duration
    return duration >= task.duration


def deadlines_met(events, tasks):
    for task in filter(lambda t: t.deadline, tasks):
        if not duration_met(task,
                            filter(lambda e: e.start and
                                   e.name == task.name and
                                   e.start+e.duration < task.deadline,
                                   events)):
            return False
    return True


def non_overlapping(events):
    for event1, event2 in combinations(filter(lambda e: e.start, events), 2):
        if event1.overlaps(event2) and event1 != event2:
            return False
    return True
