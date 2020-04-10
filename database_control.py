import pickle
from FITtingTree import FITtingTree
import constants as const

tree = FITtingTree(const.ERROR, const.BUFFER_ERROR)

f = open('input2.txt', 'r+')
for command in f:
    words = command.split()
    if words[0] == 'PUT':
        tree.put(int(words[1]), [int(w) for w in words[2:]])
        print('Added the record with key: %s' % words[1])
    elif words[0] == 'LOOK_UP':
        print('Record with key %s: ' % words[1])
        print(tree.look_up(int(words[1])))
    elif words[0] == 'PRINT':
        tree.print_tree()
    elif words[0] == 'LOAD':
        with open('my_fitting_tree', 'wb+') as f:
            tree = pickle.load(open('my_fitting_tree', 'rb'))
    elif words[0] == "SAVE":
        with open('my_fitting_tree', 'wb+') as f:
            pickle.dump(tree, f)
