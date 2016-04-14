from itertools import combinations
from datetime import timedelta, datetime
from models import within_interval, divide_timedelta

now = datetime.now()
NOW = now.replace(minute=int(round(float(now.minute)/15))*15 % 60, second=0, microsecond=0)
MAX_TIME_SPAN = timedelta(days=14)


def is_complete(events):
    for event in events:
        if not event.start:
            return False
    return True


def inbetween(event, task):
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


def inrange(events, tasks):
    for task in tasks:
        if task.time_range_lower:
            for event in events:
                if event.name == task.name:
                    if not inbetween(event, task):
                        return False

    return True


def cooldown(events):
    events = sorted(events, key=lambda e: e.start)
    for i in range(len(events)-1):
        event1, event2 = (events[i], events[i+1])
        if event1.name == event2.name and event2.start - event1.start < event1.duration*3/2:
            return False
    return True


def max_daily(events, tasks):
    today = NOW.replace(hour=0, minute=0)
    endday = today + timedelta(days=1) - timedelta(minutes=5)
    for task in tasks:
        if task.max_dur_daily:
            e = sorted(events, key=lambda e: e.start)
            duration = timedelta()
            a = list()
            for event in e:
                if event.name == task.name:
                    if event.start > today and event.start < endday:
                        a.append(event)
                        duration += event.duration
                    else:
                        a = list()
                        duration = timedelta()
                        today += timedelta(days=1)
                        endday += timedelta(days=1)
                    if duration > task.max_dur_daily:
                        '''
                        print(duration)
                        print(task.max_dur_daily)
                        for g in a:
                            print(g.start)
                        '''
                        return False
    return True


def bucketize(l, buckets, key=lambda e: e):
    buck = [list() for i in range(len(buckets)-1)]
    for e in l:
        for i, b in enumerate(buckets):
            if key(e) < b:
                buck[i-1].append(e)
                break
    return buck


def max_daily_exceeded(events, task):
    today = NOW.replace(hour=0, minute=0)
    day = timedelta(days=1)
    days = divide_timedelta(MAX_TIME_SPAN, day)
    b = [today + (i * day) for i in range(days)]
    buckets = bucketize(events, b, key=lambda e: e.start)
    for bucket in buckets:
        total_duration = timedelta()
        for event in bucket:
            total_duration += event.duration
            if total_duration > task.max_dur_daily:
                return True
        today += timedelta(days=1)
    return False


def recurrence(events, tasks):
    for task in filter(lambda t: t.recurrence, tasks):
        '''
        if len(corresponding_events) == len(scheduled_tasks):
        '''
        corresponding_events = list(filter(lambda e: e.name == task.name, events))
        scheduled_tasks = list(filter(lambda e: e.start, corresponding_events))
        if sum_duration(scheduled_tasks) >= task.duration:
            if not recurrence_met(filter(lambda e: e.name == task.name and e.start, events), task):
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
        end = start + interval + timedelta(minutes=5)
        interval_events = filter(lambda e: within_interval(start, end, e.start), events)
        total_flag = False
        for e in interval_events:
            total_duration += e.duration
            if total_duration >= task.duration:
                if total_flag:
                    '''
                    print(task.name)
                    for event in interval_events:
                        print(event.start)
                    '''
                    return False
                else:
                    total_flag = True
        ''''
        if not total_duration >= task.duration:
            print(task.name)
            print(total_duration)
            print(task.duration)

            print(task.name)
            print(start)
            print(end)

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
    events = list(sorted(events, key=lambda e: e.start))
    for i in range(len(events)-1):
        event1 = events[i]
        event2 = events[i+1]
        if event1.overlaps(event2):
            return False
    return True
