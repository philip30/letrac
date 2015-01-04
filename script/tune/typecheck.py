#!/usr/bin/env python

import sys
from collections import defaultdict

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
type_map1 = defaultdict(lambda:set([]))
type_map2 = defaultdict(lambda:set([]))
type_map1["const_cityid"].add(CITY)
type_map1["const_countryid"].add(COUNTRY)
type_map1["const_placeid"].add(PLACE)
type_map1["const_placeid"].add(LAKE)
type_map1["const_placeid"].add(MOUNTAIN)
type_map1["const_riverid"].add(RIVER)
type_map1["const_stateid"].add(STATE)
type_map1["capital"].add((CITY))
type_map1["capital"].add((PLACE))
# city(x1)
type_map1["city"].add((CITY))
# country(x1)
type_map1["country"].add((COUNTRY))
# lake(x1)
type_map1["lake"].add((PLACE))
type_map1["lake"].add((LAKE))
# major(x1)
type_map1["major"].add((CITY))
type_map1["major"].add((LAKE))
type_map1["major"].add((RIVER))
# mountain(x1)
type_map1["mountain"].add((MOUNTAIN))
type_map1["mountain"].add((PLACE))
# place(x1)
type_map1["place"].add((PLACE))
type_map1["place"].add((LAKE))
type_map1["place"].add((MOUNTAIN))
# river(x1)
type_map1["river"].add((RIVER))
# state(x1)
type_map1["state"].add((STATE))
# elevation(x1,NUM)
type_map1["elevation"].add((PLACE))
type_map1["elevation"].add((MOUNTAIN))
# area(x1].add((x2)
type_map2["area"].add((CITY, NUM))
type_map2["area"].add((COUNTRY, NUM))
type_map2["area"].add((STATE, NUM))
# capital(x1].add((x2)
type_map2["capital"].add((STATE, CITY))
# density(x1].add((x2)
type_map2["density"].add((CITY, NUM))
type_map2["density"].add((COUNTRY, NUM))
type_map2["density"].add((STATE, NUM))
# elevation(x1].add((x2)
type_map2["elevation"].add((PLACE, NUM))
type_map2["elevation"].add((MOUNTAIN, NUM))
# high_point(x1].add((x2)
type_map2["high_point"].add((COUNTRY,PLACE))
type_map2["high_point"].add((COUNTRY,MOUNTAIN))
type_map2["high_point"].add((STATE,PLACE))
type_map2["high_point"].add((STATE,MOUNTAIN))
# higher(x1].add((x2)
type_map2["higher"].add((PLACE,PLACE))
type_map2["higher"].add((PLACE,MOUNTAIN))
type_map2["higher"].add((MOUNTAIN,PLACE))
type_map2["higher"].add((MOUNTAIN,MOUNTAIN))
# len(x1].add((x2)
type_map2["len"].add((RIVER, NUM))
# loc(x1].add((x2)
type_map2["loc"].add((CITY,COUNTRY))
type_map2["loc"].add((PLACE,COUNTRY))
type_map2["loc"].add((LAKE,COUNTRY))
type_map2["loc"].add((MOUNTAIN,COUNTRY))
type_map2["loc"].add((RIVER,COUNTRY))
type_map2["loc"].add((STATE,COUNTRY))
type_map2["loc"].add((CITY,STATE))
type_map2["loc"].add((PLACE,STATE))
type_map2["loc"].add((LAKE,STATE))
type_map2["loc"].add((MOUNTAIN,STATE))
type_map2["loc"].add((RIVER,STATE))
type_map2["loc"].add((PLACE,CITY))
# longer(x1].add((x2)
type_map2["longer"].add((RIVER,RIVER))
# low_point(x1].add((x2)
type_map2["low_point"].add((COUNTRY,PLACE))
type_map2["low_point"].add((COUNTRY,MOUNTAIN))
type_map2["low_point"].add((STATE,PLACE))
type_map2["low_point"].add((STATE,MOUNTAIN))
# lower(x1].add((x2)
type_map2["lower"].add((PLACE, PLACE))
type_map2["lower"].add((COUNTRY, MOUNTAIN))
type_map2["lower"].add((MOUNTAIN, PLACE))
type_map2["lower"].add((MOUNTAIN, MOUNTAIN))
# next_to(x1].add((x2)
type_map2["next_to"].add((STATE, RIVER))
type_map2["next_to"].add((STATE, STATE))
# population(x1].add((2)
type_map2["population"].add((CITY, NUM))
type_map2["population"].add((COUNTRY, NUM))
type_map2["population"].add((STATE, NUM))
# size(x1].add((x2)
type_map2["size"].add((CITY, NUM))
type_map2["size"].add((COUNTRY, NUM))
type_map2["size"].add((PLACE, NUM))
type_map2["size"].add((LAKE, NUM))
type_map2["size"].add((MOUNTAIN, NUM))
type_map2["size"].add((RIVER, NUM))
type_map2["size"].add((STATE, NUM))
# traverse(x1].add((x2)
type_map2["traverse"].add((RIVER, CITY))
type_map2["traverse"].add((RIVER, COUNTRY))
type_map2["traverse"].add((RIVER, STATE))
# largest(x1].add((FORM)
type_map1["largest"].add((CITY))
type_map1["largest"].add((PLACE))
type_map1["largest"].add((LAKE))
type_map1["largest"].add((MOUNTAIN))
type_map1["largest"].add((NUM))
type_map1["largest"].add((RIVER))
type_map1["largest"].add((STATE))
# smallest(x1].add((FORM)
type_map1["smallest"].add((CITY))
type_map1["smallest"].add((PLACE))
type_map1["smallest"].add((LAKE))
type_map1["smallest"].add((MOUNTAIN))
type_map1["smallest"].add((NUM))
type_map1["smallest"].add((RIVER))
type_map1["smallest"].add((STATE))
# highest(x1].add((FORM)
type_map1["highest"].add((PLACE))
type_map1["highest"].add((MOUNTAIN))
# lowest(x1].add((FORM)
type_map1["lowest"].add((PLACE))
type_map1["lowest"].add((MOUNTAIN))
# longest(x1].add((FORM)
type_map1["longest"].add((RIVER))
type_map1["shortest"].add((RIVER))
# count(x1].add((FORM, x2)
type_map2["count"].add((CITY, NUM))
type_map2["count"].add((PLACE, NUM))
type_map2["count"].add((COUNTRY, NUM))
type_map2["count"].add((LAKE, NUM))
type_map2["count"].add((MOUNTAIN, NUM))
type_map2["count"].add((STATE, NUM))
type_map2["count"].add((RIVER, NUM))
type_map2["count"].add((STATE, NUM))
# sum(x1].add((FORM,x2)
type_map2["sum"].add((NUM, NUM))

# most(x1].add((x1,x2, FORM)
# fewest(x1].add((x1,x2, FORM)
for name in ["most", "fewest"]:
    for type_1 in ALL_TYPE:
        for type_2 in ALL_TYPE:
            type_map2[name].add((type_1,type_2))

# answer(x1, FORM)
for type in ALL_TYPE:
    type_map1["answer"].add(type)

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

def not_ok(message, var_map, dump):
    print >> dump, var_map
    print >> dump, "[!]!!! NOT OK"
    return False

def typecheck(line, dump=sys.stderr):
    print >> dump, "Checking line: " + line
    root, functions = collect_functions(line, [])
    var_map = defaultdict(lambda: set([]))
    for (name,variables,childs) in sorted(functions, key=lambda x: len(x[1])):
        if len(variables) == 0:
            continue
        
        if name == 'const':
            name = name + "_" + childs[0][0]
        elif name not in type_map1 and name not in type_map2:
            raise Exception("Function name is not recognized: " + name)
        if len(variables) == 1:
            if variables[0] not in var_map:
                for type in type_map1[name]:
                    var_map[variables[0]].add(type)
            else:
                result = set([type for type in type_map1[name] if type in var_map[variables[0]]])
                if len(result) == 0:
                    return not_ok("Trying to insert " + variables[0] + " into " + name + "(" + str(type_map1[name]) + ") but found conflict.", var_map, dump)
                else:
                    var_map[variables[0]] = result
        elif len(variables) == 2:
            if variables[0] not in var_map and variables[1] not in var_map:
                return not_ok("Ambiguous type for function %s(%s,%s)" % (name, variables[0], variables[1]), var_map, dump)
            elif variables[0] not in var_map:
                for (x1,x2) in type_map2[name]:
                    if (x2 in var_map[variables[1]]):
                        var_map[variables[0]].add(x1)
                if variables[0] not in var_map:
                    return not_ok("Constraint is not satisfied for function %s(%s,%s)" % (name, variables[0], variables[1]), var_map, dump)
            elif variables[1] not in var_map:
                for (x1,x2) in type_map2[name]:
                    if (x1 in var_map[variables[0]]):
                        var_map[variables[1]].add(x2)
                if variables[1] not in var_map:
                    return not_ok("Constraint is not satisfied for function %s(%s,%s)" % (name, variables[0], variables[1]), var_map, dump)
            elif not any(x1 in var_map[variables[0]] and x2 in var_map[variables[1]] for (x1,x2) in type_map2[name]):
                return not_ok("Constraint is not satisfied for function %s(%s,%s)" % (name, variables[0], variables[1]), var_map, dump)
        else:
            raise Exception("Unprocessable line: " + line)
    print >> dump, "[O]OOO This Line is OK"
    return True

if __name__ == '__main__':
    for line in sys.stdin:
        line = line.strip()
        if typecheck(line.split("\t")[-1]):
            print line

