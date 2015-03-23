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

ALL_TYPE=[CITY,PLACE,COUNTRY,LAKE,MOUNTAIN,STATE,NUM,RIVER]

### TYPE MAP
type_map = defaultdict(lambda:set([]))
type_map["const_cityid_1"].add((CITY,))
type_map["const_countryid_1"].add((COUNTRY,))
type_map["const_placeid_1"].add((PLACE,))
type_map["const_placeid_1"].add((LAKE,))
type_map["const_placeid_1"].add((MOUNTAIN,))
type_map["const_riverid_1"].add((RIVER,))
type_map["const_stateid_1"].add((STATE,))
type_map["capital_1"].add((CITY,))
type_map["capital_1"].add((PLACE,))
# city(x1)
type_map["city_1"].add((CITY,))
# country(x1)
type_map["country_1"].add((COUNTRY,))
# lake(x1)
type_map["lake_1"].add((PLACE,))
type_map["lake_1"].add((LAKE,))
# major(x1)
type_map["major_1"].add((CITY,))
type_map["major_1"].add((LAKE,))
type_map["major_1"].add((RIVER,))
# mountain(x1)
type_map["mountain_1"].add((MOUNTAIN,))
type_map["mountain_1"].add((PLACE,))
# place(x1)
type_map["place_1"].add((PLACE,))
type_map["place_1"].add((LAKE,))
type_map["place_1"].add((MOUNTAIN,))
# river(x1)
type_map["river_1"].add((RIVER,))
# state(x1)
type_map["state_1"].add((STATE,))
# area(x1].add((x2)
type_map["area_2"].add((CITY, NUM))
type_map["area_2"].add((COUNTRY, NUM))
type_map["area_2"].add((STATE, NUM))
# capital(x1].add((x2)
type_map["capital_2"].add((STATE, CITY))
# density(x1].add((x2)
type_map["density_2"].add((CITY, NUM))
type_map["density_2"].add((COUNTRY, NUM))
type_map["density_2"].add((STATE, NUM))
# elevation(x1].add((x2)
type_map["elevation_2"].add((PLACE, NUM))
type_map["elevation_2"].add((MOUNTAIN, NUM))
# high_point(x1].add((x2)
type_map["high_point_2"].add((COUNTRY,PLACE))
type_map["high_point_2"].add((COUNTRY,MOUNTAIN))
type_map["high_point_2"].add((STATE,PLACE))
type_map["high_point_2"].add((STATE,MOUNTAIN))
# higher(x1].add((x2)
type_map["higher_2"].add((PLACE,PLACE))
type_map["higher_2"].add((PLACE,MOUNTAIN))
type_map["higher_2"].add((MOUNTAIN,PLACE))
type_map["higher_2"].add((MOUNTAIN,MOUNTAIN))
# len(x1].add((x2)
type_map["len_2"].add((RIVER, NUM))
# loc(x1].add((x2)
type_map["loc_2"].add((CITY,COUNTRY))
type_map["loc_2"].add((PLACE,COUNTRY))
type_map["loc_2"].add((LAKE,COUNTRY))
type_map["loc_2"].add((MOUNTAIN,COUNTRY))
type_map["loc_2"].add((RIVER,COUNTRY))
type_map["loc_2"].add((STATE,COUNTRY))
type_map["loc_2"].add((CITY,STATE))
type_map["loc_2"].add((PLACE,STATE))
type_map["loc_2"].add((LAKE,STATE))
type_map["loc_2"].add((MOUNTAIN,STATE))
type_map["loc_2"].add((RIVER,STATE))
type_map["loc_2"].add((PLACE,CITY))
# longer(x1].add((x2)
type_map["longer_2"].add((RIVER,RIVER))
# low_point(x1].add((x2)
type_map["low_point_2"].add((COUNTRY,PLACE))
type_map["low_point_2"].add((COUNTRY,MOUNTAIN))
type_map["low_point_2"].add((STATE,PLACE))
type_map["low_point_2"].add((STATE,MOUNTAIN))
# lower(x1].add((x2)
type_map["lower_2"].add((PLACE, PLACE))
type_map["lower_2"].add((COUNTRY, MOUNTAIN))
type_map["lower_2"].add((MOUNTAIN, PLACE))
type_map["lower_2"].add((MOUNTAIN, MOUNTAIN))
# next_to(x1].add((x2)
type_map["next_to_2"].add((STATE, RIVER))
type_map["next_to_2"].add((STATE, STATE))
# population(x1].add((2)
type_map["population_2"].add((CITY, NUM))
type_map["population_2"].add((COUNTRY, NUM))
type_map["population_2"].add((STATE, NUM))
# size(x1].add((x2)
type_map["size_2"].add((CITY, NUM))
type_map["size_2"].add((COUNTRY, NUM))
type_map["size_2"].add((PLACE, NUM))
type_map["size_2"].add((LAKE, NUM))
type_map["size_2"].add((MOUNTAIN, NUM))
type_map["size_2"].add((RIVER, NUM))
type_map["size_2"].add((STATE, NUM))
# traverse(x1].add((x2)
type_map["traverse_2"].add((RIVER, CITY))
type_map["traverse_2"].add((RIVER, COUNTRY))
type_map["traverse_2"].add((RIVER, STATE))
# largest(x1].add((FORM)
type_map["largest_1"].add((CITY,))
type_map["largest_1"].add((PLACE,))
type_map["largest_1"].add((LAKE,))
type_map["largest_1"].add((MOUNTAIN,))
type_map["largest_1"].add((NUM,))
type_map["largest_1"].add((RIVER,))
type_map["largest_1"].add((STATE,))
# smallest(x1].add((FORM)
type_map["smallest_1"].add((CITY,))
type_map["smallest_1"].add((PLACE,))
type_map["smallest_1"].add((LAKE,))
type_map["smallest_1"].add((MOUNTAIN,))
type_map["smallest_1"].add((NUM,))
type_map["smallest_1"].add((RIVER,))
type_map["smallest_1"].add((STATE,))
# highest(x1].add((FORM)
type_map["highest_1"].add((PLACE,))
type_map["highest_1"].add((MOUNTAIN,))
# lowest(x1].add((FORM)
type_map["lowest_1"].add((PLACE,))
type_map["lowest_1"].add((MOUNTAIN,))
# longest(x1].add((FORM)
type_map["longest_1"].add((RIVER,))
type_map["shortest_1"].add((RIVER,))
# count(x1].add((FORM, x2)
type_map["count_2"].add((CITY, NUM))
type_map["count_2"].add((PLACE, NUM))
type_map["count_2"].add((COUNTRY, NUM))
type_map["count_2"].add((LAKE, NUM))
type_map["count_2"].add((MOUNTAIN, NUM))
type_map["count_2"].add((STATE, NUM))
type_map["count_2"].add((RIVER, NUM))
type_map["count_2"].add((STATE, NUM))
# sum(x1].add((FORM,x2)
type_map["sum_2"].add((NUM, NUM))

# most(x1].add((x1,x2, FORM)
# fewest(x1].add((x1,x2, FORM)
for name in ["most_2", "fewest_2"]:
    for type_1 in ALL_TYPE:
        for type_2 in ALL_TYPE:
            type_map[name].add((type_1,type_2))

# answer(x1, FORM)
for type in ALL_TYPE:
    type_map["answer_1"].add((type,))

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

def is_singular(var):
    if var == set([MOUNTAIN,PLACE]) or \
            var == set([LAKE,PLACE]) or \
            var == set([MOUNTAIN,PLACE,LAKE]):
        return True
    else:
        return len(var) == 1


def typecheck(line, dump=sys.stderr):
    err_msg = "Checking line: " + line + "\n"
    root, functions = collect_functions(line, [])
    var_map = defaultdict(lambda: set([]))
    singular = set()
    
    is_OK= True
    for (name,variables,childs) in sorted(functions, key=lambda x: len(x[1])):
        if len(variables) == 0:
            continue
        if name == 'const' or name == '\\+const':
            if name == '\\+const':
                name = "const"
            name = name + "_" + childs[0][0]
        
        name += "_%d" % (len(variables))
        if name not in type_map:
            err_msg += "Unrecognized name: " + name +"\n"
            is_OK = False
        
        if not is_OK:
            break

        if len(variables) == 2:
            singular.add(tuple(variables))
        
        for i, var in enumerate(variables):
            if var not in var_map:
                for type in type_map[name]:
                    if i < len(type):
                        var_map[var].add(type[i])
            else:
                var_map[var] = set([type[i] for type in type_map[name] if i < len(type) and type[i] in var_map[var]])
                if len(var_map[var]) == 0:
                    err_msg += "Variables constraint is not satisfied for variable: " + var + ", failed when assessing function %s \n" % (name)
                    is_OK = False
                    break
    
    # Check for singularity
#    if is_OK:
#        for variables in singular:
#            if not any([is_singular(var_map[var]) for var in variables]):
#                err_msg += "Variables %s should be singular" % (str(var)) + "\n"
#                is_OK = False

    # check OK OR NOT
    if is_OK:
        for var, l in sorted(var_map.items()):
            err_msg += str(var) + ": " + str(l) + "\n"
        err_msg += "[O]OOO This Line is OK\n"
    else:
        err_msg += str(dict(var_map)) + "\n"
        err_msg += str("[!]!!! NOT OK") +"\n"
    
    sync_print(dump, err_msg)
    return is_OK

if __name__ == '__main__':
    total = 0
    printed = 0
    for line in sys.stdin:
        line = line.strip()
        if typecheck(line.split("\t")[-1]):
            printed += 1
            print line
        total += 1
    print >> sys.stderr, "Typecheck: (%d/%d) = %f" % (printed, total, float(printed)/total)

