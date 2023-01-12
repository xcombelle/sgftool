import sgftool
import sgfparsing
from copy import deepcopy
import string

DEBUG = True

def dbg(*args):
    if DEBUG:
        print(*args)
    return args[-1]

class InvalidSgfException(Exception):
    pass
class InternalError(Exception):
    pass
class DecompressionError(Exception):
    pass
def sgf_to_xy(position):
    x,y = [string.ascii_letters.index(p) for p in position]
    return x,y


def has_liberties(goban, size, x, y, color):
    assert goban[x][y] == color
    for (a,b) in go_string(goban, size, x, y, color):
        for da,db in [(-1,0), (1,0), (0,-1), (0,1)]:
            aa,bb= a+da, b+db
            if not (0<=aa and aa<size and 0<=bb and bb<size):
                continue
            if goban[aa][bb]=="'":
                return True
    return False
def go_string(goban, size, x, y, color):
    visited = set()
    result = []
    _go_string(goban, size, x, y, color, visited, result)
    return result

def _go_string(goban, size, x, y, color, visited,result):
    if (x,y) in visited:
        return
    visited.add((x,y))
    if not (0<=x and x<size and 0<=y and y<size): 
        return 
    if goban[x][y] == color:
        result.append((x,y))
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            _go_string(goban, size, x+dx, y+dy, color, visited, result)
    return

def remove_dead_stone(goban, size, x, y, color):

    global DD
    if color == 'X':
        opponent_color ='O'
    elif color == 'O':
        opponent_color = 'X'
    else:
        raise InternalError(f"bad color  {color=}")
    
    for dx,dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        xx,yy = x+dx, y+dy
        if not( 0<=xx and xx<size and 0<=yy and yy<size):
            continue
        if goban[xx][yy]==opponent_color:

            if has_liberties(goban, size, xx, yy, opponent_color):
                continue
            for a,b in go_string(goban, size, xx, yy, opponent_color):  
                goban[a][b]="'" 

    #in case suicide allowed
    if has_liberties(goban, size, x, y, color):
        return

    for a,b in go_string(goban, size, x, y, color):  
        goban[a][b]="'" 
            

def goban_to_string(goban, size):
    result=[]
    for x in range(-1,size+1):
        for y in range(-1, size+1):
            if not (0<=x and x<size and 0<=y and y<size):
                result.append('#')
            else:
                result.append(goban[x][y])
    return "".join(result)

def tree_to_positions(tree, goban=None, size=19, result=None,depth=0):
    """ size is by default 19 """
    if result == None:
        result=[]
    if goban is None:
        for property, values in tree.properties:
            if "SZ" == property:
                size, *rest = values
                if len(rest) != 0:
                    raise InvalidSgfException(f'Several size specified {values=}')
        goban = [["'" for i in range(size)] for i in range(size)] 
    goban= deepcopy(goban)
    for property, values in tree.properties:

        if property in ["AW", "W"]:
            for p in values:
                x,y = sgf_to_xy(p)
                goban[x][y]="O"
                remove_dead_stone(goban,size,x,y,"O")
        if property in ["AB", "B"]:
            for p in values:
                x,y = sgf_to_xy(p)
                goban[x][y]="X"
                remove_dead_stone(goban,size,x,y,"X")
        if property == "AE":
            for p in values:
                x,y = sgf_to_xy(p)
                goban[x][y] = "'"
                # no need to check for capture after placing empty stone

    result.append(goban_to_string(deepcopy(goban),size))

#    for i in range(size):
#        for j in range(size):
#            if goban[i][j] in 'XO':
#                assert has_liberties(goban, size, i, j, goban[i][j])

    for child in tree.children:
        tree_to_positions(child,deepcopy(goban),size, result,depth +1)
    return result


def generate_positions(input_file_name):

    tree = sgfparsing.tree(sgfparsing.tokenize(open(input_file_name,
                                                        encoding="utf-8")))
    sgftool.filter_properties(tree, whitelist_property= set("SZ HA AB AW AE B W".split()))
    

    return "\n".join(tree_to_positions(tree))

def compress(positions):
    positions = positions.split("\n")
    result= ["Zgo v0"]
    previous = None
    for position in positions:
        if previous is None:
            result.append(position)
        else:
            cur = []
            for i,(a,b) in enumerate(zip(previous, position)):
                if a!=b:
                    cur.append(" ".join([str(i),a,b]))
            if len(cur) >0:
                result.append(" | ".join(cur))
        previous = position
    return "\n".join(result)
    
def decompress(zfile):
    result= []
    for i,line in enumerate(zfile.splitlines()):
        if i ==0:
            if line.strip()!="Zgo v0":
                raise DecompressionError("compressed file altered")
                
        elif i == 1:
             result.append(line)
        else:
            previous = result[-1] 
            temp = list(previous)
            for change in line.split("|"):
                n,a,b = change.split()
                n = int(n)
                if temp[n]!=a:
                    raise DecompressionError("compressed file altered")

                temp[n]=b
            result.append("".join(temp))
    return "\n".join(result)

 
def switch_color(point_list, size):
    result - []  
    for x,y,color in point_list:
        match color:
            case 'X': color = 'O'
            case 'O': color = 'X'
        result.append(x,y,color)
    return result

def apply_symetry(function, size, point_list):
    result= []
    for x,y,color in point_list:
        x,y=function(size,x,y)
        result.append(x,y,color)
    return result

def miror(size,x,y):
    return (size-x,y)



def rotate_1_4(size,x,y):
    return (size-y, x)


def symetries_and_colors(points_list, size, symetries= True, color_exact = False):
    results=[points_list]
    
    if not color_exact:
        results.append(switch_color(points_list, size))

    if symetries == True:
        pass




import sys
def main():

    (decompress(dbg(compress((generate_positions( sys.argv[1]))))))
    
if __name__ == "__main__":
    main()

    
