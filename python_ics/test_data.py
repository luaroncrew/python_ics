import datetime as dt

from classes import CalendarSetup, Calendar, Event
from writers import create_ics

event = Event(
    'title',
    dt_start=dt.datetime.now(),
    dt_end=dt.datetime.utcnow(),
    description='little description',
    location='at home'
)
setup = CalendarSetup(timezone_id='Europe/Paris')

calendar = Calendar([event], setup)

create_ics(calendar)
