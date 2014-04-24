import sys
import disjointset as ds
from collections import defaultdict

correspond = {'':'.', '(':')', '[':']', '{':'}'}
corr_val = set(correspond.values())
key_val = set(correspond.keys())
QUERY = "QUERY"
FORM = "FORM"

class Node:
    def __init__(self, label):
        self.label = label
        self.childs = []
        self.type = ""

class SearchNode:
    def __init__(self, node):
        self.label = node.label
        self.childs = node.childs
        self.type = node.type
        self.v = []
        self.vorigin = []
        self.e = set()
        self.eorigin = set()
        self.vmerged = []

def extract(line,position=0,parent=""):
    childs = []
    offset = position
    while line[position] != correspond[parent]:
        nchar = line[position]
        if nchar != '.' and nchar in corr_val:
            print >> sys.stderr, "Unbalance parentheses"
            sys.exit(1)
        if nchar in key_val:
            child_content = Node(line[offset:position].strip())
            child_content.type = nchar
            (child_content.childs, position) = extract(line, position+1, nchar)
            childs.append(child_content)
            if line[position + 1] == ',': position += 1
            offset = position+1
        elif nchar == ',':
            child_content = Node(line[offset:position].strip())
            childs.append(child_content)
            offset = position+1
        position += 1
    if offset < position:
        child_content = Node(line[offset:position].strip())
        childs.append(child_content)
    return (childs,position)

def is_variable(label):
    return type(label) != int and len(label) == 1 and label != '_'

def change_var_to_x(node,var_map):
    if is_variable(node.label):
        node.label = var_map[node.label]
    for (i,child) in enumerate(node.childs):
        node.childs[i] = change_var_to_x(child,var_map)
    return node

def print_node(n,indent=0,stream=sys.stderr):
    n_child = len(n.childs)
    for i in range (n_child/2):
        print_node(n.childs[i],indent+10,stream)
    content = (" " * indent) + "[" + str(n.label) + "]"
    print >> stream, content
    for i in range (n_child/2,n_child):
        print_node(n.childs[i],indent+10,stream)

def query_representation(node,map,input_generator=False,root=True):
    ret = map[node.label] if type(node.label) == int else node.label
    if node.label == '\+': ret += ' '
    ret += node.type
    for i, child in enumerate(node.childs):
        if i != 0:
            ret += ","
        ret += query_representation(child,map,input_generator,root=False)
    if len(node.childs) != 0: ret += correspond[node.type]
    if root: ret+= '.'
    return ret

# rule = (Type, Label, child)
def transform_into_rule(rules,node,start=False,recurse=True):
    if node.label != "":
        rule = (QUERY if start else FORM, node.label, [])
        for child in node.childs:
            if len(child.childs) == 0:
                rule[2].append(child.label)
            elif child.label == "":
                s = []
                for grandchild in child.childs:
                    s.append(grandchild.label if len(grandchild.childs) == 0 else FORM)
                rule[2].append(s)
            else:
                rule[2].append(FORM)
        rules.append(rule)

    if recurse:
        for child in node.childs:
            if len (child.childs) != 0:
                transform_into_rule(rules,child)
    return rules

def str_logical_rule(rule):
    return rule[0] + "->" + str(rule[1]) + "(" + ",".join(map(lambda x: ("x" \
            + str(x) if type(x) == int else x.replace(' ','_') if type(x) == str else ("(" + ",".join(x)+ ")")),rule[2])) + ")"

# Return the MST according to kruskal algorithm
def kruskal(vertices,edges):
    mst = defaultdict(lambda:([]))
    v = []
    for i in vertices:
        v.append(ds.make_set(i))
    for (i,j,weight) in sorted(edges,key=lambda x:x[2]):
        if ds.find(v[i]) != ds.find(v[j]):
            mst[i].append(j)
            mst[j].append(i)
            ds.union(v[i],v[j])
    return mst
