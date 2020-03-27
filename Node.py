import bisect
import math
import collections


class Leaf:
    def __init__(self, previous_leaf, next_leaf, parent, branching_factor=16):
        self.previous = previous_leaf
        self.next = next_leaf
        self.parent = parent
        self.branching_factor = branching_factor
        self.keys = []
        self.children = []  # A Segment


class Node:
    def __init__(self, previous_node, next_node, keys, children, parent=None, branching_factor=16):
        self.previous = previous_node
        self.next = next_node
        self.keys = keys  # NOTE: must keep keys sorted
        self.children = children  # NOTE: children must correspond to parents.
        self.parent = parent
        self.branching_factor = branching_factor
        for child in children:
            child.parent = self


class Segment:
    def __init__(self, high_slope, low_slope, start, end, buffer_error):
        self.high_slope = high_slope
        self.low_slope = low_slope
        self.start_point = start  # (key, location) tuple
        self.end_point = end
        self.buffer = collections.deque(buffer_error)
        self.slope = (high_slope + low_slope) / 2
