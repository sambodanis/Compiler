import parser
import AST
import pydot

__author__ = 'sambodanis'




def main():
    with open("TestCases/test0.le") as myfile:
        data = "\n".join(line.rstrip() for line in myfile)
    p = parser.ASTGenerator()
    ast = p.parse(data)

    graph = pydot.Dot(graph_type='digraph')
    printAST(ast, 0, graph, "root", [0])
    graph.write_png('example1_graph.png')

    #p = parser.py.Parser()
    #ast = p.parse(data)
    #print ast



def printAST(astnode, indentation, g, node_carry, h):
    if not astnode: return
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
        printAST(c, indentation, g, node_carry, h)



if __name__ == '__main__':
    main()
