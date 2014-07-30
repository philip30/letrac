#!/usr/bin/env python

import sys
from random import shuffle

prefix_map = {}

def prefixadd(inp):
    inp = inp.split(" ")
    for i in range(1,len(inp)):
        prefix_map[' '.join(inp[0:i])] = 1

with open(sys.argv[1],"r") as kbs:
    for line in kbs:
        line = line.strip()
        k = line.find('(')
        predicate = line[0:k]
        end = line.find(')',k)
        body = line[k+1:end].split(",")
        if predicate == 'state':
            state_name = body[0][1:-1]
            prefixadd(state_name + "state")
        elif predicate == 'city':
            state_name, state_abv, city_name = body[0][1:-1], body[1][1:-1], body[2][1:-1]
            prefixadd(city_name + " " + state_abv)
            prefixadd(city_name + " " + state_name)
        elif predicate == 'river':
            river_name = body[0][1:-1]
            prefixadd(river_name + "river")
        elif predicate == 'mountain':
            mountain_name = body[2][1:-1]
            prefixadd(mountain_name + "mountain")
        elif predicate == 'lake':
            lake_name = body[0][1:-1]
            prefixadd(lake_name + "lake")
prefixadd("united states")

def shuffle_query(q):
    l = []
    i = 0
    temp = []
    while i < len(q):
        temp.append(q[i])
        st = ' '.join(temp)
        if st not in prefix_map:
            l.append(' '.join(temp))
            temp = []
        i+=1
    if len(temp) != 0:
        l.append(' '.join(temp))
    shuffle(l)
    return l

with open(sys.argv[2],"r") as qbs:
    for line in qbs:
        line = line.strip().split(" ||| ")
        line[0] = line[0].split(" ")
        label = line[0][-2:]
        line[0] = line[0][:-2]
        line[0] = map(lambda x: x[1:-1] if x[0] == '"' and x[-1] == '"' else x, line[0])
        line[0] = shuffle_query(line[0])
        line[0] = ' '.join(map(lambda x: '"' + x +'"' if ":" not in x else x, line[0])+label)
        print " ||| ".join(line)

