# universal_code_converter/main.py
import sys
import os
import time
def delay(seconds): time.sleep(seconds)
# Ensure the project root is in sys.path to find modules
# This is important if you run main.py directly from its directory
# or from the project root.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if os.path.dirname(project_root) not in sys.path: # If inside universal_code_converter/
    sys.path.insert(0, os.path.dirname(project_root))

# Use absolute imports
from ast_module.universal_ast import ProgramNode # For type checking or inspection if needed
from parsers.python_parser import parse_python
from parsers.java_parser import JavaParser
from parsers.cpp_parser import parse_cpp

# Transformers (currently placeholders)
from transformers.python_transformer import transform_to_python_ast
from transformers.java_transformer import transform_to_java_ast
from transformers.cpp_transformer import transform_to_cpp_ast

from generators.base_generator import (
    PythonGenerator, JavaGenerator, CppGenerator, JsGenerator
)

PARSERS = {
    'python': parse_python,
    'java': JavaParser,
    'cpp': parse_cpp,
    
}

TRANSFORMERS = { # Currently placeholders
    'python': transform_to_python_ast,
    'java': transform_to_java_ast,
    'cpp': transform_to_cpp_ast,
   
}

GENERATORS = {
    'python': PythonGenerator,
    'java': JavaGenerator,
    'cpp': CppGenerator,
   
}

SUPPORTED_LANGUAGES = list(PARSERS.keys())

def get_multiline_input():
    """Reads multiline input from the user until an empty line."""
    print("\nEnter your source code (press Enter on an empty line to finish):")
    lines = []
    while True:
        try:
            line = input()
            if line == "":
                break
            lines.append(line)
        except EOFError: # Handle Ctrl+D or end of input stream
            break
    return "\n".join(lines)

def convert_code(source_code, source_lang, target_lang):
    # Parse source code into universal AST
    if source_lang == 'python':
        ast = parse_python(source_code)
    elif source_lang == 'java':
        java_parser = JavaParser()
        ast = java_parser.parse_java(source_code)
    elif source_lang == 'cpp':
        ast = parse_cpp(source_code)
    else:
        raise ValueError(f"Unsupported source language: {source_lang}")

    # Generate target code from universal AST
    if target_lang == 'python':
        generator = PythonGenerator()
    elif target_lang == 'java':
        generator = JavaGenerator()
    elif target_lang == 'cpp':
        generator = CppGenerator()
    elif target_lang == 'javascript':
        generator = JsGenerator()
    else:
        raise ValueError(f"Unsupported target language: {target_lang}")

    return generator.visit(ast)

def main():
    """Main entry point for the code converter."""
    print(" _______________________________________________________")
    print("|Welcome to the Universal Cross-Language Code Converter!|")
    print(f"|Supported languages: {', '.join(SUPPORTED_LANGUAGES)}                 |")
    print("|_______________________________________________________|")
    while True:
        source_lang = input(f"\nEnter the source language ({'/'.join(SUPPORTED_LANGUAGES)}): ").lower()
        if source_lang in SUPPORTED_LANGUAGES:
            break
        print(f"Error: Source language '{source_lang}' is not supported. Please choose from the list.")

    while True:
        target_lang = input(f"Enter the target language ({'/'.join(SUPPORTED_LANGUAGES)}): ").lower()
        if target_lang in SUPPORTED_LANGUAGES:
            break
        print(f"Error: Target language '{target_lang}' is not supported. Please choose from the list.")
    
    if source_lang == target_lang:
        print(f"Source and target languages are the same ({source_lang}). No conversion needed.")
        sys.exit(0)

    source_code = get_multiline_input()
    if not source_code.strip():
        print("Error: No source code provided.")
        sys.exit(1)

    print("\nProcessing...")
    delay(4)
    try:
        # 1. Parse source code to Universal AST
        if source_lang == 'java':
            parser = JavaParser()
            universal_ast = parser.parse_java(source_code)
        else:
            parser = PARSERS[source_lang]
            print(f"Using {source_lang} parser...")
            delay(3)
            universal_ast = parser(source_code)
        
        # 2. Generate target code from AST
        generator_class = GENERATORS[target_lang]
        generator = generator_class()
        print(f"Using {target_lang} generator...")
        delay(4)
        target_code = generator.visit(universal_ast)

        print("\n<--- Converted Code --->")
        print(f"<--- Language: {target_lang.upper()} --->")
        print(target_code)
        print("\n\nNote: This is a simplified converter. Complex code or unsupported features may not convert correctly.\n\n")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("Parsing and generation are highly simplified and might fail on code outside the supported features.")

if __name__ == "__main__":
    main()
    
