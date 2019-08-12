from context import *
from phhe.ast import *
from phhe.parse import parse_file

class TestInterpreter(TestCase):
    "Tests for the simple interpreter built in to the AST"

    def test_block(self):
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

    def test_binop(self):
        self.assertEqual(
            # 2 + (4 - 1)
            BinOp(Literal(2),
                  '+',
                  BinOp(Literal(4), '-', Literal(1))).eval(),
            5
        )

    def test_file(self):
        self.assertEqual(
            parse_file('tests/test.ph').eval(),
            308
        )
