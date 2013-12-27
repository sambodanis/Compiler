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
                return root.data
        elif root.data[0] == 'write':
            self.count += 1
            self._lines.append("")
            if len(root.data) > 1:
               # handle string
                temp = root.data[1]
            else:
                # handle expression
                #temp = iter_flatten(self._gen_ir(root.children[0], temp_number + 1))
                temp = iter_flatten(self._gen_ir(root.children[0], temp_number))
                #print temp
                self._lines.append('write ' + temp[-1])
            return temp
        return "none"

    def _gen_unary_op_ir(self, root, temp_number):
        if root.data[0] == '-':
            self._lines.append(temp(temp_number) + equals() + '-1' + times() + temp(temp_number - 1))
        else:
            self._lines.append(temp(temp_number) + equals() + '1' + times() + temp(temp_number - 1))
        return temp(temp_number)

    def _gen_expression_ir(self, root, temp_number):
        if len(root.children) == 1:
            raise NameError('expression has single child...')
        elif len(root.children) == 2:
            if root.children[0].type == 'term':
                left = self._gen_ir(root.children[0], temp_number)
                self._lines.append(temp(temp_number) + equals() + left[0])
                return self._gen_ir(root.children[1], temp_number + 1)

                #right = self._gen_ir(root.children[1], temp_number+2)
                #self._lines.append(temp(temp_number) + equals())
        elif len(root.children) == 3:
            left = [self._gen_ir(c, temp_number + i) for i, c in enumerate(root.children[1::-1])] # First two children in reverse order
            right = self._gen_ir(root.children[2], temp_number + 2)
            return temp(temp_number + 2)
        else:
            return [self._gen_ir(c, temp_number + i) for i, c in enumerate(root.children[::-1])] #the fancy reverse

    def _gen_pom_term_star_ir(self, root, temp_number):
        left = temp(temp_number - 1)
        left_pseudo = iter_flatten(self._gen_ir(root.children[0], temp_number + 1))
        if len(root.children) > 1:
            right = self._gen_ir(root.children[1], temp_number + 2)
            self._lines.append(temp(temp_number) + equals() + left + plus_or_minus(root.data[0]) + right)
        else:
            self._lines.append(temp(temp_number) + equals() + left + plus_or_minus(root.data[0]) + left_pseudo[-1])
        return temp(temp_number)

    def _gen_ir(self, root, temp_number):
        if root.type == 'program':
            return [self._gen_ir(c, temp_number) for c in root.children]
        elif root.type == 'compoundStatement':
            return [self._gen_ir(c, temp_number) for c in root.children]
        elif root.type == 'statement':
            #print iter_flatten(self._gen_statement_ir(root, temp_number))
            if self.count == 1:
                #print (self._gen_statement_ir(root, temp_number))
                #print self._lines
                for l in self._lines:
                    print l
                sys.exit(0)
            return self._gen_statement_ir(root, temp_number)

        elif root.type == 'expression':
            return self._gen_expression_ir(root, temp_number)
        elif root.type == 'factor':
            if root.data:
                self._lines.append(temp(temp_number) + equals() + str(root.data[0]))
                return temp(temp_number)
            else:
                return self._gen_ir(root.children[0], temp_number)
        elif root.type == 'unaryOp':
            return self._gen_unary_op_ir(root, temp_number)
        elif root.type == 'term':
            return [self._gen_ir(c, temp_number) for c in root.children]
        elif root.type == 'pomTermStar':
            return self._gen_pom_term_star_ir(root, temp_number)

        return "none"

    def generate_irt(self):
        #irt_root = irtree()
        ir = self._gen_ir(self._ast_root, 0)
        return ir


def equals():
    return ' = '


def temp(n):
    return '_t' + str(n)


def times():
    return ' * '

def plus_or_minus(t):
    if t == '+':
        return ' + '
    else:
        return ' - '

# how to flatten nested lists of different nesting levels
# from http://stackoverflow.com/questions/716477/join-list-of-lists-in-python

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

