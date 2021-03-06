#!/usr/bin/env python

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--tm_file', type=str, required=True)
parser.add_argument('--lm_file', type=str, default="")
parser.add_argument('--trg_factors',type=int, default=1)
parser.add_argument('--one_feat', type=int, default=0)
args = parser.parse_args()

feature={'lm':0.8,\
        'psgl':0.05,\
        'plgs':0.05,\
        'del_rule':-10,\
        'parse':0.2, \
        'prob': 0.05, \
        'p':'-0.5',\
        'unk': '-1',\
        'word': '0.05',\
        'kb':0.3}

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

for i in range(args.one_feat):
    print "r%d=%f" % (i, 0.05)

