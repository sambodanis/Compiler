import itertools
import CodeGenerator

__author__ = 'sambodanis'

class Memory:

    def __init__(self, ir):
        self._mem = []
        self._pc = 0
        self._var_map = {}
        # Filter the list of all strings in the IR to only contain temps
        # Sort those temps by their number and pick the largest.
        top_register = int(
            sorted([x for line in self._lines for x in line
                    if x[0] == '_'], key=lambda t: int(t[2:]))[-1][2:])
        # Counter that increments by 1 with every call
        count = lambda c=itertools.count(top_register + 1): next(c)
        #
        self._var_map = {line[0]: ['R' + str(count())]
                              for line in self._lines if line[0][0] not in ['_', '~', '[']
        and line[0] not in self._reserved_words}