DATABASE_LOCATION = 'datas/'
DATABASE_NAME = DATABASE_LOCATION + 'my_db'
BUFFER_ERROR = 3
ERROR = 10
KEY_SIZE = 8
FIELD_SIZE = 8
FIELD_NUM = 1
RECORD_SIZE = KEY_SIZE + FIELD_NUM * FIELD_SIZE
BUFFER_SIZE = BUFFER_ERROR * RECORD_SIZE
ALL_FIELDS_SIZE = RECORD_SIZE - KEY_SIZE  # size of the all fields except for key
