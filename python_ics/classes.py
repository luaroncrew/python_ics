import datetime as dt
import uuid
from dataclasses import dataclass
from pathlib import Path


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
            description=None,
            uid=None):

        self.title = self._is_valid_title(title)
        self.location = self._is_valid_location(location)
        self.dt_start = self._is_valid_dt(dt_start)
        self.dt_end = self._is_valid_dt(dt_end)
        self.description = self._is_valid_description(description)
        self.uid = self._is_valid_uid(uid)

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
        return title

    @staticmethod
    def _is_valid_description(notes):
        if notes is not None:
            if not isinstance(notes, str):
                raise TypeError('notes must be str or None type')
        return notes

    @staticmethod
    def _is_valid_uid(uid):
        if uid is None:
            return str(uuid.uuid4())
        if not isinstance(uid, str):
            raise TypeError('uid must be str or None type')
        return uid

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
        setup_file = open(Path(__file__).with_name('vcalendar_setup.ics'), mode='r')
        setup_string = setup_file.read() + '\n'
        # FIXME: this formatting does not work
        setup_string.format(self.timezone_id)
        setup_file.close()
        return setup_string


@dataclass
class BaseCalendar:
    events: [Event]

    @staticmethod
    def _format_utc(dt_param):
        return dt_param.astimezone(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')

    @staticmethod
    def _format_datetime_property(name, dt_param):
        if dt_param.tzinfo is None or dt_param.utcoffset() is None:
            return f'{name}:{dt_param.strftime("%Y%m%dT%H%M%S")}'
        return f'{name}:{BaseCalendar._format_utc(dt_param)}'

    @staticmethod
    def _escape_text(value):
        escaped_value = value.replace('\\', '\\\\')
        escaped_value = escaped_value.replace('\r\n', '\n').replace('\r', '\n')
        escaped_value = escaped_value.replace('\n', '\\n')
        escaped_value = escaped_value.replace(';', '\\;').replace(',', '\\,')
        return escaped_value

    @staticmethod
    def _fold_content_line(line, limit=75):
        folded_lines = []
        current = ''
        current_length = 0

        for char in line:
            char_length = len(char.encode('utf-8'))
            if current and current_length + char_length > limit:
                folded_lines.append(current)
                current = f' {char}'
                current_length = 1 + char_length
                continue

            current += char
            current_length += char_length

        folded_lines.append(current)
        return '\r\n'.join(folded_lines)

    def get_execution_string(self):
        # base calendar has no specific setup so it will be automatically generated once the
        # ics file is executed
        base_setup = Path(__file__).with_name('base_setup.txt').read_text(encoding='utf-8')
        execution_lines = [line.rstrip('\r') for line in base_setup.splitlines()]
        dtstamp = self._format_utc(dt.datetime.now(dt.timezone.utc))

        for event in self.events:
            event_lines = [
                'BEGIN:VEVENT',
                f'UID:{event.uid}',
                f'DTSTAMP:{dtstamp}',
                self._format_datetime_property('DTSTART', event.dt_start),
                self._format_datetime_property('DTEND', event.dt_end),
                f'SUMMARY:{self._escape_text(event.title)}',
            ]

            if event.location is not None:
                event_lines.append(f'LOCATION:{self._escape_text(event.location)}')

            if event.description is not None:
                event_lines.append(f'DESCRIPTION:{self._escape_text(event.description)}')

            event_lines.append('END:VEVENT')
            execution_lines.extend(self._fold_content_line(line) for line in event_lines)

        execution_lines.append('END:VCALENDAR')
        return '\r\n'.join(execution_lines) + '\r\n'


class CalendarWithSetup(BaseCalendar):
    def __init__(self, events, setup):
        super().__init__(self, events)
        self.setup = setup
