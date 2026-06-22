from .ast import *


class SemanticsError(Exception):
    pass


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}

    def declare(self, name, info):
        if name in self.symbols:
            raise SemanticsError(f"Duplicate symbol {name}")
        self.symbols[name] = info

    def lookup(self, name):
        scope = self
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None


class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.current_function = None

    def analyze(self, node):
        self.visit(node)

    def push_scope(self):
        self.current_scope = Scope(self.current_scope)

    def pop_scope(self):
        self.current_scope = self.current_scope.parent

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise SemanticsError(f"Unhandled node {type(node).__name__}")

    def visit_ProgramNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_BlockNode(self, node):
        self.push_scope()
        for statement in node.statements:
            self.visit(statement)
        self.pop_scope()

    def visit_LetNode(self, node):
        if node.value is not None:
            self.visit(node.value)
        self.current_scope.declare(node.name, {"kind": "variable"})

    def visit_AssignNode(self, node):
        if not isinstance(node.target, IdentifierNode):
            raise SemanticsError("Left side pe identifier chahiye assignment ke")

        symbol = self.current_scope.lookup(node.target.value)
        if symbol is None:
            raise SemanticsError(f"Undefined variable {node.target.value}")
        self.visit(node.value)

    def visit_OutputNode(self, node):
        for value in node.values:
            self.visit(value)

    def visit_ReturnNode(self, node):
        if node.value is not None:
            self.visit(node.value)

    def visit_IfNode(self, node):
        self.visit(node.condition)
        self.visit(node.body)

        for elif_condition, elif_body in node.elifs:
            self.visit(elif_condition)
            self.visit(elif_body)

        if node.else_body is not None:
            self.visit(node.else_body)

    def visit_WhileNode(self, node):
        self.visit(node.condition)
        self.visit(node.body)

    def visit_ForNode(self, node):
        self.visit(node.iterable)
        self.push_scope()
        self.current_scope.declare(node.name, {"kind": "variable"})
        self.visit(node.body)
        self.pop_scope()

    def visit_FunctionNode(self, node):
        self.current_scope.declare(
            node.name,
            {"kind": "function", "params": node.params},
        )

        old_function = self.current_function
        self.current_function = node
        self.push_scope()

        for param in node.params:
            self.current_scope.declare(param, {"kind": "variable"})
        self.visit(node.body)

        self.pop_scope()
        self.current_function = old_function

    def visit_ExprStatementNode(self, node):
        self.visit(node.expr)

    def visit_NumberNode(self, node):
        return None

    def visit_StringNode(self, node):
        return None

    def visit_IdentifierNode(self, node):
        symbol = self.current_scope.lookup(node.value)
        if symbol is None:
            raise SemanticsError(f"Undefined variable {node.value}")
        return symbol

    def visit_CallNode(self, node):
        if isinstance(node.callee, IdentifierNode):
            symbol = self.current_scope.lookup(node.callee.value)
            if symbol is None and node.callee.value != "input":
                raise SemanticsError(f"Undefined function {node.callee.value}")
        else:
            self.visit(node.callee)

        for arg in node.args:
            self.visit(arg)

    def visit_BinaryOpNode(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOpNode(self, node):
        self.visit(node.right)
