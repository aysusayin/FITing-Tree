DATABASE_LOCATION = 'covid/data_files/fitting/'
DATABASE_NAME = DATABASE_LOCATION + 'my_fitting_db'
BUFFER_ERROR = 20
ERROR = 25
KEY_SIZE = 8
FIELD_SIZE = 10 # fields are double so size needs to be 8-10 bytes
FIELD_NUM = 7  #COVID: ['day', 'month', 'year', 'cases', 'deaths', 'countryterritoryCode', 'popData2018']
RECORD_SIZE = KEY_SIZE + FIELD_NUM * FIELD_SIZE
BUFFER_SIZE = BUFFER_ERROR * RECORD_SIZE
ALL_FIELDS_SIZE = RECORD_SIZE - KEY_SIZE  # size of the all fields except for key
FIELD_TYPES = ['float']
FIELD_TYPE = 'float'


def read_from_file(file_path):
    input_file = open(file_path, 'r+')
    global DATABASE_LOCATION, DATABASE_NAME, KEY_SIZE, FIELD_SIZE, FIELD_NUM, \
        RECORD_SIZE, ALL_FIELDS_SIZE, BUFFER_ERROR, ERROR, BUFFER_SIZE, FIELD_TYPES
    DATABASE_LOCATION = str(input_file.readline()).rstrip() + 'fitting/'
    DATABASE_NAME = DATABASE_LOCATION + str(input_file.readline()).rstrip()
    KEY_SIZE = int(input_file.readline())
    FIELD_SIZE = int(input_file.readline())
    FIELD_NUM = int(input_file.readline())
    FIELD_TYPES = input_file.readline().split()
    BUFFER_ERROR = int(input_file.readline())
    ERROR = int(input_file.readline())
    RECORD_SIZE = KEY_SIZE + FIELD_NUM * FIELD_SIZE
    BUFFER_SIZE = BUFFER_ERROR * RECORD_SIZE
    ALL_FIELDS_SIZE = RECORD_SIZE - KEY_SIZE
    FIELD_TYPE = FIELD_TYPES[0].strip()
    input_file.close()
