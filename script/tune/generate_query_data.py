#!/usr/bin/python

import sys
import argparse

def main():
    generate_query_data(sys.argv[1],sys.argv[2],sys.argv[3])

def generate_query_data(input_arg,geoquery_arg,out_arg):
    inp = open(input_arg, "r")
    geoquery_location = geoquery_arg
    out = open(out_arg, "w")
    
    print >> out, "compile('" + geoquery_location + "')."
    print >> out, ""

    print >> out, set_prolog_print_all_list()   
    print >> out, ""

    for line in inp:
        print >> out, line.replace("-","\\+ ").replace("#$#", ' ')

def set_prolog_print_all_list():
    return "set_prolog_flag(toplevel_print_options,[max_depth(1000),quoted(true)])."

if __name__ == '__main__':
    main()
