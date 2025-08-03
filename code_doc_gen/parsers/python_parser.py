"""
Python parser for CodeDocGen.

Uses the built-in ast module to parse Python code and extract function
signatures, parameters, and analyze function bodies.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from . import BaseParser
from ..models import Function, Parameter, FunctionBody, FunctionException, ParsedFile, FunctionType
from ..config import Config


class PythonParser(BaseParser):
    """Parser for Python source files."""
    
    def __init__(self, config: Config):
        """
        Initialize the Python parser.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        self.arithmetic_operators = {'+', '-', '*', '/', '//', '%', '**', '<<', '>>', '&', '|', '^'}
        self.comparison_operators = {'==', '!=', '<', '<=', '>', '>=', 'is', 'is not', 'in', 'not in'}
        self.assignment_operators = {'=', '+=', '-=', '*=', '/=', '//=', '%=', '**=', '<<=', '>>=', '&=', '|=', '^='}
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the parser can handle this file
        """
        return file_path.suffix.lower() in ['.py', '.pyx', '.pxd']
    
    """
        Performs _set_parents operation. Function iterates over data, has side effects. Takes self, node and parent as input. Returns a object value.
        :param self: The self object.
        :param node: The node object.
        :param parent: The parent object.
        :return: Value of type object

    """
    def _set_parents(self, node, parent=None):
        for child in ast.iter_child_nodes(node):
            child.parent = parent
            self._set_parents(child, child)

    def parse_file(self, file_path: Path) -> ParsedFile:
        """
        Parse a Python source file and extract functions.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            ParsedFile object containing extracted functions
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            
            parsed_file = ParsedFile(
                file_path=str(file_path),
                language='python'
            )
            
            # Extract imports
            parsed_file.imports = self._extract_imports(tree)
            
            # Extract classes
            parsed_file.classes = self._extract_classes(tree)
            
            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function = self._parse_function_def(node, source_code)
                    if function:
                        parsed_file.add_function(function)
            
            return parsed_file
            
        except Exception as e:
            print(f"Error parsing Python file {file_path}: {e}")
            return ParsedFile(file_path=str(file_path), language='python')
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """
        Extract import statements from the AST.
        
        Args:
            tree: AST root node
            
        Returns:
            List of import statements
        """
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
        return imports
    
    def _extract_classes(self, tree: ast.AST) -> List[str]:
        """
        Extract class names from the AST.
        
        Args:
            tree: AST root node
            
        Returns:
            List of class names
        """
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        return classes
    
    def _parse_function_def(self, node: ast.FunctionDef, source_code: str) -> Optional[Function]:
        """
        Parse a function definition node.
        
        Args:
            node: Function definition AST node
            source_code: Original source code
            
        Returns:
            Function object or None if parsing fails
        """
        try:
            # Determine function type
            function_type = FunctionType.FUNCTION
            class_name = ""
            # Note: Class detection would require more complex AST traversal
            # For now, we'll treat all functions as regular functions
            
            # Parse parameters
            parameters = self._parse_parameters(node.args)
            
            # Parse return type annotation
            return_type = self._get_return_type(node)
            
            # Parse exceptions
            exceptions = self._parse_exceptions(node)
            
            # Analyze function body
            body = self._analyze_function_body(node)
            
            # Extract source code for this function
            function_source = self._extract_function_source(node, source_code)
            
            function = Function(
                name=node.name,
                return_type=return_type,
                parameters=parameters,
                exceptions=exceptions,
                body=body,
                function_type=function_type,
                class_name=class_name,
                ast_node=node,
                source_code=function_source
            )
            
            return function
            
        except Exception as e:
            print(f"Error parsing function {node.name}: {e}")
            return None
    
    def _parse_parameters(self, args: ast.arguments) -> List[Parameter]:
        """
        Parse function parameters.
        
        Args:
            args: Arguments AST node
            
        Returns:
            List of Parameter objects
        """
        parameters = []
        
        # Parse positional arguments
        for i, arg in enumerate(args.args):
            param_name = arg.arg
            param_type = self._get_parameter_type(arg)
            
            parameter = Parameter(
                name=param_name,
                type=param_type,
                description=""
            )
            parameters.append(parameter)
        
        # Parse keyword-only arguments
        for i, arg in enumerate(args.kwonlyargs):
            param_name = arg.arg
            param_type = self._get_parameter_type(arg)
            
            parameter = Parameter(
                name=param_name,
                type=param_type,
                description=""
            )
            parameters.append(parameter)
        
        return parameters
    
    def _get_parameter_type(self, arg: ast.arg) -> str:
        """
        Get the type annotation for a parameter.
        
        Args:
            arg: Argument AST node
            
        Returns:
            Type string
        """
        if arg.annotation:
            return self._ast_to_string(arg.annotation)
        return "object"
    
    def _get_default_value(self, args: ast.arguments, index: int) -> Optional[str]:
        """
        Get the default value for a positional argument.
        
        Args:
            args: Arguments AST node
            index: Argument index
            
        Returns:
            Default value string or None
        """
        if args.defaults and index >= len(args.args) - len(args.defaults):
            default_index = index - (len(args.args) - len(args.defaults))
            return self._ast_to_string(args.defaults[default_index])
        return None
    
    def _get_kwonly_default_value(self, args: ast.arguments, index: int) -> Optional[str]:
        """
        Get the default value for a keyword-only argument.
        
        Args:
            args: Arguments AST node
            index: Argument index
            
        Returns:
            Default value string or None
        """
        if args.kw_defaults and index < len(args.kw_defaults):
            default = args.kw_defaults[index]
            if default is not None:
                return self._ast_to_string(default)
        return None
    
    def _get_return_type(self, node: ast.FunctionDef) -> str:
        """
        Get the return type annotation for a function.
        
        Args:
            node: Function definition AST node
            
        Returns:
            Return type string
        """
        if node.returns:
            return self._ast_to_string(node.returns)
        return "object"
    
    def _parse_exceptions(self, node: ast.FunctionDef) -> List[FunctionException]:
        """
        Parse exceptions that can be raised by the function.
        
        Args:
            node: Function definition AST node
            
        Returns:
            List of Exception objects
        """
        exceptions = []
        
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Raise):
                if stmt.exc:
                    exc_name = self._ast_to_string(stmt.exc)
                    # Extract exception name from the expression
                    if '.' in exc_name:
                        exc_name = exc_name.split('.')[-1]
                    exceptions.append(FunctionException(name=exc_name))
        
        return exceptions
    
    def _analyze_function_body(self, node: ast.FunctionDef) -> FunctionBody:
        """
        Analyze the function body for patterns and behaviors.
        
        Args:
            node: Function definition AST node
            
        Returns:
            FunctionBody object with analysis results
        """
        body = FunctionBody()
        
        for stmt in ast.walk(node):
            # Check for loops
            if isinstance(stmt, (ast.For, ast.While)):
                body.has_loops = True
            
            # Check for conditionals
            if isinstance(stmt, (ast.If, ast.IfExp)):
                body.has_conditionals = True
            
            # Check for exceptions
            if isinstance(stmt, ast.Raise):
                body.has_exceptions = True
            
            # Check for returns
            if isinstance(stmt, ast.Return):
                body.has_returns = True
                # Check if it's an early return (not at the end)
                if stmt != node.body[-1]:
                    body.has_early_returns = True
            
            # Check for arithmetic operations
            if isinstance(stmt, ast.BinOp):
                op = type(stmt.op).__name__
                if op in ['Add', 'Sub', 'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow']:
                    body.has_arithmetic = True
            
            # Check for string operations
            if isinstance(stmt, ast.Call):
                if hasattr(stmt.func, 'id'):
                    func_name = stmt.func.id
                    if func_name in ['format', 'join', 'split', 'replace', 'strip']:
                        body.has_string_operations = True
            
            # Check for file operations
            if isinstance(stmt, ast.Call):
                if hasattr(stmt.func, 'id'):
                    func_name = stmt.func.id
                    if func_name in ['open', 'read', 'write', 'close']:
                        body.has_file_operations = True
            
            # Check for side effects (assignments, function calls)
            if isinstance(stmt, ast.Assign):
                body.has_side_effects = True
            
            if isinstance(stmt, ast.Call):
                body.has_side_effects = True
        
        # Calculate complexity score
        body.complexity_score = self._calculate_complexity(node)
        
        return body
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate cyclomatic complexity of the function.
        
        Args:
            node: Function definition AST node
            
        Returns:
            Complexity score
        """
        complexity = 1  # Base complexity
        
        for stmt in ast.walk(node):
            if isinstance(stmt, (ast.If, ast.IfExp, ast.For, ast.While)):
                complexity += 1
            elif isinstance(stmt, ast.ExceptHandler):
                complexity += 1
            elif isinstance(stmt, ast.BoolOp):
                complexity += len(stmt.values) - 1
        
        return complexity
    
    def _get_end_line(self, node: ast.FunctionDef, source_code: str) -> int:
        """
        Get the end line number of the function.
        
        Args:
            node: Function definition AST node
            source_code: Original source code
            
        Returns:
            End line number
        """
        lines = source_code.split('\n')
        start_line = node.lineno - 1  # Convert to 0-based index
        
        # Find the end of the function by looking for dedentation
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                return i
        
        return len(lines)
    
    def _ast_to_string(self, node: ast.AST) -> str:
        """
        Convert an AST node to a string representation.
        
        Args:
            node: AST node
            
        Returns:
            String representation
        """
        if node is None:
            return ""
        
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Attribute):
            return f"{self._ast_to_string(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._ast_to_string(node.value)}[{self._ast_to_string(node.slice)}]"
        elif isinstance(node, ast.List):
            elements = [self._ast_to_string(el) for el in node.elts]
            return f"[{', '.join(elements)}]"
        elif isinstance(node, ast.Tuple):
            elements = [self._ast_to_string(el) for el in node.elts]
            return f"({', '.join(elements)})"
        elif isinstance(node, ast.Dict):
            items = []
            for key, value in zip(node.keys, node.values):
                key_str = self._ast_to_string(key)
                value_str = self._ast_to_string(value)
                items.append(f"{key_str}: {value_str}")
            return f"{{{', '.join(items)}}}"
        else:
            return str(type(node).__name__)
    
    def _extract_function_source(self, node: ast.FunctionDef, source_code: str) -> str:
        """
        Extract the source code for a specific function.
        
        Args:
            node: Function definition AST node
            source_code: Original source code
            
        Returns:
            Function source code string
        """
        # Extract from original source for compatibility
        lines = source_code.split('\n')
        start_line = node.lineno - 1  # Convert to 0-based index
        end_line = self._get_end_line(node, source_code) - 1
        
        if start_line < len(lines) and end_line < len(lines):
            return '\n'.join(lines[start_line:end_line + 1])
        else:
            return "" 