#!/usr/bin/env python

import sys

feature={'parse':0.3,'lm':0.8,'psgl':0.05,'plgs':0.05,'count':0.05,'prob':0.05,'del':-1}

def main():
    write_config('tm_file',sys.argv[1])
    write_config('binarize','right')
    write_config('in_format','word')
    write_config('delete_unknown','true')
    write_config('tm_storage','fsm')
    write_config('root_symbol','QUERY')
    write_config('default_symbol','FORM')
    write_config('trg_factors','2' if len(sys.argv) > 3 and sys.argv[3] == '-three_sync' else '1')

    if len(sys.argv) > 2:
        write_config('lm_file',sys.argv[2])
    
    # Printing weight
    print "[weight_vals]"
    for weight_key, weight_val in feature.items():
        print weight_key + "=" + str(weight_val)

def write_config(key, value,stream=sys.stdout):
    print >> stream, "["+str(key)+"]"
    print >> stream, str(value)
    print >> stream, ""

if __name__ == '__main__':
    main()
