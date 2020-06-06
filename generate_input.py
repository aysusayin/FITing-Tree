import xlrd

loc = ('covid_data/COVID-19-geographic-disbtribution-worldwide.xlsx')
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
countries = dict()
c_set = set()
count = 0
for i in range(1, sheet.nrows):
    c = sheet.cell_value(i, 6)
    if c not in c_set:
        countries[c] = count
        count += 1
        c_set.add(c)

with open('covid_data/input_files/input_look_up.txt', 'w+') as f:
    # f.write('LOAD\n')
    for i in range(1, sheet.nrows):
        fields = sheet.row_values(i)

        key = int(float(str(countries[fields[6]]) + str(fields[0])))
        day = int(fields[1]) if fields[1] != '' else 0
        month = int(fields[2]) if fields[2] != '' else 0
        year = int(fields[3]) if fields[3] != '' else 0
        case = int(fields[4]) if fields[4] != '' else -1
        death = int(fields[5]) if fields[5] != '' else -1
        country = int(countries[fields[6]])
        population = int(fields[9]) if fields[9] != '' else 0

        command = 'PUT %d %d %d %d %d %d %d %d\n' % (key, day, month, year, case, death, country, population)
        # command = 'LOOK_UP %d\n' % key
        f.write(command)
    # f.write('SAVE')
