#!/usr/bin/env python

import sys

def main():
    for line in sys.stdin:
        line = ''.join(line.strip().split())
        print line.replace("\\+","\\+ ")

if __name__ == '__main__':
    main()
