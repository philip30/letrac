#!/usr/bin/env python
# Script to append the KB to the current rule
# Usage append-kb.py --kb [KB] [--trg_factors [TRG_FACTORS]]
# Philip Arthur (philip.arthur30@gmail.com)

import sys
import argparse

parser = argparse.ArgumentParser(description="Append KB")
parser.add_argument('--kb', type=str,required=True)
parser.add_argument('--trg_factors', type=int, default=1)
args = parser.parse_args()

# Global variables
trg_factors = args.trg_factors
all_map = set()

if trg_factors != 1 and trg_factors != 2:
    raise Exception("Can supports only have 1 or 2 trg_factors.")

### Functions to build the source + target string for the rule
def build_source(head,name):
    name = name.split()
    return (" ".join(['"%s"' % (x) for x in name]) + " @ " + head)

def build_target(head,trg,src):
    if ' ' in trg:
        trg = "'" + trg.replace(" ","#$#") + "'"
    s = '"%s" @ %s' % (trg, head)
    if trg_factors == 2:
        s = src + " |COL| " + s
    return s

### Function to print the KB 
def print_rule(head, src, trg, feature):
    print '%s ||| %s ||| %s=1' % (build_source(head,src),build_target(head,trg,src),feature)

### Functions to process the line
def state_kb(line):
    state_name = line[0][1:-1]
    print_rule("STATE",state_name,state_name,"state_kb")

def city_kb(line):
    global all_map
    state_name, state_abv, city_name = line[0][1:-1], line[1][1:-1], line[2][1:-1]
    if (("city",city_name)) not in all_map:
        all_map.add(("city",city_name))
        print_rule("CITY",city_name,city_name,"city_kb")
    print_rule("ABR",state_name,state_abv,"abr_kb")

def river_kb(line):
    river_name = line[0][1:-1]
    print_rule("RIVER",river_name,river_name,"river_kb")

def mountain_kb(line):
    mountain_name = "mount " + line[2][1:-1]
    print_rule("PLACE",mountain_name,mountain_name,"mountain_kb")

def lake_kb(line):
    lake_name = body[0][1:-1]
    print_rule("PLACE",lake_name,lake_name,"lake_kb")

# Functions just to map predicate to function only for beautification
functions = {'state':state_kb, 'city':city_kb, 'river':river_kb,'mountain':mountain_kb,'lake':lake_kb}

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
                
