from __future__ import print_function, division, unicode_literals
from codecs import open

import unittest

import sgftool
import sgfparsing  # Parsing logic


class MyTest(unittest.TestCase):

    def test_bad_token(self):
        self.assertRaises(sgfparsing.InvalidSgfException,
                          sgfparsing.tree, iter([("bad_token", "value")]))
            
    def test_filter(self):
        with open("test.sgf", encoding="utf-8") as input:
            with open("test_filter.sgf", encoding="utf-8") as output:
                result = sgfparsing.tree(sgfparsing.tokenize(input))
                sgftool.filter(result)
                self.assertEqual(sgftool.to_sgf(result), output.read().strip())

    def test_round_trip(self):
        with open("test.sgf", encoding="utf-8") as input:
            with open("test.sgf", encoding="utf-8") as output:
                result = sgftool.to_sgf(sgfparsing.tree(
                    sgfparsing.tokenize(input)))
                self.assertEqual(result, output.read().strip())
        
    def test_reverse(self):
        with open("test.sgf", encoding="utf-8") as input:
            with open("test_reverse.sgf", encoding="utf-8") as output:
                result = sgfparsing.tree(sgfparsing.tokenize(input))
                sgftool.reverse(result)
                self.assertEqual(sgftool.to_sgf(result), output.read().strip())

    def test_limit(self):
        with open("test.sgf", encoding="utf-8") as input:
            with open("test_limit.sgf", encoding="utf-8") as output:
                result = sgfparsing.tree(sgfparsing.tokenize(input))
                sgftool.limit(result, 1)
                self.assertEqual(sgftool.to_sgf(result), output.read().strip())

    def test_unbalanced_parenthesis(self):
        with open("test_unbalanced_parenthesis.sgf", encoding="utf-8") as input:
            self.assertRaises(sgfparsing.InvalidSgfException,
                              sgfparsing.tree,
                              sgfparsing.tokenize(input))

    def test_unclosed_parenthesis(self):
        with open("test_unclosed_parenthesis.sgf", encoding="utf-8") as input:
            self.assertRaises(sgfparsing.InvalidSgfException,
                              sgfparsing.tree,
                              sgfparsing.tokenize(input))
    
    def test_missing_semicolon(self):
        with open("test_missing_semicolon.sgf", encoding="utf-8") as input:
            self.assertRaises(sgfparsing.InvalidSgfException,
                              sgfparsing.tree,
                              sgfparsing.tokenize(input))
    
    def test_unclosed_property(self):
        with open("test_unclosed_property.sgf", encoding="utf-8") as input:
            self.assertRaises(sgfparsing.InvalidSgfException,
                              sgfparsing.tree,
                              sgfparsing.tokenize(input))
    
    def test_invalid_coordinate_number(self):
        with open("test_invalid_coordinate_number.sgf",
                  encoding="utf-8") as input:
            self.assertRaises(sgfparsing.InvalidSgfException,
                              sgftool.reverse,
                              sgfparsing.tree(sgfparsing.tokenize(input)))

    def test_invalid_coordinate_out_of_bounds(self):
        with open("test_invalid_coordinate_out_of_bounds.sgf",
                  encoding="utf-8") as input:
            self.assertRaises(sgfparsing.InvalidSgfException,
                              sgftool.reverse,
                              sgfparsing.tree(sgfparsing.tokenize(input)))


if __name__ == '__main__':
    unittest.main()
