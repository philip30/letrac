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
qdata_fp = open(sys.argv[2],"r")

gs_list = []
qdata_list = []
for (gs_line, qdata_line) in zip(gs_fp,qdata_fp):
    qdata_list.append(qdata_line.strip())
    gs_list.append(read_list(gs_line.strip()))
    
count = 0
line_count = 0
parseable_count = 0
for n, sp_line in enumerate(sys.stdin):
    sp_line = sp_line.strip()
    ans = read_list(sp_line)
    if ans == gs_list[n]:
        print n, "1"
        count += 1
    else:
        print n, "0"
    line_count += 1

    if len(qdata_list[n]) != 0 and qdata_list[n].startswith("answer") and ('Failed' not in ans):
        parseable_count += 1

if line_count != len(gs_list):
    print >> sys.stderr, "Line count != reference %d != %d" % (line_count, len(gs_list)) 
    sys.exit(1)

rec = (float(count) / line_count)
acc = (float(count) / parseable_count)
fmeasure = float(2 * rec * acc) / (rec + acc)

print >> sys.stdout, "Accuracy %f" % (acc)
print >> sys.stdout, "Recall   %f" % (rec)
print >> sys.stdout, "F-Score  %f" % (fmeasure)
print >> sys.stderr, "Accuracy %f" % (acc)
print >> sys.stderr, "Recall   %f" % (rec)
print >> sys.stderr, "F-Score  %f" % (fmeasure)

