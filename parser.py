


import ply.lex as lex
import ply.yacc as yacc
#import lexer
from lexer import tokens
import AST
import os


class Parser(object):
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()


    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = {}
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"
        #print self.debugfile, self.tabmodule

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def parse(self, data):
        #while 1:
        #    try:
        #        s = raw_input('calc > ')
        #        #s = data
        #    except EOFError:
        #        break
        #    if not s: continue
        #    yacc.parse(s)
        return yacc.parse(data)


class ASTGenerator(Parser):

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

    def t_CONSTANT(self, t):
        r'[0-9]*\.[0-9]*(e(-)?[0-9]*)?'
        t.value = float(t.value)
        return t


    def t_COMMENT(self, t):
        #TODO Still needs work ?
        r'{.*(^{)*.*}'
        #r'{.*}'
        #r'{.*(^((?!}).)*$).*}'
        #print t
        pass


    #def t_NEWLINE(self, t):
    #    r'\n+'
    #    t.lexer.lineno += t.value.count("\n")
    #    return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        #t.lexer.lineno += len(t.value)
        t.lexer.lineno += t.value.count("\n")




    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID') # Check for reserved words
        return t


    def t_error(self, t):
        print("Illegal character %s" % t.value[0])
        t.lexer.skip(1)


    #lexer = lex.lex()


    #l = lex.lex()

    #with open("TestCases/testa.le") as myfile:
    #    data = "\n".join(line.rstrip() for line in myfile)
        #i = 0
        #while i < len(data):
        #    if data[i] == '{':
        #        print 'here'
        #        data = data[:i] + '\n' + data[i:]
        #        i += 1
        #    i += 1

    #l.input(data)
    #while True:
    #    tok = l.token()
    #    if not tok:
    #        break
    #    else:
    #        print tok


    trace = False

    start = 'program'

    precedence = (
        #('nonassoc', 'LESSTHAN', 'GREATERTHAN'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE')
    )

    def p_program(self, p):
        '''program : programFront compoundStatement'''
        # if trace: print 'a'
        if p[1]:
            p[0] = AST.AST('program', None, p[1:], False)
        else:
            p[0] = AST.AST('program', None, p[2:], False)

    def p_compoundStatement(self, p):
        '''compoundStatement : BEGIN statementStar END'''
        # if trace: print 'b'
        #root = p[2]
        #children = []
        #while root is not None:
        #    if len(root.children) > 1:
        #        children.append(root.children[0])
        #    root = root.children[-1]
        #p[0] = AST.AST('compoundStatement', None, children, False)
        p[0] = AST.AST('compoundStatement', None, p[2], False)

    def p_programFront(self, p):
        '''programFront : empty
        | ARRAY declaration commaDeclaration SEMI
        '''
        # if trace: print 'c'
        if len(p) > 2:
            print p[2].data
            p[0] = AST.AST('programFront', None, [p[2], p[3]], False)


        #'''commaDeclaration : empty
        #| COMMA declaration
        #| COMMA declaration commaDeclaration'''

    def p_commaDeclaration(self, p):
        '''commaDeclaration : empty
        | COMMA declaration commaDeclaration'''
        # if trace: print 'd'
        if len(p) > 2:
            p[0] = AST.AST('commaDeclaration', None, p[2:], False)



    def p_declaration(self, p):
        '''declaration : ID LSBRACKET CONSTANT RSBRACKET'''
        # if trace: print 'e'
        #TODO check if this is actually a left and right bracket
        p[0] = AST.AST('declaration', [p[1], p[3]], None, True)

    #| statement SEMI
    def p_statementStar(self, p):
        '''statementStar : statement SEMI statementStar
        | empty
        '''
        # if trace: print 'f'
        if len(p) > 2:
            p[0] = AST.AST('statementStar', None, [p[1], p[3]], False)


    def p_statement(self, p):
        '''statement : variable ASSIGNMENT expression
        | READ LPAREN variable RPAREN
        | WRITE LPAREN expression RPAREN
        | WRITE LPAREN STRING RPAREN
        | WRITELN
        | IF expression relation expression compoundStatement lpElseCompoundStatementRp
        | REPEAT compoundStatement UNTIL expression relation expression
        '''
        # if trace: print 'g'
        if len(p) == 2:
            p[0] = AST.AST('statement', p[1], None, True)
        elif len(p) == 4:
            p[0] = AST.AST('statement', p[2], [p[1], p[3]], False)
        elif len(p) == 5:
            if isinstance(p[3], AST.AST):
                p[0] = AST.AST('statement', p[1], p[3], False)
            else:
                p[0] = AST.AST('statement', [p[1], p[3]], None, True) # Check if leaf
        elif len(p) == 7:
            if p[1] == 'if':
                p[0] = AST.AST('statement', p[1], p[2:], False)
            else:
                p[0] = AST.AST('statement', p[1], [p[2]] + p[4:], False)


    def p_lpElseCompoundStatementRp(self, p):
        '''lpElseCompoundStatementRp : ELSE compoundStatement
        | empty
        '''
        # if trace: print 'g'
        if len(p) > 2:
            p[0] = AST.AST('lpElseCompoundStatementRp', p[1], p[2], False)


    #def p_lpElseCompoundStatementRp(self, p):
    #    '''lpElseCompoundStatementRp : LPAREN ELSE compoundStatement RPAREN
    #    | empty
    #    '''


    def p_relation(self, p):
        '''relation : GT
        | GE
        | EQUALS
        | NE
        | LE
        | LT
        '''
        # if trace: print 'i'
        p[0] = AST.AST('relation', p[1], None, False)


    #def p_expression(self, p):
    #   '''expression : unaryOp term ( ( PLUS | MINUS ) term )*'''


    def p_expression(self, p):
        '''expression : unaryOp term pomTermStar'''
        # if trace: print 'j'
        p[0] = AST.AST('expression', None, p[1:], False)


    def p_plusOrMinus(self, p):
        '''plusOrMinus : PLUS
        | MINUS'''
        # if trace: print 'k'
        p[0] = AST.AST('plusOrMinus', p[1], None, False)

    def p_pomTermStar(self, p):
        '''pomTermStar : pomTermStar plusOrMinus term
        | plusOrMinus term
        | empty
        '''
        # if trace: print 'l'
        if len(p) > 2:
            p[0] = AST.AST('pomTermStar', None, p[1:], False)
        #print p[0]

    def p_unaryOp(self, p):
        '''unaryOp : plusOrMinus
        | empty'''
        # if trace: print 'm'
        if p[1] != None:
            p[0] = AST.AST('unaryOp', None, p[1], False)


    def p_term(self, p):
        '''term : factor tdFactorStar'''
        # if trace: print 'n'
        p[0] = AST.AST('term', None, p[1:], False)


    def p_timesOrDivide(self, p):
        '''timesOrDivide : TIMES
        | DIVIDE'''
        # if trace: print 'o'
        p[0] = AST.AST('timesOrDivide', p[1], None, False)


    def p_tdFactorStar(self, p):
        '''tdFactorStar : tdFactorStar timesOrDivide factor
        | timesOrDivide factor
        | empty
        '''
        # if trace: print 'p'
        if len(p) > 2:
            p[0] = AST.AST('tdFactorStar', None, p[1:], False)


    def p_factor(self, p):
        '''factor : variable
        | CONSTANT
        | LPAREN expression RPAREN
        '''
        # if trace: print 'q'
        if len(p) == 2:
            if isinstance(p[1], AST.AST):
                p[0] = AST.AST('factor', None, p[1], False)
            else:
                p[0] = AST.AST('factor', p[1], None, True)
        else:
            p[0] = AST.AST('factor', None, p[2], False)


    def p_variable(self, p):
        '''variable : ID bracketedExpressionStar'''
        # if trace: print 'r'
        p[0] = AST.AST('variable', p[1], None, True)

    def p_bracketedExpressionStar(self, p):
        '''bracketedExpressionStar : LSBRACKET expression RSBRACKET
        | empty'''
        if len(p) > 2:
            p[0] = AST.AST('bracketedExpressionStar', None, p[2], False)
        else:
            p[0] = p[1]

    def p_empty(self, p):
        'empty :'
        p[0] = None
        pass


    def p_error(self, p):
        if p:
            print p
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

    #def printAST(astnode, indentation, g, node_carry, h):
    #    if not astnode: return
    #    for dat in astnode.data:
    #        print " " * indentation, dat
    #    t = astnode.type
    #    if t == 'relation' or t == 'unaryOp' or t == 'statement' or t == 'expression' or \
    #                    t == 'expression' or t == 'term' or t == 'factor':
    #        indentation += 1
    #    else:
    #        indentation += 1
    #    source = h[0]
    #    for c in astnode.children:
    #        h[0] += 1
    #        if c:
    #            if node_carry:
    #                if c.data:
    #                    g.add_node(pydot.Node(str(h[0]), label=(str(c.type) + ' -> ' + str(c.data))))
    #                else:
    #                    g.add_node(pydot.Node(str(h[0]), label=str(c.type)))
    #                g.add_edge(pydot.Edge(str(source), str(h[0])))
    #            node_carry = str(h[0])
    #        printAST(c, indentation, g, node_carry, h)


    #with open("TestCases/test0.le") as myfile:
    #    data = "\n".join(line.rstrip() for line in myfile)

    #p = yacc.yacc()

    #def parse(self, data):
    #    p = yacc.yacc()
    #    return p.parse(data)


    #ast = p.parse(data)


    #graph = pydot.Dot(graph_type='digraph')
    #printAST(ast, 0, graph, "root", [0])
    #graph.write_png('example1_graph.png')

#TODO: Change +-*/ to be roots of their respective subtrees