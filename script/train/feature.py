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
parser.add_argument('--kb',type=str)
parser.add_argument('--del_file',type=str)
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
        feat("r"+str(i),(1 if args.one_feature else 0)),\
        feat("rule",1)\
        ])))


if args.kb:
    def build_source(head,name):
        name = name.split()
        return (" ".join(['"%s"' % (x) for x in name]) + " @ " + head)

    def build_target(targetid,arg):
        innerarg = []
        for a in arg:
            if ' ' in a: 
                a = "'" + a.replace(" ","#$#") + "'"
            innerarg.append(a)
        innerarg = ','.join(innerarg)
        s = '"%s" @ %s' % (innerarg, targetid)
        if args.col_length > 1:
            s = (" ".join(['"%s"' % (x) for x in arg[0].split()])) + " |COL| " + s
        return s

    scan = False
    with open(args.kb,"r") as kbs:
        all_map = set()
        for line in kbs:
            line = line.strip()
            k = line.find('(')
            predicate = line[0:k]
            end = line.find(')',k)
            body = line[k+1:end].split(",")
            if predicate == 'state':
                state_name = body[0][1:-1]
                print '%s ||| %s ||| state_kb=1' % (build_source("STATE",state_name),build_target("STATE",[state_name]))
            elif predicate == 'city':
                state_name, state_abv, city_name = body[0][1:-1], body[1][1:-1], body[2][1:-1]
                if (("city",city_name)) not in all_map:
                    all_map.add(("city",city_name))
                    print '%s ||| %s ||| city_kb=1' % (build_source("CITY",city_name),build_target("CITY",[city_name]))
                print '%s ||| %s ||| city_kb=1' % (build_source("ABR",state_name),build_target("ABR",[state_abv]))
            elif predicate == 'river':
                river_name = body[0][1:-1]
                print '%s ||| %s ||| river_kb=1' % (build_source("RIVER",river_name),build_target("RIVER",[river_name]))
            elif predicate == 'mountain':
                mountain_name = body[2][1:-1]
                print '%s ||| %s ||| mountain_kb=1' % (build_source("PLACE",mountain_name),build_target("PLACE",[mountain_name]))
            elif predicate == 'lake':
                lake_name = body[0][1:-1]
                print '%s ||| %s ||| lake_kb=1' % (build_source("PLACE",lake_name),build_target("PLACE",[lake_name]))

if not args.del_file:
    for word in sorted(word_fp):
        for symbol in symbol_set:
            print "\"%s\" x0:%s @ %s ||| %s @ %s ||| del=1" % (word.strip(), symbol, symbol, ' |COL| '.join(["x0:"+symbol]*col_length),symbol)
else:
    with open(args.del_file) as fp:
        for line in fp:
            print line.strip()
