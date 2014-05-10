#!/usr/bin/env python

import sys
import argparse

def main():
    for line in sys.stdin:
        print preprocess(line.strip())

def preprocess(line):
    line = process_single_negation(line)
    return line

def process_single_negation(line):
    ret = ""
    now = 0
    while True:
        next_index = line.find("\+",now)
        
        if next_index == -1:
            break
        
        ret += line[now:next_index]
        if line[next_index+2] == ' ':
            ret += "\+"
            now = next_index + 2
        else:
            ret += "\+ ("
            i=line.find("(",next_index)+1
            ret += line[next_index+2:i]
            next_index = i
            depth = 1
            while depth != 0 and i < len(line):
                if line[i] == ')': depth -= 1
                elif line[i] == '(': depth += 1
                i+=1
            ret += line[next_index:i]
            ret += ")"
            now = i
    ret += line[now:]
    return ret

if __name__ == '__main__':
    main()
