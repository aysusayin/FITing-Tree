from Node import Leaf, Node, Segment
import os

s = Segment(0.8, 0.4, (1,5), (25, 10))
print(os.path.getsize('1_buffer'))
s.insert(4, [25])
print(os.path.getsize('1_buffer'))
s.insert(5, [26])
s.insert(3, [26])
print(os.path.getsize('1_buffer'))