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
from stop_word_list import stop_word_list as stop

# flag
CONJUNCTION = "CONJ"
NEGATION = "NOT"
FORM = "FORM"
COUNT = "COUNT"

TYPE_LABEL = set([CONJUNCTION, NEGATION, COUNT])

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
    f = 0

    #### For input-sentence-fol-alignment
    for (inp_line,sent_line, fol_line, align_line) in zip(inp_file,sent_file,fol_file,align_file):
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
        query_node = change_var_to_x(query_node,var_map) # alter A->x1, B->x2, and so on
        query_node = calculate_v(query_node)             # give information about variables that bound to node
        query_node = calculate_e(query_node,s2l)         # give information about which words that are aligned to node
        query_node = change_not_and_conj(query_node)     # change '' to CONJUNCTION and \+ to NEGATION
        query_node = transform_multi_words_entity(query_node) # change 'w1 w2' entity into w1_w2

        #### Merge Unary Node (We will not have the node such FORM->FORM)
        if args.merge_unary: 
            query_node,_ = merge_unary(query_node)

        #### Extracting! finish indicates that extraction is performed until root
        lex_rule, _, finish, _, _ = lex_acq([], query_node, sent, [], args.void_span)
        if finish: f += 1
        
        if not args.no_expand:
            lex_rule = expand_rule(lex_rule)

        #### Printing all results
        if finish or args.include_fail:
            if args.verbose:
                print sent_line
                print_node(query_node,stream=sys.stdout)
            for r in lex_rule:
                now_rule = r
                if args.bare_rule:
                    label, arguments, bound, args_bound = bare_rule(r[2][0],r[2][1],r[3],r[4])
                    now_rule = (r[0],r[1],(label,arguments),bound,args_bound)
                
                #print now_rule
                rule_string = trans_lambda_rule_to_string(now_rule)
                if args.three_sync:
                    rule_string = extract_three_sync(rule_string)
                
                if rule_string != "":
                    print rule_string
            print >> rule_out_file, len(lex_rule)
            if args.verbose: print '-------------------------------------'
        else:
            print >> rule_out_file, '0'
        count += 1
    
    #### Closing all files
    map(lambda x: x.close(), [inp_file, sent_file, fol_file, align_file,rule_out_file])

    #### Printing stats
    print >> sys.stderr, "Finish extracting rule from %d pairs with %.3f of them parsed successfully." % (count, float(f)/count)  

def expand_rule(initial_rule):
    ret = []
    for rule in initial_rule:
        (head , word , ( label, arguments ) , var_bound , arg_bound) = rule
        child_funcs = []
        for (index,_word) in enumerate(word):
            if _word < 0:
                arg = arguments[-_word-1]
                if type(arg) == tuple:
                    child_funcs.append((index,_word,arg))

        enum = [('{0:0'+str(len(child_funcs))+'b}').format(x) for x in range(1,(2**len(child_funcs)))]
        ret.append(rule)
        min_x = min(0,min([x for x in map((lambda y: y if type(y) == int and y < 0 else 0), rule[1])]))
        for binstring in enum:
            funcs = [child_funcs[index] for (index,x) in enumerate(binstring) if x == '1']
            rule_cpy = copy.deepcopy(rule)
            for func in reversed(funcs):
                (w_index, _word, (arg_index,_,_,_,_)) = func
                rule_cpy[1].pop(w_index)
                offset = len(rule_cpy[2][1])
                g = offset
                for word_ in reversed(initial_rule[arg_index][1]):
                    if type(word_) == int and word_ < 0:
                        last = word_
                        g+=1
                        rule_cpy[1].insert(w_index,-g)
                        rule_cpy[2][1][-_word-1][2].insert(offset,initial_rule[arg_index][2][1][-word_-1])
                        rule_next = initial_rule[arg_index][2][1][-word_-1]
                        rule_cpy[2][1].insert(offset,(-1,rule_next[1],rule_next[2],rule_next[3],rule_next[4]))
                        rule_cpy[4].insert(offset,initial_rule[arg_index][4][-word_-1])
                    else:
                        rule_cpy[1].insert(w_index,word_)
            ret.append(rule_cpy)
    return ret

def bare_rule(label, args, bound, args_bound):
    if bound == []:
        if len(args_bound) == 1 and args_bound[0] != []:
            delta = min(map(lambda x:x-1,args_bound[0]))
            return format_label(label,delta), format_args(args,delta), bound,[map(lambda x:x-delta, args_bound[0])]     
        else:
            return label, args, bound, args_bound
    else:
        delta = min(map(lambda x:x-1, bound))
        bound = map(lambda x: x-delta,bound)
        args_bound = map(lambda x: map(lambda y: y-delta, x), args_bound)
        return format_label(label,delta), format_args(args,delta), bound, args_bound

def format_label(label, delta):
    if delta <= 0: return label
    scan = 0
    find = label.find("x")
    if find != -1:
        value = int(label[find+2]) - delta
        return label[0:find] + "x" + str(value)+label[find+3:]
    return label

def format_args(args, delta):
    ret = []
    for k in args:
        if type(k) == int:
            ret.append(k-delta)
        else:
            ret.append(k)
    return ret

def lex_acq(rules, node, sent, parent_v, void_span, start=True):
    child_spans = []
    w_i = sorted(list(node.eorigin))
    w_i_max = sorted(list(node.e))
    legal = True
    var_bound = [];
    for i, child in enumerate(node.childs):
        if len(child.childs) != 0 and len(child.e) != 0:
            _, span, _legal, var_bound, rule_number = lex_acq(rules, child, sent, [x for x in node.vorigin if x not in parent_v]+parent_v, void_span, start=False)
            legal = legal and _legal
            child_spans.append((i,span,var_bound,rule_number))

    if legal:
        is_leaf = len(child_spans) == 0
        node.leaf = is_leaf
        child_spans = sorted(list(child_spans)+[(-1,(x,x),[],-1) for x in w_i if (x,x) not in set([y[1] for y in child_spans])],key=lambda x: x[1][0])
        # analyze rule
        rule = transform_into_rule([],node,start,recurse=False)
        if (len(rule) > 0) and is_leaf:
            var_bound = list([var for var in node.vorigin if type(var) == int and var not in node.vmerged] + list(node.vmerged))
            node.extra_info = var_bound
            r = ( rule[0][0], ( sent_map(w_i,sent) ), ( node.label, ([c.label for c in node.childs]) ) , var_bound, [[]] * len(node.childs))
            if len(node.v) == 0:
                if node.childs[0].label not in r[2][1]: r[2][1].append(node.childs[0].label)
            rules.append( r )
        else:
            previous = -1
            word = []
            var_bound = [] if start else [x for x in node.v if x in parent_v]
            node.extra_info = var_bound
            arg_bound = [[]] * len(node.childs)
            arguments = [[]] * len(node.childs)
            for index, child_span, child_bound,rule_number in child_spans:
                if child_span[0] < previous:
                    var_bound = []
                    legal = False
                    break
                elif previous != -1:
                    if void_span:
                        s_range = child_span[0]-previous-1
                        if s_range > 0: word.append(s_range)
                    else:
                        for k in range(previous+1,child_span[0]):
                            word.append(sent[k])
                previous = child_span[1]
                if index == -1:
                    word.append(sent[child_span[0]])
                else:
                    word.append(-index-1)
                    arg_bound[index]=child_bound
                    arg_leaf_info = [gc.label for gc in node.childs[index].childs] if node.childs[index].leaf else []
                    arguments[index]=(rule_number,node.childs[index].label,arg_leaf_info,node.childs[index].vorigin,node.childs[index].extra_info)
            else:
                for i, child in enumerate(node.childs):
                    if child.label in node.vorigin and len(child.childs) == 0:
                        arguments[i] = child.label

                head = node.label if node.label in TYPE_LABEL else rule[0][0]
                r = (head , word , ( select_label(node.label), arguments ) , var_bound , arg_bound)
                rules.append( r )   
    return rules, (w_i_max[0],w_i_max[-1]), legal, var_bound, (len(rules)-1)

def trans_lambda_rule_to_string(r):
    head, word, (label, arguments), var_bound, arg_bound = r

    ret = ""
    index_map = {}
    for w in word:
        if type(w) == int:
            if w < 0:
                key = len(index_map)+1
                (arg_type, arg_label,_,_,_) = arguments[-w-1]
                ret += "x" + str(key-1) +":" \
                    +(arg_label if arg_label in TYPE_LABEL else FORM) \
                    + append_var_info(arg_bound[-w-1])
                index_map[-w-1] = str(key)
            else:
                ret += "\"(" + str(w) + ")\""
        else:
            ret += '"' + w + '"'
        ret += " "
    ret += "@ " + head + append_var_info(var_bound)
    logic = '"'
    logic += "".join(["\\x" + str(x) for x in reversed(sorted(var_bound))])
    if len(var_bound) > 0: logic += "."
    logic += label + "("
    args = []
    nt_last = True

    real_arg_len = 0
    for arg in arguments:
        if (type(arg) == tuple or type(arg) == list) and arg!= [] and arg[0] == -1:
            break
        real_arg_len += 1

    for index in range (0,real_arg_len):
        arg = arguments[index]
        if arg != []:
            if index > 0:
                logic += "," 
            if type(arg) == tuple or type(arg) == list:
                logic +="\" "
            occ = (type(arg) == tuple or type(arg) == list) and (-index-1 not in word)
            _arg, nt_last = trans_arg_to_string(index_map,index,arg,arg_bound[index],occ,index == rindex_nempty(list(arguments)),real_arg_len)
            logic += _arg

    if not nt_last: logic += " \""
    logic += ")" * (1 + len([x for x in label if x == '(']))
    logic += "\""
    logic+=  " @ " + head + append_var_info(var_bound)
    return ret + " ||| " + ammeliorate_error(logic)

def ammeliorate_error(logic):
    return logic.replace(' " ', ' ') 

def trans_arg_to_string(index_map,position,arg,bound,occ,last,real_arg_len):
    ret = ""
    has_args = True
    if type(arg) == int:
        ret = "x" + str(arg)
    elif type(arg) == str:
        if '_' in arg and len(arg) != 1:
            arg = "'" + arg + "'"
            arg = arg.replace('_','#$#')
        ret = arg
    elif type(arg) == tuple or type(arg) == list:
        (_, arg_label, arg_inner, v_orig, arg_bound) = arg
        if position in index_map or all(type(x) == int for x in arg_inner) or len(arg_inner) == 0:
            ret = "x" + str(int(index_map[position])-1) +":"+ (FORM if arg_label not in TYPE_LABEL else arg_label) \
                + append_var_info(bound) if not occ else \
                "\"%s.%s(%s)\"" % (''.join(["\\x"+str(i) for i in bound]),arg_label,','.join(["x"+str(i) for i in bound]))
            has_args = len(bound) != 0
            if has_args:
                ret += " \"("
                inner_arg = []
                for i_arg in sorted(bound):
                    inner_arg.append("x"+str(i_arg))
                ret += ",".join(inner_arg)
                ret += ")"
            elif not last:
                ret += " \""
        else:
            ret += '"'
            if len(bound) != 0:
                ret += ''.join(["\\x"+str(i) for i in bound])
                ret += '.'
           
            arg_inn_ =["x" + str(i) for i in v_orig]
            for (index,arg_inn) in enumerate(arg_inner):
                if type(arg_inn) == str:
                    if '_' in arg_inn and len(arg_inn) != 1:
                        arg_inn = "'" + arg_inn + "'"
                        arg_inn = arg_inn.replace('_','#$#')
                    arg_inn_.append(arg_inn)
                elif type(arg_inn) == tuple or type(arg_inn) == list:
                    var_label = 'FORM' if arg_inn[1] not in TYPE_LABEL else arg_inn[1]
                    lambda_var = ("(" + ','.join(['x' + str(i) for i in arg_inn[4]]) + ")") if len(arg_inn[4]) != 0 else ""
                    arg_inn_.append('" x%d:%s%s "%s' % (int(index_map[real_arg_len+len(arg_inner)-index-1])-1,var_label,append_var_info(arg_inn[4]),lambda_var))
            has_args = len(bound) != 0
            arg_inn_ = ','.join(arg_inn_)
            ret += select_label(arg_label) + "("  + arg_inn_ + ")"+ (("(" + ','.join(map(lambda x: "x"+str(x),bound)) +")") if has_args else "") + '"'
            if not last: ret += " \""
    return ret, has_args

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

def span_overlap(s1,s2):
    return (s1[0] < s2[0] and s1[0] < s2[1] and s1[1] < s2[1]) or (s2[0] < s1[0] and s1[0] < s2[1] and s2[1] < s1[1])

def calculate_v(node):
    if not isinstance(node, SearchNode):
        node = SearchNode(node)
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

def calculate_e(node, logic_map,start=True):
    if not isinstance(node,SearchNode):
        node = SearchNode(node)
    rule = transform_into_rule([],node,recurse=False,start=start) if len(node.childs) != 0 else []
    if len(rule) > 0:
        node.e = set([i for i in logic_map[str_logical_rule(rule[0])]])
        node.eorigin = set([i for i in logic_map[str_logical_rule(rule[0])]])
    for (i,child) in enumerate(node.childs):
        node.childs[i] = calculate_e(child, logic_map,False)
        for word in node.childs[i].e:
            node.e.add(word)
    return node

def change_not_and_conj(node):
    if node.label == '': 
        node.label = CONJUNCTION
    elif node.label == '\+':
        node.label = NEGATION
    elif node.label == 'count':
        node.label = COUNT
    for (i, child) in enumerate(node.childs):
        node.childs[i] = change_not_and_conj(child)
    return node

def transform_multi_words_entity(node):
    if type(node.label) == str and len(node.label) > 0 and node.label[0] == "'" and node.label[-1] == "'":
        node.label = "_".join(node.label[1:-1].split())
    for (i,child) in enumerate(node.childs):
        node.childs[i] = transform_multi_words_entity(child)
    return node

def rindex_nempty(l):
    k = len(l)-1
    while k >= 0:
        if l[k] != []:
            break
        k -= 1
    return k 

def merge_unary(node):
    # we start from the children
    child_spans = []
    w_i = sorted(list(node.eorigin))
    w_i_max = sorted(list(node.e))
    legal = True
    for i, child in enumerate(node.childs):
        if len(child.childs) != 0 and len(child.e) != 0:
            _, span = merge_unary(child)
            child_spans.append((i,span))

    child_spans = sorted(list(child_spans)+[(-1,(x,x)) for x in w_i if (x,x) not in set([y[1] for y in child_spans])],key=lambda x: x[1][0])

    # Checking unarity
    if len(child_spans) == 1 and child_spans[0][0] > 0:
        unary_child = node.childs[child_spans[0][0]]
        x_quer = [n.label for n in node.childs if type(n.label) == int]
        node.childs = [] # clear the child ## DANGER MAY BECOME BUG

        for e in unary_child.eorigin: node.eorigin.add(e)
        for v in unary_child.vorigin: 
            if v not in node.vorigin: node.vorigin.append(v)

        node.label += "(" + ",".join(["x" + str(n) for n in x_quer]) + ("," if len(x_quer) != 0 else "") \
             + select_label(unary_child.label)
        for unary_child_child in unary_child.childs:
            node.childs.append(unary_child_child)

    return node, (w_i_max[0],w_i_max[-1])

def select_label(label):
    if label == NEGATION:
        label = "-"
    elif label == CONJUNCTION:
        label = ""
    elif label == COUNT:
        label = "count"
    return label

def append_var_info(bound):
    bound_wo = [x for x in bound if type(x) == int]
    return "["+str(len(bound_wo))+"]" if len(bound_wo) != 0 else ""

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
    return parser.parse_args()

# 3 Synch Grammar
prec = defaultdict(lambda:0)
prec['QUERY'] = 100
prec['COUNT'] = 70
prec['FORM'] = 50
prec['CONJ'] = 30
prec['NOT'] = 40
def loop(l):
    k = False
    if len(l) == 3:
        y = l[0]
        if not (y[0] == '"' and y[-1] == '"'):
            _, label = y.split(":")
            return label == l[-1]
    return k

def unary_before(l):
    k = False
    if len(l) == 3:
        y1,label2 = l[0], l[-1]
        if y1[0] != '"' and y1[-1] != '"':
            label1 = y1.split(":")[1]
            if '[' in label1: label1 = label1[:label1.find('[')]
            if '[' in label2: label2 = label2[:label2.find('[')]

            if label1 not in prec: print >> sys.stderr, "Unrecognizable label:", label1
            if label2 not in prec: print >> sys.stderr, "Unrecognizable label:", label2

            return prec[label1] > prec[label2]
    return k

def extract_three_sync(rule):
    line = rule.split(" ||| ")
    left = []
    for word in line[0].split():
        if word[0] == '"' and word[-1] == '"':
            wordi = word[1:-1]
            if wordi == 'us' or wordi not in stop:
                left.append(word)
        else:
            left.append(word)

    if len(left) == 2 or loop(left) or unary_before(left):
        rule = ""
    else:
        rule =  "%s ||| %s |COL| %s" % (' '.join(left),line[0], line[1])
    return rule

if __name__ == "__main__":
    main()
