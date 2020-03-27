''' A generic FITting tree'''

import bisect

from Node import Leaf, Node, Segment


class FITtingTree:
    def __init__(self, error, buffer_error, branching_factor=16):
        self.branching_factor = branching_factor
        self.leaves = Leaf(None, None, None, branching_factor) # Linked List of leaves
        self.root = self.leaves
        self.error = error - buffer_error
        self.buffer_error = buffer_error

    def shrinking_cone(self, keys, locs):
        # data is the keys and pointers , it must be sorted
        segments = []
        high_slope = float('inf')
        low_slope = 0
        origin_key = keys[0]
        origin_loc = locs[0]
        end_key = keys[0]
        end_loc = locs[0]
        for (key,loc) in list(zip(keys[1:], locs[1:])):
            tmp_point_slope = (loc - origin_loc) / (key - origin_key)
            if low_slope < tmp_point_slope < high_slope:
                # Point is inside the cone
                tmp_high_slope = ((loc + self.error) - origin_loc) / (key - origin_key)
                tmp_low_slope = ((loc - self.error) - origin_loc) / (key - origin_key)
                high_slope = min(high_slope, tmp_high_slope)
                low_slope = max(low_slope, tmp_low_slope)
                end_key = key
                end_loc = loc
            else:
                new_segment = Segment(high_slope, low_slope,
                                      (origin_key, origin_loc),
                                      (end_key, end_loc))
                high_slope = float('inf')
                low_slope = 0
                origin_key = key
                origin_loc = loc
                end_key = key
                origin_loc = loc
                segments.append(new_segment)

        return segments

    def binary_search(self, segment, start_pos, end_pos, key):
        # Binary search segment and buffer and return value
        return 0

    def search_segment(self, segment, key):
        position = (key - segment.start_point) * segment.slope
        return self.binary_serarch(segment, position-self.error, position+self.error, key)

    def search_tree(self, key):
        # find the segment that this key belongs to
        return 0

    def look_up(self, key):
        seg = self.search_tree(key) # A segment
        val = self.search_segment(seg, key)
        return val


