import CodeGenerator
import parser
import AST
import pydot
import IRTree
import json

__author__ = 'sambodanis'

lift_and_remove_types = ['plusOrMinus', 'timesOrDivide']
lift_and_remove_parents = ['pomTermStar', 'tdFactorStar', 'unaryOp']
inverted_conditions = {'<': '>=', '>': '<=', '>=': '<', '<=': '>', '=': '!=', '!=': '='}


def main():
    file_num = load_config()['file_num']
    data = open_file_num(file_num)
    p = parser.ASTGenerator()
    ast = p.parse(data)
    simplify_ast(ast)
    fix_math(ast)
    print_ast(ast, True)
    irt_generator = IRTree.irt(ast)
    ir = irt_generator.generate_irt()
    print ir
    for line in ir:
        print ' '.join(line)
    write_ir_file_num(file_num, ir)
    cg = CodeGenerator.CodeGenerator(ir)
    assembly_code = cg.generate_code()
    print assembly_code
    print ''
    cg.print_assembly_to_file(file_num)


def load_config():
    with open('config.json', 'r') as in_file:
        return json.loads(in_file.read())


def open_file_num(n):
    with open("TestCases/test" + n + ".le") as my_file:
        data = "\n".join(line.rstrip() for line in my_file)
        return data


def write_ir_file_num(n, ir):
    with open('IRCodes/testIR' + n + '.ir', 'w') as out_file:
        out_file.write("\n".join([' '.join(line) for line in ir]))
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


# Fixes mathematical nodes so that all information required to evaluate
# them is in their children. Also simplifies negation.
# Basically implemented as a bunch of tree rotations
# Does similar thing for all relations
def fix_math(ast):
    if ast.type == 'expression':
        if len(ast.children) == 3:
            new_ast = AST.AST('negate', ast.children[0].data[0], ast.children[1:2])
            ast.children[-1].children.insert(0, new_ast)
            ast.children = [ast.children[2]]
        elif len(ast.children) == 2 and ast.children[0].type == 'term':
            ast.children[1].children.insert(0, ast.children[0])
            ast.children = [ast.children[1]]
        elif len(ast.children) == 2 and ast.children[1].type == 'term':
            new_ast = AST.AST('negate', ast.children[0].data[0], [ast.children[1].children[0]])
            ast.children[1].children.insert(0, new_ast)
            ast.children[1].children.pop(1)
            ast.children = [ast.children[1]]
    elif ast.type == 'pomTermStar':
        if len(ast.children) == 3:
            ast.children[2].children.insert(0, ast.children[1])
            ast.children = [ast.children[0]] + [ast.children[2]]
    elif ast.type == 'term' and ast.children[-1].type == 'tdFactorStar':
        if len(ast.children) == 3:
            print 'term with three children'
        elif len(ast.children) == 2:
            ast.children[-1].children.insert(0, ast.children[0])
            ast.children = [ast.children[-1]]
    elif ast.type == 'tdFactorStar':
        if len(ast.children) == 3:
            ast.children[-1].children.insert(0, ast.children[1])
            ast.children = [ast.children[0]] + [ast.children[-1]]
    elif ast.type == 'statement' and ast.data[0] == 'if':
        if len(ast.children) == 4:
            ast.children[1].children = [ast.children[0], ast.children[2]]
            ast.children = [ast.children[1], ast.children[3]]
        elif len(ast.children) == 5:
            ast.children[1].children = [ast.children[0], ast.children[2]]
            ast.children = [ast.children[1], ast.children[3], ast.children[4]]
    elif ast.type == 'statement' and ast.data[0] == 'repeat':
        ast.children[2].data[0] = inverted_conditions[ast.children[2].data[0]]
        ast.children[2].children = [ast.children[1], ast.children[3]]
        ast.children = [ast.children[0], ast.children[2]]
    for c in ast.children:
        fix_math(c)


def print_ast(ast, write_to_file):
    print 'PrintingAST:Start'

    def print_ast_r(astnode, indentation, g, node_carry, h):
        if not astnode:
            return
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
    print 'PrintingAST:Done'


if __name__ == '__main__':
    main()
