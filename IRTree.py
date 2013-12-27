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


    def _gen_ir(self, root, temp_number):
        if root.type == 'program':
            return [self._gen_ir(c, temp_number) for c in root.children]
        elif root.type == 'compoundStatement':
            return [self._gen_ir(c, temp_number) for c in root.children]
        elif root.type == 'statement':
            #print iter_flatten(self._gen_statement_ir(root, temp_number))
            if self.count == 2:
                print (self._gen_statement_ir(root, temp_number))
                print self._lines
                sys.exit(0)
            return self._gen_statement_ir(root, temp_number)

        elif root.type == 'expression':
            return [self._gen_ir(c, temp_number + i) for i, c in enumerate(root.children[::-1])] #the fancy reverse
        elif root.type == 'factor':
            # emit
            self._lines.append(temp(temp_number) + equals() + str(root.data[0]))
            return temp(temp_number)
        elif root.type == 'unaryOp':
            return self._gen_unary_op_ir(root, temp_number)
        elif root.type == 'term':
            return [self._gen_ir(c, temp_number) for c in root.children]
        elif root.type == 'plusOrMinus':
            return root.data[0]
        #elif root.type == ''
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

