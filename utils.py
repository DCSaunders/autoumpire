#!/usr/bin/env python
import time
    
def get_report_date(original_date):
    date_struct = get_datetime(original_date)
    new_format = '%A, %d %B'
    new_date = time.strftime(new_format, date_struct)
    return new_date


def get_datetime(date, event_time=None):
    date_format = '%d.%m.%y'
    if event_time:
        date = ' '.join((date, event_time))
        date_format = ' '.join((date_format, '%H:%M'))
    return time.strptime(date, date_format)
