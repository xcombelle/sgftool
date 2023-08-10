#!/usr/bin/env python3 

import sys
import glob
import os.path
import json
import re
import string

import search
import sgftool
import sgfparsing

from goban_to_text import tree_to_positions
DEBUG = True

def dbg(*args):
    if DEBUG:
        print(*args)
    return args[-1]

class InvalidSgfException(Exception):
    pass
class InternalError(Exception):
    pass

def sgf_to_xy(position):
    x,y = [string.ascii_letters.index(p) for p in position]
    return x,y



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
    


def main(argv):
    for source in argv[1:]:
        destination =source.replace(".sgf", ".Zgo")
        cmd_compress(source, destination)




def cmd_compress(source,destination):
    open(destination,"w").write(compress(generate_positions(source)))


    
if __name__ == "__main__":
    main(sys.argv)

    
