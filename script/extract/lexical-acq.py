#!/usr/bin/env python

import sys
import argparse
import copy
from collections import defaultdict
from geometric import transform_into_rule
from geometric import extract
from geometric import print_node
from geometric import Node
from geometric import SearchNode
from geometric import change_var_to_x
from geometric import str_logical_rule
from geometric import query_representation

# flag
QUERY = "QUERY"
CONJUNCTION = "CONJ"
NEGATION = "NOT"
FORM = "FORM"
COUNT = "COUNT"
LEAF = "PRED"
ENTITY = "ENTITY"
ABREVIATION = "ABR"

TYPE_LABEL = set([CONJUNCTION,NEGATION,LEAF])

PRECEDENCE = defaultdict(lambda:0)
PRECEDENCE[QUERY] = 100
PRECEDENCE[COUNT] = 70
PRECEDENCE[FORM] = 50
PRECEDENCE[CONJUNCTION] = 30
PRECEDENCE[NEGATION] = 40
PRECEDENCE[LEAF] = 10
PRECEDENCE[ENTITY] = 5
PRECEDENCE[ABREVIATION] = 10

def main():
    args = parse_argument()

    #### file pointer
    inp_file = open(args.input,'r')
    sent_file = open(args.sent,'r')
    fol_file = open(args.fol,'r')
    align_file = open(args.align,'r')

    #### counter
    count = 0

    #### map for validation
    cycle_map = defaultdict(lambda:set())
    
    #fp = open("geoquery.fparse","w")
    #### For input-sentence-fol-alignment
    for (index,(inp_line,sent_line, fol_line, align_line)) in enumerate(zip(inp_file,sent_file,fol_file,align_file)):
        inp_line = inp_line.strip()
        query = extract(inp_line)[0][0]
        (sentence_node, query_node) = query.childs # get the tree representation by extracting the geoquery

        #### strip, split!
        (sent, fol, align_line) = map(lambda x: x.strip().split(), (sent_line, fol_line, align_line)) 

        #### creating mapping from F -> [w1,w2,...] where w1 w2 are words aligned to F(OL)
        s2l = defaultdict(lambda:set())
        for align in align_line:
            (sent_a, fol_a) = map(int, align.split('-'))
            if fol[fol_a] not in s2l:
                s2l[fol[fol_a]] = set()
            s2l[fol[fol_a]].add(sent_a)

        #### Doing some node annotation, and bound node to which word and variable it is aligned to.
        var_map = defaultdict(lambda:len(var_map)+1)
                
        #### Query Node + preprocessing
        id = []
        query_node = construct_query_node(query_node,id)
        query_node = relax_not_node(query_node,id)
        # alter A->x1, B->x2, and so on
        query_node = change_var_to_x(query_node,var_map)
        # change '' to CONJUNCTION and \+ to NEGATION
        query_node = change_conj(query_node)
        
        #### Related to the Word alignment.
        aligned_word = set()
        # give information about which words that are aligned to node
        query_node = calculate_e(query_node,s2l,aligned_word)
        #### Related to the label.
        query_node = change_not(query_node)
        query_node = assign_head(query_node)
        # Mark NT with distinct symbols 
        query_node = mark_nt(query_node)
        
        #### Related to the bound 
        # calculating inside variable
        query_node = calculate_v(query_node) 
        # calculating outside variable
        query_node = calculate_outside_v(query_node)
        # calculating bound variable
        query_node = calculate_bound(query_node)
        # PRUNE all variable node
        query_node = prune_node(query_node)
        
        # aligning unaligned word in the source side, it is aligned to the topmost node
        query_node,_ = align_unaligned_source(query_node,0,len(sent)-1,aligned_word)
        # frontier node   
        query_node = mark_frontier_node(query_node,set())
        
        # change 'w1 w2' entity into w1_w2       
        query_node = transform_multi_words_entity(query_node)
        
        lexical_acq(query_node,sent,[],args.merge_unary)
        
        count += 1
        if (args.verbose):
            print index, "|||",  sent_line.strip()
            print_node(query_node,stream=sys.stdout) 
            print_node_list(query_node)

        #print >> fp, print_traverse_rule(query_node)[1]
        rules = []
        compose_rule(rules, query_node, args.max_size)
        rules = map(lambda x:rename_non_terminal(x,False),rules)
        check_rules(rules,cycle_map)

        for rule in rules:
            r = rule
            if r != None:
                print r
        if (args.verbose):print '----------------------------------------------------------------------------'
    #### Closing all files
    map(lambda x: x.close(), [inp_file, sent_file, fol_file, align_file])

    #### Printing stats
    print >> sys.stderr, "Finish extracting rule from %d pairs." % (count) 

def check_rules(rules,mp):
    # checking for loop 
    for rule in rules:
        src,trg = rule.split(" ||| ")
        src = src.split()
        # if it is unary
        if len(src) == 3 and src[0][0] != '"' and src[0][-1] != '"':
            child_symbol = src[0].split(":")[1]
            parent_symbol = src[2]
            if parent_symbol in mp[child_symbol]:
                raise Exception("Error with cycle: "+ parent_symbol+ " -> " + child_symbol + "->" + parent_symbol)
            mp[parent_symbol].add(child_symbol)
        # check for parentheses
        check_parentheses([" ".join(src)] + [trg])

def check_parentheses(inps):
    for inp in inps:
        g = 0
        for c in inp:
            if c == '(': g+=1
            elif c == ')': g-= 1
        if g != 0:
            raise Exception("Parentheses error: " + inp)

# This is for debug only
def print_traverse_rule(node):
    m = {}
    result = ""
    for i, child in node.frontier_child.items():
        index, res = print_traverse_rule(child)
        m[index] = map(lambda x: " ".join(x.split()[:-2]), res.split(" ||| "))
    logic = False
    for token in node.result.split(" "):
        if token == '@':
            logic = True
        if ':' in token:
            x, _ = token.split(":")
            x = int(x[1])
            result += m[node.frontier_child[x].id][1 if logic else 0]
        else:
            result += token
        result += " "
    return node.id, result

def compose_rule(rules,node, max_size):
    ret = [(node.result,1)]
    for nt, child in node.frontier_child.items():
        ret_child = compose_rule(rules,child,max_size)
        composed = []
        for r_parent,p_size in ret:
            for r,c_size in ret_child:
                if c_size+p_size <= max_size:
                    composed.append((compose_rule_string(nt, r_parent, r),c_size+p_size))
        for c,size in composed:
            ret.append((c,size))
    for r,size in ret:
        rules.append(r)
    return ret

def compose_rule_string(nt, parent, child):
    parent_col = parent.split(' ||| ')
    child_col = child.split(' ||| ')
    ret = []
    for (p_col, c_col) in zip(parent_col,child_col):
        p_col_token = p_col.split()
        c_col_token = c_col.split()
        for i, p_token in enumerate(p_col_token):
            if p_token == '@': break 
            if p_token[0] != '"' and p_token[-1] != '"' and p_token[0] == 'x' and p_token[1] == str(nt):
                p_col_token[i] = replace_x_with_y(' '.join(c_col_token[:-2]),nt)
                break
        ret.append(' '.join(p_col_token))
    return ' ||| '.join(map(lambda x: rename_non_terminal(x),ret))

def replace_x_with_y(ss,index):
    # to avoid conflict in merging, rename x in child first into y, resolve later into new x
    ss = ss.split()
    for i, s in enumerate(ss):
        if s == '@': break
        if s[0] != '"' and s[-1] != '"':
            ss[i] = str(index)+ ss[i][1:]
    return ' '.join(ss)

def rename_non_terminal(c,xFixed = True):
    nt_map = {}
    fixed = set()
    parts = c.split(" ||| ")
    ret = []
    ctr = 0

    # Mark all remaining X, don't change it.
    if xFixed:
        for token in parts[0].split():
            if token[0] == 'x':
                nt_map[token[:2]] = token[:2]
                fixed.add(int(token[1]))
    
    for part in parts:
        tokens = part.split()
        for i, token in enumerate(tokens):
            if token == '@': break
            if token[0] != '"' and token[-1] != '"':
                t = token[:2]
                if t not in nt_map:
                    while ctr in fixed:
                        ctr += 1
                    nt_new = 'x' + str(ctr)
                    nt_map[t] = nt_new
                    ctr += 1
                tokens[i] = nt_map[t] + token[2:]
        ret.append(' '.join(tokens))
    return ' ||| '.join(ret)

def mark_nt(node,parent=None):
    for child in node.childs:
        mark_nt(child,node)
    if len(node.childs) == 0:
        if parent is not None and parent.label.endswith("id"):
            if len(node.label) < 3:
                node.head = ABREVIATION
            else:
                node.head = parent.label[:-2].upper()
        else:
            node.head = LEAF
    return node


def align_unaligned_source(node, start, end, aligned_word):
    child_spans = set(node.eorigin)
    for child in node.childs:
        span = child.e
        if len(span) != 0:
            for w in range(span[0], span[-1]+1):
                child_spans.add(w)
    unaligned = [x for x in range(start,end+1) if x not in child_spans and x not in aligned_word]
    for w in unaligned:
        node.eorigin.append(w)
    for child in node.childs:
        if len(child.e) != 0:
            span = list(child.e)
            _, unaligned_child = align_unaligned_source(child, span[0], span[-1],aligned_word)
            for e in unaligned_child:
                unaligned.append(e)
    for w in unaligned:
        node.e.append(w)
    node.eorigin = sorted(node.eorigin)
    node.e = sorted(node.e)
    return (node, unaligned)

def lexical_acq(node,sent,rules,merge_unary=False):
    for child in node.childs:
        lexical_acq(child,sent,rules,merge_unary)
    if node.frontier:
        node.frontier_child = {}
        sentence, (logic,_) = extract_node(node,node,sent,{},merge_unary,{},[False] * len(sent))
        logic = merge_logic_output(logic)
        res = sentence + " @ " +  node.head+append_var_info(node.bound) + " ||| " +  logic +  " @ " + node.head+append_var_info(node.bound)
        node.result = res
        rules.append(res)
    return rules

def extract_node(root,node,sent,var_map,merge_unary,bound_map,extracted,start=True):
    # extracting sent side
    span = []
    sent_list = []
    logic_list = []
   
    for word in node.eorigin:
        if not extracted[word]:
            extracted[word] = True
            span.append((word,word,sent[word]))

    # map bound of this node
    node.bound_remap = bound_remapping(node.bound, bound_map)
    #node.bound_remap = node.bound

    for child in node.childs:
        # There is a word aligned to this subtree
        aligned = child.e
        if len(aligned) > 0:
            span.append((aligned[0],aligned[-1],child))
        else:
            span.append((-1,-1,child))

    sorted(span,key=lambda x:x[0]) # sort the key including the first prefix to come.
    for s in span:
        if type(s[2]) == str:
            sent_list.append((s[0],s[1],'"'+s[2]+'"'))
        elif s[2].frontier and not (merge_unary and is_unary(node,s[2])):
            number = len(var_map)
            nt = non_terminal(number,s[2].head,bound_remapping(s[2].bound,bound_map))
            #nt = non_terminal(number,s[2].head,s[2].bound)
            sent_list.append((s[0],s[1],nt))
            logic_list.append((nt,bound_remapping(s[2].bound, bound_map)))
            #logic_list.append((nt,s[2].bound))
            var_map[s[2].id] = number
            root.frontier_child[number] = s[2]
        else: # depth recursion to this node, extraction continued rooted at this node
            s[2].not_frontier()
            sent_child, logic_child = extract_node(root,s[2],sent,var_map,merge_unary,bound_map,extracted,start=False)
            for s in sent_child: sent_list.append(s)
            logic_list.append(logic_child)
   
    # orig info insertion
    for vor in node.vorigin:
        logic_list.insert(node.voriginfo[vor],bound_mapping(vor,bound_map))
        #logic_list.insert(node.voriginfo[vor],vor)

    # Logic string
    logic = '%s "%s' % (bound_to_lambda(node.bound_remap),select_label(node.label))
    if len(logic_list) != 0:
        logic += '(" '
        for i, item in enumerate(logic_list):
            if type(item) == int:
                logic += '"x' + str(item) + (',' if i < len(logic_list)-1 else "") + '"'
            else:
                log, log_bound = item
                logic += '%s %s %s' % (log, bound_to_string(log_bound), ("\",\"" if i < len(logic_list)-1 else ""))
            logic += " " if len(logic) > 0 and logic[-1] != " " else ""
        logic += '")'
    logic += '"'
    return (sent_list if not start else (' '.join([x[2] for x in sorted(sent_list,key=lambda x:x[0])])),\
            (logic,bound_remapping(node.bound,bound_map)))

def bound_remapping(bound, bound_map):
    ret = []
    for x in bound:
        ret.append(bound_mapping(x,bound_map))
    return ret

def bound_mapping(v, bound_map):
    if v not in bound_map:
        bound_map[v] = len(bound_map) + 1
    return bound_map[v]

def merge_logic_output(logic):
    words = logic.split()
    i = 0
    while i < len(words)-1:
        g1 = words.pop(i)
        if g1[0] == '"':
            g2 = words.pop(i)
            if g2[0] != '"':
                # do extraction
                words.insert(i,g2)
                words.insert(i,g1)
                i+=1
            else:
                merge = g1[:-1] + g2[1:]
                words.insert(i,merge)
        else:
            words.insert(i,g1)
            i+= 1
    return ' '.join(words)

def is_unary(parent, node):
    merge = parent.e[0] == node.e[0] and parent.e[-1] == node.e[-1]
    return parent.head == node.head and len(parent.childs) == 1 and merge 

def bound_to_lambda(bound):
    return ("\"" + "".join(["\\x" + str(x) for x in reversed(bound)])+".\"" if len(bound) > 0 else "")

def bound_to_string(bound):
    return ("\"(" + ",".join(["x" + str(x) for x in bound]) + ")\"") if len(bound) > 0 else ""

def mark_frontier_node(node, complement_span):
    node.complement = complement_span
    for i, child in enumerate(node.childs):
        # calculate the complement span for this child 
        # first this child inherit the parent complement span
        complement_s = set([x for x in complement_span])
        # include the word in this node
        for w in node.eorigin:
            complement_s.add(w)
        # Then include every span of the sibling 
        for j, sibling in enumerate(node.childs):
            if i != j: # means the sibling is not the node itself 
                for v in sibling.e:
                    complement_s.add(v)
        # recursively mark frontier node for the child
        mark_frontier_node(child, sorted(complement_s))
    # Thus we consistently add the definition of the frontier node
    # is a node where every of its complement span is not in the span.
    span = node.e
    node.frontier = (not len(span) == 0) and (not any(e >= span[0] and e <= span[-1] for e in node.complement))
    # Additional rule for precedence
    node.frontier = node.frontier and unary_precedence_constraint(node)
    return node

def unary_precedence_constraint(node):
    ret = True
    # For all child
    frontiers = []
    for child in node.childs:
        if child.frontier:
            frontiers.append(child)
    if len(frontiers) == 1 and PRECEDENCE[node.head] <= PRECEDENCE[frontiers[0].head]:
        if node.e[0] == frontiers[0].e[0] and node.e[-1] == frontiers[0].e[-1]:
            ret = False
    return ret

def sent_map(span,sent):
    ret = []
    if len(span) > 0:
        s_begin = span[0]
        if len(span) > 1:
            while s_begin <= span[-1]:
                if s_begin in span:
                    ret.append(sent[s_begin])
                    s_begin += 1
                else:
                    k = 0
                    while s_begin not in span and s_begin <= span[-1]:
                        s_begin += 1
                        k += 1
                    ret.append(k)
        else:
            ret.append(sent[s_begin])
    return ret

def construct_query_node(query_node,id,parent=None):
    query_node = SearchNode(query_node)
    query_node.id = len(id)
    id.append(query_node)
    for i, child in enumerate(query_node.childs):
        query_node.childs[i] = construct_query_node(child,id,query_node)
        query_node.childsize += 1
    return query_node

def relax_not_node(query_node,id):
    for i,child_node in enumerate(query_node.childs):
        relax_not_node(child_node,id)
    if query_node.label == '\+':
        child = SearchNode(Node(CONJUNCTION))
        child.childs = query_node.childs
        child.id = len(id)
        query_node.childs = [child]
        id.append(child)
    return query_node

# Calculating Inside Variable Set
def calculate_v(node):
    if type(node.label) == int:
        if node.label not in node.vorigin: node.vorigin.append(node.label)
        if node.label not in node.v : node.v.append(node.label)
    for i, child in enumerate(node.childs):
        if type(child.label) == int:
            if child.label not in node.vorigin: node.vorigin.append(child.label)
            node.voriginfo[child.label] = i
    for (i,child) in enumerate(node.childs):
        node.childs[i] = calculate_v(child)
        for var in node.childs[i].v:
            if var not in node.v: node.v.append(var)
    return node

# Calculating Outside Variable Set
def calculate_outside_v(node,parent_v=set()):
    node.voutside = parent_v
    for i, child in enumerate(node.childs):
        vsibling = set()
        for j, child_i in enumerate(node.childs):
            if i != j:
                for v in child_i.v:
                    vsibling.add(v)
        child_outside = list(set([v for v in parent_v] + [v for v in node.vorigin] + [v for v in vsibling]))
        node.childs[i] = calculate_outside_v(child,child_outside)
    return node

# Calculating Bound of Node (intersection of inside and outside variable)
def calculate_bound(node):
    node.bound = [x for x in node.v if x in node.voutside]
    for index, child in enumerate(node.childs):
        node.childs[index] = calculate_bound(child)
    return node

def prune_node(node):
    i = len(node.childs) - 1
    while i >= 0: 
        if type(node.childs[i].label) == int:
            del node.childs[i]
        else:
            node.childs[i] = prune_node(node.childs[i])
        i -= 1
    return node

def print_node_list(node):
    for child in node.childs:
        print_node_list(child)
    print node 

def assign_head(node):
    for child in node.childs:
        assign_head(child)
    node.head = select_head(node.label)
    return node

def calculate_e(node, logic_map,aligned_word,start=True):
    if type(node.label) != int:
        words = [i for i in logic_map[str_logical_rule(node.label,node.id)]]
        node.e = []
        node.eorigin = []
        for w in words:
            node.e.append(w)
            node.eorigin.append(w)
            aligned_word.add(w)
    for (i,child) in enumerate(node.childs):
        node.childs[i] = calculate_e(child, logic_map,aligned_word,False)
        for word in node.childs[i].e:
            node.e.append(word)
    node.e = sorted(node.e)
    node.eorigin = sorted(node.eorigin)
    return node

def change_conj(node):
    if node.label == '': 
        node.label = CONJUNCTION
    for (i, child) in enumerate(node.childs):
        node.childs[i] = change_conj(child)
    return node

def change_not(node):
    if node.label == '\+':
        node.label = NEGATION
    for (i,child) in enumerate(node.childs):
        node.childs[i] = change_not(child)
    return node

def transform_multi_words_entity(node):
    if type(node.label) == str and len(node.label) > 0 and node.label[0] == "'" and node.label[-1] == "'":
        node.label = "#$#".join(node.label.split())
    for (i,child) in enumerate(node.childs):
        node.childs[i] = transform_multi_words_entity(child)
    return node

def select_label(label):
    if label == NEGATION:
        label = "-"
    elif label == CONJUNCTION:
        label = ""
    return label

def select_head(name):
    ret = str()
    if name in TYPE_LABEL: ret = name
    else: ret = FORM
    if name == 'answer': ret = QUERY
    return ret

def non_terminal(number, head, bound):
    return str("x") + str(number) + ":" + head + append_var_info(bound)

def append_var_info(bound):
    return "["+str(len(bound))+"]" if len(bound) != 0 else ""

def parse_argument():
    parser = argparse.ArgumentParser(description="Run Lexical Acquisition")
    parser.add_argument('--input', type=str,required=True,help="The geoquery file")
    parser.add_argument('--sent',type=str,required=True,help="The sentence file")
    parser.add_argument('--fol',type=str,required=True,help="The sentence file in fol")
    parser.add_argument('--align',type=str,required=True,help="The alignment between sent to fol")
    parser.add_argument('--verbose',action="store_true",help="Show some other outputs to help human reading.")
    parser.add_argument('--merge_unary',action="store_true",help="Merge the unary transition node. Avoiding Rule like FORM->FORM")
    parser.add_argument('--max_size', type=int, default=4,help="Compose max size")
    return parser.parse_args()

if __name__ == "__main__":
    main()
