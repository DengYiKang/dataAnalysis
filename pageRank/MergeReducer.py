#!/usr/bin/env python

# input: "key type val"
# type=0表示PageRank值，例如"A 1 0.5"， 表示A的PageRank的值为0.5
# type=1表示转移的系数矩阵，例如"A 0 B C D"，表示A有三条出链，分别指向B、C、D
# output: "key val1 val2"
# val1表示key的PageRank值，val2表示出链
import sys

current_key = None
current_val1 = None
current_val2 = None
for line in sys.stdin:
    line = line.strip()
    key, val = line.split('\t', 1)
    if current_key and current_key != key:
        print("%s\t%s\t%s" % (current_key, current_val1, current_val2))
    current_key = key
    splits = val.split('\t', 1)
    m_type = splits[0]
    if m_type == '0':
        current_val1 = splits[1]
    else:
        current_val2 = splits[1]
print("%s\t%s\t%s" % (current_key, current_val1, current_val2))
