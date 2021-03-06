#!/usr/bin/env python

import sys
import math
import argparse
from collections import defaultdict

context = defaultdict(lambda:0)
count = defaultdict(lambda:0)

parser = argparse.ArgumentParser()
parser.add_argument('--one_feat', action="store_true")
parser.add_argument('--trg_factors', type=int, default=1)
parser.add_argument('--paralength', action="store_true")
args = parser.parse_args()

def feat(key, value):
    if float(value) > 1e-8:
        return "%s=%s" % (key, str(value))
    return ""

def paralength(paraphrase):
    count = 0
    for word in paraphrase.split():
        if word == "@":
            break
        if len(word) > 1 and word[0] == '"' and word[-1] == '"':
            count += 1
    return count if args.trg_factors == 2 else 0

for i,line in enumerate(sys.stdin):
    line_col = line.strip().split(" ||| ")
    (id, sent, log) = line_col[0], line_col[1], line_col[2]
    count[sent,log] += 1
    context[sent] += 1
    context[log] += 1
    context[""] += 1

for (i,((sent,log), cnt)) in enumerate(sorted(count.items(),key=lambda x:x[0])):
    print "%s ||| %s ||| %s" % (sent,log, ' '.join(filter(lambda x: x != "", [\
        feat("psgl", -math.log(float(cnt)/context[log])), \
        feat("plgs", -math.log(float(cnt)/context[sent])), \
        feat("prob", -math.log(float(cnt)/context[""])), \
        feat("parse", 1 if all((x[0] == '"' and x[-1] == '"') for x in sent.split()[:-2]) else 0), \
        feat("r"+str(i),(1 if args.one_feat else 0)),\
        feat("p",1),\
        feat("word", (paralength(log.split(" |COL| ")[0]) if args.paralength else 0))\
        ])))

