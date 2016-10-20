from csv import DictReader
from models import Task, Event
from datetime import datetime, timedelta

date_format = '%Y-%m-%d'
time_format = '%H:%M'
datetime_format = '%Y-%m-%d %H:%M'


def parse_events(events_file, min_datetime, max_datetime, resolution):
    return [parse_event(event, min_datetime, max_datetime, resolution)
            for event in get_data(events_file)]


def parse_tasks(tasks_file, min_datetime, max_datetime, resolution):
    return [parse_task(task, min_datetime, max_datetime) for task in get_data(tasks_file)]


def get_data(filename):
    with open(filename) as csvfile:
         return [line for line in DictReader(csvfile)]

def max_repeat_quantity(min_datetime, max_datetime, repeat_frequency, repeat_quantity):
    max_repeat_quantity = int(
        (max_datetime - min_datetime).total_seconds() / repeat_frequency.total_seconds())
    if repeat_quantity == 0:
        return max_repeat_quantity
    return min([max_repeat_quantity, repeat_quantity])

def parse_task(task, min_datetime, max_datetime, resolution):
    repeat_quantity = int(task['repeat_quantity']) if task['repeat_quantity'] else 0
    repeat_frequency = parse_repeat_frequency(task['repeat_frequency'])
    if repeat_frequency:
        repeat_quantity = max_repeat_quantity(
            min_datetime, max_datetime, repeat_frequency, repeat_quantity)
    # Come back here to make sure start times don't start after max datetime
    return Task(name=task['name'],
                start=parse_datetime(task['start']),
                due=parse_datetime(task['due']),
                duration=parse_timedelta(task['duration']),
                min_duration=parse_timedelta(task['min_duration']),
                max_duration=parse_timedelta(task['max_duration']),
                max_daily_duration=parse_timedelta(task['max_daily_duration']),
                repeat_frequency=repeat_frequency,
                repeat_quantity=repeat_quantity,
                time_range=parse_time_range(task['time_range']))


def parse_event(event, min_datetime, max_datetime, resolution):
    start = parse_datetime(event['start'])
    repeat_frequency = parse_repeat_frequency(event['repeat_frequency'])
    repeat_quantity = int(event['repeat_quantity']) if event['repeat_quantity'] else 0
    if repeat_frequency:
        if repeat_frequency:
            repeat_quantity = max_repeat_quantity(
                min_datetime, max_datetime, repeat_frequency, repeat_quantity)
    duration = max_datetime - min_datetime
    domain_length = int(duration.total_seconds() / resolution.total_seconds())
    domain = {start + (resolution * step) for step in range(domain_length)}
    events = list()
    for i in range(repeat_quantity+1):
        events.append(
            Event(name=event['name'],
                  start=start+(repeat_frequency*i),
                  duration=parse_timedelta(event['duration']),
                  domain=domain))
    return events
 
def parse_datetime(s):
    return datetime.strptime(s, datetime_format) if s else None


def parse_timedelta(hours):
    return timedelta(hours=int(float(hours)),
                     minutes=60*(float(hours)-int(float(hours)))) if hours else None


def parse_time_range(s):
    return list(map(lambda t: datetime.strptime(t, time_format).time(), s.split('-'))) \
        if s else None
    
 
def parse_repeat_frequency(days):
    return timedelta(days=int(days)) if days else None

events = parse_events('schedule1/events.csv', datetime.now(), datetime.now() + timedelta(days=14), timedelta(minutes=15))
print(events)
