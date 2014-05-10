#!/usr/bin/env python

import sys
import argparse

def main(): 
    parser = argparse.ArgumentParser(description="Run Generate stat data")
    parser.add_argument('--gs',type=str,required=True)
    parser.add_argument('--semout', type=str,required=True)
    parser.add_argument('--n', type=str)
    args = parser.parse_args()
    
    gs_fp = open(args.gs, "r")
    sp_fp = open(args.semout, "r")
        
    gs_list = []
    for line in gs_fp:
        gs_list.append(read_list(line.strip()))
    
    n_fp = open(args.n,"r")
    for sp_line, n_line in zip(sp_fp,n_fp):
        sp_line, n_line = map(lambda x: x.strip(), (sp_line,n_line))
        n = int(n_line)
        print "%d 1" % (1 if read_list(sp_line) == gs_list[n] else 0)
    map(lambda x: x.close(), [gs_fp, sp_fp, n_fp])    
    
def read_list(line):
    line_set = set()
    _, line = line.strip().split(" = ")
    line = line[1:-1]
    for item in line.split(','):
        _item = None
        try:
            _item = int(item)
        except ValueError:
            try:
                _item = float(item)
            except ValueError:
                _item = item
        line_set.add(_item)
    return line_set

if __name__ == '__main__':
    main()
