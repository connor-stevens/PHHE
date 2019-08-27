from context import *

import parsy
from phhe.parse import *
from phhe.ast import *


class TestParse(TestCase):
    def test_literal(self):
        self.assertEqual(literal.parse('3.12'), Literal(3.12))
        self.assertEqual(literal.parse('-325'), Literal(-325))
        self.assertEqual(literal.parse('+546.00001'), Literal(546.00001))
        with self.assertRaises(parsy.ParseError):
            literal.parse('12.')
        with self.assertRaises(parsy.ParseError):
            literal.parse('.54')

    def test_binop(self):
        self.assertEqual(binop.parse('8+ 1.2 +9 *(2 - 3) / -2'),
                         # With correct precedence, should be:
                         #   (8 + 1.2) + ((9 * (2 - 3)) / -2)
                         BinOp(
                BinOp(Literal(8), '+', Literal(1.2)),
                '+',
                BinOp(
                    BinOp(Literal(9), '*',
                          BinOp(Literal(2), '-', Literal(3))
                          ),
                    '/',
                    Literal(-2)
                )
            ))
        with self.assertRaises(parsy.ParseError):
            binop.parse('3 ++ 2')

    def test_var(self):
        self.assertEqual(var_declare.parse('_s0me_nam3_w1th_numb3rs = -243.8'),
                         VarDeclare('_s0me_nam3_w1th_numb3rs', Literal(-243.8))
                         )
        self.assertEqual(var_access.parse('variabl3_'), VarAccess('variabl3_'))
        self.assertEqual(var_access.parse('a'), VarAccess('a'))

    def test_block(self):
        self.assertEqual(block.parse('{ 3 }'), Block(Literal(3)))
        self.assertEqual(block.parse('''{
            12 + 2
            x = 45
            9
            x
        }'''), Block(
            BinOp(Literal(12), '+', Literal(2)),
            VarDeclare('x', Literal(45)),
            Literal(9),
            VarAccess('x')
        ))

    def test_if(self):
        self.assertEqual(if_expr.parse('if 0 then 1 else 2'),
                         If(Literal(0), Literal(1), Literal(2)))
        self.assertEqual(if_expr.parse('if 12.3 then print(55)'),
                         If(Literal(12.3), Call('print', Literal(55))))
