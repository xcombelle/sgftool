from __future__ import print_function, division, unicode_literals
from codecs import open


import unittest

from sgftool import (to_sgf,
                     tree,
                     tokenize,
                     limit,
                     reverse,
                     filter,
                     InvalidSgfException)


class MyTest(unittest.TestCase):

    def test_bad_token(self):
        self.assertRaises(InvalidSgfException,
                          tree, iter([("bad_token", "value")]))
            
    def test_filter(self):
        with open("test.sgf", encoding="utf-8") as input:
            with open("test_filter.sgf", encoding="utf-8") as output:
                result = tree(tokenize(input))
                filter(result)
                self.assertEqual(to_sgf(result), output.read().strip())

    def test_round_trip(self):
        with open("test.sgf", encoding="utf-8") as input:
            with open("test.sgf", encoding="utf-8") as output:
                result = to_sgf(tree(tokenize(input)))
                self.assertEqual(result, output.read().strip())
        
    def test_reverse(self):
        with open("test.sgf", encoding="utf-8") as input:
            with open("test_reverse.sgf", encoding="utf-8") as output:
                result = tree(tokenize(input))
                reverse(result)
                self.assertEqual(to_sgf(result), output.read().strip())

    def test_limit(self):
        with open("test.sgf", encoding="utf-8") as input:
            with open("test_limit.sgf", encoding="utf-8") as output:
                result = tree(tokenize(input))
                limit(result, 1)
                self.assertEqual(to_sgf(result), output.read().strip())

    def test_unbalanced_parenthesis(self):
        with open("test_unbalanced_parenthesis.sgf", encoding="utf-8") as input:
            self.assertRaises(InvalidSgfException,
                              tree,
                              tokenize(input))

    def test_unclosed_parenthesis(self):
        with open("test_unclosed_parenthesis.sgf", encoding="utf-8") as input:
            self.assertRaises(InvalidSgfException,
                              tree,
                              tokenize(input))
    
    def test_missing_semicolon(self):
        with open("test_missing_semicolon.sgf", encoding="utf-8") as input:
            self.assertRaises(InvalidSgfException,
                              tree, tokenize(input))
    
    def test_unclosed_property(self):
        with open("test_unclosed_property.sgf", encoding="utf-8") as input:
            self.assertRaises(InvalidSgfException,
                              tree, tokenize(input))
    
    def test_invalid_coordinate_number(self):
        with open("test_invalid_coordinate_number.sgf",
                  encoding="utf-8") as input:
            self.assertRaises(InvalidSgfException,
                              reverse, tree(tokenize(input)))

    def test_invalid_coordinate_out_of_bounds(self):
        with open("test_invalid_coordinate_out_of_bounds.sgf",
                  encoding="utf-8") as input:
            self.assertRaises(InvalidSgfException,
                              reverse, tree(tokenize(input)))


if __name__ == '__main__':
    unittest.main()
