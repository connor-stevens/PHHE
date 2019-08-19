from .ast import *
from parsy import *


def parse_file(path):
    "A helper function that parses an entire file into an AST object"
    file = open(path, 'r')
    source = file.read()
    file.close()
    return exprs.parse(source)


# These parsers return strings, and are used in other parsers

# Newlines can't be ignored, because we don't use semicolons
space = regex(r'[ \t]*')
ident_start = regex(r'[a-zA-Z_]')
ident_char = regex(r'[a-zA-Z_0-9]')
# An identifier, but could be a keyword
full_identifier = ident_start + ident_char.many().concat()
keyword = string_from('fun', 'let') << ident_char.should_fail('keyword')
# An identifier that isn't a keyword
identifier = keyword.should_fail(
    'non-keyword identifier') >> full_identifier.desc('identifier')


# These parsers return AST objects

var_access = identifier.map(VarAccess) << space

integer = regex(r'[+-]?[0-9]+').map(int).map(Literal)
float64 = regex(r'[+-]?[0-9]+\.[0-9]+').map(float).map(Literal)
literal = (float64 | integer) << space


@generate
def var_declare():
    "Parses a variable declaration: `x = 2`"
    name = yield identifier
    yield space >> string('=') >> space
    value = yield expr
    yield space
    return VarDeclare(name, value)

# Some of this is adapted from the Parsy examples
# See https://parsy.readthedocs.io/en/latest/howto/lexing.html#calculator
@generate
def mul_div():
    "Note that this function also matches simple expressions"
    simple = literal | block | var_access | paren
    lhs = yield simple
    while True:
        # We have to do this instead of recursion for left-associativity
        op = yield char_from('*/') | success('')
        yield space
        if not op:
            break
        rhs = yield simple
        lhs = BinOp(lhs, op, rhs)
    return lhs


@generate('binary operator')
def binop():
    "Note that this function also matches simple expressions"
    lhs = yield mul_div
    while True:
        # We have to do this instead of recursion for left-associativity
        op = yield char_from('+-') | success('')
        yield space
        if not op:
            break
        rhs = yield mul_div
        lhs = BinOp(lhs, op, rhs)
    return lhs


@generate
def expr():
    "Parses any expression"
    r = yield var_declare | call | binop
    return r


@generate
def exprs():
    """This returns a block in the AST, but it doesn't parse {}.
    That way, it can also be used for top level statements"""
    spaceN = regex(r'(#[^\n]*|\s)*')
    yield spaceN
    es = []
    while True:
        e = yield (expr << spaceN) | success('')
        if e:
            es.append(e)
        else:
            break
    return Block(*es)


@generate
def block():
    "{} blocks are easiest to parse, so that's what this uses for now"
    yield string('{') << space
    r = yield exprs
    yield string('}') << space
    return r

@generate
def call():
    f = yield identifier << space
    yield string('(') << space
    x = yield expr
    yield string(')') << space
    return Call(f,x)

# This needs to be specified last, to be able to refer to `expr`
paren = string('(') >> expr << string(')') << space
