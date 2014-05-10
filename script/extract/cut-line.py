#!/usr/bin/env python

import sys

inp = open(sys.argv[1], "r")
ref = open(sys.argv[2], "r")

for line, _ in zip(inp,ref):
    print " ".join(line.strip().split())

inp.close()
ref.close()

