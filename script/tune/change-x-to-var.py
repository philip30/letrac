#!/usr/bin/env python

import sys

G = { 1:'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'H', 9:'I' }

def main():
    for line in sys.stdin:
        line = line.strip()
        for x in(range(1,10)):
            line = line.replace("x"+(str(x)), G[x])
            line = line.replace("x_"+(str(x)), G[x])
        print line+'.'

if __name__ == '__main__':
    main()
