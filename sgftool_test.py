import unittest

from sgftool import to_sgf,tree,tokenize,limit,reverse,filter

class MyTest(unittest.TestCase):

    def test_filter(self):
        with open("test.sgf",encoding="utf-8") as input, \
             open("test_filter.sgf",encoding="utf-8") as output:
            result = tree(tokenize(input))
            filter(result)
            self.assertEqual(to_sgf(result),output.read().strip())

    def test_round_trip(self):
        with open("test.sgf",encoding="utf-8") as input, \
             open("test.sgf",encoding="utf-8") as output:
            result = to_sgf(tree(tokenize(input)))
            self.assertEqual(result,output.read().strip())
        
    def test_reverse(self):
        with open("test.sgf",encoding="utf-8") as input, \
             open("test_reverse.sgf",encoding="utf-8") as output:
            result = tree(tokenize(input))
            reverse(result)
            self.assertEqual(to_sgf(result),output.read().strip())

    def test_limit(self):
        with open("test.sgf",encoding="utf-8") as input, \
             open("test_limit.sgf",encoding="utf-8") as output:
            result = tree(tokenize(input))
            limit(result,1)
            self.assertEqual(to_sgf(result),output.read().strip())

if __name__ == '__main__':
    unittest.main()
