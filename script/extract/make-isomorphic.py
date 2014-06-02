#!/usr/bin/env python

import sys
import argparse
from collections import defaultdict
from geometric import transform_into_rule
from geometric import extract
from geometric import print_node
from geometric import SearchNode
from geometric import change_var_to_x
from geometric import str_logical_rule
from geometric import kruskal
from geometric import query_representation

def main():
    args = parse_argument()

    # file pointer
    inp_file = open(args.input,'r')
    sent_file = open(args.sent,'r')
    fol_file = open(args.fol,'r')
    align_file = open(args.align,'r')
    out_file = open(args.out,'w')

    # input - sentence - fol - align
    for (inp_line,sent_line, fol_line, align_line) in zip(inp_file,sent_file,fol_file,align_file):
        inp_line = inp_line.strip()
        query = extract(inp_line)[0][0]
        (sentence_node, query_node) = query.childs # get the tree representation by extracting the geoquery

        (sent, fol, align_line) = map(lambda x: x.strip().split(), (sent_line, fol_line, align_line)) 

        # creating mapping from F -> [w1,w2,...] where w1 w2 are words aligned to F(OL)
        s2l = defaultdict(lambda:set())
        for align in align_line:
            (sent_a, fol_a) = map(int, align.split('-'))
            if fol[fol_a] not in s2l:
                s2l[fol[fol_a]] = set()
            s2l[fol[fol_a]].add(sent_a)

        # adding v, e
        var_map = defaultdict(lambda:len(var_map)+1)
        query_node = construct_query_node(query_node)
        query_node = change_var_to_x(query_node,var_map) # alter A->x1, B->x2, and so on
        #query_node = calculate_v(query_node)             # v is set of logical variables x1,x2.. appearing in that node
        #query_node = calculate_e(query_node, s2l)        # e is set of which words this node alligned to
        #query_node = make_isomorphic(query_node,sent)    # make it ismorphic

        ##### Debug
        # print_node (query,stream=sys.stdout)
        # print '----------------------------------------'
        # print_node (query_node,stream=sys.stdout)
        # print query_representation(query,{value:key for (key,value) in var_map.items()})
        # print '========================================'

        # store the output
        print >> out_file, query_representation(query,{value:key for (key,value) in var_map.items()})

    # close all file
    map(lambda x:x.close(), [inp_file, sent_file, fol_file, align_file, out_file])

def construct_query_node(query_node,parent=None):
    query_node = SearchNode(query_node)
    query_node.height = 0 if parent == None else parent.height + 1
    for i, child in enumerate(query_node.childs):
        query_node.childs[i] = construct_query_node(child,query_node)
    return query_node


def calculate_v(node):
    if type(node.label) == int:
        if node.label not in node.v: node.v.append(node.label)
        if node.label not in node.vorigin: node.vorigin.append(node.label)
    for child in node.childs:
        if type(child.label) == int:
            if child.label not in node.vorigin: node.vorigin.append(child.label)
    for (i,child) in enumerate(node.childs):
        node.childs[i] = calculate_v(child)
        for var in node.childs[i].v:
            if var not in node.v: node.v.append(var)
    return node

def calculate_e(node, logic_map):
    if type(node.label) != int:
        node.e = set([i for i in logic_map[str_logical_rule(node.label,node.height)]])
        node.eorigin = set([i for i in logic_map[str_logical_rule(node.label,node.height)]])

    for (i,child) in enumerate(node.childs):
        node.childs[i] = calculate_e(child, logic_map)
        for word in node.childs[i].e:
            node.e.add(word)

    return node

# Implementation of Algorithm in (Wong and Mooney, 2007) section 4: Promoting Isomorphism
def make_isomorphic(node,sent):
    for (i,child) in enumerate(node.childs):
        # if there is a conjunction in this node' argument, then make it ismorph
        if child.label == "" and child.type == "(" or child.label == '\\+':
            #print "ISOMORPHIC ALGO: BEFORE"
            #print_node(node)
            node.childs = isomorph(node,i,sent)
            #print "ISOMORPHIC ALGO: AFTER"
            #print_node(node)
    for child in node.childs:
        make_isomorphic(child,sent)
    return node

def isomorph(node,ii,sent):
    child = node.childs[ii]
    INF = 100000

    ##### STEP 1 Create graph with nodes v1,v2,v3... and vi is adjacent to vj iff i < j and they share some variables in common
    vert = []
    edge = []
    vert.append((0,sorted(list(node.vorigin)),sorted(list(node.eorigin))))
    #print 0, node.label, node.vorigin, node.v, [sent[i] for i in node.eorigin], [sent[i] for i in node.e]
    for i, ch in enumerate(child.childs):
        #print i+1, ch.label, ch.v, [sent[k] for k in ch.e]
        vert.append((i+1,sorted(list(ch.v)),sorted(list(ch.e))))
    for i in range(len(vert)):
        for j in range (i+1, len(vert)):
            if any(x in vert[i][1] for x in vert[j][1]):
                edge.append((i,j));

    ##### STEP 2 remove edge that shares some alligned word with meta predicate 
    ##### vert[0][2] is the meta predicate!
    for i in range(len(edge)-1,0,-1):
        if any(x in vert[edge[i][0]][2] or x in vert[edge[i][1]][2] for x in vert[0][2]):
            del edge[i]

    ##### STEP 3 connect all nodes with root node (meta predicate)
    for i in range(1,len(vert)):
        if (0,i) not in edge:
            edge.append((0,i))

    ##### STEP 4 count the edge based on word distance
    for (index, (i,j)) in enumerate(edge):
        left = vert[i][2] # get the word list from vert[i]
        right = vert[j][2] # get the word list from vert[j]

        if len(left) == 0 or len(right) == 0: # some of them are unaligned
            edge[index] = (i,j,INF if i != 0 else INF -1)       # then we create edge with maximum weight
        elif (left[-1] <= right[-1] and left[0] >= right [0]) or (right[-1] <= left[-1] and right[0] >= left[0]):
            edge[index] = (i,j,0)       # (left in right) or (right in left)
        else: 
            edge[index] = (i,j, min(abs(left[0]-right[-1]),abs(left[-1]-right[0]))) # word distance

    #for e in edge:
    #   print e
    ##### STEP 5
    mst = kruskal([i for (i, item) in enumerate(vert)], edge)   

    #for x,y in mst.items():
    #   print x,y

    ##### STEP 6 traverse the tree, starting from the meta predicate
    order = traverse_mst(mst,len(vert),[],0,set())
    order.pop(0) # dont include the meta predicate, we are dealing with its child

    ##### Error check if there is some unreached nodes from spanning tree
    if len(order) != len(vert)-1:
        print >> sys.stderr, "There are some unrelated variables: "
        print_node(child)
        sys.exit(1)

    node.childs[ii].childs = [node.childs[ii].childs[i-1] for i in order] # the child in i-th position must be replaced

    return node.childs

def traverse_mst(mst, max_vert, order, now , visited):
    if len(visited) != max_vert:
        order.append(now)
        visited.add(now)
        for n in mst[now]:
            if n not in visited:
                traverse_mst(mst, max_vert, order, n, visited)
        return order


def parse_argument():
    parser = argparse.ArgumentParser(description="Run Make Isomorphic")
    parser.add_argument('--input', type=str,required=True,help="The geoquery file")
    parser.add_argument('--sent',type=str,required=True,help="The sentence file")
    parser.add_argument('--fol',type=str,required=True,help="The sentence file in fol")
    parser.add_argument('--align',type=str,required=True,help="The alignment between sent to fol")
    parser.add_argument('--out',type=str,required=True,help="Directory where data-structure will be outputed")
    return parser.parse_args()

if __name__ == "__main__":
    main()
