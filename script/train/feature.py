#!/usr/bin/env python

import sys
import math
import argparse
from collections import defaultdict

context = defaultdict(lambda:0)
count = defaultdict(lambda:0)

parser = argparse.ArgumentParser()
parser.add_argument('--trg_factors', type=int,default = 1)
parser.add_argument('--one_feat', action="store_true")
args = parser.parse_args()

trg_factors = args.trg_factors

def feat(key, value):
    if float(value) > 1e-8:
        return "%s=%s" % (key, str(value))
    return ""

def paralength(paraphrase):
    count = 0
    for word in paraphrase:
        if len(word) > 1 and word[0] == '"' and word[-1] == '"':
            count += 1
    return count

for i,line in enumerate(sys.stdin):
    (sent, log) = line.strip().split(" ||| ")
    count[sent,log] += 1
    context[sent] += 1
    context[log] += 1
    context[""] += 1

for (i,((sent,log), cnt)) in enumerate(sorted(count.items(),key=lambda x:x[0])):
    print "%s ||| %s ||| %s" % (sent,log, ' '.join(filter(lambda x: x != "", [\
        feat("psgl", -math.log(float(cnt)/context[log])), \
        feat("plgs", -math.log(float(cnt)/context[sent])), \
        feat("prob", -math.log(float(cnt)/context[""])), \
        feat("parse", 1 if all((x[0] == '"' and x[-1] == '"') for x in sent[:-2]) else 0), \
        feat("count", cnt), \
        feat("r"+str(i),(1 if args.one_feat else 0)),\
        feat("p",1)\
        ])))

