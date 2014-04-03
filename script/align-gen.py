#!/usr/bin/python
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

many_literals = []
words = set()

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
		query_node = change_var_to_x(query_node,var_map)
		rules = transform_into_rule([],query_node,start=True)

		#### Printing
		out_sent.write(" ".join(sentence) + "\n")
		out_sent_g.write(" ".join(sentence) + "\n")

		(logical_rule, logical_rule_giza) = ([str_logical_rule(rule) for rule in rules], [str_giza_in_rule(rule) for rule in rules])
		if (len(logical_rule) != len(logical_rule_giza)):
			print >> sys.stderr, "Rule size doesn't match", logical_rule_giza, logical_rule

		out_log.write(" ".join(logical_rule) + "\n")
		out_log_g.write(" ".join(logical_rule_giza)+ "\n")

		if args.output:
			out.write(" ".join(sentence) + "\n")
			for rule in rules:
				out.write(str_logical_rule(rule) + " ||| " + str_giza_in_rule(rule)+ "\n")
			out.write("------------------------------------\n") 
		linecount += 1

	inp.close()
	out_sent.close()
	out_log.close()

	if args.output:
		out.close()

	#### ADDITIONAL information for alignment
	#### Every word is aligned to itself
	for word in sorted(words):
		out_sent_g.write(word + "\n")
		out_log_g.write(word + "\n")

	#### Handle something like 'south dakota' so add alignment south -> south_dakota and dakota -> south_dakota
	for literals in many_literals:
		literals = literals.split(' ')
		for word in literals:
			out_sent_g.write(word + "\n")
			out_log_g.write('_'.join(literals) + "\n")

	out_sent_g.close()
	out_log_g.close()

	print >> sys.stderr, "Successfully extracting :",  linecount, "rule(s)."

def str_giza_in_rule(rule):
	if len(rule[2]) >= 1 and type(rule[2][0]) != int and rule[2][0] != QUERY and rule[2][0] != FORM:
		if ' ' in rule[2][0]:
			many_literals.append(rule[2][0][1:-1])
		return rule[2][0].replace(' ', '_').replace("'",'')
	else:
		return rule[1]



# ============== MAIN ======================
if __name__ == '__main__':
	main()
		
