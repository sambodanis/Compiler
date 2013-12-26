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

t_ignore = ' \t' # ?

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
#t_ignore_COMMENT = r'{(^})*}'

def t_CONSTANT(t):
    r'[0-9]*\.[0-9]*(e(-)?[0-9]*)?'
    t.value = float(t.value)
    return t


def t_COMMENT(t):
    #TODO handle multi-line comments
    r'{(.|\n)*?}'
    #r'{.*(^{)*.*}'
    #r'{.*}'
    #r'{.*(^((?!}).)*$).*}'
    #print t
    pass


#def t_NEWLINE(t):
#    r'\n+'
#    t.lexer.lineno += t.value.count("\n")
#    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    #t.lexer.lineno += len(t.value)
    t.lexer.lineno += t.value.count("\n")




def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID') # Check for reserved words
    return t


def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()


l = lex.lex()

with open("TestCases/testd.le") as myfile:
    data = "\n".join(line.rstrip() for line in myfile)
    #i = 0
    #while i < len(data):
    #    if data[i] == '{':
    #        print 'here'
    #        data = data[:i] + '\n' + data[i:]
    #        i += 1
    #    i += 1

l.input(data)
while True:
    tok = l.token()
    if not tok:
        break
    else:
        print tok
