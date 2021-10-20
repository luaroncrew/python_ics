from dataclasses import dataclass
import datetime as dt


class Event:
    def __init__(
            self,
            title: str,
            dt_start: dt.datetime,
            dt_end: dt.datetime,
            location: str or None,
            notes):

        self.title = title
        self.location = self._is_valid_location(location)
        self.dt_start = dt_start
        self.dt_end = dt_end
        self.notes = notes

    def _is_valid_location(self, location):
        if location is not None:
            if not isinstance(location, str):
                raise TypeError('location can be str or None type')
        return location


@dataclass
class CalendarSetup:
    timezone: str

    def get_setup(self):
        setup = str()
        return setup


@dataclass
class Calendar:
    events: [Event]
    setup: CalendarSetup

    def get_execution_string(self):
        execution_string = str()
        execution_string += self.setup.get_setup()

