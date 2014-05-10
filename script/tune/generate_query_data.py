#!/usr/bin/env python

import sys
import argparse

MAX_VAR = 10
DELAY = 100
OMIT_SET = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[MAX_VAR:])

def validate(line,gs):
    ret = ""
    k = 0
    # Not needed (solved)
    while True:
        i = line.find(")(",k)
        if i == -1:
            ret += line[k:]
            break
        else:
            ret += line[k:i]
            k = i+1
            while line[k] != ')' and k < len(line):
                k += 1
    
    if ret[-1] == '.': ret = ret[:-1]

    if any(x in OMIT_SET for x in ret):
        ret = 'stateid(omit) ?'

    if gs: 
        return ret + "."
    else:
        return "time_out(" +ret + ", %d, Res)." % (DELAY)

def main():
    generate_query_data(sys.argv[1],sys.argv[2],sys.argv[3],len(sys.argv)>4)

def generate_query_data(input_arg,geoquery_arg,out_arg,is_gs):
    inp = open(input_arg, "r")
    geoquery_location = geoquery_arg
    out = open(out_arg, "w")
    
    print >> out, "compile('" + geoquery_location + "')."
    print >> out, ""

    print >> out, set_prolog_print_all_list()   
    print >> out, ""

    print >> out, load_timeout()
    print >> out, ""

    for line in inp:
        line = line.strip()
        print >> out, validate(line.replace("-","\\+ ").replace("#$#", ' '),is_gs)
        print >> out, ""

def set_prolog_print_all_list():
    return "set_prolog_flag(toplevel_print_options,[max_depth(1000),quoted(true)])."

def load_timeout():
    return "use_module(library(timeout))."

if __name__ == '__main__':
    main()
