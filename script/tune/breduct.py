#!/usr/bin/env python

import sys
import argparse
from collections import defaultdict

### Validation
def check_output(output):
    depth = 0
    for c in output:
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
    return depth == 0

### Change to Alphabet (only support A-Z)
G = { x:y for (x,y) in zip([n for n in range(1,27)],"ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
def change_x_to_var(l):
    line = l
    K = defaultdict(lambda: G[len(K)+1])
    number_set = set(['0','1','2','3','4','5','6','7','8','9'])
    ret = str(line)
    now = 0
    while True:
        occ = line.find('x',now)
        if occ == -1 or occ == len(line)-1:
            break
        if line[occ+1] in number_set:
            var = line[occ:occ+2]
            ret = ret.replace(var,K[var])
        elif line[occ+1] == '_':
            var = line[occ:occ+5]
            ret = ret.replace(var,K[var])
        now = occ+1
    return ret

### PARSE
correspond = {'':'.', '(':')', '[':']', '{':'}'}
corr_val = set(correspond.values())
key_val = set(correspond.keys())

class Node:
    def __init__(self, label,id):
        self.label = label
        self.childs = []
        self.type = ""
        self.bound = []
        self.id = id

def print_node(n,indent=0,stream=sys.stderr):
    n_child = len(n.childs)
    for i in range (n_child/2):
        print_node(n.childs[i],indent+20,stream)
    content = (" " * indent) + "[" + str(n.label) + "]"
    if len(n.bound) > 0:
        content += "("+ ','.join([str(x) for x in n.bound]) +")"
    print >> stream, content
    for i in range (n_child/2,n_child):
        print_node(n.childs[i],indent+20,stream)

def extract(line,position=0,parent="",id=0):
    childs = []
    offset = position
    while line[position] != correspond[parent]:
        nchar = line[position]
        if nchar != '.' and nchar in corr_val:
            print >> sys.stderr, "Unbalance parentheses"
            sys.exit(1)
        if nchar in key_val:
            child_content = Node(line[offset:position].strip(),id)
            id += 1
            child_content.type = nchar
            (child_content.childs, position) = extract(line, position+1, nchar,id)
            childs.append(child_content)
            if line[position + 1] == ',': position += 1
            offset = position+1
        elif nchar == ',':
            child_content = Node(line[offset:position].strip(),id)
            id += 1
            childs.append(child_content)
            offset = position+1
        position += 1
    if offset < position:
        child_content = Node(line[offset:position].strip(),id)
        id += 1
        childs.append(child_content)
    return (childs,position)

def append_bound(node):
    childs = []
    i=0
    # For all childs
    while i < len(node.childs):
        childs.append(node.childs[i])
        # If this node starts with lambda
        if node.childs[i].label.startswith("\\"):
            # The next child contains all the bounds, merge it.
            for bound in node.childs[i+1].childs:
                node.childs[i].bound.append(bound.label)
            # Skip the next child
            i+=1
        i+=1
    # Replace the child with the new child
    node.childs = childs
    # Recurse deeply, Top-Down approach!
    for child in node.childs:
        append_bound(child)
    return node

def node_to_line(node):
    ret = node.label
    ret += node.type
    for i, child in enumerate(node.childs):
        if i != 0:
            ret += ","
        ret += node_to_line(child)
    if len(node.childs) != 0: ret += correspond[node.type]
    return ret

### B-REDUCTION
def breduct(node,rename_map):
    ## GET lambda information
    lmbd = []
    if node.label.startswith("\\"):
        l, f = node.label.split(".")
        # Remove lambda, we are reducting it now
        node.label = f
        # l is the lambda string
        for l_ in l.split("\\"):
            if l_ != '':
                lmbd.append(l_)

    ## ERROR CHECK
    if len(lmbd) < len(node.bound):
        cerr << "Error: Reduction can't process arguments more than lambda" << endl
        raise Exception("len(lambda) != len(bound) error")

    ## RENAMING
    # First check whether there is a variable in this node level that is not in lambda
    for child in node.childs:
        # Case is that bound in lambda don't change. If it is free, rename it
        # If parameter is a function
        if len(child.childs) > 0:
            # Check for its argument!
            child.bound = map(lambda x: x if x in lmbd else rename_map[(x,node.id)],child.bound)
        else: # Case of single variable
            if child.label not in lmbd and child.label.startswith('x'):
                child.label = rename_map[(child.label,node.id)]
   
    ## REDUCTION PHASE 
    # First create the mapping, the outermost left lambda with outermost right bound
    reduction_map = {}
    for i in range(len(lmbd)):
        reduction_map[lmbd[i]] = node.bound[-i-1]
   
    # Then proceed with reducting this level
    for child in node.childs:
        if len(child.childs) > 0: # function
            child.bound = map(lambda x: x if x not in reduction_map else reduction_map[x],child.bound)
        else: # single variable
            if child.label in reduction_map:
                child.label = reduction_map[child.label]

    # Recursing to the child
    for child in node.childs:
        breduct(child,rename_map)
    return node 

### MAIN
def main():
    parser = argparse.ArgumentParser(description="Run Beta Reduction")
    parser.add_argument('--alphabet', action="store_true",help="map x_n or xn to alphabet[n]")
    args = parser.parse_args()

    for line in sys.stdin:
        line = line.strip() + '.'
        try :
            node = append_bound(extract(line)[0][0])
            rename_map = defaultdict(lambda:"x_" + str(100+len(rename_map)))
            output = node_to_line(breduct(node,rename_map))
            if not check_output(output):
                print >> sys.stderr, "This output does not have correct parentheses:", output, "input:", line

            print (output if not args.alphabet else change_x_to_var(output))
        except:
            print "Failed to parse:",line

if __name__ == '__main__':
    main()
