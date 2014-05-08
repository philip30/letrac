#!/usr/bin/python

import sys

for line in sys.stdin:
    line = line.strip().split(" ||| ")
    print >> sys.stderr, line[0]
    print >> sys.stdout, (''.join(line[1].split())).replace("\\+","\\+ ")
