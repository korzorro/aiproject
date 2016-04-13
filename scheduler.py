#!/venv/bin/python
from datetime import datetime, timedelta
from models import Task, Event, Recurrence
from parser import parse_data
from constraints import (inrange, cooldown, max_daily, recurrence,
                         durations_met, non_overlapping, is_complete, deadlines_met)
from printer import print_schedule


now = datetime.now()
NOW = now.replace(minute=int(round(float(now.minute)/15))*15 % 60, second=0, microsecond=0)
MAX_TIME_SPAN = timedelta(days=14)

def is_consistent(events, constraints):
    for constraint in constraints:
        if not constraint(events):
            return False
    return True



def csp_solve(solution, domain, constraints):
    if is_complete(solution):
        if is_consistent(solution, constraints):
            print_schedule(solution)
            exit()

    for event in filter(lambda e: not e.start, solution):
        for candidate in domain[event]:
            event.start = candidate
            if is_consistent(solution, constraints):
                return csp_solve(solution, domain, constraints)

    print_schedule(solution)


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


if __name__ == '__main__':
    tasks, events = parse_data('schedule.txt')
    domain = init_domain(events)

    constraints = {
        non_overlapping,
    }
    '''
    cooldown,
    lambda e: durations_met(e, tasks),
    lambda e: deadlines_met(e, tasks),
    lambda e: max_daily(e, tasks),
    lambda e: recurrence(e, tasks),
    '''
    
    csp_solve(events, domain, constraints)
