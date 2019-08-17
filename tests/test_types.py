from context import *

import parsy
from phhe.parse import *
from phhe.ast import *

class TestTypes(TestCase):
    def test_literal(self):
        self.assertEqual(Literal(1).type(),
        Literal(0).type())

    def test_binop(self):
        self.assertEqual(Literal(0).type(),
        BinOp(Literal(1), '+', Literal(1)).type())
