# universal_code_converter/parsers/java_parser.py
import re
from ast_module.universal_ast import (
    ProgramNode, FunctionNode, PrintNode, MathOpNode,
    VariableNode, StringLiteralNode, NumberLiteralNode, PowerNode,
    ForLoopNode, WhileLoopNode, ComparisonNode, AssignmentNode
)

# Regex patterns for Java syntax
FUNC_DEF_REGEX = r"(?:public\s+)?(?:static\s+)?(?:void|int|String)\s+(\w+)\s*\(([^)]*)\)\s*\{"
PRINT_REGEX = r"System\.out\.println\s*\((.*)\)"
MATH_OP_REGEX = r"(.+?)\s*\+\s*(.+)"
POW_REGEX = r"Math\.pow\s*\(([^,]+)\s*,\s*([^)]+)\)"
# Updated FOR_LOOP_REGEX to handle more patterns
FOR_LOOP_REGEX = r"for\s*\(\s*(?:int\s+)?(\w+)\s*=\s*([^;]+);\s*\1\s*(<|<=|>|>=)\s*([^;]+);\s*\1\s*(\+\+|--|\+=|-=)\s*([^)]*)\)\s*\{"
WHILE_LOOP_REGEX = r"while\s*\((.*?)\)\s*\{"
COMPARISON_REGEX = r"(.+?)\s*(==|!=|<=|>=|<|>)\s*(.+)"
ASSIGNMENT_REGEX = r"(?:int\s+)?(\w+)\s*=\s*(.+)"

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

    # 1. Power function (Math.pow(a, b))
    pow_match = re.fullmatch(POW_REGEX, expr_str)
    if pow_match:
        base = _parse_expression(pow_match.group(1).strip())
        exponent = _parse_expression(pow_match.group(2).strip())
        return PowerNode(base, exponent)

    # 2. Simple addition (a + b)
    if ' + ' in expr_str and not expr_str.startswith("Math.pow("):
        parts = expr_str.split(' + ', 1)
        if len(parts) == 2:
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

    # Fallback: treat as variable
    return VariableNode(expr_str)

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

def _convert_java_for_to_range(start, end, operator, step_op, step_val):
    """Convert Java for loop parameters to Python range parameters."""
    start = start.strip()
    end = end.strip()
    
    # Handle different comparison operators
    if operator == '<=':
        end = f"{end} + 1"
    elif operator == '>':
        start, end = end, start
        if step_op == '++':
            step_val = "-1"
        elif step_op == '--':
            step_val = "1"
    
    # Handle step value
    if step_op == '++':
        step = "1"
    elif step_op == '--':
        step = "-1"
    elif step_op == '+=':
        step = step_val
    elif step_op == '-=':
        step = f"-{step_val}"
    
    return f"range({start}, {end}, {step})"

def parse_java(code):
    """
    Parse Java code into a universal AST.
    """
    statements = []
    lines = code.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line or line.startswith("//"):  # Skip empty lines and comments
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
            args = [arg.strip().split()[-1] for arg in args_str.split(',') if arg.strip()]
            
            base_indent = len(lines[i]) - len(lines[i].lstrip())
            body_lines, i = _get_indented_block(lines, i + 1, base_indent)
            body_program = parse_java('\n'.join(body_lines))
            statements.append(FunctionNode(name, args, body_program.statements))
            continue

        # For loop
        for_match = re.match(FOR_LOOP_REGEX, line)
        if for_match:
            iterator = for_match.group(1)
            start = for_match.group(2)
            operator = for_match.group(3)
            end = for_match.group(4)
            step_op = for_match.group(5)
            step_val = for_match.group(6)
            
            iterable = _convert_java_for_to_range(start, end, operator, step_op, step_val)
            
            base_indent = len(lines[i]) - len(lines[i].lstrip())
            body_lines, i = _get_indented_block(lines, i + 1, base_indent)
            body_program = parse_java('\n'.join(body_lines))
            statements.append(ForLoopNode(iterator, iterable, body_program.statements))
            continue

        # While loop
        while_match = re.match(WHILE_LOOP_REGEX, line)
        if while_match:
            condition = _parse_expression(while_match.group(1))
            
            base_indent = len(lines[i]) - len(lines[i].lstrip())
            body_lines, i = _get_indented_block(lines, i + 1, base_indent)
            body_program = parse_java('\n'.join(body_lines))
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
