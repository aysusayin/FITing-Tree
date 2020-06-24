""" A generic FITting tree """
from FITtingTree import Node
from FITtingTree import constants as const
import os
from bisect import bisect_left


class FITtingTree:
    def __init__(self, error, buffer_error, branching_factor=16):
        self.key_type = 'int'
        self.branching_factor = branching_factor
        self.root = Node.Node(None, None, True, branching_factor=branching_factor)
        seg = Node.Segment(1, 0, 0)
        self.root.set_children([0], [seg])
        self.error = error - buffer_error
        self.buffer_error = buffer_error
        if buffer_error > error:
            print('Buffer Error should be less than total error. Your values are\n'
                  'Buffer error: %f Total error: %f\n'
                  'Aborting...' % (self.buffer_error, self.error))
            exit()
        self.put(0, [0 for _ in range(const.FIELD_NUM)])

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
                slope = (high_slope + low_slope) / 2
                if end_key == origin_key:
                    slope = 1
                new_segment = Node.Segment(slope, origin_key, end_key)
                high_slope = float('inf')
                low_slope = 0
                origin_key = key
                origin_loc = loc
                end_key = key
                segments.append(new_segment)

        slope = (high_slope + low_slope) / 2
        if end_key == origin_key:
            slope = 1

        new_segment = Node.Segment(slope, origin_key, end_key)
        segments.append(new_segment)

        return segments

    def __parse_fields(self, file, pos):
        # pos is the start of the record
        fields = []
        with open(file, 'rb') as f:
            f.seek(pos, 0)
            key = self.__decode_field(f.read(const.KEY_SIZE), self.key_type)

            for i in range(const.FIELD_NUM):
                fields.append(self.__decode_field(f.read(const.FIELD_SIZE), const.FIELD_TYPE))

        return key, fields

    def __binary_file_search(self, file, key, start_pos=0, end_pos=None):
        pos = -1
        left = start_pos
        right = int(os.path.getsize(file) / const.RECORD_SIZE) - 1
        if end_pos and end_pos < right:  # check if end position is less than file length
            right = end_pos

        with open(file, 'rb') as seg_file:
            while left <= right:
                mid = int(left + (right - left) // 2)
                seg_file.seek(const.RECORD_SIZE * mid, 0)
                tmp_key = self.__decode_field(seg_file.read(const.KEY_SIZE), self.key_type)

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

        print("Data with key %d does not exist in the database" % key)
        return "Data with key %d does not exist in the database" % key

    def __search_segment(self, segment, key):
        position = (key - segment.start_key) * segment.slope
        return self.__binary_search(segment, max(0, position - self.error), position + self.error, key)

    def __search_tree(self, key):
        # find the segment that this key belongs to
        current_node = self.root
        while not current_node.is_leaf:
            idx = bisect_left(current_node.keys, key)
            if idx < len(current_node.keys) and current_node.keys[idx] == key:
                idx += 1
            current_node = current_node.children[idx]
        return current_node

    def look_up(self, key):
        node = self.__search_tree(key)
        i = self.__binary_search_list(node.keys, key)
        seg = node.children[max(i, 0)]
        val = self.__search_segment(seg, key)
        return val

    def put(self, key_value, fields):
        leaf = self.__search_tree(key_value)
        ind = self.__binary_search_list(leaf.keys, key_value)
        segment = leaf.children[ind]

        # Database update - delta insert
        buffer_name = segment.buff_file_name
        buffer_copy = open('buffer_copy', 'wb+')

        # Add to buffer
        with open(buffer_name, 'rb') as f:
            tmp_key = f.read(const.KEY_SIZE)
            readable_tmp_key = FITtingTree.__decode_field(tmp_key, self.key_type)
            # Buffer needs to be sorted so put the key to the right place
            while tmp_key and readable_tmp_key <= key_value:
                buffer_copy.write(tmp_key)
                buffer_copy.write(f.read(const.ALL_FIELDS_SIZE))
                tmp_key = f.read(const.KEY_SIZE)
                readable_tmp_key = FITtingTree.__decode_field(tmp_key, self.key_type)

            if readable_tmp_key == key_value:
                buffer_copy.close()
                os.remove('buffer_copy')
                return

            buffer_copy.write(self.__encode_field(key_value, const.KEY_SIZE))

            for field in fields:
                buffer_copy.write(self.__encode_field(field, const.FIELD_SIZE))

            while tmp_key:
                buffer_copy.write(tmp_key)
                buffer_copy.write(f.read(const.ALL_FIELDS_SIZE))
                tmp_key = f.read(const.KEY_SIZE)

        buffer_copy.close()
        os.remove(buffer_name)
        os.rename('buffer_copy', buffer_name)

        size = os.path.getsize(buffer_name)
        buffer_size = self.buffer_error * const.RECORD_SIZE
        if size >= buffer_size:
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
        node = leaf
        while len(node.children) >= self.branching_factor:
            new_child, k = node.split()  # node, new_child
            if node.parent is None:
                # create a parent node and break
                new_root = Node.Node(None, None, False, None, self.branching_factor)
                new_root.set_children([k], [node, new_child])
                self.root = new_root
                break
            else:
                node = node.parent
                # add new node to parent
                i = bisect_left(node.keys, k)
                node.keys.insert(i, k)
                node.children.insert(i + 1, new_child)

    def __split_files(self, segments, tmp_file_name):
        tmp_file = open(tmp_file_name, 'rb')
        for s in segments:
            tmp_key = tmp_file.read(const.KEY_SIZE)
            tmp_key_readable = self.__decode_field(tmp_key, self.key_type)

            # Start copying
            with open(s.seg_file_name, 'wb') as f:
                while tmp_key_readable != s.end_key:
                    f.write(tmp_key)
                    f.write(tmp_file.read(const.ALL_FIELDS_SIZE))
                    tmp_key = tmp_file.read(const.KEY_SIZE)
                    tmp_key_readable = self.__decode_field(tmp_key, self.key_type)
                f.write(tmp_key)
                f.write(tmp_file.read(const.ALL_FIELDS_SIZE))
        tmp_file.close()
        os.remove(tmp_file_name)

    def __concatenate_files(self, segment_file_name, buffer_file_name):
        new_segment_file_name = '%s_tmp' % segment_file_name
        segment_file = open(segment_file_name, 'rb')
        buffer_file = open(buffer_file_name, 'rb')
        new_segment_file = open(new_segment_file_name, 'wb+')
        keys = []
        key_seg = segment_file.read(const.KEY_SIZE)
        key_buff = buffer_file.read(const.KEY_SIZE)
        while key_buff or key_seg:
            key_buff_readable = self.__decode_field(key_buff, self.key_type)
            key_seg_readable = self.__decode_field(key_seg, self.key_type)
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
            elif key_buff and key_seg and key_seg_readable == key_buff_readable:
                buffer_file.read(const.ALL_FIELDS_SIZE)
                key_buff = buffer_file.read(const.KEY_SIZE)
            else:
                break

        segment_file.close()
        buffer_file.close()
        new_segment_file.close()
        os.remove(segment_file_name)
        os.remove(buffer_file_name)

        return keys, new_segment_file_name

    @staticmethod
    def __binary_search_list(list_name, key):
        i = bisect_left(list_name, key) - 1
        if i + 1 < len(list_name) and list_name[i + 1] == key:
            i += 1
        return max(i, 0)

    @staticmethod
    def __encode_field(number, size):
        if isinstance(number, int):
            return number.to_bytes(size, byteorder='big', signed=True)
        else:
            if isinstance(number, float) and number == int(number):
                number = int(number)
            if size - len(str(number)) < 0:
                print('Data doesn\'t fit in the provided field size: %s\nAborting...' % str(number))
                exit()
            return bytes(str(number).strip(), 'utf-8') + b" " * (size - len(str(number)))

    @staticmethod
    def __decode_field(number, decode_type):
        if decode_type == 'int':
            return int.from_bytes(number, byteorder='big')
        else:
            return str(number.decode('utf-8').strip())
