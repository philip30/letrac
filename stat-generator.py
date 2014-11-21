#!/usr/bin/env python

import sys
import argparse
import time
from multiprocessing import Pool, Process, Lock
from subprocess import Popen, PIPE
from script.tune.breduct import breduct as beta_reduction

# Arguments
parser = argparse.ArgumentParser(description="Stat Generator")
parser.add_argument('--threads', type=int, default=4,help="Number of threads")
parser.add_argument('--working_dir', type=str, required=True)
parser.add_argument('--letrac', type=str, required=True)
parser.add_argument('--input', type=str, required=True)
parser.add_argument('--trg_factors', type=int, required=True)
parser.add_argument('--geoquery', type=str, required=True)
parser.add_argument('--ref', type=str, required=True)
args = parser.parse_args()
 
# Beta Reduction
def breduct(i,line, args):
    try:
        line = line.strip()
        line = line.split(" |COL| ")[args.trg_factors-1]
        line = line.replace(" ","")
        result = beta_reduction(line)
        result = result.replace("#$#", " ")
        result = result.replace("-", "\\+")
    except:
        result = ""
    return result

# Query the database!
def geoquery(i,line, args):
    line = line.strip() + ".\n"
    program, s, location = args.geoquery.split(" ")
    process = Popen([program,s,location,'-q'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    outval, errval = process.communicate(input=line)
    retcode = process.returncode
    return outval.strip()

# Generate Stat
def stat(i,line,args):
    comp_list = read_list(line.strip())
    return "%d 1" % (1 if comp_list == gold_standard[i] else 0)
    
# Cooly process all of them in parallel 
def execpar(args, function, inf, ouf, err):
    pool = Pool(processes=args.threads)
    results = [pool.apply(function, args=(i,line,args)) for i, line in enumerate(inf)]
    for line in results:
        print >> ouf, line
    inf.close()
    ouf.close()

# Read Answer List
def read_list(line):
    line_set = set()
    temp = line.strip().split(" = ")
    if len(temp) == 1:
        return set([])
    _, line = temp[0], temp[1]
    line = line[1:-1]
    for item in line.split(','):
        line_set.add(item)
    return line_set

# Reading Gold Standard
gold_standard = []
with open(args.ref,'r') as gf:
    for line in gf:
        gold_standard.append(read_list(line.strip()))    

# Decomposing File Input
cols = args.input.split("/")
parent_dir, file_name = "/".join(cols[:-1]), cols[-1]
stripped_fname = ".".join(file_name.split(".")[:-1])

# Some Intermediate result output path
breduct_path = parent_dir + "/" if len(parent_dir) != 0 else "" + stripped_fname + ".reduct"
result_path = parent_dir + "/" if len(parent_dir) != 0 else "" + stripped_fname + ".result"

# Execution
execpar(args, breduct, open(args.input, 'r'), open(breduct_path,'w'), sys.stderr)
execpar(args, geoquery, open(breduct_path, 'r'), open(result_path,'w'), sys.stderr)
execpar(args, stat, open(result_path,'r'), sys.stdout, sys.stderr)

