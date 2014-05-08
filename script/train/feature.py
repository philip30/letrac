#!/usr/bin/python
import sys
import math
from collections import defaultdict

context = defaultdict(lambda:0)
count = defaultdict(lambda:0)

for i,line in enumerate(sys.stdin):
    (sent, log) = line.strip().split(" ||| ")
    count[i,sent,log] += 1
    context[sent] += 1
    context[log] += 1
    context[""] += 1

for ((i,sent,log), cnt) in sorted(count.items(),key=lambda x:x[0]):
#   print >> sys.stderr, sent + " ||| " + log + " ||| " + str(cnt)
    print "%s ||| %s ||| psgl=%f plgs=%f prob=%f count=%s parse=%d" % \
        (sent, log, -math.log(float(cnt)/context[log]), \
        -math.log(float(cnt)/context[sent]), \
        -math.log(float(cnt)/context[""]),\
        cnt, (1 if (len(sent.split()) == (1+2)) else 0))

#with open(sys.argv[1],"r") as word_fp:
#    for word in word_fp:
#        print "\"%s\" x0:QUERY @ QUERY ||| x0:QUERY @ QUERY ||| del=1" % (word.strip())
