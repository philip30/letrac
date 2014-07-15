#!/usr/bin/env python

import sys
import argparse
from collections import defaultdict

class RenameMap:
    def __init__ (self):
        self.i = 100
    def generate(self):
        self.i += 1
        return "x_" + str(self.i-1) 

def check_output(output):
    depth = 0
    for c in output:
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
    return depth == 0

def main():
    parser = argparse.ArgumentParser(description="Run Beta Reduction")
    parser.add_argument('--alphabet', action="store_true",help="map x_n or xn to alphabet[n]")
    args = parser.parse_args()

    for line in sys.stdin:
        line = line.strip()
        try :
            output = breduct(line,RenameMap())
        
            if not check_output(output):
                print >> sys.stderr, "This output does not have correct parentheses:", output
                sys.exit(1)


            print (output if not args.alphabet else change_x_to_var(output))
        except:
            print "Failed to parse:",line

def rename(inner, lmbd, rename_map):
    #print "RENAMING", inner, lmbd
    lmbd_set = set(lmbd)
    number_set = set(['0','1','2','3','4','5','6','7','8','9'])
    rset = set()
    now = 0
    ret = str(inner)
    while (True):
        occ= inner.find("x",now)
        if occ == len(lmbd) or occ == -1:
            break
        if inner[occ+1] in number_set :
            var = inner[occ:occ+2]
            if var not in lmbd_set and var not in rset: 
                #rename
                ret = ret.replace(var,rename_map.generate())
                rset.add(var)
        now = occ+1
    #print "---> RESULT:", ret
    return ret


def breduct(line,rename_map,start=0,parent_pre=""):
    rets = []
    i=len(line)

    while True:
        occ = line.find("\\",start)
        #### Cannot find lambda anymore
        if occ == -1:
            break
    
        pre = line[start:occ]
        
        #### Finding lambda boundary to the corresponding function
        dot = line.find(".",occ)
        if dot == -1:
            print >> sys.stderr, "Cannot find matching function with previous lambda"
            print >> sys.stderr, "With input: ", line
            sys.exit(1)

        #### Var is the lambda "\x1\x2\x3"
        lmbd = line[occ:dot].split("\\")[1:]

        #### Scanning all the function body 
        function = line.find("(",dot+1)     # character after (
        i = function+1                      # counter in first chracter in (
        depth = 1                           # we are now in one level of (
        while i < len(line) and depth != 0:
            if line[i] == '(':
                depth += 1
            elif line[i] == ')':
                depth -= 1
            i += 1

        if depth != 0:
            print >> sys.stderr, "Unbalance parentheses: ", line
            sys.exit(1)


        #### Go Depth to the child first!
        inner = breduct(line[dot+1:i],rename_map,parent_pre=pre)

        if i != len(line):
            var_next = i+1
            var_next_bound = line.find(")",i+1)
            i = var_next_bound + 1
            var = line[var_next:var_next_bound].split(",")
            
            #### Renaming variable
            inner = rename(inner,lmbd,rename_map)
          
            #### Reduction phase
            for ii, var_x in enumerate(reversed(var)):
                now = 0
                temp = ""
                if ii < len(lmbd):
                    find, target = lmbd[ii], var_x # beta reduction, the first lambda with the outmost variable
                    while True:
                        next_find = inner.find(find,now)
                        if next_find == -1:
                            break
                        elif next_find > 0 and inner[next_find-1]== '@' and inner[next_find+len(find)] == '@':
                            temp += inner[now:next_find + len(find)]
                            now = next_find + len(find)
                        else:
                            temp += inner[now:next_find]
                            temp += '@' + target + '@'
                            now = next_find + len(find)
                    temp += inner[now:]
                    inner = temp
                else:
                    print >> sys.stderr, "Too many variable for function assignment",
                    print >> sys.stderr, "In line:'", line + "'",
                    print >> sys.stderr, "Omitting...."
            if len(lmbd) > len(var):
                # Case of partial function application
                rest = lmbd[(len(lmbd)-len(var)):]
                inner = "".join(["\\"+x for x in rest]) + "." + inner

            start = var_next_bound + 2
            if start < len(line) and line[start] == ',': 
                inner += ')'
                start += 1
            rets.append(filter(lambda x: x != '@', inner))
        else:
            # Case of lambda without variable
            start = len(line)
            rets += [inner]
    return parent_pre +(','.join(rets) + line[i:] if rets != [] else line)

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

if __name__ == '__main__':
    main()
