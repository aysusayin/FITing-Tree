import pickle
from FITtingTree import FITtingTree
import constants as const
import sys

# COVID-19 DATA websites:
# https://data.humdata.org/event/covid-19
# https://data.europa.eu/euodp/en/data/dataset/covid-19-coronavirus-data/resource/55e8f966-d5c8-438e-85bc-c7a5a26f4863



f = open(str(sys.argv[1]), 'r+')
for i, command in enumerate(f):
    words = command.split()
    if i == 0 and words[0] != 'LOAD':
        tree = FITtingTree(const.ERROR, const.BUFFER_ERROR, 4)
    if words[0] == 'PUT':
        tree.put(int(words[1]), [int(w) for w in words[2:]])
        #print('Added the record with key: %s' % words[1])
    elif words[0] == 'LOOK_UP':
        #print('Record with key %s: ' % words[1])
        tree.look_up(int(words[1]))
    elif words[0] == 'PRINT':
        tree.print_tree()
    elif words[0] == 'LOAD':
        with open('my_fitting_tree', 'rb') as f:
            tree = pickle.load(f)
    elif words[0] == "SAVE":
        with open('my_fitting_tree', 'wb+') as f:
            pickle.dump(tree, f)
