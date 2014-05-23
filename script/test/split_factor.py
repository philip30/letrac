#!/usr/bin/env python

import sys

factor = int(sys.argv[1])
with open(sys.argv[2],'r') as inp:
    for line in inp:
        line = line.strip().split(' |COL| ')
        if factor < len(line):
            print line[factor].replace(" ","")
            for i in range(0,factor-1):
                print >> sys.stderr, line[i] 

        else:
            print line
            print >> sys.stderr, line
