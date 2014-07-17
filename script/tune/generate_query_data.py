#!/usr/bin/env python

import sys
import argparse
import qdatabase

MAX_VAR = 14
DELAY = 45000
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
    
    if len(ret) > 1 and ret[-1] == '.': ret = ret[:-1]

    #if any(x in OMIT_SET for x in ret):
    #    ret = 'stateid(omit)?'

    if gs: 
        return ret + "."
    else:
        return "time_out(" +ret + ",%d,Res)." % (DELAY)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str)
    parser.add_argument('--geoquery_dir', type=str)
    parser.add_argument('--gold_standard',action='store_true')
    parser.add_argument('--output',type=str)
    parser.add_argument('--database',type=str)
    args = parser.parse_args()

    generate_query_data(args.input,args.geoquery_dir,args.output,args.gold_standard, args.database)

def generate_query_data(input_arg,geoquery_arg,out_arg,is_gs,database):
    inp = open(input_arg, "r")
    geoquery_location = geoquery_arg
    out = open(out_arg, "w")
    qsync = open(out_arg[0:out_arg.rfind(".")]+".qsync","w")

    print >> out, "compile('" + geoquery_location + "')."
    print >> out, ""

    print >> out, set_prolog_print_all_list()   
    print >> out, ""

    print >> out, load_timeout()
    print >> out, ""

    db_map = {}
    qmap = {}
    for line in inp:
        line = line.strip()
        query = validate(line.replace("-","\\+ ").replace("#$#", ' ').replace('ZERO','0'),is_gs)
        if line.startswith("Failed"):
            print >> qsync, "write\tAnswer = [Failed]"
        elif not database or (query not in qmap and not qdatabase.exists(database,query)):
            qmap[query] = 1
            print >> out, query 
            print >> out, ""
            print >> qsync, "exec\t"+query
        else:
            print >> qsync, "read\t"+query

    inp.close()
    out.close()
    qsync.close()


def set_prolog_print_all_list():
    return "set_prolog_flag(toplevel_print_options,[max_depth(1000),quoted(true)])."

def load_timeout():
    return "use_module(library(timeout))."

if __name__ == '__main__':
    main()
