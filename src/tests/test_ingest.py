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
        date = 'Saturday, April 18, 2020 11:21:19 AM'
        dt = convert_parsed_date_to_datetime(date)
        assert dt == datetime.datetime(2020, 4, 18, 11, 21, 19)

    def test_month_name_to_number(self):
        name = 'April'
        number = month_name_to_number(name)
        assert number == 4
