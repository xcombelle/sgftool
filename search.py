#!/usr/bin/env python3
import json
import re 
import sys

class DecompressionError(Exception):
    pass

def decompress(zfile):
    result= []
    for i,line in enumerate(zfile.splitlines()):
        if i ==0:
            if line.strip()!="Zgo v0":
                raise DecompressionError("compressed file altered (1)")
        elif i == 1:
             result.append(line)
        else:
            previous = result[-1] 
            temp = list(previous)
            for change in line.split("|"):
                n,a,b = change.split()
                n = int(n)
                if temp[n]!=a:
                    raise DecompressionError("compressed file altered (2)")

                temp[n]=b
            result.append("".join(temp))
    return "\n".join(result)

 
def switch_color(point_list, size):
    result = []  
    for x,y,color in point_list:
        match color:
           case 'X': color = 'O'
           case 'O': color = 'X'
        result.append((x,y,color))
    return result

def apply(function, size, point_list):
    result = []
    for x,y,colors in point_list:
        x,y=function(size,x,y)
        result.append((x,y,colors))
    return result

def mirror(size,x,y):
    return (size-1-x,y)

def rotate_1_4(size,x,y):
    return (size-1-y, x)


def symetries_and_colors(points_list, size, symmetries= True, color_exact = False):
    result=[points_list]
    
    if not color_exact:
        result.append(switch_color(points_list, size))

    if symmetries == True:

        # if we did 
        # for p in result:
        #     result.append(apply( _f_ , size, p))
        # it would extend result while iterating on it 
        # and eventually run out of memory while iterating an infinite loop

        temp = result[:]
        for p in temp:
            result.append(apply(mirror, size, p))
        
        temp = result[:]
        for p in temp:
            r1 = apply(rotate_1_4, size, p)
            result.append(r1)
            r2 = apply(rotate_1_4, size, r1)
            result.append(r2)
            result.append(apply(rotate_1_4, size, r2))
    return result

def position_regexp(points_list, size):

    min_x = min([x for x,y,colors in points_list])
    max_x = max([x for x,y,colors in points_list])
    min_y = min([y for x,y,colors in points_list])
    max_y = max([y for x,y,colors in points_list])
    d = dict([
            ((x,y),colors) 
            for x,y, colors 
            in points_list
        ])
    temp = []

    for y in range(0,size):
        line = ''
        for x in range(0,size):
            if y < min_y:
                continue
            elif y == min_y and x<min_x:
                continue
            elif y > max_y:
                continue
            elif y == max_y and x> max_x:
                continue
            line+=(d.get((x,y)," . "))
        line+="\n"
        temp.append(line)
    return "".join(temp)

def create_regexp(pattern):
    return "|".join([position_regexp(point_list, pattern["size"]) 
                     for point_list 
                     in symetries_and_colors(
                            pattern["point_list"], 
                            pattern["size"], 
                            pattern["symetries"], 
                            pattern["color_exact"])])


def cmd_search(json_position):
    position = json.loads(json_position)

    pattern = create_regexp(position)
    #print(pattern)
    regexp = re.compile(pattern, re.VERBOSE|re.DOTALL)
    for file_name in sys.stdin:
        if regexp.search(decompress(open(file_name.strip()).read())):
            print(file_name.strip())
        #else:
        #    print("pas trouvé", file_name, position["size"])


def main(argv):
    cmd_search(argv[1])

   
if __name__ == "__main__":
    main(sys.argv)

    
