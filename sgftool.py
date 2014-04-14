from functools import partial
import pprint
import sys
import string
import argparse

class InvalidSgfException(Exception):
    pass
    
    
uppers = set (string.ascii_uppercase)

def tokenize(file):

    """generator which output tokens consumed by tree
    
    in a well formed sgf should be one of the following 
    ("special","(")
    ("special",")")
    ("special",";")
    ("property_name","XX")
    ("property_value","xx")
    
    """
    f = iter(partial(file.read,1),"")

    last_char = " "
    while True:
        while last_char.isspace():
            last_char = next(f)
        if last_char in uppers:
            property_name = []
            while last_char in uppers:
                property_name.append(last_char)
                last_char = next(f)
            yield "property_name","".join(property_name)
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
                
                raise InvalidSgfException("unclosed property value") from None
                
            last_char= next(f)
        else:
            
            yield "special",last_char
            last_char = next(f)

class Node:

    """represent a node in the game tree"""
    
    def __init__(self):
        self.properties = []
        self.childs = []

def tree(tokens):

    """generate a tree of game node, input is the output of tokenize"""
    
    #to remove the debug print
    def log(*args): pass

    current_node = Node()
    stack=[current_node]
    try:    
        token = next(tokens)
        
        while True:
            
            log("processing1",token)
            
            if token == ("special", "("):
                log("found (")
                
                current_node.childs.append(Node())
                current_node = current_node.childs[-1]
                stack.append(current_node)
                token = next(tokens)
                if token != ("special",";"):
                    raise InvalidSgfException("semi-colon expected")
                token = next(tokens)
                
            elif token == ("special", ")"):
                log ("found )")
                if len(stack) <2:
                    raise InvalidSgfException("unexpected right parenthesis")
                stack.pop()
                current_node = stack[-1]
                token = next(tokens)
            elif token == ("special",";"):
                log("yielding node")
                current_node.childs.append(Node())
                current_node = current_node.childs[-1]
                
                token = next(tokens)
            else:
                type,value = token
                if type != "property_name":
                    raise InvalidSgfException("unkown token"+repr(token))
                log("testing property_name",token,repr(type))
                while type == "property_name":
                    v=value
                    
                    values = []
                    token = next( tokens)
                    type,value = token
                    
                    log ("consumed",token)
                    while type == "property_value":
                        
                        values.append(value)
                        token = next( tokens)
                        type,value = token
                        log ("testing",token)
                        
                    current_node.properties.append( (v,values))
                    log("next token",token)
            
    except StopIteration:
        if len(stack) != 1:
            raise InvalidSgfException("unclosed right parenthesis") from None
        return stack.pop()        

#whitelist of properties not filtered out by filter_properties
whitelist_property = set(
"""GM FF CA RU SZ KM PW PB WR BR DT EV RO PC SO HA
AB AW AE B W""".split())

def filter_properties(tree):
    """ filter out the properties not white listed
    to keep only the move played
    modify the tree"""
    tree.properties = [(name,values) for name,values in tree.properties    
                       if name in whitelist_property]
    for child in tree.childs:
        filter_properties(child)
        
def first_variation(tree):
    """skip all the auxiliary variations
    modify the tree"""
    
    del tree.childs[1:]
    if tree.childs:
        first_variation(tree.childs[0])
    
def limit(tree,depth):
    """limit the variations to depth"""
    
    if depth<1:ValueError("limit should be strictlypositive")
    #n+1 because the root is counted 
    if depth+1 == 0:
        tree.childs = []
    for child in tree.childs:
        limit(child,depth-1)

def filter(tree):
    """filter variation and comments and notation on the board
    modify the tree"""
    first_variation(tree)
    filter_properties(tree)
    
    
    
def to_sgf(tree):
    """convert tree to sgf"""
    
    return "("+"".join(node_to_sgf(tree))+")"
def node_to_sgf(tree):
    """convert a node of the tree to sgf"""
        
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
        
    

def reverse(tree):
    """reverse all the coords in the tree
    modify the tree"""
    size = 19
    for name,value in tree.childs[0].properties:
        if name == "SZ":
            size=int(value[0])
    do_reverse(tree, size)
    
def do_reverse(tree,size):
    
    """reverse all the coords in the tree
    modify the tree"""
    def r(v):
        try:
            index = string.ascii_letters.index(v[1])
            if not 0 <= index < size:
                raise InvalidSgfException("invalid coordinate "+v)
            return v[0]+string.ascii_letters[size - index - 1]
        except ValueError:
            raise InvalidSgfException("invalid coordinate "+v)
    for i,(name,value) in enumerate(tree.properties):
        
        if name in {"B","W"}:
            value[0]=r(value[0])
            
        elif name in {"AR","LN"}: #pragma: no cover
            value=[":".join(r(coord) for coord in compound.split(":"))
               for compound in v]
        
        elif name in {"AB","AW","AE","CR","DD","MA","SL","SQ","TR"}:
            value=[r(coord) for coord in value]
        
        elif name in {"LB"}:
            def switch(v):
                point,text=v.split(":",1)
                return r(point)+":"+text
            value=[ switch(coord) for coord in value]
        tree.properties[i] = name,value
    for child in tree.childs:
        do_reverse(child,size)
      

if __name__ == "__main__":
    #test()
    parser = argparse.ArgumentParser(description="Manipulate sgf tree")
    parser.add_argument("--filter", action='store_true',
                        help="filter coments and variation")
    parser.add_argument("--limit", action='store', type=int, default=None,
                        help="limit the variations to LIMIT depth")
    parser.add_argument("--reverse",action="store_true",
                        help="reverse the board upside down")
    parser.add_argument("file",action="store")
    args = parser.parse_args()
    new_file = tree(tokenize(open(args.file,encoding="utf-8")))
    
    if args.filter:
        filter(new_file)
    
    if args.limit is not None:
        limit(new_file,args.limit)
    
    if args.reverse:
        
        reverse(new_file)
        
    print (to_sgf(new_file),
           file=open("new-"+args.file,"w",encoding="utf-8"))

