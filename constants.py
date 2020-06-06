DATABASE_LOCATION = 'iot_data/data_files/'
DATABASE_NAME = DATABASE_LOCATION + 'my_db'
BUFFER_ERROR = 20
ERROR = 10
KEY_SIZE = 8
FIELD_SIZE = 8 # fields are double so size needs to be 8 bytes
FIELD_NUM = 7  #COVID: ['day', 'month', 'year', 'cases', 'deaths', 'countryterritoryCode', 'popData2018']
RECORD_SIZE = KEY_SIZE + FIELD_NUM * FIELD_SIZE
BUFFER_SIZE = BUFFER_ERROR * RECORD_SIZE
ALL_FIELDS_SIZE = RECORD_SIZE - KEY_SIZE  # size of the all fields except for key