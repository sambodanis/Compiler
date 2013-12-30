import CodeGenerator
import parser
import AST
import pydot
import IRTree
import json

__author__ = 'sambodanis'

lift_and_remove_types = ['plusOrMinus', 'timesOrDivide']
lift_and_remove_parents = ['pomTermStar', 'tdFactorStar', 'unaryOp']


def main():
    file_num = load_config()['file_num']
    data = open_file_num(file_num)
    p = parser.ASTGenerator()
    ast = p.parse(data)
    simplify_ast(ast)
    print_ast(ast, True)
    irt_generator = IRTree.irt(ast)
    ir = irt_generator.generate_irt()
    write_ir_file_num(file_num, ir)
    #cg = CodeGenerator.CodeGenerator(ir)
    #assembly_code = cg.generate_code()
    #print assembly_code
    #print ''
    #cg.print_assembly_to_file(file_num)




def load_config():
    with open('config.json', 'r') as in_file:
        return json.loads(in_file.read())



def open_file_num(n):
    with open("TestCases/test" + n + ".le") as my_file:
        data = "\n".join(line.rstrip() for line in my_file)
        return data


def write_ir_file_num(n, ir):
    with open('IRCodes/testIR' + n + '.ir', 'w') as out_file:
        out_file.write("\n".join(ir))
        #out_file.write('\n')


# simplifies the AST by simplifying it and removing unneeded stuff
# eg transitions like A -> x -> -> y -> z -> data we actually want where xyz
# hold no important data
# Also removes any null nodes from the AST
def simplify_ast(ast):
    try: # remove potentially null children from rules like: A -> B | empty
        while True:
            ast.children.remove(None)
    except:
        pass
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
        elif ast.type in lift_and_remove_parents: # removes unneeded transitions
            ast.data = [c.data for c in ast.children if c.type in lift_and_remove_types][0]
            ast.children = [c for c in ast.children if c.type not in lift_and_remove_types]

    for i, c in enumerate(ast.children):
        simplify_ast(c)


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
