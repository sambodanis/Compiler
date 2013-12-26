import parser
import AST
import pydot

__author__ = 'sambodanis'


def main():
    with open("TestCases/testd.le") as myfile:
        data = "\n".join(line.rstrip() for line in myfile)
    p = parser.ASTGenerator()
    ast = p.parse(data)
    simplify_ast(ast)
    print_ast(ast, True)


def simplify_ast(ast):
    if not ast:
        return
    if ast.children and ast.type == 'compoundStatement':
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

    for c in ast.children:
        simplify_ast(c)



def print_ast(ast, write_to_file):
    def print_ast_r(astnode, indentation, g, node_carry, h):
        if not astnode:
            return
        for dat in astnode.data:
            print " " * indentation, dat
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
                        g.add_node(pydot.Node(str(h[0]), label=(str(c.type) + ' -> ' + str(c.data))))
                    else:
                        g.add_node(pydot.Node(str(h[0]), label=str(c.type)))
                    g.add_edge(pydot.Edge(str(source), str(h[0])))
                node_carry = str(h[0])
            print_ast_r(c, indentation, g, node_carry, h)

    graph = pydot.Dot(graph_type='digraph')
    print_ast_r(ast, 0, graph, "root", [0])
    if write_to_file:
        graph.write_png('example1_graph.png')


if __name__ == '__main__':
    main()
