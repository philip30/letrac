#!/usr/bin/env python

import sys
import argparse
import copy
from collections import defaultdict
from geometric import transform_into_rule
from geometric import extract
from geometric import print_node
from geometric import SearchNode
from geometric import change_var_to_x
from geometric import str_logical_rule
from geometric import kruskal
from geometric import query_representation
from stop_word_list import stop_word_list as stop_word
from find_error import check_valid_sync_symbol

exclusion = set(['us'])
stop = [x for x in stop_word if x not in exclusion]

# flag
QUERY = "QUERY"
CONJUNCTION = "CONJ"
NEGATION = "NOT"
FORM = "FORM"
COUNT = "COUNT"
LEAF = "PRED"
ENTITY = "ENTITY"

TYPE_LABEL = set([CONJUNCTION,NEGATION,LEAF])

PRECEDENCE = defaultdict(lambda:0)
PRECEDENCE[QUERY] = 100
PRECEDENCE[COUNT] = 70
PRECEDENCE[FORM] = 50
PRECEDENCE[CONJUNCTION] = 30
PRECEDENCE[NEGATION] = 40
PRECEDENCE[LEAF] = 10
PRECEDENCE[ENTITY] = 5

def main():
    args = parse_argument()

    #### file pointer
    inp_file = open(args.input,'r')
    sent_file = open(args.sent,'r')
    fol_file = open(args.fol,'r')
    align_file = open(args.align,'r')
    rule_out_file = open(args.out_num_rule,'w')

    #### counter
    count = 0

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
        aligned_word = set()
        query_node = construct_query_node(query_node,[])
        query_node = change_var_to_x(query_node,var_map) # alter A->x1, B->x2, and so on
        query_node = calculate_v(query_node)             # give information about variables that bound to node
        query_node = calculate_e(query_node,s2l,aligned_word)         # give information about which words that are aligned to node
        query_node,_ = align_unaligned_source(query_node,0,len(sent)-1,aligned_word)
        query_node = change_not_and_conj(query_node)     # change '' to CONJUNCTION and \+ to NEGATION
        query_node = transform_multi_words_entity(query_node) # change 'w1 w2' entity into w1_w2
        query_node = prune_node(query_node)
        query_node = calculate_bound(query_node)
        query_node = assign_head(query_node)
        #query_node = mark_leaf(query_node)
        query_node = mark_frontier_node(query_node,set())

        rules = lexical_acq(query_node,sent,[],args.merge_unary)
        
        if args.three_sync:
            query_node = calculate_e_key(query_node,sent)
            query_node = three_sync_frontier_marker(query_node,sent)
            rules = lexical_acq(query_node,sent,[],args.merge_unary) 
        
        count += 1
        if (args.verbose):
            print index, "|||",  sent_line.strip()
            print_node(query_node,stream=sys.stdout) 
            print_node_list(query_node)
        
        for rule in rules:
            print extract_three_sync(rule) if args.three_sync else rule
        if (args.verbose):print '----------------------------------------------------------------------------'
    #### Closing all files
    map(lambda x: x.close(), [inp_file, sent_file, fol_file, align_file,rule_out_file])

    #### Printing stats
    print >> sys.stderr, "Finish extracting rule from %d pairs." % (count) 

def calculate_e_key(node, sent):
    for child in node.childs:
        calculate_e_key(child,sent)
    for e in node.e:
        if sent[e] not in stop:
            node.ekeyword.append(e)
    return node

def mark_leaf(node):
    for child in node.childs:
        mark_leaf(child)
    if len(node.childs) == 0:
        if len(node.bound) == 0:
            node.head = ENTITY
        else:
            node.head = LEAF
    return node

def three_sync_frontier_marker(node,sent):
    for child in node.childs:
        three_sync_frontier_marker(child,sent)
    if node.frontier:
        words_head = node.result.split(" ||| ")[0].split()
        words = words_head[:-2]
        count = 0
        for w in words:
            if w[0] == '"' and w[-1] == '"':
                w = w[1:-1]
                if w in stop:
                    count += 1
        unary = count == len(words)-1 and len(node.childs) == 1 and node.label == node.childs[0].label and len(node.bound) == len(node.childs[0].bound)
        if count == len(words) or unary:
            node.frontier = False # Merge this node
        node.frontier = node.frontier and unary_precedence_constraint(node)
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
    if node.frontier:
        sentence, (logic,_) = extract_node(node,sent,{},merge_unary)
        logic = merge_logic_output(logic)
        res = sentence + " @ " +  node.head+append_var_info(node.bound) + " ||| " +  logic +  " @ " + node.head+append_var_info(node.bound)
        node.result = res
        rules.append(res)
    for child in node.childs:
        lexical_acq(child,sent,rules,merge_unary)
    return rules

def extract_node(node,sent,var_map,merge_unary,start=True):
    # extracting sent side
    span = []
    sent_list = []
    logic_list = []
    for word in node.eorigin:
        span.append((word,word,sent[word]))
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
            nt = non_terminal(number,s[2].head,s[2].bound)
            sent_list.append((s[0],s[1],nt))
            logic_list.append((nt,s[2].bound))
            var_map[s[2].id] = number
        else: # depth recursion to this node, extraction continued rooted at this node
            s[2].frontier = False
            sent_child, logic_child = extract_node(s[2],sent,var_map,merge_unary,start=False)
            for s in sent_child: sent_list.append(s)
            logic_list.append(logic_child)
   
    # orig info insertion
    for vor in node.vorigin:
        logic_list.insert(node.voriginfo[vor],vor)

    # Logic string
    logic = '%s "%s' % (bound_to_lambda(node.bound),select_label(node.label))
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
            (logic,node.bound))

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
    return parent.head == node.head and len(parent.childs) == 1

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

def unary_precedence_constraint(node,three_sync=False):
    ret = True
    # For all child
    frontiers = []
    for child in node.childs:
        if child.frontier:
            frontiers.append(child)
    if len(frontiers) == 1 and PRECEDENCE[node.head] <= PRECEDENCE[frontiers[0].head]:
        if not three_sync:
            ret = False
        else:
            spanb1,spanb2 = (node.ekeyword[0], node.ekeyword[-1])
            spanc1,spanc2 = (frontiers[0].ekeyword[0], frontiers[0].ekeyword[-1])
            ret = not ((spanb1 == spanc1) and (spanc1 == spanc2))
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
    query_node.height = 0 if parent == None else parent.height + 1
    query_node.id = len(id)
    id.append(query_node)
    for i, child in enumerate(query_node.childs):
        query_node.childs[i] = construct_query_node(child,id,query_node)
        query_node.childsize += 1
    return query_node

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

def prune_node(node):
    i = len(node.childs) - 1
    while i >= 0: 
        if type(node.childs[i].label) == int:
            del node.childs[i]
        else:
            node.childs[i] = prune_node(node.childs[i])
        i -= 1
    return node

def calculate_bound(node,parent_bound=set([])):
    node.bound = [x for x in node.v if x in parent_bound] if len(node.childs) > 0 else node.vorigin
    for index, child in enumerate(node.childs):
        sibling_bound = filter(lambda x: x not in child.v, node.v)
        child_set = set()
        for child_index, y in enumerate(node.childs):
            if child_index != index:
                for z in y.v:
                    child_set.add(z)
        for v in node.vorigin:
            child_set.add(v)
        calculate_bound(child,child_set)
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

def change_not_and_conj(node):
    if node.label == '': 
        node.label = CONJUNCTION
    elif node.label == '\+':
        node.label = NEGATION
    for (i, child) in enumerate(node.childs):
        node.childs[i] = change_not_and_conj(child)
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
    parser.add_argument('--out_num_rule',type=str,required=True,help="The output file where number of rules from each line is extracted.")
    parser.add_argument('--verbose',action="store_true",help="Show some other outputs to help human reading.")
    parser.add_argument('--three_sync',action="store_true",help="Extract 3-synchronous grammar.")
    parser.add_argument('--include_fail',action="store_true",help="Include (partially) extracted rules even it is failed to extract until root.")
    parser.add_argument('--merge_unary',action="store_true",help="Merge the unary transition node. Avoiding Rule like FORM->FORM")
    parser.add_argument('--void_span', action="store_true",help="Give void span to unaligned words.")
    parser.add_argument('--bare_rule', action="store_true",help="print rule independently.")
    parser.add_argument('--no_expand', action="store_true",help="Do not permute all the merging.")
    parser.add_argument('--max_compose_depth',type=int, default=0)
    return parser.parse_args()

# 3 Synch Grammar
def extract_three_sync(rule):
    line = rule.split(" ||| ")
    left = []
    for word in line[0].split():
        if word[0] == '"' and word[-1] == '"':
            wordi = word[1:-1]
            if  wordi not in stop:
                left.append(word)
        else:
            left.append(word)

    if len(left) == 2: left.insert(0,"")
    rule =  "%s ||| %s |COL| %s" % (' '.join(left),line[0], line[1])
    return rule

if __name__ == "__main__":
    main()
