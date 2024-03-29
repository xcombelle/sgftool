from __future__ import print_function, division, unicode_literals
from codecs import open

import pprint
import sys
import string
import argparse
import traceback
import pdb

import sgfparsing  # Parsing logic

# Whitelist of properties not filtered out by filter_properties
whitelist_property = set("AP ST GM FF CA RU SZ KM PW PB WR BR DT EV RO PC SO HA AB AW AE B W".split())


def filter_properties(tree, whitelist_property=whitelist_property):
    """filter out the properties not white listed
    to keep only the move played
    modify the tree"""

    tree.properties = [(name, values) for name, values in tree.properties
                       if name in whitelist_property]
    for child in tree.children:
        filter_properties(child, whitelist_property)


def first_variation(tree):
    """skip all the auxiliary variations
    modify the tree"""
    
    del tree.children[1:]
    if tree.children:
        first_variation(tree.children[0])


def limit(tree, depth):
    """limit the variations to depth"""
    
    if depth < 1:
        ValueError("limit should be strictly positive")

    # n + 1 because the root is counted
    if depth + 1 == 0:
        tree.children = []
    for child in tree.children:
        limit(child, depth-1)


def filter(tree):
    """filter variation and comments and notation on the board
    modify the tree"""

    first_variation(tree)
    filter_properties(tree)
    

def to_sgf(tree):
    """convert tree to sgf"""
    
    return "".join("".join(node_to_sgf(node)) for node in tree.children)[1:]


def to_txt(tree):
    return "".join(node_to_txt(tree))


def node_to_sgf(tree, has_siblings=True):
    """convert a node of the tree to sgf"""

    yield '\n'
    
    if has_siblings:
        yield "("
    yield ";"
        
    for name, values in tree.properties:
        if name in ("RU", "PW"):
            yield "\n"
        yield name
        for value in values:
            yield "["
            yield value.replace("\\", "\\\\").replace("]", "\\]")
            yield "]"
    
    for v in tree.children:
        for node in node_to_sgf(v, has_siblings=len(tree.children) > 1):
            yield node
            
    if has_siblings:
        yield ")"


def position_to_txt(position, size):
    """ TODO finish this function"""

    coords = [string.ascii_letters.index(p) for p in position]
    if len(coords) != 2:
        raise sgfparsing.InvalidSgfException("bad coordinate " + position)
    # print(coords)
    # print("ABCDEFGHJKLMNOPQRST"[coords[0]])
    # print(str(size - coords[1]))
    return "ABCDEFGHJKLMNOPQRST"[coords[0]] + str(size - coords[1])


def node_to_txt(tree, depth=0, size=None,
                ha=0, color="B", handicap=None, first=-1, first_white=False):
    """TODO finish this function"""    

    # print(depth, tree.properties)

    if handicap is None:
        handicap = []
    if depth == 1:
        japanese = False
        
        rules = None
        for name, values in tree.properties:
            if name == "RU":
                if len(values) != 1:
                    raise sgfparsing.InvalidSgfException("too much values for RU")
                else:
                    if values[0] == "Japanese":
                        japanese = True
                    rules = values[0]
            elif name == "AB":
                handicap.extend(values)
            elif name == "AW":
                raise sgfparsing.CantProcessSgfException("adding stones is unexpected")
            elif name == "SZ":
                if len(values) != 1:
                    raise sgfparsing.InvalidSgfException("SZ property has several values")
                if not values[0].isdigit():
                    raise sgfparsing.InvalidSgfException("SZ property is not integer")
                size = int(values[0])
            elif name == "HA":
                if len(values) != 1:
                    raise sgfparsing.InvalidSgfException("HA property has several values")
                if not values[0].isdigit():
                    raise sgfparsing.InvalidSgfException("HA property is not integer")
                ha = int(values[0])
        if ha is None:
            ha = 0
        if size is None:
            size = 19
        if size > 19:
            raise sgfparsing.CantProcessSgfException("Can't handle size >19")
        yield('[Size "{}"]\n'.format(size))
        yield('[Rules "{}"]\n'.format(rules))
        if ha == 0:
            first = depth+1
    elif depth > 1:
        b = []
        w = []
        comment = ""
        for name, values in tree.properties:
            # print(name)
            if name == "B":
                b = values
            elif name == "W":
                w = values
            elif name in ("AW", "AB"):
                raise sgfparsing.CantProcessSgfException("add white or black in tree")
            elif name == "C":
                if len(values) != 1:
                    raise sgfparsing.InvalidSgfException("comment values !=1")
                comment = " {" + values[0].replace("}", r"\}")+"}"
        if first == -1:
            
            if w:
                yield('[Handicap "{}"]\n').format(
                    " ".join(position_to_txt(h, size) for h in handicap))
                ha = 0
                first = depth
                first_white = True
                if len(w) != 1:
                    raise sgfparsing.CantProcessSgfException("length W is !=1")
                yield("1.{coords}{comment}\n".format(
                    coords=position_to_txt(w[0], size), comment=comment))
            else:
                handicap.extend(b)
            
        else:
            print(depth - first, b, w, not(b and not w), depth - first % 2 == 1,
                  first_white)
            
            if w or b:
                if first_white ^ (depth-first) % 2 == 1:
                    if not (w and not b):
                        raise sgfparsing.CantProcessSgfException("non altering colors")
                    else:
                        if len(w) != 1:
                            raise sgfparsing.InvalidSgfException("W property length != 1")
                        else:
                            # print(w[0])
                            yield "{num}.{coord}{comment}\n".format(
                                num=depth - first + 1,
                                coord=position_to_txt(w[0], size),
                                comment=comment)
                else:
                    if not (b and not w):
                        raise sgfparsing.CantProcessSgfException("non altering colors")
                    else:
                        if len(b) != 1:
                            raise sgfparsing.InvalidSgfException("B property length != 1")
                        else:
                            yield "{num}.{coord}{comment}\n".format(
                                num=depth - first + 1,
                                coord=position_to_txt(b[0], size),
                                comment=comment)

    for v in tree.children:
        # print("yielding depth", depth)
        # print("sgf", to_sgf(tree))
        for node in node_to_txt(v, depth=depth + 1, size=size, ha=ha,
                                handicap=handicap, first=first,
                                first_white=first_white):
            yield node
        # print("returning from child, depth:", depth)
    if not tree.children:
        if ha > 0:
            yield('[Handicap "{}"]\n').format(
                " ".join(position_to_txt(h, size) for h in handicap))
                

def reverse(tree):
    """reverse all the coords in the tree
    modify the tree"""

    size = 19
    for name, value in tree.children[0].properties:
        if name == "SZ":
            size = int(value[0])
    do_reverse(tree, size)


def do_reverse(tree, size):
    """reverse all the coords in the tree
    modify the tree"""

    def r(v):
        try:
            index = string.ascii_letters.index(v[1])
            if not 0 <= index < size:
                raise sgfparsing.InvalidSgfException("invalid coordinate " + v)
            return v[0] + string.ascii_letters[size - index - 1]
        except ValueError:
            raise sgfparsing.InvalidSgfException("invalid coordinate "+v)
    for i, (name, value) in enumerate(tree.properties):
        
        if name in ("B", "W"):
            value[0] = r(value[0])
            
        elif name in ("AR", "LN"):  # pragma: no cover
            value = [":".join(r(coord) for coord in compound.split(":"))
                for compound in v]
        
        elif name in ("AB", "AW", "AE", "CR", "DD", "MA", "SL", "SQ", "TR"):
            value = [r(coord) for coord in value]
        
        elif name in ("LB",):
            def switch(v):
                point, text = v.split(":", 1)
                return r(point)+":"+text
            value = [switch(coord) for coord in value]
        tree.properties[i] = name, value
    for child in tree.children:
        do_reverse(child, size)
      

if __name__ == "__main__":
    # test()

    # Arguments processing
    parser = argparse.ArgumentParser(description="Manipulate sgf tree")
    parser.add_argument("--filter", action='store_true',
                        help="filter comments and variation")
    parser.add_argument("--limit", action='store', type=int, default=None,
                        help="limit the variations to LIMIT depth")
    parser.add_argument("--reverse", action="store_true",
                        help="reverse the board upside down")
    parser.add_argument("--to-txt", action="store_true",
                        help="save to txt format")
    parser.add_argument("file", action="store")

    # Arguments loading
    args = parser.parse_args()

    # File loading and pre-processing
    new_file = sgfparsing.tree(sgfparsing.tokenize(open(args.file,
                                                        encoding="utf-8")))
   
    if args.filter:
        filter(new_file)
    
    if args.limit is not None:
        limit(new_file, args.limit)
    
    if args.reverse:
        reverse(new_file)

    if args.to_txt:
        try:
            print(to_txt(new_file),
                  file=open("new-"+args.file.replace(".sgf", ".txt"), "w",
                            encoding="utf-8"))
        except:
            # raise
            
            traceback.print_exc()
            
            pdb.post_mortem()
    else:
        print(to_sgf(new_file), file=open("new-"+args.file, "w",
                                          encoding="utf-8"))
