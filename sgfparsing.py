from functools import partial

import string


class InvalidSgfException(Exception):
    pass


class CantProcessSgfException(Exception):
    pass


class Node:
    """represent a node in the game tree"""

    def __init__(self):
        self.properties = []
        self.children = []


def tokenize(file):
    """generator which output tokens consumed by tree

    in a well formed sgf should be one of the following
    ("special","(")
    ("special",")")
    ("special",";")
    ("property_name","XX")
    ("property_value","xx")
    """
    import re
    regexp = re.compile(r"""\s*(?P<special>
                \(
                |\)
                |;)
                |(?P<property_name>[A-Z]{1,2})
                 (\[
                 (?P<property_value>(\\.
                                    |[^\]]
                                    )*
                )
                \])+
               \s*""",
               re.VERBOSE|re.DOTALL)

    f = file.read()
    
    for match in regexp.finditer(f):
        match=match.groupdict()

        if match["special"] is not None:  yield ("special",match["special"])
        if match["property_name"] is not None: yield ("property_name", match["property_name"])
        property_value = match["property_value"]
        if property_value is not None:
            if isinstance(property_value,str):
                property_value = re.sub(r"\\(.)",lambda m:m.group(1),property_value)
                yield("property_value",property_value)
            else:
                for p in property_value:
                    p = re.sub(r"\\(.)",lambda m:m.group(1) ,p)
                    yield ("property_value",p)



def tree(tokens):
    """generate a tree of game node, input is the output of tokenize"""

    # To remove the debug print
    def log(*args):
        pass
    # log = print

    current_node = Node()
    tree_node = current_node
    stack = []

    try:
        token = next(tokens)

        while True:
            # log("stack", [to_sgf(n) for n in stack])
            log("processing1", token)

            if token == ("special", "("):
                log("found (")

                stack.append(current_node)
                current_node.children.append(Node())
                current_node = current_node.children[-1]
                token = next(tokens)

                if token != ("special", ";"):

                    raise InvalidSgfException("semi-colon expected")

                token = next(tokens)

            elif token == ("special", ")"):
                log("found )")

                if len(stack) < 1:

                    raise InvalidSgfException("unexpected right parenthesis")

                current_node = stack.pop()
                token = next(tokens)

            elif token == ("special", ";"):
                log("yielding node")

                current_node.children.append(Node())
                current_node = current_node.children[-1]
                token = next(tokens)

            else:
                # print(token, file=sys.stderr)
                type, value = token

                if type != "property_name":

                    raise InvalidSgfException("unknown token" + repr(token))

                log("testing property_name", token, repr(type))

                while type == "property_name":
                    v = value
                    values = []
                    token = next(tokens)
                    type, value = token

                    log("consumed", token)

                    while type == "property_value":

                        values.append(value)
                        token = next(tokens)
                        type, value = token

                        log("testing", token)

                    current_node.properties.append((v, values))

                    log("next token", token)

    except StopIteration:
        if len(stack) != 0:
            raise InvalidSgfException("unclosed right parenthesis")
        return tree_node
