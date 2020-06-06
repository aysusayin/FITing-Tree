import csv
from datetime import datetime
import time

csv_file = open('iot_data/household_power_consumption.csv')
csv_reader = csv.reader(csv_file, delimiter=',')
next(csv_reader)

with open('iot_data/input_files/input_add_data.txt', 'w+') as f:
    # f.write('LOAD\n')
    for row in csv_reader:
        fields = row
        if '?' in fields or 'NA' in fields:
            continue
        # IOT DATA
        date = fields[0].split('/')
        if len(date[2]) == 2:
            date[2] = '20' + date[2]
        date = '/'.join(date)
        s = str('%s %s' % (date, fields[1]))
        key = time.mktime(datetime.strptime(s, "%d/%m/%Y %H:%M:%S").timetuple())
        global_active_power = float(fields[2])
        global_reactive_power = float(fields[3])
        voltage = float(fields[4])
        global_intensity = float(fields[5])
        sub_metering_1 = float(fields[6])
        sub_metering_2 = float(fields[7])
        sub_metering_3 = float(fields[8])
        command = 'PUT %d %f %f %f %f %f %f %f\n' % (key, global_active_power, global_reactive_power, voltage,
                                                     global_intensity, sub_metering_1, sub_metering_2, sub_metering_3)
        f.write(command)

    f.write('SAVE')




# command = 'LOOK_UP %d\n' % key
    '''
    Attribute Information

date: Date in format dd/mm/yyyy
time: time in format hh:mm:ss
global_active_power: household global minute-averaged active power (in kilowatt)
global_reactive_power: household global minute-averaged reactive power (in kilowatt)
voltage: minute-averaged voltage (in volt)
global_intensity: household global minute-averaged current intensity (in ampere)
sub_metering_1: energy sub-metering No. 1 (in watt-hour of active energy). It corresponds to the kitchen, containing mainly a dishwasher, an oven and a microwave (hot plates are not electric but gas powered).
sub_metering_2: energy sub-metering No. 2 (in watt-hour of active energy). It corresponds to the laundry room, containing a washing-machine, a tumble-drier, a refrigerator and a light.
sub_metering_3: energy sub-metering No. 3 (in watt-hour of active energy). It corresponds to an electric water-heater and an air-conditioner.
    '''