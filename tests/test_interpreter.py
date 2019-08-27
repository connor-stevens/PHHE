from context import *
from phhe.ast import *
from phhe.parse import *


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
            ).eval(Context()),
            9
        )

    def test_binop(self):
        self.assertEqual(
            # 2 + (4 - 1)
            BinOp(Literal(2),
                  '+',
                  BinOp(Literal(4), '-', Literal(1))).eval(Context()),
            5
        )

    def test_file(self):
        self.assertEqual(
            parse_file('tests/test.ph').eval(Context()),
            308
        )

    def test_if(self):
        self.assertEqual(
            if_expr.parse('if 0 then 1 else 2').eval(Context()),
            2
        )
        self.assertEqual(
            if_expr.parse('if 1.2 then 21').eval(Context()),
            21
        )
        self.assertIsNone(if_expr.parse('if 0.0 then 12').eval(Context()))
