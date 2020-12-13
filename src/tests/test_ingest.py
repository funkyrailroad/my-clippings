import datetime
import unittest

from ingest import *


class TestIngest(unittest.TestCase):
    def test_process_clipping(self):
        '''
        Process a highlight
        Assumption:  the text of a highlight doesn't have any newlines in it,
                but notes might
        '''
        clipping = \
'''Pro Git (Scott Chacon;Ben Straub)
- Your Highlight Location 2868-2871 | Added on Saturday, April 18, 2020 11:21:19 AM

comparing the content of the newly-fetched featureA branch with her local copy of the same branch: $ git log featureA..origin/featureA'''
        title, metadata, content = process_clipping(clipping)

        assert title == 'Pro Git (Scott Chacon;Ben Straub)', title
        assert metadata == '- Your Highlight Location 2868-2871 | Added on Saturday, April 18, 2020 11:21:19 AM', metadata
        assert content == 'comparing the content of the newly-fetched featureA branch with her local copy of the same branch: $ git log featureA..origin/featureA', content

    def test_get_clipping_type(self):
        metadata = '- Your Highlight Location 2868-2871 | Added on Saturday, April 18, 2020 11:21:19 AM'
        type = get_clipping_type(metadata)
        assert type == 'highlight', type

    def test_get_clipping_location(self):
        metadata = '- Your Highlight Location 2868-2871 | Added on Saturday, April 18, 2020 11:21:19 AM'
        loc = get_clipping_location(metadata)
        assert loc == '2868-2871', loc

    def test_get_date(self):
        metadata = '- Your Highlight Location 2868-2871 | Added on Saturday, April 18, 2020 11:21:19 AM'
        date = get_date(metadata)
        assert date == 'Saturday, April 18, 2020 11:21:19 AM'

    def test_convert_parsed_date_to_datetime(self):
        date = 'Saturday, April 18, 2020 11:21:19 PM'
        dt = convert_parsed_date_to_datetime(date)
        assert dt == datetime.datetime(2020, 4, 18, 23, 21, 19)

    def test_month_name_to_number(self):
        name = 'April'
        number = month_name_to_number(name)
        assert number == 4

    def test_split_clippings(self):

        clippings = '''The Compound Effect (Darren Hardy)
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
'''

        clipping_1 = '''The Compound Effect (Darren Hardy)
- Your Highlight Location 626-626 | Added on Friday, December 11, 2020 1:42:54 PM

Become very conscious of every choice you make today so you can begin to make smarter choices moving forward.'''

        clipping_2 = '''The Compound Effect (Darren Hardy)
- Your Highlight Location 636-637 | Added on Friday, December 11, 2020 1:45:14 PM

The biggest difference between successful people and unsuccessful people is that successful people are willing to do what unsuccessful people are not.'''

        clipping_3 = '''The Compound Effect (Darren Hardy)
- Your Highlight Location 666-668 | Added on Friday, December 11, 2020 1:49:33 PM

Do you know how the casinos make so much money in Vegas? Because they track every table, every winner, every hour. Why do Olympic trainers get paid top dollar? Because they track every workout, every calorie, and every micronutrient for their athletes. All winners are trackers. Right now I want you to track your life with the same intention: to bring your goals within sight.'''

        answer = [clipping_1, clipping_2, clipping_3]

        clipping_list = split_clippings(clippings)

        assert clipping_list == answer, clipping_list


class TestClipping(unittest.TestCase):
    def setUp(self):
        self.raw_clipping = '''The Compound Effect (Darren Hardy)
- Your Highlight Location 666-668 | Added on Friday, December 11, 2020 1:49:33 PM

Do you know how the casinos make so much money in Vegas? Because they track every table, every winner, every hour. Why do Olympic trainers get paid top dollar? Because they track every workout, every calorie, and every micronutrient for their athletes. All winners are trackers. Right now I want you to track your life with the same intention: to bring your goals within sight.'''

    def test_init(self):
        '''Test with no note, only highlight'''

        raw_clipping = self.raw_clipping
        title, metadata, content = process_clipping(raw_clipping)
        date = get_date(metadata)
        dt = convert_parsed_date_to_datetime(date)
        location = get_clipping_location(metadata)
        kind = get_clipping_type(metadata)

        clipping = Clipping(title, content, dt, kind, location)

        assert clipping.title == 'The Compound Effect (Darren Hardy)'
        assert clipping.content == 'Do you know how the casinos make so much money in Vegas? Because they track every table, every winner, every hour. Why do Olympic trainers get paid top dollar? Because they track every workout, every calorie, and every micronutrient for their athletes. All winners are trackers. Right now I want you to track your life with the same intention: to bring your goals within sight.'
        assert clipping.dt == datetime.datetime(2020, 12, 11, 13, 49, 33)
        assert clipping.kind == 'highlight'
        assert clipping.location == '666-668'
