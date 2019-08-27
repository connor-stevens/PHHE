"""Generates C code from the AST. We could have another method on AST nodes,
    but that makes it harder to switch code generators in the future"""

from .ast import *


class CBlock:
    def __init__(self):
        self.exprs = []

    def add(self, node):
        self.exprs.append(node)

    def __str__(self):
        ret = ' {\n'

        for i in self.exprs:
            ret += '\t%s;\n' % i

        ret += '}\n'
        return ret


class CFunction:
    def __init__(self, name, args=None, ret_type=None):
        self.block = CBlock()
        self.name = name
        self.args = args
        self.ret_type = ret_type

    def __str__(self):
        arg_str = ""
        if self.args:
            arg_str = "%s %s" % (self.args[1]['primitive'], self.args[0])
        if self.ret_type:
            ret_type = self.ret_type['primitive']
        else:
            ret_type = 'void'
        ret = "%s %s(%s)" % (ret_type, self.name, arg_str)

        if self.block.exprs:
            ret += ' %s' % self.block
            return ret
        else:
            ret += ';\n'
            return ret


class Module:
    def __init__(self):
        self.functions = [CFunction('main', ret_type={'primitive': 'int'})]
        self.block = [self.functions[0].block]
        self.type_ctx = Context()
        self.name_ctx = Context()

        self.name_ctx.add_binding('print', 'print')
        self.type_ctx.add_binding('print', Function(
            'print', ('i', {'primitive': 'int'}), None, None).type(self.type_ctx))

        self.var_number = 0

    def push(self):
        self.name_ctx.push_scope()
        self.type_ctx.push_scope()

    def pop(self):
        self.name_ctx.pop_scope()
        self.type_ctx.pop_scope()

    def add_fun(self, node):
        self.push()

        if node.args:
            self.name_ctx.add_binding(node.args[0], node.args[0])
            self.type_ctx.add_binding(node.args[0], node.args[1])
        node_type = node.type(self.type_ctx)

        self.start_fun(CFunction(node.name, node.args, node_type['return']))

        if node.body:
            self.add_str(gen_expr(node.body, self, True))

        self.pop()
        self.end_fun()

        # Right now we don't do this scope-based name mangling for functions
        self.name_ctx.add_binding(node.name, node.name)
        self.type_ctx.add_binding(node.name, node_type)

    def start_block(self):
        block = CBlock()
        self.block[-1].add(block)
        self.block.append(block)

    def end_block(self):
        self.block.pop()

    def start_fun(self, fun):
        self.functions.append(fun)
        self.block.append(self.functions[-1].block)

    def end_fun(self):
        self.block.pop()

    def add_var(self, type, name, value):
        """Here `type` is a dict, `name` and `value` are str"""
        # C doesn't let us return from blocks, so we use pretend scopes
        fresh_name = "%s$%r" % (name, self.var_number)
        self.var_number += 1

        r = "%s %s = %s" % (type['primitive'], fresh_name, value)

        self.type_ctx.add_binding(name, type)
        self.name_ctx.add_binding(name, fresh_name)

        self.block[-1].add(r)

    def add_str(self, s):
        s = s.strip()
        if s:
            self.block[-1].add(s)

    def __str__(self):
        import pathlib
        rts = open(pathlib.Path(__file__).resolve().parent / 'runtime.c')
        ret = rts.read() + '\n'
        rts.close()

        for i in self.functions[::-1]:
            ret += str(i) + '\n'

        return ret

    def name(self, name):
        self.name_ctx.lookup(name)

    def type(self, name):
        self.type_ctx.lookup(type)


def gen_expr(node, mod, is_return=False):
    return_string = "return " if is_return else ""
    if isinstance(node, Literal):
        return "%s%r" % (return_string, node.value)
    elif isinstance(node, BinOp):
        return "%s(%s) %s (%s)" % (
            return_string,
            gen_expr(node.lhs, mod),
            node.op,
            gen_expr(node.rhs, mod))
    elif isinstance(node, VarDeclare):
        t = node.value.type(mod.type_ctx)
        mod.add_var(t, node.name, gen_expr(
            node.value, mod))
        return ''

    elif isinstance(node, VarAccess):
        return "%s%s" % (return_string, mod.name_ctx.lookup(node.name))
    elif isinstance(node, Block):
        ret = ""
        mod.push()

        i = 0
        for expr in node.exprs:
            i += 1
            mod.add_str(ret)
            ret = '%s' % gen_expr(
                expr, mod, is_return and (i == len(node.exprs)))

        mod.pop()
        return ret

    elif isinstance(node, Call):
        return "%s%s(%s)" % (return_string, node.function, gen_expr(node.args, mod))

    elif isinstance(node, Function):
        mod.add_fun(node)

        return ''

    elif isinstance(node, If):
        mod.push()
        cond = gen_expr(node.cond, mod)
        # mod.start_block()
        true = CBlock()
        mod.block.append(true)
        mod.push()
        true.add(gen_expr(node.if_branch, mod, is_return))
        mod.pop()
        mod.end_block()

        if node.else_branch is not None:
            false = CBlock()
            mod.block.append(false)
            mod.push()
            false.add(gen_expr(node.else_branch, mod, is_return))
            mod.pop()
            mod.end_block()
            ret = 'if (%s) %s else %s' % (cond, true, false)
        else:
            ret = 'if (%s) %s' % (cond, true)
        mod.pop()
        return ret


def codegen(nodes):
    ret = Module()

    for node in nodes:
        # Pattern matching would be awesome here
        ret.add_str(gen_expr(node, ret))

    return str(ret)
