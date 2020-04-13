""" A generic FITting tree """
from Node import Node, Segment
import constants as const
import os
import collections
from bisect import bisect_left


class FITtingTree:
    def __init__(self, error, buffer_error, branching_factor=16):
        self.branching_factor = branching_factor
        self.root = Node(None, None, True, branching_factor=branching_factor)
        seg = Segment(1, 1, 1)
        self.root.set_children([1], [seg])
        self.put(1, [0 for _ in range(const.FIELD_NUM)])
        self.error = error - buffer_error
        self.buffer_error = buffer_error

    def __shrinking_cone_segmentation(self, keys, locations):
        # data is the keys and pointers , it must be sorted
        segments = []
        high_slope = float('inf')
        low_slope = 0
        origin_key = keys[0]
        origin_loc = locations[0]
        end_key = keys[0]
        for i in range(1, len(keys)):
            key = keys[i]
            loc = locations[i]
            tmp_point_slope = (loc - origin_loc) / (key - origin_key)
            if low_slope <= tmp_point_slope <= high_slope:
                # Point is inside the cone
                tmp_high_slope = ((loc + self.error) - origin_loc) / (key - origin_key)
                tmp_low_slope = ((loc - self.error) - origin_loc) / (key - origin_key)
                high_slope = min(high_slope, tmp_high_slope)
                low_slope = max(low_slope, tmp_low_slope)
                end_key = key
            else:
                slope = (high_slope + low_slope)/2
                if end_key == origin_key:
                    slope = 1
                new_segment = Segment(slope,
                                      origin_key,
                                      end_key)
                high_slope = float('inf')
                low_slope = 0
                origin_key = key
                origin_loc = loc
                end_key = key
                segments.append(new_segment)

        slope = (high_slope + low_slope) / 2
        if end_key == origin_key:
            slope = 1

        new_segment = Segment(slope,
                              origin_key,
                              end_key)
        segments.append(new_segment)

        return segments

    @staticmethod
    def __parse_fields(file, pos):
        # pos is the start of the record
        fields = []
        with open(file, 'rb') as f:
            f.seek(pos, 0)
            key = int.from_bytes(f.read(const.KEY_SIZE), byteorder='big')
            for i in range(const.FIELD_NUM):
                fields.append(int.from_bytes(f.read(const.FIELD_SIZE), byteorder='big'))

        return key, fields

    @staticmethod
    def __binary_file_search(file, key, start_pos=0, end_pos=None):
        pos = -1
        left = start_pos
        if end_pos:
            right = end_pos
        else:
            right = int(os.path.getsize(file) / const.RECORD_SIZE) - 1
        with open(file, 'rb') as seg_file:
            while left <= right:
                mid = int(left + (right - left) // 2)
                print('file: %s' % file)
                print('left: %d right: %d' % (left, right))
                seg_file.seek(const.RECORD_SIZE * mid, 0)
                tmp_key = int.from_bytes(seg_file.read(const.KEY_SIZE), byteorder='big')
                if tmp_key == key:
                    pos = mid * const.RECORD_SIZE
                    break
                elif tmp_key < key:
                    left = mid + +1
                else:
                    right = mid - 1

        return pos

    def __binary_search(self, segment, start_pos, end_pos, key):
        # Binary search segment and buffer and return value
        position = self.__binary_file_search(segment.seg_file_name, key, start_pos, end_pos)

        if position != -1:
            return self.__parse_fields(segment.seg_file_name, position)

        position = self.__binary_file_search(segment.buff_file_name, key)

        if position != -1:
            return self.__parse_fields(segment.buff_file_name, position)

        return "Data with key %d does not exist in the database" % key

    def __search_segment(self, segment, key):
        position = (key - segment.start_key) * segment.slope
        return self.__binary_search(segment, max(0, position - self.error), position + self.error, key)

    def __search_tree(self, key):
        # find the segment that this key belongs to
        current_node = self.root
        while not current_node.is_leaf:
            idx = bisect_left(current_node.keys, key)
            current_node = current_node.children[idx-1]
        return current_node

    def look_up(self, key):
        node = self.__search_tree(key)
        seg = node.children[min(bisect_left(node.keys, key), len(node.children)-1)]
        val = self.__search_segment(seg, key)
        return val

    def put(self, key_value, fields):
        leaf = self.__search_tree(key_value)

        ind = bisect_left(leaf.keys, key_value) - 1
        segment = leaf.children[ind]
        #print('HERE33 key_to_add: %d, ind: %d, segment_start_key: %d' % (key_value, ind, segment.start_key))

        # Database update - delta insert
        buffer_name = segment.buff_file_name
        buffer_copy = open('buffer_copy', 'wb+')

        # Add to buffer
        with open(buffer_name, 'rb') as f:
            tmp_key = f.read(const.KEY_SIZE)
            readable_tmp_key = int.from_bytes(tmp_key, byteorder='big')
            # Buffer needs to be sorted so put the key to the right place
            while tmp_key and readable_tmp_key < key_value:
                buffer_copy.write(tmp_key)
                buffer_copy.write(f.read(const.ALL_FIELDS_SIZE))
                tmp_key = f.read(const.KEY_SIZE)
                readable_tmp_key = int.from_bytes(tmp_key, byteorder='big')

            buffer_copy.write(key_value.to_bytes(const.KEY_SIZE, byteorder='big', signed=True))
            for field in fields:
                buffer_copy.write(field.to_bytes(const.FIELD_SIZE, byteorder='big', signed=True))

            while tmp_key:
                buffer_copy.write(tmp_key)
                buffer_copy.write(f.read(const.ALL_FIELDS_SIZE))
                tmp_key = f.read(const.KEY_SIZE)

        buffer_copy.close()
        os.remove(buffer_name)
        os.rename('buffer_copy', buffer_name)

        if os.path.getsize(buffer_name) >= const.BUFFER_SIZE:
            # re segment buffer and the segment data
            # if new segments are formed, add it to tree
            segment_file_name = segment.seg_file_name
            (keys, tmp_segment_file_name) = self.__concatenate_files(segment_file_name, buffer_name)
            locations = range(len(keys))
            new_segments = self.__shrinking_cone_segmentation(keys, locations)
            if len(new_segments) == 1:
                # No new segments so change the name of the tmp file
                os.remove(new_segments[0].seg_file_name)
                os.rename(tmp_segment_file_name, new_segments[0].seg_file_name)
            else:
                # Split tmp segment file to new files
                self.__split_files(new_segments, tmp_segment_file_name)

            # Index update
            # remove this segment and add the new ones
            leaf.keys.remove(segment.start_key)
            leaf.children.remove(segment)  # remove this segment
            for s in new_segments:
                self.__insert_segment(s, leaf)

    def __insert_segment(self, segment, leaf):
        key = segment.start_key
        i = bisect_left(leaf.keys, key)
        leaf.keys.insert(i, key)
        leaf.children.insert(i, segment)

        while len(leaf.children) >= self.branching_factor:
            new_child = leaf.split()  # leaf, new_child
            if leaf.parent is None:
                # create a parent node and break
                new_root = Node(None, None, False, None, self.branching_factor)
                new_root.set_children([new_child.keys[0]], [leaf, new_child])
                self.root = new_root
                break
            else:
                leaf = leaf.parent
                # add new node to parent
                i = bisect_left(leaf.keys, new_child.keys[0])
                leaf.keys.insert(i, new_child.keys[0])
                leaf.children.insert(i + 1, new_child)

    def print_tree(self):
        queue = collections.deque()
        node = self.root
        queue.append(node)
        while queue:
            tmp = queue.pop()
            if not tmp.is_leaf:
                for c in tmp.children:
                    queue.append(c)
            print('Node:')
            print(tmp)
            print('Parent:')
            print(tmp.parent)
            print('Node keys:')
            print(tmp.keys)
            print('-----------------')

    @staticmethod
    def __split_files(segments, tmp_file_name):
        tmp_file = open(tmp_file_name, 'rb')
        for s in segments:
            tmp_key = tmp_file.read(const.KEY_SIZE)
            tmp_key_readable = int.from_bytes(tmp_key, byteorder='big')
            # Start copying
            with open(s.seg_file_name, 'wb') as f:
                while tmp_key_readable != s.end_key:
                    f.write(tmp_key)
                    f.write(tmp_file.read(const.ALL_FIELDS_SIZE))
                    tmp_key = tmp_file.read(const.KEY_SIZE)
                    tmp_key_readable = int.from_bytes(tmp_key, byteorder='big')
                f.write(tmp_key)
                f.write(tmp_file.read(const.ALL_FIELDS_SIZE))
        tmp_file.close()
        os.remove(tmp_file_name)

    @staticmethod
    def __concatenate_files(segment_file_name, buffer_file_name):
        new_segment_file_name = '%s_tmp' % segment_file_name
        segment_file = open(segment_file_name, 'rb')
        buffer_file = open(buffer_file_name, 'rb')
        new_segment_file = open(new_segment_file_name, 'wb+')
        keys = []
        key_seg = segment_file.read(const.KEY_SIZE)
        key_buff = buffer_file.read(const.KEY_SIZE)
        while key_buff or key_seg:
            key_buff_readable = int.from_bytes(key_buff, byteorder='big')
            key_seg_readable = int.from_bytes(key_seg, byteorder='big')
            if key_seg and (not key_buff or key_buff_readable > key_seg_readable):
                new_segment_file.write(key_seg)
                keys.append(key_seg_readable)
                new_segment_file.write(segment_file.read(const.ALL_FIELDS_SIZE))
                key_seg = segment_file.read(const.KEY_SIZE)
            elif key_buff and (not key_seg or key_seg_readable > key_buff_readable):
                new_segment_file.write(key_buff)
                keys.append(key_buff_readable)
                new_segment_file.write(buffer_file.read(const.ALL_FIELDS_SIZE))
                key_buff = buffer_file.read(const.KEY_SIZE)
            else:
                break

        segment_file.close()
        buffer_file.close()
        new_segment_file.close()
        os.remove(segment_file_name)
        os.remove(buffer_file_name)

        return keys, new_segment_file_name
