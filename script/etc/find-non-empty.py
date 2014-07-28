#!/usr/bin/env python

import sys
from collections import defaultdict

mp = defaultdict(lambda:"Answer = []")
big = -1
for line in sys.stdin:
    n, ans = line.strip().split("\t")
    if n not in mp and ans != "Answer = []":
        mp[n] = ans
    big = max(big,int(n))

for i in range(big+1):
    print mp[str(i)]

