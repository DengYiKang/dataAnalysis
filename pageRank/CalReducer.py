#!/usr/bin/env python
# input: "key val"
# key表示point，val表示PageRank
# output: "key 0 val"
# key表示point，0表示类型，用于后续迭代，val表示PageRank的总和

import sys

current_key = None
current_val = 0.0
alpha = 0.8
N = 4
for line in sys.stdin:
    line = line.strip()
    if len(line) <= 1:
        continue
    key, val = line.split('\t', 1)
    if current_key and current_key != key:
        print("%s\t%s\t%s" % (current_key, str(0), str(current_val * alpha + (1 - alpha) / N)))
        current_val = 0.0
    current_key = key
    current_val += float(val)
print("%s\t%s\t%s" % (current_key, str(0), str(current_val * alpha + (1 - alpha) / N)))
