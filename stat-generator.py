#!/usr/bin/env python
# Script to generate a stat for Travatar's batch-tune
# Philip Arthur (philip.arthur30@gmail.com)

import sys
import argparse
import threading
import signal
import math
from script.util.qdatabase import MySql
from script.util.breduct import breduct as beta_reduction
from script.util.typecheck import typecheck as type_check
from multiprocessing import Pool, Process, Lock
from subprocess import Popen, PIPE

# Arguments
parser = argparse.ArgumentParser(description="Stat Generator")
parser.add_argument('-threads', type=int, default=4,help="Number of threads")
parser.add_argument('-working_dir', type=str, required=True)
parser.add_argument('-letrac', type=str, required=True)
parser.add_argument('-input', type=str, required=True)
parser.add_argument('-trg_factors', type=int, required=True)
parser.add_argument('-geoquery', type=str, required=True)
parser.add_argument('-ref', type=str, required=True)
#parser.add_argument('-original_ref', type=str, required=True)
parser.add_argument('-database_config', type=str)
#parser.add_argument('-time', type=str, required=True)
parser.add_argument('-timeout', type=int, default=1)
parser.add_argument('-driver_function', type=str, default="execute_query")
parser.add_argument('-no_typecheck', action="store_true")
parser.add_argument('-check_empty', action="store_true")
args = parser.parse_args()

# Global variables
BAD_QUERY = "Answer = [BadQuery]"
EMPTY_RESULT = "Answer = [EmptyResult]"
TIMEOUT_RESULT = "Answer = [Timeout]"
BREDUCT_ERR = "Error"
stderr_lock = Lock()
TIMEOUT = args.timeout

# Decomposing File Input
cols = args.input.split("/")
parent_dir, file_name = "/".join(cols[:-1]), cols[-1]
stripped_fname = ".".join(file_name.split(".")[:-1])

# Database preparation
database = MySql(args.database_config)

# Some Intermediate result output path
nbest_path = args.input
breduct_path = parent_dir + ("/" if len(parent_dir) != 0 else "") + stripped_fname + ".reduct"
typecheck_path = parent_dir + ("/" if len(parent_dir) != 0 else "") + stripped_fname + ".typecheck"
empty_path = parent_dir + ("/" if len(parent_dir) != 0 else "") + stripped_fname + ".empty" 
result_path = parent_dir + ("/" if len(parent_dir) != 0 else "") + stripped_fname + ".result"

# log files
typecheck_log = open(parent_dir + ("/" if len(parent_dir) != 0 else "") + stripped_fname + ".typecheck.log", 'w')

# Global Data Structure
gold_standard = []
original_ref = []
breduct_list = []
time = []

#### FUNCTIONS ####
# Is answer malformed or not
def malformed_answer(q):
    return q == BAD_QUERY or q == EMPTY_RESULT

# Beta Reduction
def breduct(i,line, args):
    line = line.strip().split(" ||| ")
    n, line = line[0], line[1]
    if len(line.strip()) == 0:
        return "%s\t%s" % (n, BREDUCT_ERR)

    line_col = line.split(" |COL| ")
    
    if args.trg_factors == 2:
        paraphrase = line_col[0]
        
    line = line_col[args.trg_factors-1].replace(" ","") 

    try:
        result = beta_reduction(line)
        result = result.replace("#$#", " ")
        result = result.replace("-", "\\+ ")
    except:
        sync_print("Beta Reduction Error: " + n + " " + line)
        result = BREDUCT_ERR

    if args.trg_factors == 2:
        result = "%s |COL| %s" % (result, paraphrase)

    return "%s\t%s" % (n, result)

# Doing typecheck
def typecheck(i,line,args):
    global typecheck_log
    line = line.strip().split("\t")
    n, line = line[0], line[1].split(" |COL| ")[0]
    return str(i) if type_check(line,typecheck_log) else ""

# Checking whether line is empty or not
def check_empty(i, line, args):
    global gold_standard
    line = line.strip().split("\t")
    n, line = line[0], line[1]
    return str(i) if len(read_list(line)) != 0 else ""

# Synchronous printing for multithreading
def sync_print(line):
    global stderr_lock
    stderr_lock.acquire()
    sys.stderr.write(str(line) + "\n")
    stderr_lock.release()

# A thread object to access SWIPL -s eval.pl
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
        
        outval, errval = self.process.communicate(input=(self.line+"\nhalt.\n"))
        
        if errval is not None:
            for line in errval.split("\n"):
                if line.startswith("Answer = "):
                    outval = line
                    break
            else:
                outval = BAD_QUERY
        else:
            outval = BAD_QUERY

        self.result = (self.process.returncode, outval, errval) 
    def terminate(self):
        if self.process is not None:
            self.process.terminate()

# Query the database!
def geoquery(i,line, args):
    n, line = line.strip().split("\t")
    line = line.split(" |COL| ")[0]
    cmd = "%s(%s,Answer)." % (args.driver_function, line)
    result = None
    result_ok = True
# FOR THE SAKE OF DETECTING UNSTABLE RESULT THESE LINES ARE COMMENTED
    try:
        result = database.read(line)
        if result is None:
            result_ok = False
        else:
            sync_print("Reading Query: " + line)
    except:
        result_ok = False
    if not result_ok:
        sync_print("Executing Query: " + line)
        program, s, location = args.geoquery.split(" ")
        
        thread = GeoThread(cmd,program,s,location)
        thread.start()
        thread.join(set_timeout(n,TIMEOUT))

        if thread.is_alive():
            thread.terminate()
            thread.join()

        retcode, outval, errval = thread.result
        if outval is None:
            outval = EMPTY_RESULT
        
        if retcode != 0:
            if retcode == -15:
                sync_print("Timeout Query: " + line)
                outval = TIMEOUT_RESULT
            else:
                sync_print("BadQuery: " + line)
                outval = BAD_QUERY
        elif len(outval.strip()) == 0:
            outval = EMPTY_RESULT
        result = outval.strip()
        database.write(line,result)
    return "%s\t%s" % (n,result)

# Setting timeout
def set_timeout(n, base):
    global time
    n = int(n)
    if n >= 0 and n < len(time):
        return int(math.ceil(time[n])+1)
    else:
        return base

# Generate Stat
def stat(i,line,args):
    global gold_standard
    global original_ref
    global breduct_list
    n, line = line.strip().split("\t")
    comp_list = read_list(line)
    n = int(n) 
    return "%d 1" % (1 if breduct_list[i] == original_ref[n] or comp_list == gold_standard[n] else 0)

def exec_single(inf, ouf, function, args):
    inf.seek(0)
    for i, line in enumerate(inf):
        print >> ouf, function(i,line,args)

# Cooly process all of them in parallel 
def execpar(args, function, inf, ouf, err,print_empty=True):
    if args.threads == 1:
        exec_single(inf, ouf, function, args)
    else:
        try:
            pool = Pool(processes=args.threads)
            inp = [line for line in inf]
            out = [pool.apply_async(function, args=(i,line,args)) for i, line in enumerate(inp)]
            results = [p.get() for p in out]

            for line in results:
                if print_empty or len(line) != 0:
                    print >> ouf, line
        except:
            print >> err,"Multiprocessing exception, executing in single thread..."
            exec_single(inf, ouf, function, args)
    inf.close()
    ouf.close()

# Read Answer List
def read_list(line):
    line_set = set()
    temp = line.strip().split(" = ")
    if len(temp) == 1:
        return set([])
    _, line = temp[0], temp[1]
    if line[-1] == '.':
        line = line[:-1]
    line = line[1:-1]
    for item in line.split(','):
        if len(item) > 0:
            if item[0] == "'" and item[-1] == "'":
                item = item[1:-1]
            line_set.add(item)
    return line_set

# Function to purge line if the line number does not exists in ref_file
# used to sync the type-checking
def purge_line(ref_file, inp_files):
    # First read the reference
    lines = set()
    with open(ref_file) as ref_fp:
        for line in ref_fp:
            line = line.strip()
            if len(line) != 0:
                lines.add(int(line))

    # Second purge them!
    for inp_file in inp_files:
        buffer = []
        with open(inp_file) as inp_read:
            for i, line in enumerate(inp_read):
                if i in lines:
                    buffer.append(line.strip())
        with open(inp_file,'w') as inp_write:
            for line in buffer:
                print >> inp_write, line

#### EXECUTION BEGINS HERE ####
# Reading Gold Standard
with open(args.ref,'r') as gf:
    for line in gf:
        line = line.strip().split("\t")
        gold_standard.append(read_list(line[0]))    
        original_ref.append(line[1][:-1].replace(" ",""))
        time.append(float(line[2]))

# Beta Reduction
execpar(args, breduct, open(args.input, 'r'), open(breduct_path,'w'), sys.stderr)

# Type checking (if no_typecheck flag == false)
if not args.no_typecheck:
    execpar(args, typecheck, open(breduct_path, 'r'), open(typecheck_path, 'w'), sys.stderr, print_empty=False)
    purge_line(typecheck_path, [nbest_path, breduct_path])
else:
    print >> typecheck_log, "No Typechecking is performed!"    
typecheck_log.close()

# Query the database
execpar(args, geoquery, open(breduct_path, 'r'), open(result_path,'w'), sys.stderr)

# Check empty
if args.check_empty:
    execpar(args, check_empty, open(result_path, 'r'), open(empty_path, 'w'), sys.stderr, print_empty=False)
    purge_line(empty_path, [nbest_path, breduct_path, result_path])

# Read the reduction list (After typecheck)
with open(breduct_path) as b_fp:
    for line in b_fp:
        breduct_list.append(line.strip().split("\t")[1].split(" |COL| ")[-1].replace(" ",""))

# Finally, stat = [answer(GS) == answer(sys)] OR [GS == sys]
execpar(args, stat, open(result_path,'r'), sys.stdout, sys.stderr)
sys.stderr.flush()

