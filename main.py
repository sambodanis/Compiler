import parser
import AST
import pydot
import IRTree

__author__ = 'sambodanis'

lift_and_remove_types = ['plusOrMinus', 'timesOrDivide']
lift_and_remove_parents = ['pomTermStar', 'tdFactorStar', 'unaryOp']


def main():
    with open("TestCases/test1.le") as myfile:
        data = "\n".join(line.rstrip() for line in myfile)
    p = parser.ASTGenerator()
    ast = p.parse(data)
    simplify_ast(ast)
    print_ast(ast, True)
    irt_generator = IRTree.irt(ast)
    irt = irt_generator.generate_irt()
    print irt


def simplify_ast(ast):
    if not ast:
        return
    if ast.children:
        if ast.type == 'compoundStatement':
            root = ast.children[0]
            children = []
            while root is not None:
                if len(root.children) > 1:
                    children.append(root.children[0])
                if len(root.children) > 0:
                    root = root.children[-1]
                else:
                    root = None
            ast.children = children
        elif ast.type in lift_and_remove_parents:
        #elif ast.type == 'pomTermStar' or ast.type == 'tdFactorStar' or ast.type == 'unaryOp':
            ast.data = [c.data for c in ast.children if c and c.type in lift_and_remove_types][0]# c.type == 'plusOrMinus' or c.type == 'timesOrDivide')][0]
            ast.children = [c for c in ast.children if c and c.type not in lift_and_remove_types]
    for i, c in enumerate(ast.children):
        simplify_ast(c)
    try: # remove potentially null children from rules like: A -> B | empty
        while True:
            ast.children.remove(None)
    except:
        pass





def print_ast(ast, write_to_file):
    print 'PrintingAST:Start'
    def print_ast_r(astnode, indentation, g, node_carry, h):
        if not astnode:
            return
        #for dat in astnode.data:
        #    print " " * indentation, dat
        t = astnode.type
        if t == 'relation' or t == 'unaryOp' or t == 'statement' or t == 'expression' or \
                        t == 'expression' or t == 'term' or t == 'factor':
            indentation += 1
        else:
            indentation += 1
        source = h[0]
        for c in astnode.children:
            h[0] += 1
            if c:
                if node_carry:
                    if c.data:
                        #print 'd', c.type
                        g.add_node(pydot.Node(str(h[0]), label=(str(c.type) + ' -> ' + str(c.data))))
                    else:
                        #print 'nd', c.type
                        g.add_node(pydot.Node(str(h[0]), label=str(c.type)))
                    g.add_edge(pydot.Edge(str(source), str(h[0])))
                node_carry = str(h[0])
            print_ast_r(c, indentation, g, node_carry, h)

    graph = pydot.Dot(graph_type='digraph')
    print_ast_r(ast, 0, graph, "root", [0])
    if write_to_file:
        graph.write_png('example1_graph.png')
    print 'PrintingAST:Done'


if __name__ == '__main__':
    main()
