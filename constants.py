DATABASE_LOCATION = '/'
DATABASE_NAME = DATABASE_LOCATION + ''
BUFFER_ERROR = 20
ERROR = 25
KEY_SIZE = 8
FIELD_SIZE = 10
FIELD_NUM = 10
RECORD_SIZE = KEY_SIZE + FIELD_NUM * FIELD_SIZE
BUFFER_SIZE = BUFFER_ERROR * RECORD_SIZE
ALL_FIELDS_SIZE = RECORD_SIZE - KEY_SIZE  # size of the all fields except for key
FIELD_TYPES = ['string']
FIELD_TYPE = 'string'


def read_from_file(file_path):
    """
    Metadata file format:
    Database location
    Database Name
    Key Size
    Field Size
    Number of Fields
    Types of Fields : A list of types. Unfortunately only one type for all fields is supported now.
    Buffer Error
    Error: Total error which includes buffer error in it
    """
    input_file = open(file_path, 'r+')
    global DATABASE_LOCATION, DATABASE_NAME, KEY_SIZE, FIELD_SIZE, FIELD_NUM, \
        RECORD_SIZE, ALL_FIELDS_SIZE, BUFFER_ERROR, ERROR, BUFFER_SIZE, FIELD_TYPES, FIELD_TYPE
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
