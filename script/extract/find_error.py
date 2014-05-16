#!/usr/bin/env python

import sys

def valid(map1,map2s):
    return all((len(map1) == len(map2) and all(map1[k1] == map2[k1] for k1 in map1)) for map2 in map2s)

def check_valid_sync_symbol(line):
    src, trg = line.strip().split(" ||| ")
    trg_s = trg.split(" |COL| ")
    
    src_map = {}
    trg_map = [{}] * len(trg_s)

    for src_word in src.split():
        if src_word == '@': break
        if src_word[0] != '"' and src_word[-1] != '"':
            x, label = src_word.split(":")
            x_int = int(x[1:])
            src_map[x_int] = label
    for i, trg in enumerate(trg_s):
        for trg_word in trg.split():
            if trg_word == '@': break
            if trg_word[0] != '"' and trg_word[-1] != '"':
                x, label = trg_word.split(":")
                x_int = int(x[1:])
                trg_map[i][x_int] = label
    
    return valid(src_map, trg_map)
            
