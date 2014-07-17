#!/usr/bin/python

import sys
import time
import os
import hashlib 
from collections import defaultdict

MAX_TRIES = 20
QUERY_MAP = defaultdict(lambda x:str(hashlib.sha224(x).hexdigest()))
def main():
    init(sys.argv[1])

def init(loc):
    print >> sys.stderr, "Checking exists:", loc
    if not os.path.exists(loc):
        print >> sys.stderr, "Not exists, creating dir:", loc
        os.makedirs(loc)

def build_path(loc,query):
    return loc + '/' + QUERY_MAP[query]

def strip_query(query):
    if query.startswith("time_out("):
        query = query[len("time_out("):]
        i = query.find('(') + 1
        depth = 1
        while (depth != 0):
            if query[i] == '(': depth += 1
            elif query[i] == ')':depth -= 1
            i+= 1
        query = query[:i]
    return query

def exists(loc, query):
    query = strip_query(query)
    return os.path.exists(build_path(loc,query))

def write(loc,query,result):
    query = strip_query(query)
    loc = build_path(loc,query)
    if os.path.exists(loc):
        f = open(loc,"r")
        line1 = f.readline().strip()
        if query != line1:
            print >> sys.stderr, "ERROR, hash error double:" + query + " with " + line1
            return 1
        f.close()
    else:
        f = open(loc,"w")
        f.write(query + os.linesep)
        f.write(result + os.linesep)
        f.close()
    return 0

def read(loc,query,default="Answer = [ReadingTimeOut]"):
    query = strip_query(query)
    tries = 0
    while not exists(loc,query):
        print >> sys.stderr, "Waiting for",build_path(loc,query)
        tries += 1
        if tries == MAX_TRIES:
            return default
        time.sleep(1)
    f = open(build_path(loc,query),"r")
    line1 = f.readline().strip()
    if line1 != query:
        if line1 == '':
            os.remove(build_path(loc,query))
        else:
            print >> sys.stderr, "ERROR, hash error double:" + query + " with " + line1
        return None
    ret = f.readline().strip()
    f.close()
    return ret
    
if __name__ == '__main__':
    main()
