#!/usr/bin/env python
# Script to append rules to the current rule
# Usage append-kb.py -i [INPUT_RULES] [--trg_factors [TRG_FACTORS]]
# Philip Arthur (philip.arthur30@gmail.com)

import sys
import argparse

parser = argparse.ArgumentParser(description="Append KB")
parser.add_argument('-i', dest='rules', type=str,required=True)
parser.add_argument('--trg_factors', type=int, default=1)
args = parser.parse_args()

def print_rule(line,trg_factor):
    src, trg, feat = line.split(" ||| ")
    trgs = " |COL| ".join([trg for i in range(trg_factor)])
    print "%s ||| %s ||| %s" % (src,trgs,feat)

for line in sys.stdin:
    print line.strip()

with open(args.rules) as rule_fp:
    for line in rule_fp:
        line = line.strip()
        print_rule(line,args.trg_factors)

