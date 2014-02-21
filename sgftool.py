from functools import partial
import pprint
import sys
import string
import argparse
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
            last_char = next(f)
            property_value = []
            while last_char != "]":
                if last_char == "\\":
                    property_value.append(next(f))
                else:
                    property_value.append(last_char)
                last_char = next(f)
            yield "property_value","".join(property_value)
            last_char= next(f)
        else:
            
            yield "special",last_char
            last_char = next(f)
def tree(tokens):
    def print(*args): pass
    token = next(tokens)
    
    while True:
        
        print ("processing1",token)
        
        if token == ("special", "("):
            print ("found (")
            v = "variation",list(tree(tokens))
            yield v
            token = next(tokens)
        
        elif token == ("special", ")"):
            print ("found )")
            return
        
        elif token == ("special",";"):
            print ("yielding node")
            token = next(tokens)
            type,value = token
            node = []
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
                    
                node.append( ("property",(v,values)))
                print("adding to node",node)
                print("next token",token)
                print ("yielding node",node)
            yield "node",node
whitelist_property = set(
"""GM FF CA RU SZ KM PW PB WR BR DT EV RO PC SO
AB AW AE B W""".split())

def filter_properties(tree):
    for type,value in tree:
        if type == "property":
            if value[0] in whitelist_property:
                yield type,value
        else:
            yield type,list(filter_properties(value))
          
def cut_to_first_variation(tree):
    
    for type, value in tree:
        if type == "variation":
            for v in cut_to_first_variation(value):
                yield v
            break
        elif type == "node":
            yield type, list(cut_to_first_variation(value))
        elif type == "property":
            yield type,value
        else: 
            raise Exception("invalid type "+type)

def first_variation(tree):
    for type,value in tree:
        yield type,list(cut_to_first_variation(value))

def filter(tree):
    tree= list(first_variation(tree))
    tree=list(filter_properties(tree))
    return tree
    
    
def to_sgf(tree):
    for type,value in tree:
        if type=="variation":
            yield "("
            for v in to_sgf(value):
                yield v
            yield ")"
        elif type == "node":
            yield "\n"
            yield ";"
            for v in to_sgf(value):
                yield v
        elif type == "property":
            yield value[0]
            for v in value[1]:
                yield "["
                yield v.replace("\\","\\\\").replace("]","\\]")
                yield "]"
import pprint      
def test():
    f=open("test.sgf",encoding="utf-8")
    t=list(tree(tokenize(f)))
    pprint.pprint(t)
    print ("".join(to_sgf(t)))
    t=filter(t)
    pprint.pprint(t)
    print ("".join(to_sgf(t)))
def reverse(tree,size):
    def r(v):
        return v[0]+string.ascii_letters[size-string.ascii_letters.index(v[1])-1]
    for type,value in tree:
        if type == "property":
            name,v = value
            if name in {"AB","AW","AE","B","W"}:
                #print(v)
                #print(size-string.ascii_letters.index(v[0][1]))
                v[0]=r(v[0])
                #print (v)
            elif name in {"AR","LN"}:
                v=[":".join(r(coord) for coord in compound.split(":"))
                   for compound in v]
            elif name in {"CR","DD","MA","SL","SQ","TR"}:
                v=[r(coord) for coord in v]
            elif name in {"LB"}:
                def switch(v):
                    point,text=v.split(":")
                    return r(point)+":"+text
                v=[ switch(coord) for coord in v]
            yield type,(name,v)
        else:
            yield type,list(reverse(value,size))
#sys.exit(0)

if __name__ == "__main__":
    #test()
    parser = argparse.ArgumentParser(description="Manipulate sgf tree")
    parser.add_argument("--filter", action='store_true',
                        help="filter coments and variation")
    parser.add_argument("--limit", action='store', type=int, default=None,
                        help="limit the principal variation work only with with filter")
    parser.add_argument("--reverse",action="store_true",
                        help="reverse the board upside down")
    parser.add_argument("file",action="store")
    args = parser.parse_args()
    if args.limit is not None and not args.filter:
        parser.help()
        sys.exit(1)
    new_file = tree(tokenize(open(args.file,encoding="utf-8")))
    if args.filter:
        new_file=filter(new_file)
        if args.limit is not None:
            del new_file[0][1][args.limit+1:]
    if args.reverse:
        size = 19
        new_file = list(new_file)
        #pprint.pprint(new_file[0][1][0][1])
        for p,(name,value) in new_file[0][1][0][1]:
            if name == "SZ":
                size=int(value[0])
        new_file = reverse(new_file,size)
        
    new_file = list(new_file)
    #pprint.pprint(new_file)
    print ("".join(to_sgf(new_file)),
           file=open("new-"+args.file,"w",encoding="utf-8"))

