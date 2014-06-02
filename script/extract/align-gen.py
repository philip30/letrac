#!/usr/bin/env python
# Logical Form extraction 
# Philip Arthur

import argparse
import sys
from collections import defaultdict
from geometric import extract
from geometric import print_node
from geometric import transform_into_rule
from geometric import change_var_to_x
from geometric import str_logical_rule
from geometric import QUERY
from geometric import FORM
from geometric import query_representation
from geometric import SearchNode

many_literals = []
words = set()


manual_align = {"in":"loc", "me":"answer","the":"answer", "can":"answer", "you":"answer", "tell":"answer", "is":"answer", "name":"answer", "cities": "city", "rivers":"river"}

def main():
    parser = argparse.ArgumentParser(description="Run Geoparse Alignment Input Generator")
    parser.add_argument('--input',type=str,required=True,help="Input file of geoparse")
    parser.add_argument('--osent',type=str,required=True,help="Directory where sentence is outputed")
    parser.add_argument('--ologic',type=str,required=True,help="Directory where logical-form is outputed")
    parser.add_argument('--output',type=str,help="Directory where verbosed output is generated")
    args = parser.parse_args()

    linecount = 0 
    inp = open(args.input,"r")
    out_sent = open(args.osent, "w")
    out_sent_g = open(args.osent + ".gin", "w")
    out_log = open(args.ologic,"w")
    out_log_g = open(args.ologic + ".gin", "w")
    out_log_p = open(args.ologic + ".parse", "w")
    out_w = open(args.osent + ".word", "w")
    out = None
    if args.output:
        out = open(args.output, "w")

    #### For every well formed query in file extract the rule!
    for line in inp:
        line = line.strip()

        (sentence_node, query_node) = extract(line,0,"")[0][0].childs

        #### Sentence and node
        sentence = [node.label for node in sentence_node.childs][:-1]
        # print_node(sentence_node)
        # print_node(query_node)
        for word in sentence: words.add(word)

        #### logical rule extraction
        var_map = defaultdict(lambda: len(var_map)+1)
        query_node = construct_query_node(query_node,[])
        query_node = change_var_to_x(query_node,var_map)
        rules = transform_into_rule([],query_node,start=True)

        #### Printing
        out_sent.write(" ".join(sentence) + "\n")
        out_sent_g.write(" ".join(sentence) + "\n")

        (logical_rule, logical_rule_giza) = ([str_logical_rule(rule[1],rule[4]) for rule in rules], [str_giza_in_rule(rule) for rule in rules])
        if (len(logical_rule) != len(logical_rule_giza)):
            print >> sys.stderr, "Rule size doesn't match", logical_rule_giza, logical_rule

        out_log.write(" ".join(logical_rule) + "\n")
        out_log_g.write(" ".join(logical_rule_giza)+ "\n")
        out_log_p.write(query_representation(query_node,{value:key for key, value in var_map.items()},input_generator=True) +"\n")

        if args.output:
            out.write(" ".join(sentence) + "\n")
            for rule in rules:
                out.write(str_logical_rule(rule[1],rule[4]) + " ||| " + str_giza_in_rule(rule)+ "\n")
            out.write("------------------------------------\n") 
        linecount += 1

    inp.close()
    out_sent.close()
    out_log.close()

    if args.output:
        out.close()

    #### ADDITIONAL information for alignment
    #### Every word is aligned to itself
    for i in range(0,10):
        for word in sorted(words):
            out_sent_g.write(word + "\n")
            out_log_g.write(word + "\n")
            out_w.write(word +"\n")
        
        for word1, word2 in manual_align.items():
            out_sent_g.write(word1 + "\n")
            out_log_g.write(word2 + "\n")
            out_w.write(word1 + "\n")

    #### Handle something like 'south dakota' so add alignment south -> south_dakota and dakota -> south_dakota
    for literals in many_literals:
        literals = literals.split(' ')
        for word in literals:
            out_sent_g.write(word + "\n")
            out_log_g.write('_'.join(literals) + "\n")

    out_sent_g.close()
    out_log_g.close()

    print >> sys.stderr, "Successfully extracting :",  linecount, "pair(s)."

def str_giza_in_rule(rule):
    if len(rule[2]) == 0:
        if ' ' in rule[1]:
            many_literals.append(rule[1][1:-1])
        return rule[1].replace(' ', '_').replace("'",'')
    else:
        return rule[1]

def construct_query_node(query_node,id,parent=None):
    query_node = SearchNode(query_node)
    query_node.height = 0 if parent == None else parent.height + 1
    query_node.id = len(id)
    id.append(query_node)
    for i, child in enumerate(query_node.childs):
        query_node.childs[i] = construct_query_node(child,id,query_node)
        query_node.childsize += 1
    return query_node


# ============== MAIN ======================
if __name__ == '__main__':
    main()
        
