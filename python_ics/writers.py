import uuid

from classes import Calendar


def create_ics(calendar: Calendar, filename='') -> None:
    # giving random id to calendar if name is not mentioned
    if filename == '':
        filename = str(uuid.uuid4())

    ics_file = open(f'{filename}.ics', mode='w')
    ics_file.write(calendar.get_execution_string())
    ics_file.close()

