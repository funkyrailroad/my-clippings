from abc import ABC, abstractmethod
import datetime

import psycopg2

"""
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

"""


class PostgresImporter(ABC):
    """Import objects into a database table"""

    def get_connection(self):
        """Get connection object to database.
        Although this is not generic, it's bound to postgres"""
        db = "myclippings"
        usr = "postgres"
        pw = "mypassword"
        host = "127.0.0.1"
        port = "5432"
        return psycopg2.connect(
            database=db, user=usr, password=pw, host=host, port=port
        )

    def write_to_db(self):
        pass


class Clipping(PostgresImporter):
    def __init__(
        self,
        title: str,
        content: str,
        dt: datetime.datetime,
        kind: str,
        location: str,
    ):
        """Data structure for the different parts of a clipping"""
        self.title = title
        self.content = content
        self.dt = dt
        self.kind = kind
        self.location = location
        self.start_loc = self.get_start_loc()
        self.end_loc = self.get_end_loc()
        self.connection = super().get_connection()

    # can be made an abstract class and defined in subclasses Note and
    # Highlight
    def get_start_loc(self):
        pass

    def get_end_loc(self):
        pass

    def write_to_db(self):
        pass

    def delete_from_db(self):
        pass


class Note(Clipping):
    def __init__(
        self,
        title: str,
        content: str,
        dt: datetime.datetime,
        location: str,
    ):
        self.title = title
        self.content = content
        self.dt = dt
        self.location = location
        self.start_loc = self.get_start_loc()
        self.end_loc = self.get_end_loc()
        self.connection = super().get_connection()

    def get_start_loc(self):
        return None

    def get_end_loc(self):
        return int(self.location)

    def write_to_db(self):
        add_note_to_db(self, self.connection)

    def delete_from_db(self):
        delete_note_from_db(self, self.connection)


class Highlight(Clipping):
    def __init__(
        self,
        title: str,
        content: str,
        dt: datetime.datetime,
        location: str,
    ):
        """Data structure for the different parts of a clipping"""
        self.title = title
        self.content = content
        self.dt = dt
        self.location = location
        self.start_loc = self.get_start_loc()
        self.end_loc = self.get_end_loc()
        self.connection = super().get_connection()

    # can be made an abstract class and defined in subclasses Note and
    # Highlight
    def get_start_loc(self):
        return int(self.location.split("-")[0])

    def get_end_loc(self):
        return int(self.location.split("-")[1])

    def write_to_db(self):
        add_highlight_to_db(self, self.connection)

    def delete_from_db(self):
        delete_highlight_from_db(self, self.connection)


def process_clippings():
    pass


def process_clipping(clipping):
    """Split a clipping into its title, metadata and content """

    clipping = clipping.split("\n")
    title = clipping.pop(0)
    metadata = clipping.pop(0)
    assert clipping.pop(0) == "", "Unexpected Clipping Format"
    return title, metadata, "\n".join(clipping)


def process_metadata(metadata):
    # get location
    # get type
    # get date
    pass


def get_clipping_type(metadata):
    """Determine if type is highlight or note"""

    type_loc = metadata.split("|")[0]
    _, _, type, _, _ = type_loc.split()
    return type.lower()


def get_clipping_location(metadata):
    """Might need to differentiate between location and location range"""

    type_loc = metadata.split("|")[0]
    _, _, _, _, loc = type_loc.split()
    return loc


def get_date(metadata):
    """Parse date from metadata"""

    temp = metadata.split("|")[1]
    date = " ".join(temp.split()[2:])
    return date


def convert_parsed_date_to_datetime(date):
    _, month_name, day, year, time, semi = date.replace(",", "").split()
    month = month_name_to_number(month_name)
    hr, min, sec = time.split(":")
    if semi == "PM":
        hr = int(hr) + 12
    dt = [year, month, day, hr, min, sec]
    dt = [int(x) for x in dt]
    return datetime.datetime(*dt).replace(tzinfo=datetime.timezone.utc)


def month_name_to_number(name):
    """Convert month name to month number
    https://www.kite.com/python/answers/how-to-convert-between-month-name-and-month-number-in-python
    """

    return datetime.datetime.strptime(name, "%B").month


def split_clippings(clippings, sep="==========\n"):
    """Chunk full clippings text into a list of individual files
    TODO: might need to consider that text may not fit in memory at once
    (although that would be a ridiculously huge clippings file)"""

    clippings_list = clippings.split(sep)
    clippings_list = [c[:-1] for c in clippings_list]
    # final item in split will be empty
    return clippings_list[:-1]


def get_db_connection(
    db: str = "myclippings",
    usr: str = "postgres",
    pw: str = "mypassword",
    host: str = "127.0.0.1",
    port="5432",
):
    connection = psycopg2.connect(
        database=db, user=usr, password=pw, host=host, port=port
    )
    return connection


def create_highlight_table(connection):
    """Create postgres table for highlights.
    Unique entries have a unique set of title, location and time
    """

    cursor = connection.cursor()
    query = """CREATE TABLE IF NOT EXISTS highlights (
    id SERIAL,
    title VARCHAR ( 500 ),
    location VARCHAR( 20 ),
    datetime TIMESTAMPTZ,
    content TEXT,
    PRIMARY KEY (title, location, datetime)
    );"""
    cursor.execute(query)
    connection.commit()


def create_note_table(connection):
    """Create postgres table for notes.
    Unique entries have a unique set of title, location and time
    """

    cursor = connection.cursor()
    query = """CREATE TABLE IF NOT EXISTS notes (
    id SERIAL,
    title VARCHAR ( 500 ),
    location VARCHAR( 20 ),
    datetime TIMESTAMPTZ,
    content TEXT,
    PRIMARY KEY (title, location, datetime)
    );"""
    cursor.execute(query)
    connection.commit()


def add_highlight_to_db(clipping, connection):
    """Add highlight to database"""

    title = clipping.title
    location = clipping.location
    dt = clipping.dt
    content = clipping.content

    cursor = connection.cursor()
    query = f"""INSERT INTO highlights
    (title, location, datetime, content)
    VALUES ( '{title}', '{location}', '{dt}', '{content}' );
    """
    cursor.execute(query)
    connection.commit()


def add_note_to_db(clipping, connection):
    """Add note to database"""

    title = clipping.title
    location = clipping.location
    dt = clipping.dt
    content = clipping.content

    cursor = connection.cursor()
    query = f"""INSERT INTO notes
    (title, location, datetime, content)
    VALUES ( '{title}', '{location}', '{dt}', '{content}' );
    """
    cursor.execute(query)
    connection.commit()


def delete_highlight_from_db(clipping, connection):
    """Delete highlight from database"""

    title = clipping.title
    location = clipping.location
    dt = clipping.dt
    content = clipping.content

    cursor = connection.cursor()
    query = f"""DELETE FROM highlights
    WHERE
    location = '{location}' AND
    datetime = '{dt}' AND
    content = '{content}';
    """
    cursor.execute(query)
    connection.commit()


def delete_note_from_db(clipping, connection):
    """Delete note from database"""

    title = clipping.title
    location = clipping.location
    dt = clipping.dt
    content = clipping.content

    cursor = connection.cursor()
    query = f"""DELETE FROM notes
    WHERE
    location = '{location}' AND
    datetime = '{dt}' AND
    content = '{content}';
    """
    cursor.execute(query)
    connection.commit()


if __name__ == "__main__":
    pass
