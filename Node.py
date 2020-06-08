from FITtingTree import constants as const


class Node:
    def __init__(self, previous_node, next_node, is_leaf, parent=None, branching_factor=16):
        self.previous = previous_node
        self.next = next_node
        self.parent = parent
        self.branching_factor = branching_factor
        self.keys = []  # NOTE: must keep keys sorted
        self.children = []  # NOTE: children must correspond to parents.
        self.is_leaf = is_leaf

    def set_children(self, keys, children):
        self.keys = keys
        self.children = children
        if not self.is_leaf:
            for child in children:
                child.parent = self

    def split(self):
        is_leaf = False
        if self.is_leaf:
            new_node_keys = self.keys[(len(self.keys) // 2):]
            new_node_children = self.children[(len(self.children) // 2):]
            self.keys = self.keys[:(len(self.keys) // 2)]
            self.children = self.children[:(len(self.children) // 2)]
            is_leaf = True
            k = new_node_keys[0]
        else:
            new_node_keys = self.keys[((len(self.keys) + 1) // 2) - 1:]
            new_node_children = self.children[(len(self.children) // 2):]
            self.keys = self.keys[:((len(self.keys) + 1) // 2) - 1]
            self.children = self.children[:(len(self.children) // 2)]
            k = new_node_keys.pop(0)
        new_node = Node(self, self.next, is_leaf, self.parent, self.branching_factor)
        new_node.set_children(new_node_keys, new_node_children)
        self.next = new_node

        return new_node, k


class Segment:
    def __init__(self, slope, start, end):
        self.start_key = start  # (key, location) tuple
        self.end_key = end
        self.slope = slope
        self.seg_file_name = '%s%d_segment' % (const.DATABASE_LOCATION, self.start_key)
        self.buff_file_name = '%s%d_buffer' % (const.DATABASE_LOCATION, self.start_key)
        f = open(self.seg_file_name, 'wb+')
        f.close()
        f = open(self.buff_file_name, 'wb+')
        f.close()
        #print('new segment created start_key: %d, end_key: %d, slope: %f' % (start, end, slope))