import subprocess
import os

from context import *

import parsy
from phhe.parse import *
from phhe.ast import *
from phhe.codegen import *


def compile_and_run(code):
    e = exprs.parse(code)
    s = str(codegen([e]))
    f = open('test.c', 'w')
    f.write(s)
    f.close()
    subprocess.run(['cc', '-o', 'test.out', 'test.c'], check=True)

    completed = subprocess.run(['.' + os.sep + 'test.out'],
                               capture_output=True, text=True)

    return completed.stdout


class TestCodegen(TestCase):
    def test_ffi(self):
        output = compile_and_run('''
fun putchar ( x : {primitive : int }): {primitive: int}
putchar(55) # Should print '7'
''')

        self.assertEqual(output, '7')

    def test_block(self):
        output = compile_and_run('''
x = 5
x = x + 2

print(x) # 7

print({
  y = x - 4
  x = y + 10
  x # 13
})

print(x) # 7, because this is the old x
''')
        self.assertEqual(output, '7\n13\n7\n')

    def test_function(self):
        output = compile_and_run('''
fun test(i: {primitive: int}) = i + 2

x = 48 / 4 # 12
x = x / 3 # 4
print(test(x))
''')
        self.assertEqual(output, '6\n')
