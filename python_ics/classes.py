from dataclasses import dataclass
import datetime as dt


class Event:
    """
    Event class is the base of this library.
    An ics calendar can contain multiple events so we can use
    this class to create Calendars with multiple Events
     """
    def __init__(
            self,
            title: str,
            dt_start: dt.datetime,
            dt_end: dt.datetime,
            location=None,
            description=None):

        self.title = self._is_valid_title(title)
        self.location = self._is_valid_location(location)
        self.dt_start = self._is_valid_dt(dt_start)
        self.dt_end = self._is_valid_dt(dt_end)
        self.description = self._is_valid_description(description)

        self.validate_time(dt_start, dt_end)

    @staticmethod
    def _is_valid_location(location):
        if location is not None:
            if not isinstance(location, str):
                raise TypeError('location can be str or None type')
        return location

    @staticmethod
    def _is_valid_dt(dt_param):  # noqa
        if not isinstance(dt_param, dt.datetime):
            raise TypeError('dt_start/end attributes can be datetime.datetime type only')
        return dt_param

    @staticmethod
    def _is_valid_title(title):
        if not isinstance(title, str):
            raise TypeError('title can be str type only')
        if len(title) > 75:
            raise ValueError('title cannot be longer than 75 symbols')
        return title

    @staticmethod
    def _is_valid_description(notes):
        if notes is not None:
            if not isinstance(notes, str):
                raise TypeError('notes must be str or None type')
        if len(notes) > 75:
            raise ValueError('title cannot be longer than 75 symbols')
        return notes

    @staticmethod
    def validate_time(start, end):
        if start > end:
            raise ValueError('event cannot start later than it ends')

    def __str__(self):
        return f'{self.title}, {self.location}, {self.description}, {self.dt_end}, {self.dt_start}'


class CalendarSetup:
    # TODO: make interactive timezones work properly
    def __init__(self, timezone_id: str):
        self.timezone_id = self._is_valid_tzid(timezone_id)

    @staticmethod
    def _is_valid_tzid(timezone_id):
        if not isinstance(timezone_id, str):
            raise TypeError('timezone_id must be str type')
        return timezone_id

    def stringify(self):
        setup_file = open('vcalendar_setup.ics', mode='r')
        setup_string = setup_file.read() + '\n'
        # FIXME: this formatting does not work
        setup_string.format(self.timezone_id)
        setup_file.close()
        return setup_string


@dataclass
class BaseCalendar:
    events: [Event]

    def get_execution_string(self):
        # base calendar has no specific setup so it will be automatically generated once the
        # ics file is executed
        base_setup = open('base_setup.txt', mode='r').read()
        execution_string = base_setup

        for event in self.events:
            # making ics compatible strings out of datetime objects
            st_date = event.dt_start.strftime('%Y%m%d')
            st_time = 'T' + event.dt_start.strftime('%H%M%S')
            st_datetime = st_date + st_time

            end_date = event.dt_end.strftime('%Y%m%d')
            end_time = 'T' + event.dt_end.strftime('%H%M%S')
            end_datetime = end_date + end_time

            # writing event block
            event_string = 'BEGIN:VEVENT\n'
            event_string += 'DTSTAMP:20210904T194914Z\n'  # here we have to add a custom date
            event_string += f'DTSTART;TZID=Europe/Paris:{st_datetime}\n'
            event_string += f'DTEND;TZID=Europe/Paris:{end_datetime}\n'
            event_string += f'SUMMARY:{event.title}\n'

            if event.location is not None:
                event_string += f'LOCATION:{event.location}\n'

            if event.description is not None:
                event_string += f'DESCRIPTION:{event.description}\n'
            event_string += 'END:VEVENT\n'

            execution_string += event_string

        execution_string += 'END:VCALENDAR'
        return execution_string


class CalendarWithSetup(BaseCalendar):
    def __init__(self, events, setup):
        super().__init__(self, events)
        self.setup = setup
