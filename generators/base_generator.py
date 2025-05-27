# universal_code_converter/generators/base_generator.py (Relevant Parts)
from ast_module.universal_ast import (
    Node, ProgramNode, FunctionNode, PrintNode, MathOpNode,
    VariableNode, StringLiteralNode, NumberLiteralNode, PowerNode,
    ForLoopNode, WhileLoopNode, ComparisonNode, AssignmentNode
)

class BaseGenerator:
    """
    Base class for code generators. Uses the Visitor pattern.
    """
    def __init__(self, indent_char='    ', initial_indent_level=0):
        self.indent_char = indent_char
        self.current_indent_level = initial_indent_level

    def _make_indent(self):
        return self.indent_char * self.current_indent_level

    def visit(self, node):
        if isinstance(node, Node):
            method_name = f'visit_{node.__class__.__name__}'
            visitor = getattr(self, method_name, self.generic_visit)
            return visitor(node)
        return str(node)

    def generic_visit(self, node):
        return str(node)

    def visit_ProgramNode(self, node):
        # Default program generation: visit each statement and join with newlines.
        # Specific generators might override this for global structure (e.g., class wrapper).
        return "\n".join(self.visit(stmt) for stmt in node.statements)

    def visit_VariableNode(self, node):
        return node.name

    def visit_StringLiteralNode(self, node):
        # Default string representation. Target languages might need escaping.
        return f'"{node.value}"' # Python, JS, Java, C++ common

    def visit_NumberLiteralNode(self, node):
        return node.value # Assumes value is already a string representation of number

    def visit_MathOpNode(self, node):
        # Assumes infix operators are common.
        # No parentheses handling for precedence here; relies on AST structure.
        left_code = self.visit(node.left)
        right_code = self.visit(node.right)
        return f"{left_code} {node.operator} {right_code}"

    def visit_ComparisonNode(self, node):
        left_code = self.visit(node.left)
        right_code = self.visit(node.right)
        return f"{left_code} {node.operator} {right_code}"

    def visit_AssignmentNode(self, node):
        target = self.visit(node.target)
        value = self.visit(node.value)
        return f"{self._make_indent()}{target} = {value}"
    



class JavaGenerator(BaseGenerator):
    def __init__(self, indent_char='    ', initial_indent_level=0):
        super().__init__(indent_char, initial_indent_level)
        self.is_wrapped_in_class = False


    def visit_ProgramNode(self, node):
        # Wrap the entire program in a class and main method for executable Java.
        # This is a simplification; a real converter would handle existing classes.
        
        # Generate statements for the main part of the program
        # If functions are present, they will be generated as static methods.
        # Top-level print statements could go into a main method or a static block.
        
        # For simplicity, we'll assume functions are static methods.
        # Any "loose" statements (like print) will be put inside a main method.
        
        main_method_body_statements = []
        static_method_definitions = []

        for stmt in node.statements:
            if isinstance(stmt, FunctionNode):
                static_method_definitions.append(self.visit(stmt))
            else: # Assume other statements go into main
                main_method_body_statements.append(self.visit(stmt) + ";") # Add semicolon

        self.current_indent_level = 1 # Indent for class content
        
        main_method_code = ""
        if main_method_body_statements:
            main_body_str = "\n".join([self._make_indent() + self._make_indent() + s for s in main_method_body_statements]) # Double indent for main
            main_method_code = (
                f"{self._make_indent()}public static void main(String[] args) {{\n"
                f"{main_body_str}\n"
                f"{self._make_indent()}}}"
            )

        static_methods_code = "\n\n".join(static_method_definitions)
        
        self.current_indent_level = 0 # Reset for class definition
        class_body_parts = []
        if static_methods_code:
            class_body_parts.append(static_methods_code)
        if main_method_code:
            class_body_parts.append(main_method_code)
        
        class_body_str = "\n\n".join(class_body_parts)

        return (
            "public class ConvertedCode {\n"
            f"{class_body_str}\n"
            "}"
        )

    def visit_FunctionNode(self, node):
        # Assume String type for all args for simplicity.
        args_str = ", ".join([f"String {arg}" for arg in node.args])
        # Assume void return type for all functions.
        header = f"{self._make_indent()}public static void {node.name}({args_str}) {{"
        self.current_indent_level += 1
        # Java statements end with a semicolon.
        body_code = "\n".join([self.visit(stmt) + ";" for stmt in node.body])
        if not node.body:
            body_code = f"{self._make_indent()}// Empty body" # Or just an empty line
        self.current_indent_level -= 1
        return f"{header}\n{body_code}\n{self._make_indent()}}}"

    def visit_PrintNode(self, node):
        expr_code = self.visit(node.expression)
        return f"{self._make_indent()}System.out.println({expr_code})"

    def visit_PowerNode(self, node):
        base_code = self.visit(node.base)
        exponent_code = self.visit(node.exponent)
        # Java requires casting for Math.pow if used with integers for integer results,
        # but for general purpose, double is fine.
        return f"Math.pow({base_code}, {exponent_code})"

    def visit_ForLoopNode(self, node):
        iterator = node.iterator
        iterable = self.visit(node.iterable)
        
        # Convert Python range to Java for loop
        if isinstance(iterable, str) and iterable.startswith("range("):
            # Parse range arguments
            range_args = iterable[6:-1].split(',')
            if len(range_args) == 1:
                # range(n) -> for(int i = 0; i < n; i++)
                end = range_args[0].strip()
                header = f"{self._make_indent()}for (int {iterator} = 0; {iterator} < {end}; {iterator}++) {{"
            elif len(range_args) == 2:
                # range(start, end) -> for(int i = start; i < end; i++)
                start = range_args[0].strip()
                end = range_args[1].strip()
                header = f"{self._make_indent()}for (int {iterator} = {start}; {iterator} < {end}; {iterator}++) {{"
            else:
                # range(start, end, step) -> for(int i = start; i < end; i += step)
                start = range_args[0].strip()
                end = range_args[1].strip()
                step = range_args[2].strip()
                header = f"{self._make_indent()}for (int {iterator} = {start}; {iterator} < {end}; {iterator} += {step}) {{"
        else:
            # For other iterables, use enhanced for loop
            header = f"{self._make_indent()}for (String {iterator} : {iterable}) {{"
        
        self.current_indent_level += 1
        body_code = "\n".join([self.visit(stmt) + ";" for stmt in node.body])
        if not node.body:
            body_code = f"{self._make_indent()}// Empty body"
        self.current_indent_level -= 1
        return f"{header}\n{body_code}\n{self._make_indent()}}}"

    def visit_WhileLoopNode(self, node):
        condition = self.visit(node.condition)
        header = f"{self._make_indent()}while ({condition}) {{"
        self.current_indent_level += 1
        body_code = "\n".join([self.visit(stmt) + ";" for stmt in node.body])
        if not node.body:
            body_code = f"{self._make_indent()}// Empty body"
        self.current_indent_level -= 1
        return f"{header}\n{body_code}\n{self._make_indent()}}}"

    def visit_AssignmentNode(self, node):
        target = self.visit(node.target)
        value = self.visit(node.value)
        return f"{self._make_indent()}int {target} = {value}"

# --- Python Generator ---
class PythonGenerator(BaseGenerator):
    def visit(self, node):
        if isinstance(node, ProgramNode):
            return self.visit_program(node)
        elif isinstance(node, FunctionNode):
            return self.visit_function(node)
        elif isinstance(node, PrintNode):
            return self.visit_print(node)
        elif isinstance(node, MathOpNode):
            return self.visit_math_op(node)
        elif isinstance(node, VariableNode):
            return self.visit_variable(node)
        elif isinstance(node, StringLiteralNode):
            return self.visit_string_literal(node)
        elif isinstance(node, NumberLiteralNode):
            return self.visit_number_literal(node)
        elif isinstance(node, PowerNode):
            return self.visit_power(node)
        elif isinstance(node, ForLoopNode):
            return self.visit_for_loop(node)
        elif isinstance(node, WhileLoopNode):
            return self.visit_while_loop(node)
        elif isinstance(node, ComparisonNode):
            return self.visit_comparison(node)
        elif isinstance(node, AssignmentNode):
            return self.visit_assignment(node)
        elif isinstance(node, FunctionCallNode):
            return self.visit_function_call(node)
        else:
            raise NotImplementedError(f"Unsupported node type: {type(node)}")

    def visit_program(self, node):
        return "\n".join(self.visit(stmt) for stmt in node.statements)

    def visit_function(self, node):
        args_str = ", ".join(node.args)
        body = "\n".join("    " + self.visit(stmt) for stmt in node.body)
        return f"def {node.name}({args_str}):\n{body}"

    def visit_print(self, node):
        expr = self.visit(node.expression)
        # If the expression contains a variable, wrap it in str()
        if isinstance(node.expression, VariableNode):
            return f"print({expr})"
        elif isinstance(node.expression, MathOpNode):
            return f"print({expr})"
        else:
            return f"print({expr})"

    def visit_math_op(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        # If either operand is a variable, wrap it in str()
        if isinstance(node.left, VariableNode):
            left = f"str({left})"
        if isinstance(node.right, VariableNode):
            right = f"str({right})"
        return f"({left} {node.operator} {right})"

    def visit_variable(self, node):
        return node.name

    def visit_string_literal(self, node):
        return f'"{node.value}"'

    def visit_number_literal(self, node):
        return node.value

    def visit_power(self, node):
        return f"({self.visit(node.base)} ** {self.visit(node.exponent)})"

    def visit_for_loop(self, node):
        # Format the for loop with proper spacing and indentation
        body = "\n".join("    " + self.visit(stmt) for stmt in node.body)
        return f"for {node.iterator} in {node.iterable}:\n{body}"

    def visit_while_loop(self, node):
        body = "\n".join("    " + self.visit(stmt) for stmt in node.body)
        return f"while {self.visit(node.condition)}:\n{body}"

    def visit_comparison(self, node):
        return f"({self.visit(node.left)} {node.operator} {self.visit(node.right)})"

    def visit_assignment(self, node):
        return f"{self.visit(node.target)} = {self.visit(node.value)}"

    def visit_function_call(self, node):
        args_str = ", ".join(self.visit(arg) for arg in node.args)
        return f"{node.name}({args_str})"
