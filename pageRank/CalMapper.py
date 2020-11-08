#!/usr/bin/env python
# input: "key1 val1 val2"
# val1表示key1的PageRank值，val2表示出链
# output: "key2 val"
# val2为key1中的某个出链key2从key1得到的PageRank值
import sys

for line in sys.stdin:
    line = line.strip()
    if len(line) <= 1:
        continue
    key1, y1 = line.split('\t', 1)
    val1, val2 = y1.split('\t', 1)
    val1 = float(val1)
    outPoints = val2.strip().split('\t')
    length = len(outPoints)
    for outPoint in outPoints:
        outVal = float(val1 / length)
        print("%s\t%s" % (outPoint, str(outVal)))
    # 防止key1的丢失
    print("%s\t%s" % (key1, str(0)))
