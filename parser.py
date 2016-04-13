from csv import reader
from models import Task, Event, Recurrence
from datetime import datetime, timedelta, time
from copy import deepcopy

tformat = '%Y/%m/%d%H:%M'


def parse_data(filename):
    tasks = list()
    events = list()
    with open(filename) as csvfile:
        csv = reader(csvfile)
        for line in csv:
            if line[0] == 'Task':
                tasks.append(parse_task(line))
            if line[0] == 'Event':
                events.append(parse_event(line))

    return (tasks, repeat_recurring_events(events) + split_tasks(tasks))


def parse_task(line):
    return Task(name=line[1],
                deadline=strf_datetime(line[2]),
                duration=strf_timedelta(line[3]),
                min_dur=strf_timedelta(line[4]),
                max_dur=strf_timedelta(line[5]),
                max_dur_daily=strf_timedelta(line[6]),
                recurrence=parse_recurrence(line[7]),
                time_range=parse_time_range(line[8]))


def parse_event(line):
     return Event(name=line[1],
                  start=datetime.strptime(line[2], tformat),
                  duration=strf_timedelta(line[3]),
                  recurrence=parse_recurrence(line[4]))


def parse_time_range(s):
    try:
        time_range = tuple(map(lambda t: datetime.strptime(t, '%H:%M').time(), s.split('-')))
        return time_range
    except:
        return None
    
 
def parse_recurrence(line):
    try:
        return Recurrence(interval=timedelta(days=int(line[:2])), occurrences=int(line[2:]))
    except:
        None


def strf_timedelta(s):
    try:
        return timedelta(hours=int(s[:2]), minutes=int(s[3:]))
    except:
        return None


def strf_datetime(datetime_string):
    if len(datetime_string) > 0:
        datetime.strptime(datetime_string, tformat)


def split_tasks(tasks):
    events = list()
    for task in tasks:
        events += split_task(task)
    return events


def repeat_recurring_events(events):
    all_events = list()
    for event in events:
        if event.recurrence:
            for i in range(event.recurrence.times()):
                e = deepcopy(event)
                e.start += event.recurrence.interval * i
                all_events.append(e)
        else:
            all_events.append(e)

    return all_events

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

