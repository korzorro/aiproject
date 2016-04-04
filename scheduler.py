#!venv/bin/python

from recordclass import recordclass
from datetime import datetime, timedelta
from csv import reader
from datetime import datetime


Task = recordclass('Task', 'name deadline duration min_dur max_dur max_dur_daily recurrence')
Event = recordclass('Event', 'name start duration')
Recurrence = recordclass('Recurrence', 'type occurrences')

t_step = timedelta(minutes=15)

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


def is_consistent(tasks, events, constraints):
    for constraint in constraints:
        if not constraint(events):
            return False
    return True


def is_complete(events):
    for event in events:
        if event.start_time is None:
            return False
    return True


def durations_met(events, tasks):
    for task in tasks:
        if not duration_met(task, filter(lambda e: e.name == task.name, events)):
            return False
    return True


def duration_met(task, events):
    duration = timedelta()
    for event in events:
        duration += event.duration
    return duration >= task.duration
        

def deadline_met(events, tasks):
    for task in tasks:
        if not duration_met(task, filter(lambda e: e.name == task.name and
                                         e.start+e.duration < task.deadline, events)):
            return False
    return True

def non_overlapping(events):
    for i, event in enumerate(events):
        for j in range(i, len(events)):
            if not event == events[i]:
                if event.start < events[i].start:
                    if event.start+event.duration > events[i].start:
                        return 
if __name__ == '__main__':
    tasks, events = read_data('schedule.txt')
    print(split_tasks(tasks))