""" The Abstract Syntax Tree

The 'eval()' methods act like a tiny built-in AST interpreter
I'm thinking in the future there will be a 'type()' method that returns the type of the expression, for type checking & inference
"""
import operator


class Literal:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Literal(%r)" % self.value

    def eval(self):
        return self.value


class BinOp:
    """A binary operation (e.g. *, +, ...)"""
    def __init__(self, lhs, op, rhs):
        """`op` is a str"""
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return "BinOp(%r %r %r)" % (self.lhs, self.op, self.rhs)

    def eval(self):
        ops = {
         '+': operator.add,
         '-': operator.sub,
         '*': operator.mul,
         '/': operator.truediv
        }
        return ops.get(self.op)(self.lhs.eval(), self.rhs.eval())


# This is hacky and obviously shouldn't be used in a real interpreter
# It also means there's no concept of scope
variables = {}


class VarDeclare:
    """A variable declaration. The way it works right now, it can be a variable assignment as well"""
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "%r = %r" % (self.name, self.value)

    def eval(self):
        variables[self.name] = self.value
        return None


class VarAccess:
    """A use of a variable"""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "VarAccess(%r)" % self.name

    def eval(self):
        return variables[self.name].eval()


class Block:
    """A block of several expressions. The last one is the return value of the block"""
    def __init__(self, *exprs):
        self.exprs = exprs

    def __repr__(self):
        ret = '{\n'
        for i in self.exprs:
            ret += '\t%r\n' % i
        ret += '}'
        return ret

    def eval(self):
        ret = None
        # They do all run, but only the last one gets returned
        for i in self.exprs:
            ret = i.eval()
        return ret
