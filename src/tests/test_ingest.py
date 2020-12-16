import datetime
import unittest

import psycopg2

from ingest import *


class TestIngest(unittest.TestCase):
    def test_month_name_to_number(self):
        name = "April"
        number = month_name_to_number(name)
        assert number == 4

    def test_split_clippings(self):

        clippings = """The Compound Effect (Darren Hardy)
- Your Highlight Location 626-626 | Added on Friday, December 11, 2020 1:42:54 PM

Become very conscious of every choice you make today so you can begin to make smarter choices moving forward.
==========
The Compound Effect (Darren Hardy)
- Your Highlight Location 636-637 | Added on Friday, December 11, 2020 1:45:14 PM

The biggest difference between successful people and unsuccessful people is that successful people are willing to do what unsuccessful people are not.
==========
The Compound Effect (Darren Hardy)
- Your Highlight Location 666-668 | Added on Friday, December 11, 2020 1:49:33 PM

Do you know how the casinos make so much money in Vegas? Because they track every table, every winner, every hour. Why do Olympic trainers get paid top dollar? Because they track every workout, every calorie, and every micronutrient for their athletes. All winners are trackers. Right now I want you to track your life with the same intention: to bring your goals within sight.
==========
"""

        clipping_1 = """The Compound Effect (Darren Hardy)
- Your Highlight Location 626-626 | Added on Friday, December 11, 2020 1:42:54 PM

Become very conscious of every choice you make today so you can begin to make smarter choices moving forward."""

        clipping_2 = """The Compound Effect (Darren Hardy)
- Your Highlight Location 636-637 | Added on Friday, December 11, 2020 1:45:14 PM

The biggest difference between successful people and unsuccessful people is that successful people are willing to do what unsuccessful people are not."""

        clipping_3 = """The Compound Effect (Darren Hardy)
- Your Highlight Location 666-668 | Added on Friday, December 11, 2020 1:49:33 PM

Do you know how the casinos make so much money in Vegas? Because they track every table, every winner, every hour. Why do Olympic trainers get paid top dollar? Because they track every workout, every calorie, and every micronutrient for their athletes. All winners are trackers. Right now I want you to track your life with the same intention: to bring your goals within sight."""

        answer = [clipping_1, clipping_2, clipping_3]

        clipping_list = split_clippings(clippings)

        assert clipping_list == answer, clipping_list


class TestClipping(unittest.TestCase):
    def setUp(self):
        self.raw_clipping = """The Compound Effect (Darren Hardy)
- Your Highlight Location 666-668 | Added on Friday, December 11, 2020 1:49:33 PM

Do you know how the casinos make so much money in Vegas? Because they track every table, every winner, every hour. Why do Olympic trainers get paid top dollar? Because they track every workout, every calorie, and every micronutrient for their athletes. All winners are trackers. Right now I want you to track your life with the same intention: to bring your goals within sight."""
        self.clipping = Clipping(self.raw_clipping)

    def test_init(self):
        """Test with no note, only highlight"""

        assert self.clipping.title == "The Compound Effect (Darren Hardy)"
        assert (
            self.clipping.content
            == "Do you know how the casinos make so much money in Vegas? Because they track every table, every winner, every hour. Why do Olympic trainers get paid top dollar? Because they track every workout, every calorie, and every micronutrient for their athletes. All winners are trackers. Right now I want you to track your life with the same intention: to bring your goals within sight."
        )
        assert self.clipping.dt == datetime.datetime(
            2020, 12, 11, 13, 49, 33, tzinfo=datetime.timezone.utc
        )
        assert self.clipping.kind == "highlight"
        assert self.clipping.location == "666-668"

    def test_convert_parsed_date_to_datetime(self):
        date = "Saturday, April 18, 2020 11:21:19 PM"
        dt = self.clipping.convert_parsed_date_to_datetime(date)
        assert dt == datetime.datetime(
            2020, 4, 18, 23, 21, 19, tzinfo=datetime.timezone.utc
        )

    def test_process_clipping(self):
        """
        Process a highlight
        Assumption:  the text of a highlight doesn't have any newlines in it,
                but notes might
        """
        clipping = """Pro Git (Scott Chacon;Ben Straub)
- Your Highlight Location 2868-2871 | Added on Saturday, April 18, 2020 11:21:19 AM

comparing the content of the newly-fetched featureA branch with her local copy of the same branch: $ git log featureA..origin/featureA"""
        title, metadata, content = self.clipping.process_clipping(clipping)

        assert title == "Pro Git (Scott Chacon;Ben Straub)", title
        assert (
            metadata
            == "- Your Highlight Location 2868-2871 | Added on Saturday, April 18, 2020 11:21:19 AM"
        ), metadata
        assert (
            content
            == "comparing the content of the newly-fetched featureA branch with her local copy of the same branch: $ git log featureA..origin/featureA"
        ), content

    def test_get_clipping_type(self):
        metadata = "- Your Highlight Location 2868-2871 | Added on Saturday, April 18, 2020 11:21:19 AM"
        type = self.clipping.get_clipping_type(metadata)
        assert type == "highlight", type

    def test_get_clipping_location(self):
        metadata = "- Your Highlight Location 2868-2871 | Added on Saturday, April 18, 2020 11:21:19 AM"
        loc = self.clipping.get_clipping_location(metadata)
        assert loc == "2868-2871", loc

    def test_get_date(self):
        metadata = "- Your Highlight Location 2868-2871 | Added on Saturday, April 18, 2020 11:21:19 AM"
        date = self.clipping.get_date(metadata)
        assert date == "Saturday, April 18, 2020 11:21:19 AM"


class TestPostgres(unittest.TestCase):
    def setUp(self):
        # grab these from env vars
        self.db = "test_myclippings"
        self.usr = "postgres"
        self.pw = "mypassword"
        self.host = "127.0.0.1"
        self.port = "5432"

        self.create_test_db()
        self.connection = self.get_test_db_connection()

        self.raw_highlight = """The Compound Effect (Darren Hardy)
- Your Highlight Location 666-668 | Added on Friday, December 11, 2020 1:49:33 PM

Do you know how the casinos make so much money in Vegas? Because they track every table, every winner, every hour. Why do Olympic trainers get paid top dollar? Because they track every workout, every calorie, and every micronutrient for their athletes. All winners are trackers. Right now I want you to track your life with the same intention: to bring your goals within sight."""
        self.raw_note = """The Compound Effect (Darren Hardy)
- Your Note Location 548 | Added on Friday, December 11, 2020 1:24:32 PM

amazingly thoughtful and mutually beneficial gift idea for a loved one"""

        c = Clipping(self.raw_highlight)
        self.highlight = Highlight(c.title, c.content, c.dt, c.location)

        c = Clipping(self.raw_note)
        self.note = Note(c.title, c.content, c.dt, c.location)

        self.highlight.create_table(self.connection)
        self.note.create_table(self.connection)

        # Note.create_table(self.connection)

    def get_test_db_connection(self):
        """Use this connection for everything except creating databases"""

        connection = psycopg2.connect(
            database=self.db,
            user=self.usr,
            password=self.pw,
            host=self.host,
            port=self.port,
        )
        return connection

    def create_test_db(self):
        """Create the test database
        https://pythontic.com/database/postgresql/create%20database"""

        connection = psycopg2.connect(
            user=self.usr, password=self.pw, host=self.host, port=self.port
        )
        connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        query = """CREATE DATABASE "test_myclippings";"""
        cursor.execute(query)
        connection.commit()

    def destroy_test_db(self):
        """Destroy the test database"""

        connection = psycopg2.connect(
            user=self.usr, password=self.pw, host=self.host, port=self.port
        )
        connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        query = """DROP DATABASE "test_myclippings";"""
        cursor.execute(query)
        connection.commit()

    def test_init(self):
        pass

    def tearDown(self):
        self.connection.close()
        self.destroy_test_db()


class TestNote(unittest.TestCase):
    def setUp(self):
        self.raw_note = """The Compound Effect (Darren Hardy)
- Your Note Location 548 | Added on Friday, December 11, 2020 1:24:32 PM

amazingly thoughtful and mutually beneficial gift idea for a loved one"""
        c = Clipping(self.raw_note)
        self.note = Note(c.title, c.content, c.dt, c.location)

    def test_location(self):
        start_loc = self.note.get_start_loc()
        assert start_loc == None, start_loc

        end_loc = self.note.get_end_loc()
        assert end_loc == 548, end_loc

    def test_db_calls(self):
        self.note.write_to_db()
        self.note.delete_from_db()


class TestHighlight(unittest.TestCase):
    def setUp(self):
        self.raw_highlight = """The Compound Effect (Darren Hardy)
- Your Highlight Location 666-668 | Added on Friday, December 11, 2020 1:49:33 PM

Do you know how the casinos make so much money in Vegas? Because they track every table, every winner, every hour. Why do Olympic trainers get paid top dollar? Because they track every workout, every calorie, and every micronutrient for their athletes. All winners are trackers. Right now I want you to track your life with the same intention: to bring your goals within sight."""
        c = Clipping(self.raw_highlight)
        self.highlight = Highlight(c.title, c.content, c.dt, c.location)

    def test_location(self):
        start_loc = self.highlight.get_start_loc()
        assert start_loc == 666, start_loc

        end_loc = self.highlight.get_end_loc()
        assert end_loc == 668, end_loc

    def test_db_calls(self):
        self.highlight.write_to_db()
        self.highlight.delete_from_db()
