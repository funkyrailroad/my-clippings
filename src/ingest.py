import datetime

import psycopg2
'''
Types of clippings:
    - Note
    - Highlight

Information in each kind:
    - Note:
        - Title (str)
        - Location (int)
        - Date Added (datetime)
        - Note (str)
    - Highlight
        - Title (str)
        - Location Range (int, int)
        - Date Added (datetime)
        - Highlight (str)


Overall project

- ingest notes
- read through them
- separate them into individual tags
- UID seems to be the title, location (end range) and datetime
- store in database

Database Schema
- two intermediate tables, join into the final table that relates them

Notes
    - Title (str)
    - Location (int)
    - Date Added (datetime)
    - Note (str)

Highlights
    - Title (str)
    - Start Location (int)
    - End Location (int)
    - Date Added (datetime)
    - Highlight (str)

Clippings
    - Title (required)
    - Location start int
    - Location (end) int (required)
    - Date datetime (required)
    - Highlight (required)
    - Note (optional)

'''


class Clipping(object):
    def __init__(
        self,
        title: str,
        content: str,
        dt: datetime.datetime,
        kind: str,
        location: str,
    ):
        '''Data structure for the different parts of a clipping
        '''
        self.title = title
        self.content = content
        self.dt = dt
        self.kind = kind
        self.location = location


def process_clippings():
    pass


def process_clipping(clipping):
    '''Split a clipping into its title, metadata and content
        TODO: Determine if clipping is a note or highlight
    '''

    clipping = clipping.split('\n')
    title = clipping.pop(0)
    metadata = clipping.pop(0)
    assert clipping.pop(0) == '', 'Unexpected Clipping Format'
    return title, metadata, '\n'.join(clipping)


def process_metadata(metadata):
    # get location
    # get type
    # get date
    pass


def get_clipping_type(metadata):
    '''Determine if type is highlight or note'''

    type_loc = metadata.split('|')[0]
    _, _, type, _, _ = type_loc.split()
    return type.lower()


def get_clipping_location(metadata):
    '''Might need to differentiate between location and location range'''

    type_loc = metadata.split('|')[0]
    _, _, _, _, loc = type_loc.split()
    return loc


def get_date(metadata):
    '''Parse date from metadata'''

    temp = metadata.split('|')[1]
    date = ' '.join(temp.split()[2:])
    return date


def convert_parsed_date_to_datetime(date):
    _, month_name, day, year, time, semi = date.replace(',', '').split()
    month = month_name_to_number(month_name)
    hr, min, sec = time.split(':')
    if semi == 'PM':
        hr = int(hr) + 12
    dt = [year, month, day, hr, min, sec]
    dt = [int(x) for x in dt]
    return datetime.datetime(*dt)


def month_name_to_number(name):
    '''Convert month name to month number
    https://www.kite.com/python/answers/how-to-convert-between-month-name-and-month-number-in-python
    '''

    return datetime.datetime.strptime(name, "%B").month


def split_clippings(clippings, sep='==========\n'):
    '''Chunk full clippings text into a list of individual files
    TODO: might need to consider that text may not fit in memory at once
    (although that would be a ridiculously huge clippings file)'''

    clippings_list = clippings.split(sep)
    clippings_list = [c[:-1] for c in clippings_list]
    # final item in split will be empty
    return clippings_list[:-1]

def get_db_connection(
        db: str='myclippings',
        usr: str="postgres",
        pw: str="mypassword",
        host: str='127.0.0.1',
        port='5432'
        ):
    connection = psycopg2.connect(database=db, user=usr, password=pw,
            host=host, port=port)
    return connection

def create_highlight_table(cursor):
    '''Create postgres table for highlights.
    Unique entries have a unique set of title, location and time
    '''
    query = \
    '''CREATE TABLE IF NOT EXISTS highlights (
    id SERIAL,
    title VARCHAR ( 500 ),
    start_loc INTEGER,
    end_loc INTEGER,
    datetime TIMESTAMP,
    content TEXT,
    PRIMARY KEY (title, start_loc, end_loc, datetime)
    );'''
    cursor.execute(query)

def create_note_table(cursor):
    '''Create postgres table for notes.
    Unique entries have a unique set of title, location and time
    '''
    query = \
    '''CREATE TABLE IF NOT EXISTS notes (
    id SERIAL,
    title VARCHAR ( 500 ),
    end_loc INTEGER,
    datetime TIMESTAMP,
    content TEXT,
    PRIMARY KEY (title, end_loc, datetime)
    );'''
    cursor.execute(query)


if __name__ == "__main__":
    pass
