#!/usr/bin/env python

import sys
import argparse
import time
import script.tune.qdatabase as database
import threading
from multiprocessing import Pool, Process, Lock
from subprocess import Popen, PIPE
from script.tune.breduct import breduct as beta_reduction

TIMEOUT=60 # second
BAD_QUERY = "Answer = [BadQuery]"
EMPTY_RESULT = "Answer = [EmptyResult]"
TIMEOUT_RESULT = "Answer = [Timeout]"

# Arguments
parser = argparse.ArgumentParser(description="Stat Generator")
parser.add_argument('-threads', type=int, default=4,help="Number of threads")
parser.add_argument('-working_dir', type=str, required=True)
parser.add_argument('-letrac', type=str, required=True)
parser.add_argument('-input', type=str, required=True)
parser.add_argument('-trg_factors', type=int, required=True)
parser.add_argument('-geoquery', type=str, required=True)
parser.add_argument('-ref', type=str, required=True)
parser.add_argument('-database', type=str, required=True)
parser.add_argument('-timeout', type=int, default=60)
args = parser.parse_args()

TIMEOUT = args.timeout
database.init(args.database)

def malformed_answer(q):
    return q == BAD_QUERY or q == EMPTY_RESULT

# Beta Reduction
def breduct(i,line, args):
    line = line.strip().split(" ||| ")
    n, line = line[0], line[1]
    line = line.split(" |COL| ")[args.trg_factors-1]
    line = line.replace(" ","") 
    try:
        result = beta_reduction(line)
        result = result.replace("#$#", " ")
        result = result.replace("-", "\\+ ")
    except:
        print >> sys.stderr, "Beta Reduction Error:", n, line
        result = "Error"
    return "%s\t%s" % (n, result)

class GeoThread (threading.Thread):
    def __init__ (self, line, program, s, location):
        threading.Thread.__init__(self)
        self.program = program
        self.line = line
        self.s = s
        self.location = location
        self.result = None
        self.process = None
    
    def run(self):
        self.process = Popen([self.program, self.s, self.location, 'q'], stdin=PIPE,stdout=PIPE,stderr=PIPE)
        outval,errval = self.process.communicate(input=(self.line+"\n"))
        self.result = (self.process.returncode, outval, errval) 
    def terminate(self):
        self.process.terminate()


# Query the database!
def geoquery(i,line, args):
    n, line = line.strip().split("\t")
    line = line + "."
    result = None
    result_ok = True
    if database.exists(args.database, line):
        try:
            result = database.read(args.database, line)
        except:
            result_ok = False
    else:
        result_ok = False
    if not result_ok:
        # print >> sys.stderr, i,"Executing Query:", line
        program, s, location = args.geoquery.split(" ")
        
        thread = GeoThread(line,program,s,location)
        thread.start()
        thread.join(TIMEOUT)

        if thread.is_alive():
            thread.terminate()
            thread.join()

        retcode, outval, errval = thread.result
        if retcode != 0:
            if retcode == -15:
                print >> sys.stderr, "Timeout Query:", n, line
                outval = TIMEOUT_RESULT
            else:
                print >> sys.stderr, "BadQuery:", n, line
                outval = BAD_QUERY
        elif len(outval.strip()) == 0:
            outval = EMPTY_RESULT
        result = outval.strip()
        database.write(args.database,line,result)
    return "%s\t%s" % (n,result)

gold_standard = []
# Generate Stat
def stat(i,line,args):
    global gold_standard
    n, line = line.strip().split("\t")
    comp_list = read_list(line)
    return "%d 1" % (1 if comp_list == gold_standard[int(n)] else 0)

# Cooly process all of them in parallel 
def execpar(args, function, inf, ouf, err):
    pool = Pool(processes=args.threads)
    inp = [line for line in inf]
    out = [pool.apply_async(function, args=(i,line,args)) for i, line in enumerate(inp)]
    results = [p.get() for p in out]

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
with open(args.ref,'r') as gf:
    for line in gf:
        gold_standard.append(read_list(line.strip()))    

# Decomposing File Input
cols = args.input.split("/")
parent_dir, file_name = "/".join(cols[:-1]), cols[-1]
stripped_fname = ".".join(file_name.split(".")[:-1])

# Some Intermediate result output path
breduct_path = parent_dir + ("/" if len(parent_dir) != 0 else "") + stripped_fname + ".reduct"
result_path = parent_dir + ("/" if len(parent_dir) != 0 else "") + stripped_fname + ".result"

# Execution
if args.threads != 1:
    execpar(args, breduct, open(args.input, 'r'), open(breduct_path,'w'), sys.stderr)
    execpar(args, geoquery, open(breduct_path, 'r'), open(result_path,'w'), sys.stderr)
    execpar(args, stat, open(result_path,'r'), sys.stdout, sys.stderr)
else:
    with open(args.input, 'r') as inp_file:
        with open(breduct_path,'w') as bred_file:
            with open(result_path, 'w') as res_file:
                for i, line in enumerate(inp_file):
                    _b = breduct(i, line, args)
                    print >> bred_file, _b
                    _g = geoquery(i, _b, args)
                    print >> res_file, _g
                    print >> sys.stdout, stat(i, _g, args)

