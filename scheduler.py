#!/venv/bin/python
from recordclass import recordclass
from datetime import datetime, timedelta
from csv import reader
from datetime import datetime
from itertools import combinations


now = datetime.now()
NOW = now.replace(minute=int(round(float(now.minute)/15))*15 % 60)
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


tformat = '%Y/%m/%d%H:%M'


def read_data(filename):
    tasks = list()
    events = list()
    with open(filename) as csvfile:
        csv = reader(csvfile)
        for line in csv:
            if line[0] == 'Task':
                tasks.append(parse_task(line))
            if line[0] == 'Event':
                events.append(parse_event(line))

    return (tasks, events)


def within_range_constraint(events, tasks):
    for task in filter(lambda t: t.range, tasks):
        if not starts_ends_within_range(
                filter(lambda e: event.name == task.name and event.start, events)
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


def max_daily_constraint(events, tasks):
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


def recurring_constraint(events, tasks):
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


def parse_task(line):
    return Task(name=line[1],
                deadline=strf_datetime(line[2]),
                duration=strf_timedelta(line[3]),
                min_dur=strf_timedelta(line[4]),
                max_dur=strf_timedelta(line[5]),
                max_dur_daily=strf_timedelta(line[6]),
                recurrence=parse_recurrence(line[7]))


def parse_event(line):
    return Event(name=line[1],
                 start=datetime.strptime(line[2], tformat),
                 duration=strf_timedelta(line[3]))


def strf_timedelta(s):
    try:
        return timedelta(hours=int(s[:2]), minutes=int(s[3:]))
    except:
        return None


def strf_datetime(s):
    if len(s) > 0:
        datetime.strptime(s, tformat)


def parse_recurrence(s):
    try:
        return Recurrence(interval=timedelta(days=int(s[:2])), occurrences=int(s[2:]))
    except:
        None


def split_tasks(tasks):
    events = list()
    for task in tasks:
        events += split_task(task)
    return events


def split_task(task):
    rem = task.duration
    if task.recurrence:
        rem *= task.recurrence.times()
    events = list()
    while rem > timedelta():
        duration = task.max_dur if task.max_dur < rem else rem
        rem -= duration
        if duration == rem:
            rem == timedelta()

        events.append(Event(name=task.name,
                            start=None,
                            duration=duration))
    
    return events


def is_consistent(events, constraints):
    for constraint in constraints:
        if not constraint(events):
            return False
    return True


def is_complete(events):
    for event in events:
        if not event.start:
            return False
    return True


# Constraints
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


def deadline_met(events, tasks):
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


def csp_solve(solution, domain, constraints):
    if is_complete(solution):
        if is_consistent(solution, constraints):
            print_solution(solution)
            exit()

    for event in filter(lambda e: not e.start, solution):
        for candidate in domain[event]:
            event.start = candidate
            if is_consistent(solution, constraints):
                return csp_solve(solution, domain, constraints)

    print_solution(solution)


def init_domain(events):
    domain = dict()

    for event in events:
        if event.start:
            domain[event] = [event.start]
        else:
            domain[event] = all_time_slots(NOW, NOW + MAX_TIME_SPAN)
    return domain


def all_time_slots(start, end):
    slots = list()
    while start < end:
        slots.append(start)
        start += timedelta(minutes=15)
    return slots


def print_solution(solution):
    for event in sorted(solution, key=lambda e: e.start):
        print('%s %s' % (event.name, event.start))

if __name__ == '__main__':
    tasks, events = read_data('schedule.txt')
    events += split_tasks(tasks)
    domain = init_domain(events)

    constraints = {
        non_overlapping,
        cooldown,
        lambda e: durations_met(e, tasks),
        lambda e: deadline_met(e, tasks),
        lambda e: max_daily_constraint(e, tasks),
        lambda e: recurring_constraint(e, tasks),
    }
    
    csp_solve(events, domain, constraints)
