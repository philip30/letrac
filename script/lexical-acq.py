#!/usr/bin/python

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

# flag

CONJUNCTION = "CONJ"
NEGATION = "NOT"
FORM = "FORM"

def main():
	args = parse_argument()

	#### file pointer
	inp_file = open(args.input,'r')
	sent_file = open(args.sent,'r')
	fol_file = open(args.fol,'r')
	align_file = open(args.align,'r')

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
		query_node = calculate_v(query_node)			 # give information about variables that bound to node
		query_node = calculate_e(query_node,s2l)		 # give information about which words that are aligned to node
		query_node = change_not_and_conj(query_node)	 # change '' to CONJUNCTION and \+ to NEGATION
		query_node = transform_multi_words_entity(query_node) # change 'w1 w2' entity into w1_w2

		#### Extracting! finish indicates that extraction is performed until root
		lex_rule, _, finish = lex_acq([], query_node, sent, set([]))
		if finish: f += 1

		#### Printing all results
		if finish or args.include_fail:
			if args.verbose:
				print sent_line
				print_node(query_node,stream=sys.stdout)
			for r in lex_rule:
				if args.translation_rule:
					print trans_lambda_rule_to_string(r)
				else:
					print lambda_rule_to_string(r)
			if args.verbose: print '-------------------------------------'
		count += 1

	#### Closing all files
	map(lambda x: x.close(), [inp_file, sent_file, fol_file, align_file])

	#### Printing stats
	print >> sys.stderr, "Finish extracting rule from %d pairs with %.3f of them parsed successfully." % (count, float(f)/count)  

def lex_acq(rules, node, sent, parent_v, start=True):
	child_spans = []
	w_i = sorted(list(node.eorigin))
	w_i_max = sorted(list(node.e))
	legal = True
	for i, child in enumerate(node.childs):
		if len(child.childs) != 0 and len(child.e) != 0:
			_, span, _legal = lex_acq(rules, child, sent, set(list(node.vorigin)+list(parent_v)), start=False)
			legal = legal and _legal
			child_spans.append((i,span))

	if legal:
		is_leave = len(child_spans) == 0
		child_spans = sorted(list(child_spans)+[(-1,(x,x)) for x in w_i],key=lambda x: x[1][0])
		# analyze rule
		rule = transform_into_rule([],node,start,recurse=False)
		if (len(rule) > 0) and is_leave:
			r = ( rule[0][0], ( sent_map(w_i,sent) ), ( node.label, set([c.label for c in node.childs]) ) , [var for var in node.v if type(var) == int])
			if len(node.v) == 0:
				r[2][1].add(node.childs[0].label)
			rules.append( r )
			node.type = r
		else:
			previous = -1
			word = []
			var_bound = [] if start else [x for x in node.v if x in parent_v]

			arguments = [[]] * len(node.childs)
			for index, child_span in child_spans:
				if child_span[0] < previous:
					legal = False
					break
				elif previous != -1:
					s_range = child_span[0]-previous-1
					if s_range > 0: word.append(s_range)
				previous = child_span[1]
				if index == -1:
					word.append(sent[child_span[0]])
				else:
					word.append(-index-1)
					arguments[index]=(node.childs[index].type[2][1],node.childs[index].label)
			else:
				for i, child in enumerate(node.childs):
					if child.label in node.vorigin and len(child.childs) == 0:
						arguments[i] = child.label

				head = node.label if node.label == CONJUNCTION or node.label == NEGATION else rule[0][0]

				r = (head , word , ( node.label, arguments ) , var_bound )
				node.type = r
				rules.append( r )	
	return rules, (w_i_max[0],w_i_max[-1]), legal

def lambda_rule_to_string(r):
	ret = r[0] + " ||| "
	index_map = {}
	for w in r[1]:
		if type(w) == int:
			if w < 0:
				key = len(index_map)+1
				arg_type = r[2][1][-w-1][1]
				ret += (arg_type if arg_type == CONJUNCTION or arg_type == NEGATION else FORM) + str(key)
				index_map[-w-1] = str(key)
			else:
				ret += "(" + str(w) + ")"
		else:
			ret += w
		ret += " "
	ret += "||| "
	ret += "".join(["\\x" + str(x) for x in r[3]])
	if len(r[3]) > 0: ret += "." 
	ret += r[2][0] + "("
	args = []
	for index, arg in enumerate(r[2][1]):
		if arg != []:
			args.append(arg_to_string(index_map,index,arg))
			
	ret += ",".join(args)
	ret += ")"

	return ret

def arg_to_string(index_map,position,arg): 
	ret = ""
	if type(arg) == int:
		ret = "x" + str(arg)
	elif type(arg) == str:
		ret = arg
	elif type(arg) == tuple:
		ret = (FORM if arg[1] != CONJUNCTION and arg[1] != NEGATION else arg[1]) + index_map[position] 
		has_args = len([x for x in list(arg[0]) if type(x) == int]) != 0
		if has_args:
			ret += "("
			inner_arg = []
			for i_arg in [x for x in list(arg[0]) if type(x) == int]:
				if type(i_arg) == int:
					inner_arg.append("x"+str(i_arg))
				elif type(i_arg) == str:
					inner_arg.append(str(i_arg))
				elif i_arg != []:
					inner_arg.append(i_arg[1] if i_arg[1] == CONJUNCTION or i_arg[1] == NEGATION else FORM)
			ret += ",".join(inner_arg)
			ret += ")"
	return ret


def trans_lambda_rule_to_string(r):
	ret = ""
	index_map = {}
	for w in r[1]:
		if type(w) == int:
			if w < 0:
				key = len(index_map)+1
				arg_type = r[2][1][-w-1][1]
				ret += "x" + str(key-1) +":"+(arg_type if arg_type == CONJUNCTION or arg_type == NEGATION else FORM) 
				index_map[-w-1] = str(key)
			else:
				ret += "\"(" + str(w) + ")\""
		else:
			ret += '"' + w + '"'
		ret += " "
	ret += "@ " + r[0]
	ret += " ||| \""
	ret += "".join(["\\x" + str(x) for x in r[3]])
	if len(r[3]) > 0: ret += "." 
	ret += r[2][0] + "("
	args = []
	nt_last = True
	for index, arg in enumerate(r[2][1]):
		if arg != []:
			if index > 0:
				ret += "," 
			if type(arg) == tuple:
				ret +="\" "
			_arg, nt_last = trav_arg_to_string(index_map,index,arg)
			ret += _arg

	ret += ")\"" if nt_last else " \")\""
	ret +=  " @ " + r[0]
	return ret

def trav_arg_to_string(index_map,position,arg): 
	ret = ""
	has_args = True
	if type(arg) == int:
		ret = "x" + str(arg)
	elif type(arg) == str:
		ret = arg
	elif type(arg) == tuple:
		ret = "x" + str(int(index_map[position])-1) +":"+ (FORM if arg[1] != CONJUNCTION and arg[1] != NEGATION else arg[1])
		has_args = len([x for x in list(arg[0]) if type(x) == int]) != 0
		if has_args:
			ret += " \"("
			inner_arg = []
			for i_arg in [x for x in list(arg[0]) if type(x) == int]:
				if type(i_arg) == int:
					inner_arg.append("x"+str(i_arg))
				elif type(i_arg) == str:
					inner_arg.append(str(i_arg))
				elif i_arg != []:
					inner_arg.append(i_arg[1] if i_arg[1] == CONJUNCTION or i_arg[1] == NEGATION else FORM)
			ret += ",".join(inner_arg)
			ret += ")"
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
		node.v.add(node.label)
		node.vorigin.add(node.label)
	for child in node.childs:
		if type(child.label) == int:
			node.vorigin.add(child.label)
	for (i,child) in enumerate(node.childs):
		node.childs[i] = calculate_v(child)
		for var in node.childs[i].v:
			node.v.add(var)
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
	for (i, child) in enumerate(node.childs):
		node.childs[i] = change_not_and_conj(child)
	return node

def transform_multi_words_entity(node):
	if type(node.label) == str and len(node.label) > 0 and node.label[0] == "'" and node.label[-1] == "'":
		node.label = "_".join(node.label[1:-1].split())
	for (i,child) in enumerate(node.childs):
		node.childs[i] = transform_multi_words_entity(child)
	return node

def parse_argument():
	parser = argparse.ArgumentParser(description="Run Lexical Acquisition")
	parser.add_argument('--input', type=str,required=True,help="The geoquery file")
	parser.add_argument('--sent',type=str,required=True,help="The sentence file")
	parser.add_argument('--fol',type=str,required=True,help="The sentence file in fol")
	parser.add_argument('--align',type=str,required=True,help="The alignment between sent to fol")
	parser.add_argument('--translation_rule',action="store_true",help="Output the rule into translation rule instead.")
	parser.add_argument('--verbose',action="store_true",help="Show some other outputs to help human reading.")
	parser.add_argument('--include_fail',action="store_true",help="Include (partially) extracted rules even it is failed to extract until root.")
	return parser.parse_args()

if __name__ == "__main__":
	main()
