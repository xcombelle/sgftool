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
    f = iter(partial(file.read, 1), "")
    last_char = " "
    uppers = set(string.ascii_uppercase)

    while True:
        # Skip space characters
        while last_char.isspace():
            last_char = next(f)

        # Return property name
        if last_char in uppers:
            property_name = []
            while last_char in uppers:
                property_name.append(last_char)
                last_char = next(f)
            yield "property_name", "".join(property_name)

        # Return property value
        elif last_char == "[":
            try:
                last_char = next(f)
                property_value = []
                while last_char != "]":

                    # Skip first "]" for comment property value
                    if last_char == "\\":
                        property_value.append(next(f))

                    else:
                        property_value.append(last_char)
                    last_char = next(f)
                yield "property_value", "".join(property_value)

            except StopIteration:

                raise InvalidSgfException("unclosed property value")

            last_char = next(f)

        # Return special token
        else:
            yield "special", last_char
            last_char = next(f)


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