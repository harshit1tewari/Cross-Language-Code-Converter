# universal_code_converter/parsers/python_parser.py
import re
from ast_module.universal_ast import (
    ProgramNode, FunctionNode, PrintNode, MathOpNode,
    VariableNode, StringLiteralNode, NumberLiteralNode, PowerNode,
    ForLoopNode, WhileLoopNode, ComparisonNode, AssignmentNode
)

# More robust regex might be needed for complex scenarios
FUNC_DEF_REGEX = r"def\s+(\w+)\s*\(([^)]*)\)\s*:"
PRINT_REGEX = r"print\s*\((.*)\)"
# Simple math: look for + operator not inside strings or parentheses (very simplified)
# This regex is extremely basic and will break easily.
# A proper parser would use tokenization and a grammar.
MATH_OP_REGEX = r"(.+?)\s*\+\s*(.+)" # Catches the first '+'
POW_REGEX = r"pow\s*\(([^,]+)\s*,\s*([^)]+)\)"
FOR_LOOP_REGEX = r"for\s+(\w+)\s+in\s+(.+?)\s*:"
WHILE_LOOP_REGEX = r"while\s+(.+?)\s*:"
COMPARISON_REGEX = r"(.+?)\s*(==|!=|<=|>=|<|>)\s*(.+)"
ASSIGNMENT_REGEX = r"(\w+)\s*=\s*(.+)"
FUNCTION_CALL_REGEX = r"(\w+)\s*\((.*?)\)"

def _parse_expression(expr_str):
    """Parse expressions including comparisons."""
    expr_str = expr_str.strip()

    # Check for comparison operators
    for op in ['==', '!=', '<=', '>=', '<', '>']:
        if f" {op} " in expr_str:
            parts = expr_str.split(f" {op} ", 1)
            if len(parts) == 2:
                left = _parse_expression(parts[0].strip())
                right = _parse_expression(parts[1].strip())
                return ComparisonNode(op, left, right)

    # 1. Power function (pow(a, b))
    pow_match = re.fullmatch(POW_REGEX, expr_str)
    if pow_match:
        base = _parse_expression(pow_match.group(1).strip())
        exponent = _parse_expression(pow_match.group(2).strip())
        return PowerNode(base, exponent)

    # 2. Simple addition (a + b) - very basic
    # This needs to be careful not to misinterpret function args like "a, b + c"
    # For this demo, we assume it's a standalone expression.
    # A real parser would handle operator precedence.
    # We'll only handle one level of '+' for simplicity.
    if ' + ' in expr_str and not expr_str.startswith("pow("): # Avoid conflict with pow
        parts = expr_str.split(' + ', 1)
        if len(parts) == 2:
            # Check if parts are not part of a larger structure like a string
            # This is still very naive.
            if not (parts[0].count('"') % 2 != 0 or parts[0].count("'") % 2 != 0):
                 left = _parse_expression(parts[0].strip())
                 right = _parse_expression(parts[1].strip())
                 return MathOpNode('+', left, right)


    # 3. String literal
    if (expr_str.startswith('"') and expr_str.endswith('"')) or \
       (expr_str.startswith("'") and expr_str.endswith("'")):
        return StringLiteralNode(expr_str[1:-1])

    # 4. Number literal (integer or float)
    if re.fullmatch(r"-?\d+(\.\d+)?", expr_str):
        return NumberLiteralNode(expr_str)

    # 5. Variable
    if re.fullmatch(r"[a-zA-Z_]\w*", expr_str):
        return VariableNode(expr_str)

    # Fallback: if unrecognized, treat as a complex string or unparsable
    # For this demo, we'll assume it's a variable if nothing else matches.
    # This is a major simplification.
    # print(f"Warning: Python parser could not fully identify expression: '{expr_str}', treating as VariableNode.")
    return VariableNode(expr_str) # Fallback, potentially incorrect

def _get_indented_block(lines, start_idx, base_indent):
    """Helper to get indented block of code."""
    block_lines = []
    i = start_idx
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= base_indent and i > start_idx:
            break
        block_lines.append(line)
        i += 1
    return block_lines, i

def parse_python(code):
    """
    Parses Python code into a universal AST.
    """
    statements = []
    lines = code.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line or line.startswith("#"): # Skip empty lines and comments
            i += 1
            continue

        # Check for function call first
        func_call_match = re.match(FUNCTION_CALL_REGEX, line)
        if func_call_match:
            func_name = func_call_match.group(1)
            args_str = func_call_match.group(2)
            args = [arg.strip() for arg in args_str.split(',')] if args_str else []
            statements.append(FunctionNode(func_name, args, []))
            i += 1
            continue

        # Assignment
        assign_match = re.match(ASSIGNMENT_REGEX, line)
        if assign_match:
            target = assign_match.group(1)
            value = assign_match.group(2)
            statements.append(AssignmentNode(
                VariableNode(target),
                _parse_expression(value)
            ))
            i += 1
            continue

        # Function definition
        func_match = re.match(FUNC_DEF_REGEX, line)
        if func_match:
            name = func_match.group(1)
            args_str = func_match.group(2)
            args = [arg.strip() for arg in args_str.split(',') if arg.strip()]
            
            base_indent = len(lines[i]) - len(lines[i].lstrip())
            body_lines, i = _get_indented_block(lines, i + 1, base_indent)
            body_program = parse_python('\n'.join(body_lines))
            statements.append(FunctionNode(name, args, body_program.statements))
            continue

        # For loop
        for_match = re.match(FOR_LOOP_REGEX, line)
        if for_match:
            iterator = for_match.group(1)
            iterable = _parse_expression(for_match.group(2))
            
            base_indent = len(lines[i]) - len(lines[i].lstrip())
            body_lines, i = _get_indented_block(lines, i + 1, base_indent)
            body_program = parse_python('\n'.join(body_lines))
            statements.append(ForLoopNode(iterator, iterable, body_program.statements))
            continue

        # While loop
        while_match = re.match(WHILE_LOOP_REGEX, line)
        if while_match:
            condition = _parse_expression(while_match.group(1))
            
            base_indent = len(lines[i]) - len(lines[i].lstrip())
            body_lines, i = _get_indented_block(lines, i + 1, base_indent)
            body_program = parse_python('\n'.join(body_lines))
            statements.append(WhileLoopNode(condition, body_program.statements))
            continue

        # Print statement
        print_match = re.match(PRINT_REGEX, line)
        if print_match:
            expression_str = print_match.group(1).strip()
            expression_node = _parse_expression(expression_str)
            statements.append(PrintNode(expression_node))
            i += 1
            continue

        i += 1

    return ProgramNode(statements)
