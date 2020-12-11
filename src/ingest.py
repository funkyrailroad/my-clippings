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

def process_clippings():
    pass


def process_clipping(clipping):
    '''Split a clipping into its title, metadata and content
        TODO: Determine if clipping is a note or highlight
    '''

    clipping =  clipping.split('\n')
    title = clipping.pop(0)
    metadata = clipping.pop(0)
    assert clipping.pop(0) == '', 'Unexpected Clipping Format'
    return title, metadata, '\n'.join(clipping)
