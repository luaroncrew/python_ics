# python-ics

python-ics is a library for creating Icalendar files easily.

iCalendar is used and supported by many products, including:
* Google Calendar
* Apple Calendar (formerly iCal)
* Microsoft Outlook
* HCL Domino (formerly IBM Notes and Lotus Notes)
* Yahoo! Calendar
* Evolution (software)
* eM Client
* Lightning extension for Mozilla Thunderbird and SeaMonkey

## Installation



```bash
pip install pyhton-ics
```

## Basic usage

```python
import datetime as dt
from pyhton_ics import Event, BaseCalendar

meeting = Event(
        title='Elon Musk birthday',
        dt_start=dt.datetime.now(),
        dt_end=dt.datetime.now() + dt.timedelta(hours=4),
        description='a little party on a spaceship',
        location='Mars'
    )
    
reading_club = Event(
        title='reading club',
        dt_start=dt.datetime.now()+ dt.timedelta(hours=4) ,
        dt_end=dt.datetime.now() + dt.timedelta(hours=8),
        description='today speaking about Jules Verne',
        location='246 rue de la Marne'
    )
    
calendar = BaseCalendar(events=[meeting, reading_club])

# export the calendar as an ics file
calendar.export(destination='calendars/important', filename='very_important_agenda')
```

## Event serialization notes

Generated `.ics` output should include a per-event `UID` when one is not supplied, emit a fresh UTC `DTSTAMP` at serialization time, and preserve timezone-aware datetimes instead of forcing `Europe/Paris`.

Text values such as `SUMMARY`, `LOCATION`, and `DESCRIPTION` are expected to be escaped according to RFC 5545, and long content lines should be folded onto continuation lines so the result imports cleanly across common calendar clients.


## License
[MIT](https://choosealicense.com/licenses/mit/)
