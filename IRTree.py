import AST
import sys

__author__ = 'sambodanis'


class irt:

    def __init__(self, ast):
        self._ast_root = ast
        self._lines = []
        self.count = 0

    def _gen_statement_ir(self, root, temp_number):
        if root.data[0] == 'writeln':
            self.count += 1
            self._lines.append("writeln")
            return root.data
        elif root.data[0] == 'write':
            self.count += 1
            #self._lines.append("writeln")
            if len(root.data) > 1:
               # handle string
                temp = root.data[1]
            else:
                # handle expression
                temp = iter_flatten(self._gen_ir(root.children[0], temp_number))
                #print temp
                self._lines.append('write ' + temp[-1])
            return temp
        return "none"

    def _gen_unary_op_ir(self, root, temp_number):
        if root.data[0] == '-':
            #self._lines.append(temp(temp_number) + equals() + '-1' + times() + temp(temp_number - 1))
            self._lines.append(temp(temp_number) + equals() + temp(0) + minus() + temp(temp_number - 1))
        #else:
        #    self._lines.append(temp(temp_number) + equals() + '1' + times() + temp(temp_number - 1))
        return temp(temp_number)

    def _gen_expression_ir(self, root, temp_number):
        if len(root.children) == 1:
            if root.children[0].type == 'term':
                return self._gen_ir(root.children[0], temp_number + 1)
            return self._gen_ir(root.children[0], temp_number)
        elif len(root.children) == 2:
            if root.children[0].type == 'term':
                if len(root.children[0].children) == 2:
                    left = self._gen_ir(root.children[0], temp_number + 1)
                    #self._lines.append(temp(temp_number) + equals() + left[0]) # redundant 'tn = tn'
                    return self._gen_ir(root.children[1], temp_number + 2)

                else:

                    left = self._gen_ir(root.children[0], temp_number)
                    #self._lines.append(temp(temp_number) + equals() + left[0]) # redundant 'tn = tn'
                    return self._gen_ir(root.children[1], temp_number + 1)
        elif len(root.children) == 3:
            left = [self._gen_ir(c, temp_number + i) for i, c in enumerate(root.children[1::-1])]  # First two children
            right = self._gen_ir(root.children[2], temp_number + 2)
            return temp(temp_number + 2)
        return [self._gen_ir(c, temp_number + i) for i, c in enumerate(root.children[::-1])]  # Children in Reverse

    def _gen_pom_term_star_ir(self, root, temp_number):
        left = temp(temp_number - 1)
        left_pseudo = iter_flatten(self._gen_ir(root.children[0], temp_number + 1))
        if len(root.children) > 1:
            right = self._gen_ir(root.children[1], temp_number + 2)
            self._lines.append(temp(temp_number) + equals() + left + plus_or_minus(root.data[0]) + right)
        else:
            self._lines.append(temp(temp_number) + equals() + left + plus_or_minus(root.data[0]) + left_pseudo[-1])
        return temp(temp_number)

    def _gen_factor_ir(self, root, temp_number):
        if root.data:
            self._lines.append(temp(temp_number) + equals() + str(root.data[0]))
            return temp(temp_number)
        else:
            return self._gen_ir(root.children[0], temp_number)

    def _gen_td_factor_star_ir(self, root, temp_number):
        left = temp(temp_number - 1)
        left_pseudo = iter_flatten(self._gen_ir(root.children[0], temp_number + 1))
        if len(root.children) > 1:
            right = self._gen_ir(root.children[1], temp_number + 2)
            self._lines.append(temp(temp_number) + equals() + left + times_or_divide(root.data[0]) + right)
        else:
            self._lines.append(temp(temp_number) + equals() + left + times_or_divide(root.data[0]) + left_pseudo[-1])
        return temp(temp_number)

    def _gen_ir(self, root, temp_number):
        #assert '_t-1' not in ''.join(self._lines)
        if root.type == 'program':
            return [self._gen_ir(c, temp_number) for c in root.children]
        elif root.type == 'compoundStatement':
            return [self._gen_ir(c, temp_number) for c in root.children]
        elif root.type == 'statement':
            #print iter_flatten(self._gen_statement_ir(root, temp_number))
            #if self.count % 2 == 1 and False:
            if self.count == 1:
                #print (self._gen_statement_ir(root, temp_number))
                #print self._lines
                for l in self._lines:
                    print l
                #sys.exit(0)
                print ''
            return self._gen_statement_ir(root, temp_number)
        elif root.type == 'expression':
            return self._gen_expression_ir(root, temp_number)
        elif root.type == 'factor':
            return self._gen_factor_ir(root, temp_number)
        elif root.type == 'unaryOp':
            return self._gen_unary_op_ir(root, temp_number)
        elif root.type == 'term':
            return [self._gen_ir(c, temp_number + (-1 if (c.type == 'factor' and len(root.children) == 2 and root.children[1].type == 'tdFactorStar') else 0)) for c in root.children]
            #return [self._gen_ir(c, temp_number) for c in root.children]
        elif root.type == 'pomTermStar':
            return self._gen_pom_term_star_ir(root, temp_number)
        elif root.type == 'tdFactorStar':
            return self._gen_td_factor_star_ir(root, temp_number)
        return "none"

    def generate_irt(self):
        #irt_root = irtree()
        special_registers = 1 # offset usable registers by number of internally used registers, eg 0 in R0
        ir = self._gen_ir(self._ast_root, special_registers)
        return self._lines


def equals():
    return ' = '


def temp(n):
    return '_t' + str(n)


def times():
    return ' * '

def minus():
    return ' - '

def times_or_divide(t):
    if t == '*':
        return ' * '
    else:
        return ' / '

def plus_or_minus(t):
    if t == '+':
        return ' + '
    else:
        return ' - '

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


class irtree:

    def __init__(self):
        self.op = None
        self.subtree = []
        pass

