import datetime

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
    '''Parse date from metadata
    TODO: convert this to datetime
    '''

    temp = metadata.split('|')[1]
    date = ' '.join(temp.split()[2:])
    return date

def convert_parsed_date_to_datetime(date):
    weekday, month_name, day, year, time, semi = date.replace(',', '').split()
    month = month_name_to_number(month_name)
    hr, min, sec = time.split(':')
    dt = [year, month, day, hr, min, sec]
    dt = [int(x) for x in dt]
    return datetime.datetime(*dt)

def month_name_to_number(name):
    # https://www.kite.com/python/answers/how-to-convert-between-month-name-and-month-number-in-python
    return datetime.datetime.strptime(name, "%B").month
