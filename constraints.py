from itertools import combinations
from datetime import timedelta, datetime
from models import within_interval, divide_timedelta

now = datetime.now()
NOW = now.replace(minute=int(round(float(now.minute)/15))*15 % 60, second=0, microsecond=0)

def is_complete(events):
    for event in events:
        if not event.start:
            return False
    return True


def inrange(events, tasks):
    for task in filter(lambda t: t.time_range_lower, tasks):
        for event in filter(lambda e: e.name == task.name, events):
            if event.start.time() < task.time_range_lower:
                if task.time_range_lower > task.time_range_upper:
                    if event.start.time() > task.time_range_upper:
                        return False
                else:
                    return False
            if event.end.time() > task.time_range_upper:
                if task.time_range_lower > task.time_range_upper:
                    if event.end.time() < task.time_range_lower:
                        return False
                else:
                    return False
            if event.start.time() > event.end.time():
                if task.time_range_upper > task.time_range_lower:
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
    events = sorted(events, key=lambda e: e.start)
    for i in range(len(events)-1):
        event1, event2 = (events[i], events[i+1])
        if event1.name == event2.name and event2.start - event1.start < event1.duration*2:
            return False
    return True


def max_daily(events, tasks):
    for task in filter(lambda t: t.max_dur_daily, tasks):
        if max_daily_exceeded(filter(lambda e: e.name == task.name, events), task):
            return False
    return True


def max_daily_exceeded(events, task):
    today = NOW.replace(hour=0, minute=0)
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
    for task in filter(lambda t: t.recurrence, tasks):
        corresponding_events = list(filter(lambda e: e.name == task.name, events))
        scheduled_tasks = list(filter(lambda e: e.start, corresponding_events))
        if len(corresponding_events) == len(scheduled_tasks):
            if not recurrence_met(filter(lambda e: e.name == task.name, events), task):
                return False
    return True


def recurrence_met(events, task):
    cur = NOW.replace(hour=0, minute=0)
    last_event = max(events, key=lambda e: e.start)
    interval = task.recurrence.interval
    num_intervals = divide_timedelta((last_event.start - cur), interval)
    for i in range(num_intervals):
        total_duration = timedelta()
        start = cur + (interval * i)
        end = start + interval
        interval_events = filter(lambda e: within_interval(start, end, e.start), events)
        if not duration_met(interval_events, task):
            '''
            print(task.name)
            for event in events:
                print(event.start)
            print('*'*100)
            for event in interval_events:
                print(event.start)
            return False
            '''
    return True


def sum_duration(events):
    total = timedelta()
    for event in events:
        total += event.duration
    return total


def durations_met(events, tasks):
    for task in tasks:
        if not duration_met(
                filter(lambda e: e.name == task.name, events),
                task):
            return False
    return True


def duration_met(events, task):
    return sum_duration(events) >= task.duration


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
    for event1, event2 in combinations(events, 2):
        if event1.overlaps(event2):
            return False
    return True
