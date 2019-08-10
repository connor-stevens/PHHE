from unittest import TestCase
import unittest

import os
import sys
# This way we can access phhe from inside of the `tests` folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phhe.ast import *

class TestInterpreter(TestCase):
    "Tests for the simple interpreter built in to the AST"
    def test(self):
        self.assertEqual(
            # This is the equivalent of {
            #    12.7
            #    x = 4 + 5
            #    "string literal"
            #    x
            # }
            Block(
                Literal(12.7),
                VarDeclare('x', BinOp(Literal(4), '+', Literal(5))),
                Literal('string literal'),
                VarAccess('x')
            ).eval(),
            9
        )

        self.assertEqual(
            # 2 + (4 - 1)
            BinOp(Literal(2),
                '+',
                BinOp(Literal(4), '-', Literal(1))).eval(),
            5
        )

if __name__ == '__main__':
    unittest.main()
