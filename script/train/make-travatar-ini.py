#!/usr/bin/env python

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--tm_file', type=str, required=True)
parser.add_argument('--lm_file', type=str, default="")
parser.add_argument('--trg_factors',type=int, default=1)
args = parser.parse_args()

feature={'lm':0.8,\
        'psgl':0.05,\
        'plgs':0.05,\
        'count':0.05,\
        'del_rule':-1,\
        'p':'-0.5',\
        'state_kb':'0.5',\
        'city_kb':'0.5',\
        'river_kb':0.2, \
        'mountain_kb':0.1, \
        'lake_kb':0.2,\
        'abr_kb':0.3}

ROOT_SYMBOL = "QUERY"

def write_config(key, value,stream=sys.stdout):
    if key != 'lm' or args.lm_file:
        print >> stream, "["+str(key)+"]"
        print >> stream, str(value)
        print >> stream, ""

# Running the script
write_config('tm_file',args.tm_file)
write_config('in_format','word')
write_config('delete_unknown','true')
write_config('tm_storage','fsm')
write_config('root_symbol', ROOT_SYMBOL)
write_config('trg_factors', args.trg_factors)

if args.lm_file != "":
    write_config('lm_file',args.lm_file)

# Printing weight
print "[weight_vals]"
for weight_key, weight_val in feature.items():
    if weight_key != "lm" or args.lm_file != "": 
        print weight_key + "=" + str(weight_val)


