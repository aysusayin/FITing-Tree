import constants as c


def read_file(file_name):
    with open(file_name, 'rb') as f:
        val = f.read(c.KEY_SIZE)
        while val:
            fields = []
            for i in range(c.FIELD_NUM):
                fields.append(int.from_bytes(f.read(c.FIELD_SIZE), byteorder='big'))

            print('key: %d fields: ' % int.from_bytes(val, byteorder='big'))
            print(fields)
            val = f.read(c.KEY_SIZE)


file = '%s43881_segment' % c.DATABASE_LOCATION
read_file(file)
