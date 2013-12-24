# Class for generic Abstract Syntax Tree (AST) nodes


class AST:

    def __init__(self, type, data=None, children=None, leaf=None):
        self.type = type

        if data is not None and not isinstance(data, list):
            self.data = [data]
        elif data:
            self.data = data
        else:
            self.data = []

        if children is not None and not isinstance(children, list):
            self.children = [children]
        elif children:
            self.children = children
        else:
            self.children = []

        self.leaf = leaf