from datetime import timedelta, datetime


ONE_WEEK = timedelta(days=7)
COLUMN_WIDTH = 10
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday']


def print_schedule(events, slot_length=timedelta(minutes=15)):
    events = list(sorted(events, key=lambda e: e.start))
    events.reverse()
    beginning = min(events, key=lambda e: e.start).start
    end = max(events, key=lambda e: e.start)
    end = end.start + end.duration

    num_weeks = divide_timedelta((end -beginning), ONE_WEEK)
    
    print(num_weeks)
    for week in range(1, num_weeks+1):
        print_week(week, events, slot_length)


def divide_timedelta(a, b):
    count = 0
    while a > timedelta():
        a -= b
        count += 1
    return count

def print_week(week, events, slot_length):
    print_week_header(week)
    beginning = last_monday().replace(hour=0, minute=0, second=0, microsecond=0)
    cur = beginning
    for slot in range(divide_timedelta(timedelta(days=1), slot_length)):
        if len(events) == 0:
            break
        line = '|' + center_string(cur.strftime('%H:%M'))
        for i in range(7):
            if len(events) == 0:
                break

            if events[-1].start == cur + timedelta(days=i):
                
                event = events.pop()
                line += '|' + center_string(event.name)
            else:
                line += '|' + center_string('')
        cur += slot_length
        print(line)
        print('-'*line_width())


def line_width():
    return (COLUMN_WIDTH + 1)*7 + 1

def last_monday():
    now = datetime.now()
    return now - timedelta(days=now.weekday())
    

def center_string(s):
    spaces = COLUMN_WIDTH - len(s)
    return ' '*(spaces/2) + s + ' '*(spaces - (spaces/2))


def print_week_header(week):
    print('\nWEEK %d' % week)
    print('-'*line_width())
    line = center_string('')
    for day in weekdays:
        line += '|' + center_string(day)
    print(line + '|')
    print('-'*line_width())
