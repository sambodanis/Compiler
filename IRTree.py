import AST
import sys

__author__ = 'sambodanis'

debug = False


class irt:
    def __init__(self, ast):
        self._ast_root = ast
        self._lines = []
        self.count = 0

    def _gen_statement_ir(self, root, temp_number):
        if root.data[0] == 'writeln':
            self.count += 1
            self._lines.append(["writeln"])
            return root.data
        elif root.data[0] == 'write':
            self.count += 1
            if len(root.data) > 1:
            # handle string
                temp_v = root.data[1]
                self._lines.append([temp(temp_number), equals(), root.data[1]])
                self._lines.append(['writes', temp(temp_number)])
            else:
                # handle expression
                temp_v = iter_flatten(self._gen_ir(root.children[0], temp_number))
                self._lines.append(['write', temp_v[-1]])
            return temp_v
        elif root.data[0] == ':=':
            val = iter_flatten([self._gen_ir(root.children[1], temp_number)])
            var = self._gen_ir(root.children[0], temp_number)
            self._lines.append([var, equals(), val[0]])
        elif root.data[0] == 'read':
            var = self._gen_ir(root.children[0], temp_number)
            self._lines.append([var, equals(), temp(temp_number)])
            self._lines.append(['read', var])

        return "none"

    def _gen_unary_op_ir(self, root, temp_number):
        if root.data[0] == '-':
            self._lines.append([temp(temp_number), equals(), temp(0), minus(), temp(temp_number - 1)])
        else:
            self._lines.append([temp(temp_number), equals(), temp(0), plus(), temp(temp_number - 1)])
        return temp(temp_number)

    def _gen_term_ir(self, root, temp_number):
        return [self._gen_ir(c, temp_number) for c in root.children]

    def _gen_expression_ir(self, root, temp_number):
        return [self._gen_ir(c, temp_number) for c in root.children]

    def _gen_pom_term_star_ir(self, root, temp_number):
        left = iter_flatten(self._gen_ir(root.children[0], temp_number + 1))[0]
        right = iter_flatten(self._gen_ir(root.children[1], temp_number + 2))[0]
        self._lines.append([temp(temp_number), equals(), left, plus_or_minus(root.data[0]), right])
        return temp(temp_number)

    def _gen_factor_ir(self, root, temp_number):
        if root.data:
            self._lines.append([temp(temp_number), equals(), str(root.data[0])])
            return temp(temp_number)
        else:
            return self._gen_ir(root.children[0], temp_number)

    def _gen_td_factor_star_ir(self, root, temp_number):
        left = iter_flatten(self._gen_ir(root.children[0], temp_number + 1))[0]
        right = iter_flatten(self._gen_ir(root.children[1], temp_number + 2))[0]
        self._lines.append([temp(temp_number), equals(), left, times_or_divide(root.data[0]), right])
        return temp(temp_number)

    def _gen_variable_ir(self, root, temp_number):
        return root.data[0]

    def _gen_negate_ir(self, root, temp_number):
        if root.data[0] == '-':
            right = iter_flatten(self._gen_ir(root.children[0], temp_number + 1))[0]
            self._lines.append([temp(temp_number), equals(), temp(0), minus(), right])
            return temp(temp_number)
        else:
            return iter_flatten(self._gen_ir(root.children[0], temp_number))[0]

    def _gen_ir(self, root, temp_number):
        if debug:
            self._lines += [root.type]
        if root.type == 'program':
            return [self._gen_ir(c, temp_number) for c in root.children]
        elif root.type == 'compoundStatement':
            results = []
            for c in root.children:
                results.append(self._gen_ir(c, temp_number))
                #if c.data[0] == ':=':
                #    temp_number += 1
            return results
        elif root.type == 'statement':
        #if self.count % 2 == 1 and False:
        #if self.count == 7:
        #    for l in self._lines:
        #        print l
        #    sys.exit(0)
        #print ''
            return self._gen_statement_ir(root, temp_number)
            #r = self._gen_statement_ir(root, temp_number)
            #if root.data == ':=':
            #    temp_number += 1

        elif root.type == 'expression':
            return self._gen_expression_ir(root, temp_number)
        elif root.type == 'factor':
            return self._gen_factor_ir(root, temp_number)
        elif root.type == 'unaryOp':
            return self._gen_unary_op_ir(root, temp_number)
        elif root.type == 'term':
            return self._gen_term_ir(root, temp_number)
        elif root.type == 'pomTermStar':
            return self._gen_pom_term_star_ir(root, temp_number)
        elif root.type == 'tdFactorStar':
            return self._gen_td_factor_star_ir(root, temp_number)
        elif root.type == 'variable':
            return self._gen_variable_ir(root, temp_number)
        elif root.type == 'negate':
            return self._gen_negate_ir(root, temp_number)
        return "none"

    def generate_irt(self):
        special_registers = 1  # offset usable registers by number of internally used registers, eg 0 in R0
        ir = self._gen_ir(self._ast_root, special_registers)
        return self._lines


def equals():
    return '='


def temp(n):
    return '_t' + str(n)


def times():
    return '*'


def divide():
    return '/'


def plus():
    return '+'


def minus():
    return '-'


def times_or_divide(t):
    if t == '*':
        return times()
    else:
        return divide()


def plus_or_minus(t):
    if t == '+':
        return plus()
    else:
        return minus()


# How to flatten nested lists of different nesting levels
# Adapted from http://stackoverflow.com/questions/716477/join-list-of-lists-in-python
def iter_flatten(root):
    def _iter_flatten(r):
        if isinstance(r, (list, tuple)):
            for element in r:
                for e in _iter_flatten(element):
                    yield e
        else:
            yield r

    return list(_iter_flatten(root))
