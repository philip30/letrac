#!/usr/bin/env python
# Script to append rules to the current rule
# Usage append-kb.py -i [INPUT_RULES] [--trg_factors [TRG_FACTORS]]
# Philip Arthur (philip.arthur30@gmail.com)

import sys
import argparse

parser = argparse.ArgumentParser(description="Append KB")
parser.add_argument('-i', dest='rules', type=str,required=True)
parser.add_argument('--trg_factors', type=int, default=1)
parser.add_argument('-duplicate_src', action="store_true")
args = parser.parse_args()

def print_rule(line,trg_factor):
    src, trg, feat = line.split(" ||| ")
    if trg_factor == 2:
        trgs = " |COL| ".join([src if args.duplicate_src else trg, trg])
    else:
        trgs = trg
    print "%s ||| %s ||| %s" % (src,trgs,feat)

for line in sys.stdin:
    print line.strip()

with open(args.rules) as rule_fp:
    for line in rule_fp:
        line = line.strip()
        if len(line) != 0:
            print_rule(line,args.trg_factors)

