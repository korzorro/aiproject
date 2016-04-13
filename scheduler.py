#!/venv/bin/python
from datetime import datetime, timedelta
from models import Task, Event, Recurrence
from parser import parse_data
from constraints import (inrange, cooldown, max_daily, recurrence,
                         durations_met, non_overlapping, is_complete, deadlines_met,
                         inrange)
from printer import print_schedule
import time
from copy import deepcopy

now = datetime.now()
NOW = now.replace(minute=int(round(float(now.minute)/15))*15 % 60, second=0, microsecond=0)
MAX_TIME_SPAN = timedelta(days=14)

def csp_solve(solution, domain, is_consistent):
    if is_complete(solution):
        print('Complete')
        if is_consistent(solution):
            return solution
        
    for event in filter(lambda e: not e.start, solution):
        for candidate in domain[event]:
            event.start = candidate
            if is_consistent(solution):
                sln = csp_solve(solution, domain, is_consistent)
                if sln != None:
                    print('this')
                    print_schedule(sln)
                    exit()
    return None

'''
def forward_check(assigned, not_assigned, domain, is_consistent):
    for event in not_assigned:
        for candidate in domain[event]:
            event.start = candidate
            if not is_consistent(solution):
                domain[event].remove(candidate)
        event.start = None
    return domain
'''

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

    
def is_consistent(tasks):
    def _is_consistent(solution):
        assigned = filter(lambda e: e.start, solution)
        if not inrange(assigned, tasks):
            return False
        if not cooldown(assigned):
            return False
        if not max_daily(assigned, tasks):
            return False
        if not non_overlapping(assigned):
            return False
        if not deadlines_met(solution, tasks):
            return False
        if not recurrence(solution, tasks):
            return False
        return True


    return _is_consistent


if __name__ == '__main__':
    tasks, events = parse_data('schedule.txt')
    domain = init_domain(events)
    is_consistent = is_consistent(tasks)

    csp_solve(events, domain, is_consistent)
    

