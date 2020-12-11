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
        process_clipping(clipping)
