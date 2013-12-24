import ply.lex as lex


#reserved = {
#   'array': 'ARRAY',
#   'begin': 'BEGIN',
#   'else': 'ELSE',
#   'end': 'END',
#   'if': 'IF',
#   'read': 'READ',
#   'repeat': 'REPEAT',
#   'until': 'UNTIL',
#   'write': 'WRITE',
#   'writeln': 'WRITELN'
#}
#
#tokens = ['INTEGER', 'CONSTANT', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN', 'EQUALS',
#         'LT', 'LE', 'GT', 'GE', 'NE', 'ASSIGNMENT' 'COMMA', 'SEMI', 'STRING', 'ID', 'NEWLINE'] + list(reserved.values())
#
#
#class Lexer:

reserved = {
    'array': 'ARRAY',
    'begin': 'BEGIN',
    'else': 'ELSE',
    'end': 'END',
    'if': 'IF',
    'read': 'READ',
    'repeat': 'REPEAT',
    'until': 'UNTIL',
    'write': 'WRITE',
    'writeln': 'WRITELN'
}

tokens = ['CONSTANT', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN',
          'LSBRACKET', 'RSBRACKET',  'EQUALS', 'LT', 'LE', 'GT', 'GE', 'NE', 'ASSIGNMENT',
          'COMMA', 'SEMI', 'STRING', 'ID'] + list(reserved.values())

t_ignore = ' \t'

t_EQUALS = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSBRACKET = r'\['
t_RSBRACKET = r'\]'
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_NE = r'!='
t_ASSIGNMENT = r':='
t_COMMA = r'\,'
t_SEMI = r';'
t_STRING = r'\'.*?(\'\'.*?\'\')*\''


def t_CONSTANT(t):
    r'[0-9]*\.[0-9]*(e(-)?[0-9]*)?'
    t.value = float(t.value)
    return t


def t_COMMENT(t):
    # Still needs work
    r'{(^{)*.*}'
    pass


#def t_NEWLINE(t):
#    r'\n+'
#    t.lexer.lineno += t.value.count("\n")
#    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID') # Check for reserved words
    return t


def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()


#   # Build the lexer
#   def build(self, **kwargs):
#       self.lexer = lex.lex(module=self, **kwargs)
#
#   # Test it output
#   def test(self, data):
#       self.lexer.input(data)
#       while True:
#           tok = self.lexer.token()
#           if not tok:
#               break
#           print tok
#       print tok
#
#
#lx = Lexer()
#lx.build()
##lx.test("3 + 4")
l = lex.lex()

#with open("TestCases/test1.le") as myfile:
#    data = "".join(line.rstrip() for line in myfile)
#l.input(data)
#while True:
#    tok = l.token()
#    if not tok:
#        break
#    else:
#        print tok
