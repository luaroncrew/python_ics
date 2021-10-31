import datetime as dt

from classes import CalendarSetup, BaseCalendar, Event
from writers import create_ics


def create_base_calendar_with_one_event():
    event = Event(
        'title',
        dt_start=dt.datetime.now(),
        dt_end=dt.datetime.now() + dt.timedelta(hours=4),
        description='little description',
        location='at home'
    )

    calendar = BaseCalendar([event])
    create_ics(calendar)


create_base_calendar_with_one_event()

