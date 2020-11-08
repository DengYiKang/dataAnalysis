#!/usr/bin/env python
import sys

for line in sys.stdin:
    line = line.strip()
    if len(line) >= 2:
        print(line)
