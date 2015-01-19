#!/usr/bin/env python

import sys
from threading import Lock
from collections import defaultdict

lock = Lock()

### Enumeration
CITY="city"
PLACE="place"
COUNTRY="country"
LAKE="lake"
MOUNTAIN="mountain"
STATE="state"
NUM="num"
RIVER="river"
STATE="state"

ALL_TYPE=[CITY,PLACE,COUNTRY,LAKE,MOUNTAIN,STATE,NUM,RIVER,STATE]

### TYPE MAP
type_map = defaultdict(lambda:set([]))
type_map["const_cityid"].add((CITY,))
type_map["const_countryid"].add((COUNTRY,))
type_map["const_placeid"].add((PLACE,))
type_map["const_placeid"].add((LAKE,))
type_map["const_placeid"].add((MOUNTAIN,))
type_map["const_riverid"].add((RIVER,))
type_map["const_stateid"].add((STATE,))
type_map["capital"].add((CITY,))
type_map["capital"].add((PLACE,))
# city(x1)
type_map["city"].add((CITY,))
# country(x1)
type_map["country"].add((COUNTRY,))
# lake(x1)
type_map["lake"].add((PLACE,))
type_map["lake"].add((LAKE,))
# major(x1)
type_map["major"].add((CITY,))
type_map["major"].add((LAKE,))
type_map["major"].add((RIVER,))
# mountain(x1)
type_map["mountain"].add((MOUNTAIN,))
type_map["mountain"].add((PLACE,))
# place(x1)
type_map["place"].add((PLACE,))
type_map["place"].add((LAKE,))
type_map["place"].add((MOUNTAIN,))
# river(x1)
type_map["river"].add((RIVER,))
# state(x1)
type_map["state"].add((STATE,))
# area(x1].add((x2)
type_map["area"].add((CITY, NUM))
type_map["area"].add((COUNTRY, NUM))
type_map["area"].add((STATE, NUM))
# capital(x1].add((x2)
type_map["capital"].add((STATE, CITY))
# density(x1].add((x2)
type_map["density"].add((CITY, NUM))
type_map["density"].add((COUNTRY, NUM))
type_map["density"].add((STATE, NUM))
# elevation(x1].add((x2)
type_map["elevation"].add((PLACE, NUM))
type_map["elevation"].add((MOUNTAIN, NUM))
# high_point(x1].add((x2)
type_map["high_point"].add((COUNTRY,PLACE))
type_map["high_point"].add((COUNTRY,MOUNTAIN))
type_map["high_point"].add((STATE,PLACE))
type_map["high_point"].add((STATE,MOUNTAIN))
# higher(x1].add((x2)
type_map["higher"].add((PLACE,PLACE))
type_map["higher"].add((PLACE,MOUNTAIN))
type_map["higher"].add((MOUNTAIN,PLACE))
type_map["higher"].add((MOUNTAIN,MOUNTAIN))
# len(x1].add((x2)
type_map["len"].add((RIVER, NUM))
# loc(x1].add((x2)
type_map["loc"].add((CITY,COUNTRY))
type_map["loc"].add((PLACE,COUNTRY))
type_map["loc"].add((LAKE,COUNTRY))
type_map["loc"].add((MOUNTAIN,COUNTRY))
type_map["loc"].add((RIVER,COUNTRY))
type_map["loc"].add((STATE,COUNTRY))
type_map["loc"].add((CITY,STATE))
type_map["loc"].add((PLACE,STATE))
type_map["loc"].add((LAKE,STATE))
type_map["loc"].add((MOUNTAIN,STATE))
type_map["loc"].add((RIVER,STATE))
type_map["loc"].add((PLACE,CITY))
# longer(x1].add((x2)
type_map["longer"].add((RIVER,RIVER))
# low_point(x1].add((x2)
type_map["low_point"].add((COUNTRY,PLACE))
type_map["low_point"].add((COUNTRY,MOUNTAIN))
type_map["low_point"].add((STATE,PLACE))
type_map["low_point"].add((STATE,MOUNTAIN))
# lower(x1].add((x2)
type_map["lower"].add((PLACE, PLACE))
type_map["lower"].add((COUNTRY, MOUNTAIN))
type_map["lower"].add((MOUNTAIN, PLACE))
type_map["lower"].add((MOUNTAIN, MOUNTAIN))
# next_to(x1].add((x2)
type_map["next_to"].add((STATE, RIVER))
type_map["next_to"].add((STATE, STATE))
# population(x1].add((2)
type_map["population"].add((CITY, NUM))
type_map["population"].add((COUNTRY, NUM))
type_map["population"].add((STATE, NUM))
# size(x1].add((x2)
type_map["size"].add((CITY, NUM))
type_map["size"].add((COUNTRY, NUM))
type_map["size"].add((PLACE, NUM))
type_map["size"].add((LAKE, NUM))
type_map["size"].add((MOUNTAIN, NUM))
type_map["size"].add((RIVER, NUM))
type_map["size"].add((STATE, NUM))
# traverse(x1].add((x2)
type_map["traverse"].add((RIVER, CITY))
type_map["traverse"].add((RIVER, COUNTRY))
type_map["traverse"].add((RIVER, STATE))
# largest(x1].add((FORM)
type_map["largest"].add((CITY,))
type_map["largest"].add((PLACE,))
type_map["largest"].add((LAKE,))
type_map["largest"].add((MOUNTAIN,))
type_map["largest"].add((NUM,))
type_map["largest"].add((RIVER,))
type_map["largest"].add((STATE,))
# smallest(x1].add((FORM)
type_map["smallest"].add((CITY,))
type_map["smallest"].add((PLACE,))
type_map["smallest"].add((LAKE,))
type_map["smallest"].add((MOUNTAIN,))
type_map["smallest"].add((NUM,))
type_map["smallest"].add((RIVER,))
type_map["smallest"].add((STATE,))
# highest(x1].add((FORM)
type_map["highest"].add((PLACE,))
type_map["highest"].add((MOUNTAIN,))
# lowest(x1].add((FORM)
type_map["lowest"].add((PLACE,))
type_map["lowest"].add((MOUNTAIN,))
# longest(x1].add((FORM)
type_map["longest"].add((RIVER,))
type_map["shortest"].add((RIVER,))
# count(x1].add((FORM, x2)
type_map["count"].add((CITY, NUM))
type_map["count"].add((PLACE, NUM))
type_map["count"].add((COUNTRY, NUM))
type_map["count"].add((LAKE, NUM))
type_map["count"].add((MOUNTAIN, NUM))
type_map["count"].add((STATE, NUM))
type_map["count"].add((RIVER, NUM))
type_map["count"].add((STATE, NUM))
# sum(x1].add((FORM,x2)
type_map["sum"].add((NUM, NUM))

# most(x1].add((x1,x2, FORM)
# fewest(x1].add((x1,x2, FORM)
for name in ["most", "fewest"]:
    for type_1 in ALL_TYPE:
        for type_2 in ALL_TYPE:
            type_map[name].add((type_1,type_2))

# answer(x1, FORM)
for type in ALL_TYPE:
    type_map["answer"].add((type,))

### The function that we need
def collect_functions(line, ret):
    if "(" not in line:
        return line, ret

    # Parsing the function at this level
    index = line.index ("(")
    function_name = line[:index]
    depth = 1
    end_index = index + 1
    args_index = [index]
    while depth != 0:
        if line[end_index] == '(': 
            depth += 1
        elif line[end_index] == ')': 
            depth -= 1
        if line[end_index] == ',' and depth == 1: 
            args_index.append(end_index)
        end_index += 1
    args_index.append(end_index-1)
  
    # Collect the ARGS
    args = [] 
    for i in range(len(args_index)-1):
        args.append(line[args_index[i]+1:args_index[i+1]].strip())
        
    # The function 
    function_body = line[index:end_index]
    function = (function_name, [], [])
    ret.append(function)

    # Process the childs
    for arg in args:
        if len(arg) == 1 and ord(arg) >= ord('A') and ord(arg) <= ord('Z'):
            function[1].append(arg)
        else:
            function[2].append(collect_functions(arg,ret)[0])
    return function, ret

def sync_print(stream, string):
    lock.acquire()
    print >> stream, string
    lock.release()

def typecheck(line, dump=sys.stderr):
    err_msg = "Checking line: " + line + "\n"
    root, functions = collect_functions(line, [])
    var_map = defaultdict(lambda: set([]))
    for (name,variables,childs) in sorted(functions, key=lambda x: len(x[1])):
        if len(variables) == 0:
            continue
        
        if name == 'const' or name == '\\+const':
            name = name + "_" + childs[0][0]
        elif name not in type_map and name not in type_map:
            raise Exception("Function name is not recognized: " + name)

        for i, var in enumerate(variables):
            if var not in var_map:
                for type in type_map[name]:
                    if i < len(type):
                        var_map[var].add(type[i])
            else:
                var_map[var] = set([type[i] for type in type_map[name] if i < len(type) and type[i] in var_map[var]])
                if len(var_map[var]) == 0:
                    err_msg += str(var_map) + "\n"
                    err_msg += str("[!]!!! NOT OK") +"\n"
                    err_msg += "Variables constraint is not satisfied for variable: " + var + "\n"
                    sync_print(dump, err_msg)
                    return False

    err_msg += "[O]OOO This Line is OK\n"
    for var, l in sorted(var_map.items()):
        err_msg += str(var) + ": " + str(l) + "\n"
    sync_print(dump, err_msg)
    return True

if __name__ == '__main__':
    for line in sys.stdin:
        line = line.strip()
        if typecheck(line.split("\t")[-1]):
            print line

