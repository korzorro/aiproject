#!/venv/bin/python
from recordclass import recordclass
from datetime import datetime, timedelta
from csv import reader
from datetime import datetime
from itertools import combinations


class Task:
    def __init__(self, name=None, deadline=None, duration=None, min_dur=None,
                 max_dur=None, max_dur_daily=None, recurrence=None):
        self.name = name
        self.deadline = deadline
        self.duration = duration
        self.min_dur = min_dur
        self.max_dur = max_dur
        self.max_dur_daily = max_dur_daily
        self.recurrence = recurrence

    def __hash__(self):
        return hash(self.name)


class Event:
    def __init__(self, name=None, start=None, duration=None):
        self.name = name
        self.start = start
        self.duration = duration

    def __hash__(self):
        return hash(self.name)


class Recurrence:
    def __init__(self, type=None, occurrences=None):
        self.type = type
        self.occurrences = occurrences

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
        return Recurrence(type=s[0], occurrences=int(s[1:]))
    except:
        None


def split_tasks(tasks):
    events = list()
    for task in tasks:
        events += split_task(task)
    return events


def split_task(task):
    rem = task.duration
    events = list()
    while rem > timedelta():
        duration = task.min_dur if task.min_dur < rem else rem
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
        if event.start_time is None:
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
    for task in tasks:
        if not duration_met(task,
                            filter(lambda e: e.start and task.deadline and
                                   e.name == task.name and
                                   e.start+e.duration < task.deadline,
                                   events)):
            return False
    return True


def non_overlapping(events):
    for event1, event2 in combinations(events, 2):
        if overlaps(event1, event2):
            return False
    return True


def overlaps(event1, event2):
    if not event1.start or not event2.start:
        return False
    if event1.start < event2.start:
        return event1.start + event1.duration > event2.start
    elif event1.start > event2.start:
        return event2.start + event2.duration > event1.start
    else:
        return False


# Solution is a dict
def csp_solve(solution, domain, constraints):
    if is_consistent(solution, constraints) and is_complete(solution):
        return solution

    temp_solution = solution
    for event in solution:
        print(event.start)
        if not event.start:
            for candidate in domain[event]:
                event.start = candidate
                if csp_solve(solution, domain, constraints):
                    return solution
                else:
                    csp_solve(temp_solution, domain, constraints)
    return list()


def init_domain(events):
    domain = dict()
    now = datetime.now()
    for event in events:
        if event.start:
            domain[event] = [event.start]
        else:
            domain[event] = all_time_slots(now, now + timedelta(days=7))
    return domain


def all_time_slots(start, end):
    slots = list()
    while start < end:
        slots.append(start)
        start += timedelta(minutes=15)
    return slots


if __name__ == '__main__':
    tasks, events = read_data('schedule.txt')
    events += split_tasks(tasks)
    domain = init_domain(events)

    constraints = {
        non_overlapping,
        lambda e: durations_met(e, tasks),
        lambda e: deadline_met(e, tasks),
    }
    
    solution = csp_solve(events, domain, constraints)
    print(solution)
