from unittest import TestCase
import unittest

# This module suggested by
#   https://docs.python-guide.org/writing/structure/#test-suite


import os
import sys
# This way we can access phhe from inside of the `tests` folder
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
