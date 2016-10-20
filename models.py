from datetime import timedelta, datetime

cooldown_coefficient = 1


class Task:

    def __init__(self, name, duration, min_duration, max_duration, max_daily_duration,
                 start=None, due=None, time_range=None, repeat_frequency=None,
                 repeat_quantity=None):
        self.name = name
        self.duration = duration
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.max_daily_duration = max_daily_duration
        self.repeat_frequency=repeat_frequency
        self.repeat_quantity=repeat_quantity
        self.start = start if start else datetime.min
        self.due = due if due else datetime.max
        self.events = [list() for i in range(self.repeat_quantity)]
        self.sum_duration = [timedelta() for event in self.events]
        
        if time_range:
            self.time_range_lower = time_range[0]
            self.time_range_upper = time_range[1]
        else:
            self.time_range_lower = None
            self.time_range_upper = None

    @property
    def is_duration_met(self):        
        return self.sum_duration == self.duration

    def add_event(self, event):
        repeat_number = self.get_repeat_number(event)
        if self.check_constraints(event, repeat_number):
            self.events[repeat_number].append(event)
            self.sum_duration[repeat_number] += event.duration
            return True
        else:
            return False

    def check_constraints(self, event, repeat_number):
        if not self.cooldown_constraint(event, repeat_number):
            return False
        if not self.max_daily_constraint(event, repeat_number):
            return False
    
    def cooldown_constraint(self, candidate, repeat_number):
        for event in self.events[repeat_number]:
            if candidate.starts_before(event):
                if event.start - candidate.start < \
                   event.duration * cooldown_coefficient:
                    return False
            else:
                if candidate.start - event.start < \
                   event.duration * cooldown_coefficient:
                    return False
        return True
            
    def max_daily_constraint(self, candidate, repeat_number):
        day_total = candidate.duration
        for event in self.events[repeat_number]:
            if event.start.date == candidate.start.date:
                day_total += event.duration
            if day_total > self.max_daily_duration:
                return False
        return True

    def get_repeat_number(self, event):
        repeat_number = 0
        start = self.start
        end = start + (self.repeat_frequency)
        if self.repeat_frequency and self.repeat_quantity:
            while(not event.starts_inbetween(start, end) and repeat_number <= self.repeat_quantity):
                start += self.repeat_frequency
                end += self.repeat_frequency
                repeat_number += 1
        return repeat_number

    def __str__(self):
        s = ''
        for key, val in self.__dict__.items():
            s += '%s: %s\n' % (key, val)
        return s
    
    def __hash__(self):
        return self.name


class Event:

    def __init__(self, name, domain, duration, start=None):
        self.name = name
        self.domain = domain
        self.duration = duration
        self.start = start

    @property
    def start(self):
        return self.__start
    
    @start.setter
    def start(self, target):
        self.__start = target
        self.slots_used = set(filter(lambda t: self.contains(t) , self.domain))
        
    def ends_on(self, target):
        return self.end == target
    
    def ends_after(self, target):
        return self.end > target
    
    def ends_before(self, target):
        return self.end < target

    def starts_on(self, target):
        return self.start == target

    def starts_after(self, target):
        return self.start > target

    def starts_before(self, target):
        return self.start < target

    def starts_inbetween(self, start, end):
        return self.starts_after(start) and self.starts_before(end)

    def ends_inbetween(self, start, end):
        return self.ends_after(start) and self.ends_before(end)

    def overlaps(self, event):
        return self.starts_inbetween or self.ends_inbetween

    def contains(self, target):
        return (self.starts_before(target) and self.ends_after(target)) or \
            self.starts_on(target)
        
    @property
    def end(self):
        return self.start + self.duration

    def __str__(self):
        s = ''
        for key, val in self.__dict__.items():
            s += '%s: %s\n' % (key, val)
        return s
