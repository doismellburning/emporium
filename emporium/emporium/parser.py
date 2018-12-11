"""
Incredibly crude parser - just tries to find a `setup(install_requires=[`

Might be able to do something fancy with astroid and its inference,
but maybe this will be good enough...!
"""

import ast


def parse_install_requires(setuppy):
    tree = ast.parse(setuppy)
    irf = InstallRequiresFinder()
    irf.visit(tree)
    return irf.install_requires


class InstallRequiresFinder(ast.NodeVisitor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.install_requires = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id == "setup":
                for keyword in node.keywords:
                    if keyword.arg == "install_requires":
                        if isinstance(keyword.value, ast.Tuple) or isinstance(
                            keyword.value, ast.List
                        ):
                            self.install_requires = [s.s for s in keyword.value.elts]

        self.generic_visit(node)
