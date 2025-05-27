# universal_code_converter/ast_module/universal_ast.py

class Node:
    """Base class for all AST nodes."""
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

class ProgramNode(Node):
    """Represents the entire program, a collection of statements."""
    def __init__(self, statements):
        self.statements = statements  # List of statement nodes

class FunctionNode(Node):
    """Represents a function definition."""
    def __init__(self, name, args, body):
        self.name = name      # String: function name
        self.args = args      # List of strings: argument names
        self.body = body      # List of statement nodes: function body

class PrintNode(Node):
    """Represents a print or output statement."""
    def __init__(self, expression):
        self.expression = expression  # Node: the expression to print

class MathOpNode(Node):
    """Represents a mathematical operation."""
    def __init__(self, operator, left, right):
        self.operator = operator  # String: e.g., '+', '-', '*', '/'
        self.left = left          # Node: left operand
        self.right = right        # Node: right operand

class VariableNode(Node):
    """Represents a variable identifier."""
    def __init__(self, name):
        self.name = name  # String: variable name

class StringLiteralNode(Node):
    """Represents a string literal."""
    def __init__(self, value):
        self.value = value  # String: the actual string value

class NumberLiteralNode(Node):
    """Represents a number literal."""
    # For simplicity, we'll treat all numbers as strings initially in the AST
    # and let the generator handle specific formatting if needed.
    def __init__(self, value):
        self.value = value # String: numeric value as a string

class PowerNode(Node):
    """Represents a power/pow function call (e.g., pow(base, exponent))."""
    def __init__(self, base, exponent):
        self.base = base          # Node: base expression
        self.exponent = exponent  # Node: exponent expression

class ForLoopNode(Node):
    """Represents a for loop."""
    def __init__(self, iterator, iterable, body):
        self.iterator = iterator  # String: iterator variable name
        self.iterable = iterable  # String: range expression or other iterable
        self.body = body         # List of statement nodes: loop body

    def __repr__(self):
        return f"ForLoopNode(iterator='{self.iterator}', iterable='{self.iterable}', body={self.body})"

class WhileLoopNode(Node):
    """Represents a while loop."""
    def __init__(self, condition, body):
        self.condition = condition  # Node: condition expression
        self.body = body           # List of statement nodes: loop body

class ComparisonNode(Node):
    """Represents a comparison operation."""
    def __init__(self, operator, left, right):
        self.operator = operator  # String: e.g., '<', '>', '<=', '>=', '==', '!='
        self.left = left          # Node: left operand
        self.right = right        # Node: right operand

class AssignmentNode(Node):
    """Represents a variable assignment."""
    def __init__(self, target, value):
        self.target = target  # Node: target variable
        self.value = value    # Node: value to assign

class FunctionCallNode(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args
