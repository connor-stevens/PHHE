""" The Abstract Syntax Tree

The 'eval()' methods act like a tiny built-in AST interpreter
I'm thinking in the future there will be a 'type()' method that returns the type of the expression, for type checking & inference
"""


import operator


class DictEq:
    """A base class that will implement the __eq__ method the right way"""

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

reservedTags = ["primitive", "struct"]
primitiveTypes = ["type", "struct", "int", "null"]
NULL = {"primitive":"null"}


class TypePrimitive(DictEq):
    def __init__(self, type):
        if type in primitiveTypes:
            self.primitive = type
        else:
            raise Exception("%r is not a primitive type" % r)

    def __repr__(self):
        return "TypePrimitive(%r)" % self.primitive

    def eval(self):
        return self.type

    def type(self):
        return {"primitive":"type"}

class TypeTag(DictEq):
    def __init__(self, key, val):
        if key != "primitive":
            self.type = {key:val}
        else:
            raise "Cannot use primitive as a type Tag."

    def __repr__(self):
        return "Typetag(%r)" % self.type["tag"][0]

    def eval(self):
        return self.type

    def type(self):
        return {"primitive":"type"}

class TypeUserDef(DictEq):
    def __init__(self, name):
        self.name = name
        self.type = {"primitive":"struct", "struct":name}

    def __repr__(self):
        return "TypeUserDef(%r)" % self.name

    def eval(self):
        return self.type

    def type(self):
        return {"primitive":"type"}

class Literal(DictEq):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Literal(%r)" % self.value

    def eval(self):
        return self.value

    def type(self):
        return {"primitive":type(self.value).__name__}


class BinOp(DictEq):
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

    def type(self):
        lhsType = self.lhs.type()
        rhsType = self.rhs.type()
        if lhsType == rhsType:
            return lhsType
        else:
            #Not sure if this is the how we want to do this
            return NULL



# This is hacky and obviously shouldn't be used in a real interpreter
# It also means there's no concept of scope
variables = {}



class VarDeclare(DictEq):
    """A variable declaration.
    The way it works right now, it also can be a variable assignment"""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "%r = %r" % (self.name, self.value)

    def eval(self):
        variables[self.name] = self.value
        return self.value

    def type(self):
        return NULL

class VarAccess(DictEq):
    """A use of a variable"""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "VarAccess(%r)" % self.name

    def eval(self):
        return variables[self.name].eval()

    def type(self):
        return NULL


class Block(DictEq):
    """A block containing expressions.
    The last one is used as the return value of the block"""

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

    def type(self):
        return NULL
