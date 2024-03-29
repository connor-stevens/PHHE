""" The Abstract Syntax Tree

The 'eval()' methods act like a tiny built-in AST interpreter
The 'type()' methods return the type of the node
"""


import operator


class Context:
    """Holds variable definitions and keeps track of scopes,
        both for type checking and interpreting"""

    def __init__(self):
        self.stack = [{}]

    def add_binding(self, name, value):
        self.stack[-1][name] = value

    def push_scope(self):
        self.stack.append({})

    def pop_scope(self):
        self.stack.pop()

    def lookup(self, name):
        # Go up the stack from innermost to outermost
        for i in self.stack[::-1]:
            v = i.get(name)
            if v is not None:
                return v


class DictEq:
    """A base class that will implement the __eq__ method the right way"""

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


reservedTags = ["primitive", "struct"]
primitiveTypes = ["type", "struct", "int", "null", "function"]
NULL = {"primitive": "null"}


class TypePrimitive(DictEq):
    def __init__(self, type):
        if type in primitiveTypes:
            self.primitive = type
        else:
            raise Exception("%r is not a primitive type" % r)

    def __repr__(self):
        return "TypePrimitive(%r)" % self.primitive

    def eval(self, ctx):
        return self.type

    def type(self, ctx):
        return {"primitive": "type"}


class TypeTag(DictEq):
    def __init__(self, key, val):
        if key != "primitive":
            self.type = {key: val}
        else:
            raise "Cannot use primitive as a type Tag."

    def __repr__(self):
        return "Typetag(%r)" % self.type["tag"][0]

    def eval(self, ctx):
        return self.type

    def type(self, ctx):
        return {"primitive": "type"}


class TypeUserDef(DictEq):
    def __init__(self, name):
        self.name = name
        self.type = {"primitive": "struct", "struct": name}

    def __repr__(self):
        return "TypeUserDef(%r)" % self.name

    def eval(self, ctx):
        return self.type

    def type(self, ctx):
        return {"primitive": "type"}


class Literal(DictEq):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Literal(%r)" % self.value

    def eval(self, ctx):
        return self.value

    def type(self, ctx):
        return {"primitive": type(self.value).__name__}


class If(DictEq):
    """This language currently only has numbers, so that's the condition.
       The else branch is run if the condition is 0, otherwise the if branch is run."""

    def __init__(self, cond, if_branch, else_branch=None):
        self.cond = cond
        self.if_branch = if_branch
        self.else_branch = else_branch

    def __repr__(self):
        return "if (%r) then (%r) else (%r)" % (self.cond, self.if_branch,
                                                self.else_branch)

    def eval(self, ctx):
        cond = self.cond.eval(ctx)
        if cond != 0:
            return self.if_branch.eval(ctx)
        elif self.else_branch is not None:
            return self.else_branch.eval(ctx)

    def type(self, ctx):
        if self.else_branch is not None:
            # It doesn't return anything if there isn't an else branch
            t1 = self.if_branch.type(ctx)
            t2 = self.else_branch.type(ctx)
            if t1 == t2:
                return t1
            else:
                raise TypeError("Incompatible types for 'if' branches: %r and %r"
                                % (t1, t2))


class Function(DictEq):
    """A function definition"""

    def __init__(self, name, args, body, ret_type=None):
        """Right now, 'args' should be a tuple of (name,type)"""
        self.name = name
        self.args = args
        self.body = body
        self.ret_type = ret_type

    def __repr__(self):
        return "fun %s(%r) = %r" % (self.name, self.args, self.body)

    def eval(self, ctx):
        ctx.add_binding(self.name, self)

    def type(self, ctx):
        if self.ret_type is not None:
            if self.body is not None:
                ret_t = self.body.type(ctx)
                if ret_t != self.ret_type:
                    # I don't know if this belongs here
                    raise TypeError('Wrong return type %r, really returns %r',
                                    self.ret_type, ret_t)
            else:
                ret_t = self.ret_type
        else:
            if self.body is not None:
                ret_t = self.body.type(ctx)
            else:
                ret_t = NULL
        arg_t = self.args[1]
        self_t = {'primitive': 'function', 'return': ret_t, 'argument': arg_t}
        ctx.add_binding(self.name, self_t)
        return self_t

    def call(self, ctx, args):
        if self.body is not None:
            ctx.push_scope()
            ctx.add_binding(self.args[0], args)
            ret = self.body.eval(ctx)
            ctx.pop_scope()
            return ret


class Call(DictEq):
    """A function call `f(x)`"""

    def __init__(self, function, args):
        self.function = function
        self.args = args

    def __repr__(self):
        return "%r(%r)" % (self.function, self.args)

    def eval(self, ctx):
        if self.function == 'print':
            print(self.args.eval(ctx))
        else:
            fun = ctx.lookup(self.function)
            return fun.call(ctx, self.args.eval(ctx))

    def type(self, ctx):
        fun = ctx.lookup(self.function)
        if fun:
            return fun['return']
        else:
            return NULL


class BinOp(DictEq):
    """A binary operation (e.g. *, +, ...)"""

    def __init__(self, lhs, op, rhs):
        """`op` is a str"""
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return "BinOp(%r %r %r)" % (self.lhs, self.op, self.rhs)

    def eval(self, ctx):
        ops = {
         '+': operator.add,
         '-': operator.sub,
         '*': operator.mul,
         '/': operator.truediv
        }
        return ops.get(self.op)(self.lhs.eval(ctx), self.rhs.eval(ctx))

    def type(self, ctx):
        lhsType = self.lhs.type(ctx)
        rhsType = self.rhs.type(ctx)
        if lhsType == rhsType:
            return lhsType
        else:
            # Not sure if this is the how we want to do this
            return NULL
            # I guess this might be a place to raise a type error?
            # Do we want .type() to be the type checker?


class VarDeclare(DictEq):
    """A variable declaration.
    The way it works right now, it also can be a variable assignment"""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "%r = %r" % (self.name, self.value)

    def eval(self, ctx):
        ctx.add_binding(self.name, self.value.eval(ctx))
        return self.value

    def type(self, ctx):
        # Right now, `ctx` holds types, but it could hold values instead
        # Also, right now we have to check the type of a VarDeclare
        #   before we can do it with a VarAccess
        # That's probably not good but I don't know how else we would do it
        ctx.add_binding(self.name, self.value.type(ctx))
        return NULL


class VarAccess(DictEq):
    """A use of a variable"""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "VarAccess(%r)" % self.name

    def eval(self, ctx):
        return ctx.lookup(self.name)

    def type(self, ctx):
        # Right now, `ctx` holds types, but it could hold values instead
        return ctx.lookup(self.name)


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

    def eval(self, ctx):
        ret = None
        ctx.push_scope()
        # They do all run, but only the last one gets returned
        for i in self.exprs:
            ret = i.eval(ctx)
        ctx.pop_scope()

        return ret

    def type(self, ctx):
        """The block has the type of the last expression"""
        ret = None
        ctx.push_scope()

        for i in self.exprs:
            ret = i.type(ctx)
        ctx.pop_scope()

        return ret
