#!/usr/bin/env python

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--tm_file', type=str, required=True)
parser.add_argument('--lm_file', type=str, default="")
parser.add_argument('--three_sync',action='store_true')
args = parser.parse_args()



feature={'parse':0.3,'lm':0.8,'psgl':0.05,'plgs':0.05,'count':0.05,'prob':0.05,'del':-1}

def main():
    write_config('tm_file',args.tm_file)
    write_config('binarize','right')
    write_config('in_format','word')
    write_config('delete_unknown','true')
    write_config('tm_storage','fsm')
    write_config('root_symbol','QUERY')
    write_config('default_symbol','FORM')
    write_config('trg_factors','2' if args.three_sync else '1')

    if args.lm_file != "":
        write_config('lm_file',args.lm_file)
    
    # Printing weight
    print "[weight_vals]"
    for weight_key, weight_val in feature.items():
        if weight_key != "lm" or args.lm_file != "": 
            print weight_key + "=" + str(weight_val)

def write_config(key, value,stream=sys.stdout):
    if key != 'lm' or args.lm_file:
        print >> stream, "["+str(key)+"]"
        print >> stream, str(value)
        print >> stream, ""

if __name__ == '__main__':
    main()
