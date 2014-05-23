#!/usr/bin/env python

import sys
import re
import argparse
import qdatabase

err = [];
out = [];
EMPTY_ANSWER = "Ans = []"

parser = argparse.ArgumentParser()
parser.add_argument('--log_file', type=str)
parser.add_argument('--output_file', type=str)
parser.add_argument('--database_dir', type=str)
parser.add_argument('--sync', type=str)
args = parser.parse_args()

def print_answer(answer,query):
    if args.database_dir:
        qdatabase.write(args.database_dir,query,answer)
    print answer

def read_answer(query):
    return qdatabase.read(args.database_dir,query)

with open (args.log_file,"r") as f:
    err = f.readlines()

with open (args.output_file,"r") as f:
    out = f.readlines()

ep = 25
op = 0

sy_file = open(args.sync,"r")
for line in sy_file:
    command,query = line.strip().split("\t")
    if command == 'exec':
        err[ep] = err[ep].strip()
        if ep > len(err):
            print >> sys.stderr, "Error pointer goes out of bounds"
            sys.exit(1)
        if err[ep].startswith('Res = success ?'):
            print_answer(out[op].strip(),query)
            op += 1
            ep += 2
        elif err[ep].startswith('Res = time_out ?'):
            print_answer(EMPTY_ANSWER,query)
            ep += 2
        elif err[ep].startswith('! Existence') or err[ep].startswith('! Domain') or err[ep].startswith('! Type'):
            print_answer(EMPTY_ANSWER,query)
            ep += 3
        elif err[ep].startswith('! Inst'):
            print_answer(EMPTY_ANSWER,query)
            ep += 2
        elif re.match('[A-Z] = ',err[ep]):
            print_answer(EMPTY_ANSWER,query)
            if err[ep].endswith('?'): 
                ep += 3
            else:
                k = 1
                while ep+k < len(err) and not err[ep+k].startswith('Res ='):
                    k+=1
                ep += 2 + k
        elif err[ep].startswith('no'):
            print_answer(EMPTY_ANSWER,query)
            ep += 1
        elif err[ep].startswith('yes'):
            print_answer(out[op].strip(),query)
            op += 1
            ep += 1
        elif err[ep].startswith('! Syntax'):
            print_answer(EMPTY_ANSWER,query)
            ep += 6
            #ep += (6 if not err[ep+1].startswith("! ) cannot start") else 5)
        else:
            print >> sys.stderr, "Unrecognized pattern generated by SICSTUS", err[ep]
            sys.exit(1)
    else:
        print read_answer(query)
