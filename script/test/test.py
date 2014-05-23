#!/usr/bin/env python

import sys

def read_list(line):
    line_set = set()
    _, line = line.strip().split(" = ")
    line = line[1:-1]
    for item in line.split(','):
        _item = None
        try:
            _item = int(item)
        except ValueError:
            try:
                _item = float(item)
            except ValueError:
                _item = item
        line_set.add(_item)
    return line_set

gs_fp = open(sys.argv[1],"r")

gs_list = []
for line in gs_fp:
    gs_list.append(read_list(line.strip()))
    
count = 0
line_count = 0
for n, sp_line in enumerate(sys.stdin):
    sp_line = sp_line.strip()
    if read_list(sp_line) == gs_list[n]:
        print n, "1"
        count += 1
    else:
        print n, "0"
    line_count += 1

if line_count != len(gs_list):
    print >> sys.stderr, "Line count != reference %d != %d" % (line_count, len(gs_list)) 
    sys.exit(1)
print >> sys.stdout, "Accuracy %f" % (float(count) / len(gs_list))
print >> sys.stderr, "Accuracy %f" % (float(count) / len(gs_list))


