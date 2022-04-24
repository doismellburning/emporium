"""
Incredibly crude parser - just tries to find a `setup(install_requires=[`

Might be able to do something fancy with astroid and its inference,
but maybe this will be good enough...!
"""

import ast

import parsley
import pep508


def parse_dependencies(setuppy):
    tree = ast.parse(setuppy)
    dependency_finder = DependencyFinder()
    dependency_finder.visit(tree)
    return dependency_finder


class DependencyFinder(ast.NodeVisitor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.install_requires = []
        self.tests_require = []

        # setup.py uses a Dict<Str, List<Str>> for extras
        # but this stores as List<Str,Str> - closer to the Dependency Model style
        self.extras_require = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id == "setup":
                for keyword in node.keywords:
                    if keyword.arg == "install_requires":
                        if isinstance(keyword.value, ast.Tuple) or isinstance(
                            keyword.value, ast.List
                        ):
                            self.install_requires = [s.s for s in keyword.value.elts]
                    elif keyword.arg == "tests_require":
                        if isinstance(keyword.value, ast.Tuple) or isinstance(
                            keyword.value, ast.List
                        ):
                            self.tests_requires = [s.s for s in keyword.value.elts]
                    elif keyword.arg == "extras_require":
                        if isinstance(keyword.value, ast.Dict):
                            # I'd really love to just have the dict here, but that seems tricky
                            # So instead, time to fluffle `Dict(expr* keys, expr* values)`
                            kvs = zip(keyword.value.keys, keyword.value.values)
                            for (k, v) in kvs:
                                if isinstance(k, ast.Str) and (
                                    isinstance(v, ast.Tuple) or isinstance(v, ast.List)
                                ):
                                    for elt in v.elts:
                                        self.extras_require.append(k, elt)

        self.generic_visit(node)


_PEP508_PARSER = None


def get_pep508_parser():
    global _PEP508_PARSER
    if _PEP508_PARSER is None:
        _PEP508_PARSER = parsley.makeGrammar(pep508.grammar, {"lookup": lambda x: x})
    return _PEP508_PARSER


def parse_dependency_name(specification: str) -> str:  # TODO Handle errors
    pep508parser = get_pep508_parser()
    return pep508parser(specification).specification()[0]


def parse_dependency_names(setuppy):

    install_requires = parse_install_requires(setuppy)

    dependency_names = []

    for spec in install_requires:
        dependency_names.append(parse_dependency_name(spec))

    return dependency_names
