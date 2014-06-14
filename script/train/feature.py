#!/usr/bin/env python

import sys
import math
import argparse
from collections import defaultdict

context = defaultdict(lambda:0)
count = defaultdict(lambda:0)
word_fp = set()
symbol_set = set()

parser = argparse.ArgumentParser()
parser.add_argument('--col_length', type=int,default = 1)
parser.add_argument('--one_feature', action="store_true")
args = parser.parse_args()

col_length = args.col_length

def feat(key, value):
    if float(value) > 1e-8:
        return "%s=%s" % (key, str(value))
    return ""

def is_parse(inp):
    parse = True
    for word in inp:
        if word[0] != '"' or word[-1] != '"':
            parse = False
            break
    return "1" if parse else "0"

def paralength(paraphrase):
    count = 0
    for word in paraphrase:
        if len(word) > 1 and word[0] == '"' and word[-1] == '"':
            count += 1
    return count

for i,line in enumerate(sys.stdin):
    (sent, log) = line.strip().split(" ||| ")
    for word in sent.split():
        if word == '@': break
        if len(word) > 1 and word[0] == '"' and word[-1] == '"':
            word_fp.add(word[1:-1])
        else:
            symbol_set.add(word[word.find(":")+1:])

    count[sent,log] += 1
    context[sent] += 1
    context[log] += 1
    context[""] += 1

for (i,((sent,log), cnt)) in enumerate(sorted(count.items(),key=lambda x:x[0])):
    print "%s ||| %s ||| %s" % (sent,log, ' '.join(filter(lambda x: x != "", [\
        feat("psgl", -math.log(float(cnt)/context[log])), \
        feat("plgs", -math.log(float(cnt)/context[sent])), \
        feat("prob", -math.log(float(cnt)/context[""])),\
        feat("count", cnt), \
        feat("parse", is_parse(sent.split()[:-2])),\
        feat("paralen", paralength((log.split(" |COL| ")[0]).split())),\
        feat("r"+str(i),(1 if args.one_feature else 0))\
        ])))

for word in sorted(word_fp):
    for symbol in symbol_set:
        print "\"%s\" x0:%s @ %s ||| %s @ %s ||| del=1" % (word.strip(), symbol, symbol, ' |COL| '.join(["x0:"+symbol]*col_length),symbol)
