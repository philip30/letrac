#!/usr/bin/env python
# Script to append the KB to the current rule
# Usage append-kb.py --kb [KB] [--trg_factors [TRG_FACTORS]]
# Philip Arthur (philip.arthur30@gmail.com)

import sys
import argparse
import subprocess

parser = argparse.ArgumentParser(description="Append KB")
parser.add_argument('--kb', type=str,required=True)
parser.add_argument('--trg_factors', type=int, default=1)
parser.add_argument('--stem', type=str)
args = parser.parse_args()

# Global variables
trg_factors = args.trg_factors
all_map = set()

if trg_factors != 1 and trg_factors != 2:
    raise Exception("Can supports only have 1 or 2 trg_factors.")


def stem(word):
    pipe = subprocess.Popen(["perl", args.stem], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = pipe.communicate(input=word)
    return out.strip()

### Functions to build the source + target string for the rule
def build_source(head,name):
    name = name.split()
    if args.stem:
        name = [stem(x) for x in name]
        
    return (" ".join(['"%s"' % (x) for x in name]) + " @ " + head)

def build_target(head,trg,src):
    if ' ' in trg:
        trg = "'" + trg.replace(" ","#$#") + "'"
    s = '"%s" @ %s' % (trg, head)
    if trg_factors == 2:
        s = build_source(head,src) + " |COL| " + s
    return s

### Function to print the KB 
def print_rule(head, src, trg, feature):
    print '%s ||| %s ||| %s=1' % (build_source(head,src),build_target(head,trg,src),"kb")

### Functions to process the line
def state_kb(line):
    state_name = line[0][1:-1]
    print_rule("STATE",state_name,state_name,"kb")

def city_kb(line):
    global all_map
    state_name, state_abv, city_name = line[0][1:-1], line[1][1:-1], line[2][1:-1]
    if (("city",city_name)) not in all_map:
        all_map.add(("city",city_name))
        print_rule("CITY",city_name,city_name,"kb")
    print_rule("ABR",state_name,state_abv,"kb")

def river_kb(line):
    river_name = line[0][1:-1]
    print_rule("RIVER",river_name,river_name,"kb")

def mountain_kb(line):
    mountain_name = "mount " + line[2][1:-1]
    print_rule("PLACE",mountain_name,mountain_name,"kb")

def lake_kb(line):
    lake_name = body[0][1:-1]
    print_rule("PLACE",lake_name,lake_name,"kb")

def highlow(line):
    high_name = body[2][1:-1]
    low_name = body[4][1:-1]
    print_rule("PLACE", high_name,high_name, "kb")
    print_rule("PLACE", low_name, low_name, "kb")

# Functions just to map predicate to function only for beautification
functions = {'state':state_kb, 'city':city_kb, 'river':river_kb,'mountain':mountain_kb,'lake':lake_kb, 'highlow':highlow}

# Printing the previous rule
for line in sys.stdin:
    print line.strip()

# Appending the KB information to the rule
with open(args.kb,"r") as kbs:
    for line in kbs:
        line = line.strip()
        k = line.find('(')
        predicate = line[0:k]
        end = line.find(')',k)
        body = line[k+1:end].split(",")
        if predicate not in functions:
            pass
            #raise Exception("Unknown predicate: " + predicate)
        else:
            functions[predicate](body)
                
