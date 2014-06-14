#!/usr/bin/python

import sys
from collections import defaultdict
k = defaultdict(lambda:0)
gs_fp = open(sys.argv[3],"r")
gs_q = open(sys.argv[4],"r")
sent = open(sys.argv[5],"r")
test = False
if sys.argv[2] == '--test':
    test = True
    n_s = 1
else:
    n_s = int(sys.argv[2])
item = defaultdict(lambda:[])
 
for i in range(1, n_s+1):
    if test: i = ""

    n_best = open(sys.argv[1]+str(i) + ".reduct","r")
    n_fp = open(sys.argv[1]+str(i) +".n","r")
    stat_fp = open(sys.argv[1]+str(i)+".stats","r")
    
    for n_line, stat_line, n_best in zip(n_fp,stat_fp,n_best):
        n_line, stat_line, n_best_line = map(lambda x:x.strip(), [n_line,stat_line, n_best])
        #print n_line, "|||", stat_line
        
        if stat_line.split()[0] == '1':
            k[int(n_line)] += 1
        else:
            k[int(n_line)] += 0
        k[n_line] += 1
    
        item[int(n_line)].append((stat_line,n_best_line))
    if test: break
    
g = 0
for n in sorted(k):
    if type(n) == int:
        rate = float(k[n])/k[str(n)]
        if rate != 0.0:
            g += 1
      #  print n, rate

for n, (gs_line, gsq_line,sent_line) in enumerate(zip(gs_fp,gs_q,sent)):
    gs_line, gsq_line, sent_line = map(lambda x: x.strip(), [gs_line,gsq_line,sent_line])
    print n, sent_line
    print "  FORM  :", gs_line
    print "  QUERY :", gsq_line
    print "  RATE  :", (float(k[n]) / k[str(n)] if str(n) in k else 0.0)
    for i in item[n]:
        print "       ", i

print "Repairable", float(g) / (len(k) / 2)
