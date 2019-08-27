"""Generates C code from the AST. We could have another method on AST nodes,
    but that makes it harder to switch code generators in the future"""

from .ast import *


class CFunction:
    def __init__(self, name, args=None, ret_type=None):
        self.block = []
        self.name = name
        self.args = args
        self.ret_type = ret_type

    def add(self, node):
        self.block.append(node)

    def __str__(self):
        arg_str = ""
        if self.args:
            arg_str = "%s %s" % (self.args[1]['primitive'], self.args[0])
        if self.ret_type:
            ret_type = self.ret_type['primitive']
        else:
            ret_type = 'void'
        ret = "%s %s(%s)" % (ret_type, self.name, arg_str)

        if self.block:
            ret += ' {\n'
            for i in self.block:
                ret += '\t' + i + ';\n'

            ret += '}\n'
            return ret
        else:
            ret += ';\n'
            return ret


class Module:
    def __init__(self):
        self.functions = [CFunction('main', ret_type={'primitive': 'int'})]
        self.type_ctx = Context()
        self.name_ctx = Context()

        self.name_ctx.add_binding('print', 'print')
        self.type_ctx.add_binding('print', Function(
            'print', ('i', {'primitive': 'int'}), None, None).type(self.type_ctx))

        self.func = [0]
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

    def start_fun(self, fun):
        self.func.append(len(self.functions))
        self.functions.append(fun)

    def end_fun(self):
        self.func.pop()

    def add_var(self, type, name, value):
        """Here `type` is a dict, `name` and `value` are str"""
        # C doesn't let us return from blocks, so we use pretend scopes
        fresh_name = "%s$%r" % (name, self.var_number)
        self.var_number += 1

        r = "%s %s = %s" % (type['primitive'], fresh_name, value)

        self.type_ctx.add_binding(name, type)
        self.name_ctx.add_binding(name, fresh_name)

        self.functions[self.func[-1]].add(r)

    def add_str(self, s):
        s = s.strip()
        if s:
            self.functions[self.func[-1]].add(s)

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
        mod.name_ctx.push_scope()
        mod.type_ctx.push_scope()

        i = 0
        for expr in node.exprs:
            i += 1
            mod.add_str(ret)
            ret = '%s' % gen_expr(
                expr, mod, is_return and (i == len(node.exprs)))

        mod.name_ctx.pop_scope()
        mod.type_ctx.pop_scope()
        return ret

    elif isinstance(node, Call):
        return "%s%s(%s)" % (return_string, node.function, gen_expr(node.args, mod))

    elif isinstance(node, Function):
        mod.add_fun(node)

        return ''


def codegen(nodes):
    ret = Module()

    for node in nodes:
        # Pattern matching would be awesome here
        ret.add_str(gen_expr(node, ret))

    return str(ret)
