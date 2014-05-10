#!/usr/bin/env python

import sys
from stop_word_list import stop_word_list as stop

for line in sys.stdin:
    line = line.strip().split()
    print ' '.join(filter(lambda x: x not in stop, line))
