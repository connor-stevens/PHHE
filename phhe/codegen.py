"""Generates C code from the AST. We could have another method on AST nodes,
    but that makes it harder to switch code generators in the future"""

from .ast import *

class MutString:
    def __init__(self, s):
        self.s = s

    def __iadd__(self, other):
        self.s = self.s + other
        return self

    def __str__(self):
        return self.s

def gen_expr(node, name_ctx, type_ctx, pre):
    if isinstance(node, Literal):
        return repr(node.value)
    elif isinstance(node, BinOp):
        return "(%s) %s (%s)" % (gen_expr(node.lhs, name_ctx, type_ctx, pre), node.op, gen_expr(node.rhs, name_ctx, type_ctx, pre))
    elif isinstance(node, VarDeclare):
        t = node.value.type(type_ctx)

        # C doesn't let us return from blocks, so we use pretend scopes
        fresh_name = "%s$%r" % (node.name, len(name_ctx.stack))

        r = "%s %s = %s" % (t['primitive'], fresh_name, gen_expr(node.value, name_ctx, type_ctx, pre))

        type_ctx.add_binding(node.name, t)
        name_ctx.add_binding(node.name, fresh_name)

        return r

    elif isinstance(node, VarAccess):
        return name_ctx.lookup(node.name)
    elif isinstance(node, Block):
        ret = ""
        name_ctx.push_scope()
        type_ctx.push_scope()

        for i in node.exprs:
            pre += ret
            ret = '%s;\n' % gen_expr(i, name_ctx, type_ctx, pre)

        name_ctx.pop_scope()
        type_ctx.pop_scope()
        return ret
    elif isinstance(node, Call):
        return "%s(%s)" % (node.function, gen_expr(node.args, name_ctx, type_ctx, pre))


def codegen(nodes):
    ret = MutString("""#include <stdio.h>

void main() {
""")

    name_ctx = Context()
    type_ctx = Context()

    for node in nodes:
         # Pattern matching would be awesome here
         ret += gen_expr(node, name_ctx, type_ctx, ret)

    ret += '}'
    return ret
