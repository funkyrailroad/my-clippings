from abc import ABC, abstractmethod
import datetime

import psycopg2

import tqdm

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

    def __init__(
        self,
        db="myclippings",
        usr="postgres",
        pw="mypassword",
        host="127.0.0.1",
        port="5432",
    ):
        self.db = db
        self.usr = usr
        self.pw = pw
        self.host = host
        self.port = port
        self.create_db()

    def get_connection(self):
        """Get connection object to database.
        Although this is not generic, it's bound to postgres"""
        return psycopg2.connect(
            database=self.db,
            user=self.usr,
            password=self.pw,
            host=self.host,
            port=self.port,
        )

    def get_sudo_connection(self):
        connection = psycopg2.connect(
            user=self.usr, password=self.pw, host=self.host, port=self.port
        )
        connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        return connection

    def create_db(self):
        """Create the database
        https://pythontic.com/database/postgresql/create%20database"""

        try:
            connection = self.get_sudo_connection()
            cursor = connection.cursor()
            query = f"""CREATE DATABASE {self.db};"""
            cursor.execute(query)
            connection.commit()
        except psycopg2.errors.DuplicateDatabase:
            pass

    def destroy_db(self):

        connection = self.get_sudo_connection()
        connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        query = f"""DROP DATABASE {self.db};"""
        cursor.execute(query)
        connection.commit()

    def create_table(self):
        pass

    def write_to_db(self):
        '''
        Pass arguments to sql statements like so:
        conn.execute("""SELECT pet_name
                       FROM pet
                       WHERE name = %s""", (name,))
        https://stackoverflow.com/a/42547594
        '''
        pass

    def delete_from_db(self):
        pass


class Clipping(PostgresImporter):
    def __init__(
        self,
        raw_clipping: str,
    ):
        """Data structure for the different parts of a clipping"""
        self.title, self.metadata, self.content = self.process_clipping(raw_clipping)
        self.kind = self.get_clipping_type(self.metadata)
        self.location = self.get_clipping_location(self.metadata)
        self.date = self.get_date(self.metadata)
        self.dt = self.convert_parsed_date_to_datetime(self.date)

    # can be made an abstract class and defined in subclasses Note and
    # Highlight
    def get_start_loc(self):
        pass

    def get_end_loc(self):
        pass

    def create_table(self):
        pass

    def write_to_db(self):
        pass

    def delete_from_db(self):
        pass

    def process_clipping(self, clipping):
        """Split a clipping into its title, metadata and content """

        clipping = clipping.split("\n")
        title = clipping.pop(0)
        metadata = clipping.pop(0)
        assert clipping.pop(0) == "", "Unexpected Clipping Format"
        return title, metadata, "\n".join(clipping)

    def process_metadata(self, metadata):
        # get location
        # get type
        # get date
        pass

    def get_clipping_type(self, metadata):
        """Determine if type is highlight or note"""

        temp = metadata.split("|")[0].split()
        if len(temp) == 5:
            _, _, type, _, _ = temp
        if len(temp) == 6:
            _, _, type, _, _, _ = temp
        return type.lower()

    def get_clipping_location(self, metadata):
        """Might need to differentiate between location and location range"""

        temp = metadata.split("|")[0].split()
        if len(temp) == 5:
            _, _, _, _, loc = temp
        elif len(temp) == 6:
            _, _, _, _, _, loc = temp
        else:
            raise NotImplementedError
        return loc

    def get_date(self, metadata):
        """Parse date from metadata"""

        temp = metadata.split("|")[1]
        date = " ".join(temp.split()[2:])
        return date

    def convert_parsed_date_to_datetime(self, date):
        _, month_name, day, year, time, semi = date.replace(",", "").split()
        month = month_name_to_number(month_name)
        hr, min, sec = time.split(":")
        hr = int(hr)
        if (semi == "PM") and (hr != 12):
            hr = hr + 12
        elif (semi == "AM") and (hr == 12):
            hr = 0
        dt = [year, month, day, hr, min, sec]
        dt = [int(x) for x in dt]

        return datetime.datetime(*dt).replace(tzinfo=datetime.timezone.utc)


def month_name_to_number(name):
    """Convert month name to month number
    https://www.kite.com/python/answers/how-to-convert-between-month-name-and-month-number-in-python
    """

    return datetime.datetime.strptime(name, "%B").month


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

    def get_start_loc(self):
        return None

    def get_end_loc(self):
        return int(self.location)

    @staticmethod
    def create_table(connection):
        """Create postgres table for notes.
        Unique entries have a unique set of title, location and time
        """

        cursor = connection.cursor()
        query = """CREATE TABLE IF NOT EXISTS notes (
        id SERIAL,
        title VARCHAR ( 500 ),
        location INTEGER,
        datetime TIMESTAMPTZ,
        content TEXT,
        PRIMARY KEY (title, location, datetime)
        );"""
        cursor.execute(query)
        connection.commit()

    def write_to_db(self, connection):
        """Add note to database"""

        cursor = connection.cursor()
        query = """INSERT INTO notes
        (title, location, datetime, content)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (self.title, self.location, self.dt, self.content))
        connection.commit()

    def delete_from_db(self, connection):
        """Delete note from database"""

        cursor = connection.cursor()
        query = """DELETE FROM notes
        WHERE
        location = %s AND
        datetime = %s AND
        content = %s;
        """
        cursor.execute(query, (self.location, self.dt, self.content))
        connection.commit()


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

    # can be made an abstract class and defined in subclasses Note and
    # Highlight
    def get_start_loc(self):
        return int(self.location.split("-")[0])

    def get_end_loc(self):
        return int(self.location.split("-")[1])

    @staticmethod
    def create_table(connection):
        """Create postgres table for highlights.
        Unique entries have a unique set of title, location and time
        """

        cursor = connection.cursor()
        query = """CREATE TABLE IF NOT EXISTS highlights (
        id SERIAL,
        title VARCHAR ( 500 ),
        start_loc INTEGER,
        end_loc INTEGER,
        datetime TIMESTAMPTZ,
        content TEXT,
        PRIMARY KEY (title, start_loc, end_loc, datetime)
        );"""
        cursor.execute(query)
        connection.commit()

    def write_to_db(self, connection):
        """Add highlight to database"""

        cursor = connection.cursor()
        query = """INSERT INTO highlights
        (title, start_loc, end_loc, datetime, content)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(
            query, (self.title, self.start_loc, self.end_loc, self.dt, self.content)
        )
        connection.commit()

    def delete_from_db(self, connection):
        """Delete highlight from database"""

        cursor = connection.cursor()
        query = """DELETE FROM highlights
        WHERE
        start_loc = %s AND
        end_loc = %s AND
        datetime = %s AND
        content = %s;
        """
        cursor.execute(query, (self.start_loc, self.end_loc, self.dt, self.content))
        connection.commit()


def process_clippings():
    pass


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


def import_clippings(
    fn="../My Clippings-newest.txt",
    connection=PostgresImporter().get_connection(),
):
    with open(fn) as f:
        all_raw_clippings = "".join(f.readlines())
        raw_clippings = split_clippings(all_raw_clippings)
        for ind, rc in enumerate(tqdm.tqdm(raw_clippings)):
            c = Clipping(rc)
            if c.kind == "note":
                Note(c.title, c.content, c.dt, c.location).write_to_db(connection)
            if c.kind == "highlight":
                Highlight(c.title, c.content, c.dt, c.location).write_to_db(connection)


def get_titles(connection, table):
    cursor = connection.cursor()
    query = f"""SELECT
                DISTINCT title
                FROM {table} ;
                """
    cursor.execute(query)
    results = cursor.fetchall()
    titles = [result[0] for result in results]
    return titles


def get_highlights(con, title):
    query = """SELECT content, start_loc, end_loc
                FROM highlights
                WHERE title = %s
                ORDER BY start_loc, end_loc"""
    with con.cursor() as curs:
        curs.execute(query, (title,))
        results = curs.fetchall()
        highlights = [r for r in results]
    return highlights


if __name__ == "__main__":
    pass
