from functools import partial
import pprint
import sys
import string
import argparse

class InvalidSgfException(Exception):
    pass
uppers = set (string.ascii_uppercase)
def tokenize(file):
    f = iter(partial(file.read,1),"")

    last_char = " "
    while True:
        while last_char.isspace():
            last_char = next(f)
        if last_char in uppers:
            property_id = []
            while last_char in uppers:
                property_id.append(last_char)
                last_char = next(f)
            yield "property_id","".join(property_id)
        elif last_char == "[":
            try:
                last_char = next(f)
                property_value = []
                while last_char != "]":
                    if last_char == "\\":
                        property_value.append(next(f))
                    else:
                        property_value.append(last_char)
                    last_char = next(f)
                yield "property_value","".join(property_value)
            except StopIteration as e:
                #in python 3.3 could use from None
                raise InvalidSgfException("unclosed property value") 
                
            last_char= next(f)
        else:
            
            yield "special",last_char
            last_char = next(f)
from collections import namedtuple
class Node:
    def __init__(self):
        self.properties = []
        self.childs = []
    def __repr__(self):
        return "Node(properties="+repr(self.properties)+",childs="+repr(self.childs)+")"
def tree(tokens):
    def print(*args): pass
    current_node = Node()
    stack=[current_node]
    try:    
        token = next(tokens)
        
        while True:
            
            print ("processing1",token)
            
            if token == ("special", "("):
                print ("found (")
                
                current_node.childs.append(Node())
                current_node = current_node.childs[-1]
                stack.append(current_node)
                token = next(tokens)
                if token != ("special",";"):
                    raise InvalidSgfException("semi-colon expected")
                token = next(tokens)
                
            elif token == ("special", ")"):
                print ("found )")
                if len(stack) <2:
                    raise InvalidSgfInvalidSgfException("unexpected right parenthesis")
                stack.pop()
                current_node = stack[-1]
                token = next(tokens)
            elif token == ("special",";"):
                print ("yielding node")
                current_node.childs.append(Node())
                current_node = current_node.childs[-1]
                
                token = next(tokens)
            else:
                type,value = token
                if type != "property_id":
                    raise InvalidSgfException("unkown token"+repr(token))
                print("testing property_id",token,repr(type))
                while type == "property_id":
                    v=value
                    
                    values = []
                    token = next( tokens)
                    type,value = token
                    
                    print ("consumed",token)
                    while type == "property_value":
                        
                        values.append(value)
                        token = next( tokens)
                        type,value = token
                        print ("testing",token)
                        
                    current_node.properties.append( (v,values))
                    print("next token",token)
            
    except StopIteration:
        if len(stack) != 1:
            raise InvalidSgfException("unclosed right parenthesis")
        return stack.pop()        
whitelist_property = set(
"""GM FF CA RU SZ KM PW PB WR BR DT EV RO PC SO
AB AW AE B W""".split())

def filter_properties(tree):
    
    tree.properties = [(name,values) for name,values in tree.properties    
                       if name in whitelist_property]
    for child in tree.childs:
        filter_properties(child)
def first_variation(tree):
    del tree.childs[1:]
    if tree.childs:
        first_variation(tree.childs[0])
    
def limit(tree,n):
    if n == 0:
        tree.childs = []
    for child in tree.childs:
        limit(child,n-1)

def filter(tree):
    first_variation(tree)
    filter_properties(tree)
    
    
    
def to_sgf(tree):
    return "("+"".join(node_to_sgf(tree))+")"
def node_to_sgf(tree):
    
        
    for name,values in tree.properties:
        yield name
        for value in values:
            yield "["
            yield value.replace("\\","\\\\").replace("]","\\]")
            yield "]"
    
        
    
    for v in tree.childs:
        yield '\n'
        if len(tree.childs) > 1:
            yield "("
    
        yield ";"
        
        for x in node_to_sgf(v):
            yield x
        if len(tree.childs) >1:
            yield ")"
        
    

def reverse(tree,size):
    def r(v):
        return v[0]+string.ascii_letters[size-string.ascii_letters.index(v[1])-1]
    for i,(name,value) in enumerate(tree.properties):
        
        if name in {"AB","AW","AE","B","W"}:
            value[0]=r(value[0])
            
        elif name in {"AR","LN"}:
            value=[":".join(r(coord) for coord in compound.split(":"))
               for compound in v]
        
        elif name in {"CR","DD","MA","SL","SQ","TR"}:
            value=[r(coord) for coord in value]
        
        elif name in {"LB"}:
            def switch(v):
                point,text=v.split(":",1)
                return r(point)+":"+text
            value=[ switch(coord) for coord in value]
        tree.properties[i] = name,value
    for child in tree.childs:
        reverse(child,size)
      

if __name__ == "__main__":
    #test()
    parser = argparse.ArgumentParser(description="Manipulate sgf tree")
    parser.add_argument("--filter", action='store_true',
                        help="filter coments and variation")
    parser.add_argument("--limit", action='store', type=int, default=None,
                        help="limit the variations to max depth")
    parser.add_argument("--reverse",action="store_true",
                        help="reverse the board upside down")
    parser.add_argument("file",action="store")
    args = parser.parse_args()
    new_file = tree(tokenize(open(args.file,encoding="utf-8")))
    
    if args.filter:
        filter(new_file)
    
    if args.limit is not None:
        limit(new_file,args.limit+1)
    
    if args.reverse:
        size = 19
        for name,value in new_file.childs[0].properties:
            if name == "SZ":
                size=int(value[0])
        reverse(new_file,size)
        
    print ("".join(to_sgf(new_file)),
           file=open("new-"+args.file,"w",encoding="utf-8"))

