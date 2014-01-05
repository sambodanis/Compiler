import AST
import sys

__author__ = 'sambodanis'

debug = False


class irt:

    def __init__(self, ast):
        self._ast_root = ast
        self._lines = []
        self.count = 0
        self._label_num = 0

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
                #print temp_v
                if len(temp_v) > 1:
                    self._lines.append(['write', temp_v[0], temp_v[1]])
                else:
                    self._lines.append(['write', temp_v[-1]])
            return temp_v
        elif root.data[0] == ':=':
            val = iter_flatten([self._gen_ir(root.children[1], temp_number)])
            var = self._gen_ir(root.children[0], temp_number)
            #print val, 'v', var
            if len(var) == 1 and len(val) == 1:
                #self._lines.append(['hi'])

                self._lines.append([var[0], equals(), val[0]])
            else:
                #self._lines.append(['hi'])
                #self._lines.append([var[0], var[1], equals(), val[0]])
                self._lines.append(var + [equals()] + val)
        elif root.data[0] == 'read':
            var = self._gen_ir(root.children[0], temp_number)
            #print 'v', var
            if isinstance(var, list):
                var = var[0]
            self._lines.append([var, equals(), temp(temp_number)])
            self._lines.append(['read', var])
        elif root.data[0] == 'if':
            # Keeping all this commented out stuff around because logical operators extn?
            #if root.children[0].data[0] in ['>', '<=']:
            #    print root.children[0].data[0]
            #    t = root.children[0].data[0]
            #    root.children[0].data[0] = '<' if t == '<=' else '>='
            #    condition = self._gen_ir(root.children[0], temp_number)
            #    root.children[0].data[0] = t
            #else:
            #    condition = self._gen_ir(root.children[0], temp_number)
            condition = self._gen_ir(root.children[0], temp_number)
            true_label = label(self._label_num)
            self._label_num += 1
            end_label = label(self._label_num)
            self._label_num += 1
            #if root.children[0].data[0] == '>':
            #    intermediate_label = label(self._label_num)
            #    self._label_num += 1

            #self._lines.append(['ifZ', condition, 'Goto', true_label if root.children[0].data[0] != '>' else intermediate_label])
            self._lines.append(['ifZ', condition, 'Goto', true_label])
            # <= --> < || ==
            #if root.children[0].data[0] == '<=':
            #    root.children[0].data = ['==']
            #    condition = self._gen_ir(root.children[0], temp_number)
            #    self._lines.append(['ifZ', condition, 'Goto', true_label])

            self._gen_ir(root.children[2], temp_number) if len(root.children) == 3 else None
            self._lines.append(['Goto', end_label])
            #if root.children[0].data[0] == '>':
            #    self._lines.append([intermediate_label])

            # > --> >= && !=
            #if root.children[0].data[0] == '>':
            #    root.children[0].data = ['!=']
            #    condition = self._gen_ir(root.children[0], temp_number)
            #    self._lines.append(['ifZ', condition, 'Goto', true_label])
            #    self._lines.append(['Goto', end_label])

            self._lines.append([true_label])
            self._gen_ir(root.children[1], temp_number)
            self._lines.append([end_label])
        elif root.data[0] == 'repeat':
            #root.children[1].data[0] = self._inverted_conditions[]
            start_label = label(self._label_num)
            self._label_num += 1
            #end_label = label(self._label_num)
            #self._label_num += 1
            self._lines.append([start_label])
            self._gen_ir(root.children[0], temp_number)
            condition = self._gen_ir(root.children[1], temp_number)
            self._lines.append(['ifZ', condition, 'Goto', start_label])


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
        left = iter_flatten(self._gen_ir(root.children[0], temp_number + 1))
        right = iter_flatten(self._gen_ir(root.children[1], temp_number + 2))
        self._lines.append([temp(temp_number), equals()] + left + [plus_or_minus(root.data[0])] + right)
        return temp(temp_number)

    def _gen_factor_ir(self, root, temp_number):
        if root.data:
            self._lines.append([temp(temp_number), equals(), str(root.data[0])])
            return temp(temp_number)
        else:
            return self._gen_ir(root.children[0], temp_number)

    def _gen_td_factor_star_ir(self, root, temp_number):
        left = ' '.join(iter_flatten(self._gen_ir(root.children[0], temp_number + 1)))
        right = ' '.join(iter_flatten(self._gen_ir(root.children[1], temp_number + 2)))

        self._lines.append([temp(temp_number), equals(), left, times_or_divide(root.data[0]), right])
        return temp(temp_number)

    def _gen_variable_ir(self, root, temp_number):
        if len(root.children) == 1:
            return [root.data[0], '[' + self._gen_ir(root.children[0], temp_number + 1) + ']']
        else:
            return [root.data[0]]

    def _gen_negate_ir(self, root, temp_number):
        if root.data[0] == '-':
            right = ' '.join(iter_flatten(self._gen_ir(root.children[0], temp_number + 1)))
            self._lines.append([temp(temp_number), equals(), temp(0), minus(), right])
            return temp(temp_number)
        else:
            return ' '.join(iter_flatten(self._gen_ir(root.children[0], temp_number)))

    def _gen_relation_ir(self, root, temp_number):
        left = iter_flatten(self._gen_ir(root.children[0], temp_number + 1))[0]
        right = iter_flatten(self._gen_ir(root.children[1], temp_number + 2))[0]
        self._lines.append([temp(temp_number), equals(), left, root.data[0] if root.data[0] != '=' else '==', right])
        return temp(temp_number)

    def _gen_lpElseCompoundStatementRp_ir(self, root, temp_number):
        return self._gen_ir(root.children[0], temp_number)

    def _gen_program_front_ir(self, root, temp_number):
        pass
        for array in root.children:
            self._lines.append([temp(temp_number), equals(), 'Alloc', str(int(array.data[1]))])
            self._lines.append([array.data[0], equals(), temp(temp_number)])
            temp_number += 1
        return temp_number

    def _gen_bracketed_expression_star_ir(self, root, temp_number):
        return iter_flatten(self._gen_ir(root.children[0], temp_number))[0]

    def _gen_ir(self, root, temp_number):
        if debug:
            self._lines += [root.type]
        if root.type == 'program':
            if len(root.children) == 3:
                temp_number += self._gen_ir(root.children[0], temp_number)
                self._gen_ir(root.children[1], temp_number)

            elif len(root.children) == 2:
                temp_number += self._gen_ir(root.children[0], temp_number)
                self._gen_ir(root.children[1], temp_number)
            else:
                self._gen_ir(root.children[0], temp_number)
            #return [self._gen_ir(c, temp_number) for c in root.children]
        elif root.type == 'programFront':
            return self._gen_program_front_ir(root, temp_number)
        elif root.type == 'compoundStatement':
            results = []
            for c in root.children:
                results.append(self._gen_ir(c, temp_number))
            return results
        elif root.type == 'statement':
        #if self.count % 2 == 1 and False:
        #if self.count == 7:
        #    for l in self._lines:
        #        print l
        #    sys.exit(0)
        #print ''
            return self._gen_statement_ir(root, temp_number)
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
        elif root.type == 'relation':
            return self._gen_relation_ir(root, temp_number)
        elif root.type == 'lpElseCompoundStatementRp':
            return self._gen_lpElseCompoundStatementRp_ir(root, temp_number)
        elif root.type == 'bracketedExpressionStar':
            return self._gen_bracketed_expression_star_ir(root, temp_number)
        #elif root.type == 'functionStar':

        return "none"

    def generate_irt(self):
        special_registers = 1  # offset usable registers by number of internally used registers, eg 0 in R0
        ir = self._gen_ir(self._ast_root, special_registers)
        return self._lines


def equals():
    return '='


def temp(n):
    return '_t' + str(n)


def label(n):
    return '~L' + str(n)


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
