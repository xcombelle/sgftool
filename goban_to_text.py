import sys
import glob
import os.path
import json
import re
import string

import search
import sgftool
import sgfparsing
import copy

class InvalidSgfException(Exception):
    pass
class InternalError(Exception):
    pass

def sgf_to_xy(position):
    
    x,y = [string.ascii_letters.index(p) for p in position if p.strip()!=""]
    return x,y
    
def has_liberties(goban, size, x, y, color):
    assert goban[x][y] == color
    for (a,b) in go_string(goban, size, x, y, color):
        for da,db in [(-1,0), (1,0), (0,-1), (0,1)]:
            aa,bb= a+da, b+db
            if not (0<=aa and aa<size and 0<=bb and bb<size):
                continue
            if goban[aa][bb]=="-":
                return True
    return False

def go_string(goban, size, x, y, color):
    visited = set()
    result = []
    reccurent_go_string(goban, size, x, y, color, visited, result)
    return result

def reccurent_go_string(goban, size, x, y, color, visited,result):
    if (x,y) in visited:
        return
    visited.add((x,y))
    if not (0<=x and x<size and 0<=y and y<size): 
        return 
    if goban[x][y] == color:
        result.append((x,y))
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            reccurent_go_string(goban, size, x+dx, y+dy, color, visited, result)
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
                goban[a][b]="-" 

    #in case suicide allowed
    if has_liberties(goban, size, x, y, color):
        return

    for a,b in go_string(goban, size, x, y, color):  
        goban[a][b]="-" 
            

def goban_to_string(goban, size):
    result=[]
    for x in range(-1,size+1):
        for y in range(-1, size+1):
            if  -1==x or x==size or y==-1 or y==size:
                result.append('Z')
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
        goban = [["-" for i in range(size)] for i in range(size)] 
    goban= copy.deepcopy(goban)
    for property, values in tree.properties:

        if property in ["AW", "W"]:
            for p in values:
                if p=='':continue
                x,y = sgf_to_xy(p)
                goban[x][y]="O"
                remove_dead_stone(goban,size,x,y,"O")
        if property in ["AB", "B"]:
            for p in values:
                if p=='':continue
                x,y = sgf_to_xy(p)
                goban[x][y]="X"
                remove_dead_stone(goban,size,x,y,"X")
        if property == "AE":
            for p in values:
                if p=='':continue
                x,y = sgf_to_xy(p)
                goban[x][y] = "-"
                # no need to check for capture after placing empty stone

    result.append(goban_to_string(copy.deepcopy(goban),size))


    for child in tree.children:
        tree_to_positions(child,copy.deepcopy(goban),size, result,depth +1)
    return result

