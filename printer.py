from datetime import timedelta, datetime
from models import within_interval, divide_timedelta
from copy import deepcopy


ONE_WEEK = timedelta(days=7)
COLUMN_WIDTH = 10
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday']


def print_schedule(events, slot_length=timedelta(minutes=15)):
    events = expand_events_into_slots(events, slot_length)
    beginning = last_monday()
    print(beginning)
    last_event = max(events, key=lambda e: e.start)
    end = last_event.start + last_event.duration

    num_weeks = divide_timedelta((end - beginning), ONE_WEEK)

    
    for week in range(1, num_weeks+1):
        start = beginning + (ONE_WEEK * (week-1))
        end = start + ONE_WEEK
        week_events = sorted(
            sorted(
                filter(lambda e: within_interval(start, end, e.start),
                       events),
                key=lambda e: e.start,
                reverse=True),
            key=lambda e: e.start.time(),
            reverse=True)
        print_week_header(week)
        print_week(start, week_events, slot_length)


def expand_events_into_slots(events, slot_length):
    expanded_events = list()
    count = 0
    for event in events:
        count += 1
        for i in range(divide_timedelta(event.duration, slot_length)):
            e = deepcopy(event)
            e.duration = slot_length
            e.start += slot_length * i
            expanded_events.append(e)
    return expanded_events


def print_week(week_start, events, slot_length):
    cur = week_start
    for slot in range(divide_timedelta(timedelta(days=1), slot_length)):
        if len(events) == 0:
            continue
        line = '|' + center_string(cur.strftime('%H:%M'))
        for i in range(7):
            if len(events) > 0:
                event = events[-1]
                days = timedelta(days=1) * i
                if event.start == cur + days:
                    line += '|' + center_string(event.name)
                    events.pop()
                else:
                    line += '|' + center_string('')
            else:
                line += '|' + center_string('')
        cur += slot_length
        print(line + '|')
        print('-'*line_width())
    assert len(events) == 0


def line_width():
    return (COLUMN_WIDTH + 1)*8 + 1


def last_monday():
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return now - timedelta(days=now.weekday())
    

def center_string(s):
    spaces = COLUMN_WIDTH - len(s)
    return ' '*(spaces/2) + s + ' '*(spaces - (spaces/2))


def print_week_header(week):
    print('\nWEEK %d' % week)
    print('-'*line_width())
    line = '|' + center_string('')
    for day in weekdays:
        line += '|' + center_string(day)
    print(line + '|')
    print('-'*line_width())
