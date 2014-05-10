#!/usr/bin/env python

import sys

factor = int(sys.argv[1])
with open(sys.argv[2],'r') as inp:
    for line in inp:
        line = line.strip().split(' ||| ')
        print ' ||| '.join([line[0],line[1].split(' |COL| ')[factor], line[2],line[3]])
