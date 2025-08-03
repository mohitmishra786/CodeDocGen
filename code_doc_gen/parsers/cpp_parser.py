"""
C++ parser for CodeDocGen.

Uses libclang to parse C++ code and extract function signatures,
parameters, and analyze function bodies.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from . import BaseParser
from ..models import Function, Parameter, FunctionBody, FunctionException, ParsedFile, FunctionType
from ..config import Config

# Try to import clang, but don't fail if it's not available
try:
    import clang.cindex
    CLANG_AVAILABLE = True
    if TYPE_CHECKING:
        from clang.cindex import Cursor, Type
except ImportError:
    CLANG_AVAILABLE = False
    # Create dummy types for type hints when clang is not available
    if TYPE_CHECKING:
        Cursor = Any
        Type = Any

# Define types for use throughout the module
if CLANG_AVAILABLE:
    Cursor = clang.cindex.Cursor
    Type = clang.cindex.Type
else:
    Cursor = Any
    Type = Any


class CppParser(BaseParser):
    """Parser for C++ source files."""
    
    def __init__(self, config: Config):
        """
        Initialize the C++ parser.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        if not CLANG_AVAILABLE:
            print("Warning: clang package not available. C++ parsing will use regex fallback only.")
            return
            
        # Initialize libclang
        try:
            clang.cindex.Config.set_library_file('/Library/Developer/CommandLineTools/usr/lib/libclang.dylib')
        except Exception:
            # Try alternative paths
            try:
                clang.cindex.Config.set_library_file('/System/Volumes/Data/Library/Developer/CommandLineTools/usr/lib/libclang.dylib')
            except Exception:
                try:
                    clang.cindex.Config.set_library_file('/usr/local/lib/libclang.dylib')
                except Exception:
                    try:
                        clang.cindex.Config.set_library_file('/usr/lib/libclang.so')
                    except Exception:
                        try:
                            clang.cindex.Config.set_library_file('/usr/lib/x86_64-linux-gnu/libclang.so')
                        except Exception:
                            # If all paths fail, we'll use regex fallback
                            print("Warning: Could not configure libclang library path. C++ parsing will use regex fallback only.")
                            pass
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the parser can handle this file
        """
        return file_path.suffix.lower() in ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hh', '.hxx']
    
    def parse_file(self, file_path: Path) -> ParsedFile:
        """
        Parse a C++ source file and extract functions.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            ParsedFile object containing extracted functions
        """
        if not CLANG_AVAILABLE:
            # Use regex-based parsing if clang is not available
            return self._parse_with_regex_fallback(file_path)
            
        try:
            # Create libclang index
            index = clang.cindex.Index.create()
            
            # Parse the file
            translation_unit = index.parse(
                str(file_path),
                args=['-std=c++17', '-x', 'c++']  # Use C++17 standard
            )
            
            parsed_file = ParsedFile(
                file_path=str(file_path),
                language='c++'
            )
            
            # Extract functions from the AST
            self._extract_functions(translation_unit.cursor, parsed_file)
            
            return parsed_file
            
        except Exception as e:
            # Fallback to regex-based parsing for C++
            return self._parse_with_regex_fallback(file_path)
    
    def _extract_functions(self, cursor: Cursor, parsed_file: ParsedFile) -> None:
        """
        Extract functions from the AST cursor.
        
        Args:
            cursor: libclang cursor
            parsed_file: ParsedFile object to populate
        """
        if not CLANG_AVAILABLE:
            return
            
        for child in cursor.get_children():
            if child.location.file and str(child.location.file) == parsed_file.file_path:
                if child.kind == clang.cindex.CursorKind.FUNCTION_DECL:
                    function = self._parse_function_decl(child)
                    if function:
                        parsed_file.add_function(function)
                elif child.kind == clang.cindex.CursorKind.CXX_METHOD:
                    function = self._parse_method_decl(child)
                    if function:
                        parsed_file.add_function(function)
                elif child.kind == clang.cindex.CursorKind.CONSTRUCTOR:
                    function = self._parse_constructor_decl(child)
                    if function:
                        parsed_file.add_function(function)
                elif child.kind == clang.cindex.CursorKind.DESTRUCTOR:
                    function = self._parse_destructor_decl(child)
                    if function:
                        parsed_file.add_function(function)
                elif child.kind == clang.cindex.CursorKind.NAMESPACE:
                    # Recursively process namespace
                    self._extract_functions(child, parsed_file)
                elif child.kind == clang.cindex.CursorKind.CLASS_DECL:
                    # Recursively process class
                    self._extract_functions(child, parsed_file)
    
    def _parse_function_decl(self, cursor: Cursor) -> Optional[Function]:
        """
        Parse a function declaration.
        
        Args:
            cursor: Function declaration cursor
            
        Returns:
            Function object or None if parsing fails
        """
        if not CLANG_AVAILABLE:
            return None
            
        try:
            # Get function name
            name = cursor.spelling
            
            # Get return type
            return_type = self._get_type_string(cursor.result_type)
            
            # Get parameters
            parameters = self._parse_parameters(cursor)
            
            # Get exceptions
            exceptions = self._parse_exceptions(cursor)
            
            # Analyze function body
            body = self._analyze_function_body(cursor)
            
            # Get source code for AST analysis
            source_code = self._extract_function_source(cursor)
            
            function = Function(
                name=name,
                return_type=return_type,
                parameters=parameters,
                exceptions=exceptions,
                body=body,
                function_type=FunctionType.FUNCTION,
                source_code=source_code
            )
            
            return function
            
        except Exception as e:
            print(f"Error parsing function {cursor.spelling}: {e}")
            return None
    
    def _parse_method_decl(self, cursor: Cursor) -> Optional[Function]:
        """
        Parse a method declaration.
        
        Args:
            cursor: Method declaration cursor
            
        Returns:
            Function object or None if parsing fails
        """
        if not CLANG_AVAILABLE:
            return None
            
        try:
            # Get method name
            name = cursor.spelling
            
            # Get return type
            return_type = self._get_type_string(cursor.result_type)
            
            # Get parameters
            parameters = self._parse_parameters(cursor)
            
            # Get exceptions
            exceptions = self._parse_exceptions(cursor)
            
            # Get class name
            class_name = self._get_class_name(cursor)
            
            # Analyze function body
            body = self._analyze_function_body(cursor)
            
            # Get source code for AST analysis
            source_code = self._extract_function_source(cursor)
            
            function = Function(
                name=name,
                return_type=return_type,
                parameters=parameters,
                exceptions=exceptions,
                body=body,
                function_type=FunctionType.METHOD,
                class_name=class_name,
                source_code=source_code
            )
            
            return function
            
        except Exception as e:
            print(f"Error parsing method {cursor.spelling}: {e}")
            return None
    
    def _parse_constructor_decl(self, cursor: Cursor) -> Optional[Function]:
        """
        Parse a constructor declaration.
        
        Args:
            cursor: Constructor declaration cursor
            
        Returns:
            Function object or None if parsing fails
        """
        if not CLANG_AVAILABLE:
            return None
            
        try:
            # Get constructor name (same as class name)
            name = cursor.spelling
            
            # Get parameters
            parameters = self._parse_parameters(cursor)
            
            # Get exceptions
            exceptions = self._parse_exceptions(cursor)
            
            # Get class name
            class_name = self._get_class_name(cursor)
            
            # Analyze function body
            body = self._analyze_function_body(cursor)
            
            # Get line numbers
            line_number = cursor.location.line
            end_line = self._get_end_line(cursor)
            
            function = Function(
                name=name,
                return_type="void",  # Constructors don't return anything
                parameters=parameters,
                exceptions=exceptions,
                body=body,
                function_type=FunctionType.CONSTRUCTOR,
                class_name=class_name,
                line_number=line_number,
                end_line=end_line
            )
            
            return function
            
        except Exception as e:
            print(f"Error parsing constructor {cursor.spelling}: {e}")
            return None
    
    def _parse_destructor_decl(self, cursor: Cursor) -> Optional[Function]:
        """
        Parse a destructor declaration.
        
        Args:
            cursor: Destructor declaration cursor
            
        Returns:
            Function object or None if parsing fails
        """
        if not CLANG_AVAILABLE:
            return None
            
        try:
            # Get destructor name
            name = cursor.spelling
            
            # Get parameters (destructors have no parameters)
            parameters = []
            
            # Get exceptions
            exceptions = self._parse_exceptions(cursor)
            
            # Get class name
            class_name = self._get_class_name(cursor)
            
            # Analyze function body
            body = self._analyze_function_body(cursor)
            
            # Get line numbers
            line_number = cursor.location.line
            end_line = self._get_end_line(cursor)
            
            function = Function(
                name=name,
                return_type="void",  # Destructors don't return anything
                parameters=parameters,
                exceptions=exceptions,
                body=body,
                function_type=FunctionType.DESTRUCTOR,
                class_name=class_name,
                line_number=line_number,
                end_line=end_line
            )
            
            return function
            
        except Exception as e:
            print(f"Error parsing destructor {cursor.spelling}: {e}")
            return None
    
    def _parse_parameters(self, cursor: Cursor) -> List[Parameter]:
        """
        Parse function parameters.
        
        Args:
            cursor: Function cursor
            
        Returns:
            List of Parameter objects
        """
        if not CLANG_AVAILABLE:
            return []
            
        parameters = []
        
        for child in cursor.get_children():
            if child.kind == clang.cindex.CursorKind.PARM_DECL:
                param_name = child.spelling
                param_type = self._get_type_string(child.type)
                
                parameter = Parameter(
                    name=param_name,
                    type=param_type
                )
                parameters.append(parameter)
        
        return parameters
    
    def _parse_exceptions(self, cursor: Cursor) -> List[FunctionException]:
        """
        Parse exceptions that can be thrown by the function.
        
        Args:
            cursor: Function cursor
            
        Returns:
            List of Exception objects
        """
        if not CLANG_AVAILABLE:
            return []
            
        exceptions = []
        
        # This is a simplified implementation
        # In a real implementation, you would need to analyze the function body
        # and look for throw statements or exception specifications
        
        # For now, we'll look for common exception patterns in the function body
        for child in cursor.get_children():
            if child.kind == clang.cindex.CursorKind.COMPOUND_STMT:
                self._find_exceptions_in_body(child, exceptions)
        
        return exceptions
    
    def _find_exceptions_in_body(self, cursor: Cursor, exceptions: List[FunctionException]) -> None:
        """
        Find exceptions in function body.
        
        Args:
            cursor: Function body cursor
            exceptions: List to populate with exceptions
        """
        if not CLANG_AVAILABLE:
            return
            
        for child in cursor.get_children():
            if child.kind == clang.cindex.CursorKind.CALL_EXPR:
                # Check if this is a throw call
                if child.spelling == "throw":
                    # Extract exception type from throw statement
                    for arg in child.get_children():
                        if arg.kind == clang.cindex.CursorKind.TYPE_REF:
                            exc_name = arg.spelling
                            exceptions.append(Exception(name=exc_name))
            
            # Recursively search in compound statements
            if child.kind == clang.cindex.CursorKind.COMPOUND_STMT:
                self._find_exceptions_in_body(child, exceptions)
    
    def _analyze_function_body(self, cursor: Cursor) -> FunctionBody:
        """
        Analyze the function body for patterns and behaviors.
        
        Args:
            cursor: Function cursor
            
        Returns:
            FunctionBody object with analysis results
        """
        if not CLANG_AVAILABLE:
            return FunctionBody()
            
        body = FunctionBody()
        
        # Find the function body (compound statement)
        for child in cursor.get_children():
            if child.kind == clang.cindex.CursorKind.COMPOUND_STMT:
                self._analyze_compound_statement(child, body, cursor.spelling)
                break
        
        return body
    
    def _analyze_compound_statement(self, cursor: Cursor, body: FunctionBody, function_name: str = "") -> None:
        """
        Analyze a compound statement for patterns.
        
        Args:
            cursor: Compound statement cursor
            body: FunctionBody object to update
        """
        if not CLANG_AVAILABLE:
            return
            
        for child in cursor.get_children():
            if child.kind == clang.cindex.CursorKind.FOR_STMT:
                body.has_loops = True
                # Recursively analyze the for loop body
                self._analyze_compound_statement(child, body, function_name)
            elif child.kind == clang.cindex.CursorKind.WHILE_STMT:
                body.has_loops = True
                # Recursively analyze the while loop body
                self._analyze_compound_statement(child, body, function_name)
            elif child.kind == clang.cindex.CursorKind.DO_STMT:
                body.has_loops = True
                # Recursively analyze the do-while loop body
                self._analyze_compound_statement(child, body, function_name)
            elif child.kind == clang.cindex.CursorKind.IF_STMT:
                body.has_conditionals = True
                # Recursively analyze the if statement body
                self._analyze_compound_statement(child, body, function_name)
            elif child.kind == clang.cindex.CursorKind.SWITCH_STMT:
                body.has_conditionals = True
                # Recursively analyze the switch statement body
                self._analyze_compound_statement(child, body, function_name)
            elif child.kind == clang.cindex.CursorKind.RETURN_STMT:
                body.has_returns = True
                # Recursively analyze the return statement to find function calls
                self._analyze_compound_statement(child, body, function_name)
            elif child.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
                # Check for arithmetic operations
                op = child.spelling
                if op in ['+', '-', '*', '/', '%', '<<', '>>', '&', '|', '^']:
                    body.has_arithmetic = True
                # Recursively analyze binary operators to find function calls
                self._analyze_compound_statement(child, body, function_name)
            elif child.kind == clang.cindex.CursorKind.CALL_EXPR:
                body.has_side_effects = True
                # Check for specific function calls
                func_name = child.spelling
                if func_name in ['printf', 'cout', 'cerr', 'fprintf', 'cin', 'scanf']:
                    body.has_string_operations = True
                elif func_name in ['fopen', 'fclose', 'fread', 'fwrite', 'remove', 'rename']:
                    body.has_file_operations = True
                elif func_name in ['malloc', 'free', 'new', 'delete', 'vector', 'map', 'set', 'list']:
                    body.has_collections = True
                elif func_name in ['regex_match', 'regex_search', 'regex_replace']:
                    body.has_regex = True
                # Check for recursion
                if func_name == function_name:
                    body.has_recursion = True
            
            # Recursively analyze nested compound statements
            if child.kind == clang.cindex.CursorKind.COMPOUND_STMT:
                self._analyze_compound_statement(child, body, function_name)
    
    def _get_type_string(self, type_obj: Type) -> str:
        """
        Get a string representation of a type.
        
        Args:
            type_obj: libclang type object
            
        Returns:
            Type string
        """
        if not CLANG_AVAILABLE:
            return type_obj.spelling
            
        return type_obj.spelling
    
    def _get_class_name(self, cursor: Cursor) -> Optional[str]:
        """
        Get the class name for a method.
        
        Args:
            cursor: Method cursor
            
        Returns:
            Class name or None
        """
        if not CLANG_AVAILABLE:
            return None
            
        # Find the parent class
        parent = cursor.semantic_parent
        if parent and parent.kind == clang.cindex.CursorKind.CLASS_DECL:
            return parent.spelling
        return None
    
    def _get_end_line(self, cursor: Cursor) -> int:
        """
        Get the end line number of the function.
        
        Args:
            cursor: Function cursor
            
        Returns:
            End line number
        """
        if not CLANG_AVAILABLE:
            # This is a simplified implementation
            # In a real implementation, you would need to traverse the AST
            # to find the actual end of the function
            
            # For now, we'll use a reasonable estimate
            return cursor.location.line + 10  # Assume 10 lines for the function
            
        # This is a simplified implementation
        # In a real implementation, you would need to traverse the AST
        # to find the actual end of the function
        
        # For now, we'll use a reasonable estimate
        return cursor.location.line + 10  # Assume 10 lines for the function
    
    def _extract_function_source(self, cursor: Cursor) -> str:
        """
        Extract the source code for a function from the cursor.
        
        Args:
            cursor: Function cursor
            
        Returns:
            Function source code as string
        """
        if not CLANG_AVAILABLE:
            return ""
            
        try:
            # Get the file content
            file_path = cursor.location.file
            if not file_path:
                return ""
                
            with open(str(file_path), 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
            
            # Get start and end lines
            start_line = cursor.location.line - 1  # 0-indexed
            end_line = self._get_end_line(cursor) - 1  # 0-indexed
            
            # Extract the function source
            function_lines = source_lines[start_line:end_line + 1]
            return ''.join(function_lines)
            
        except Exception as e:
            print(f"Error extracting function source: {e}")
            return ""
    
    def _parse_with_regex_fallback(self, file_path: Path) -> ParsedFile:
        """
        Fallback regex-based parsing for C++ files when libclang fails.
        
        Args:
            file_path: Path to the C++ file
            
        Returns:
            ParsedFile object with extracted functions
        """
        import re
        
        if not CLANG_AVAILABLE:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                parsed_file = ParsedFile(
                    file_path=str(file_path),
                    language='c++'
                )
                
                # Extract functions using regex patterns
                functions = self._extract_functions_regex(source_code)
                for function in functions:
                    parsed_file.add_function(function)
                
                return parsed_file
                
            except Exception as e:
                print(f"Error in regex fallback for {file_path}: {e}")
                return ParsedFile(file_path=str(file_path), language='c++')
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            parsed_file = ParsedFile(
                file_path=str(file_path),
                language='c++'
            )
            
            # Extract functions using regex patterns
            functions = self._extract_functions_regex(source_code)
            for function in functions:
                parsed_file.add_function(function)
            
            return parsed_file
            
        except Exception as e:
            print(f"Error in regex fallback for {file_path}: {e}")
            return ParsedFile(file_path=str(file_path), language='c++')
    
    def _extract_functions_regex(self, source_code: str) -> List[Function]:
        """
        Extract functions using regex patterns with basic body analysis.
        
        Args:
            source_code: C++ source code
            
        Returns:
            List of Function objects
        """
        import re
        
        if not CLANG_AVAILABLE:
            functions = []
            
            # Pattern for function definitions
            # Matches: return_type function_name(parameters) { body }
            function_pattern = r'(\w+(?:\s*<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{'
            
            matches = re.finditer(function_pattern, source_code)
            for match in matches:
                return_type = match.group(1).strip()
                function_name = match.group(2).strip()
                params_str = match.group(3).strip()
                
                # Parse parameters
                parameters = []
                if params_str:
                    parameters = self._parse_parameters_regex(params_str)
                
                # Extract function body for analysis
                body = self._analyze_function_body_regex(source_code, match.start(), function_name)
                
                function = Function(
                    name=function_name,
                    return_type=return_type,
                    parameters=parameters,
                    body=body,
                    function_type=FunctionType.FUNCTION
                )
                
                functions.append(function)
            
            return functions
            
        functions = []
        
        # Pattern for function definitions
        # Matches: return_type function_name(parameters) { body }
        function_pattern = r'(\w+(?:\s*<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{'
        
        matches = re.finditer(function_pattern, source_code)
        for match in matches:
            return_type = match.group(1).strip()
            function_name = match.group(2).strip()
            params_str = match.group(3).strip()
            
            # Parse parameters
            parameters = []
            if params_str:
                parameters = self._parse_parameters_regex(params_str)
            
            # Extract function body for analysis
            body = self._analyze_function_body_regex(source_code, match.start())
            
            function = Function(
                name=function_name,
                return_type=return_type,
                parameters=parameters,
                body=body,
                function_type=FunctionType.FUNCTION
            )
            
            functions.append(function)
        
        return functions
    
    def _analyze_function_body_regex(self, source_code: str, function_start: int, function_name: str) -> FunctionBody:
        """
        Analyze function body using regex patterns for NLTK analysis.
        
        Args:
            source_code: Complete source code
            function_start: Start position of function definition
            
        Returns:
            FunctionBody object with analysis results
        """
        import re
        
        if not CLANG_AVAILABLE:
            body = FunctionBody()
            
            # Extract the function body
            # Find the opening brace and extract everything until matching closing brace
            brace_count = 0
            body_start = -1
            body_end = -1
            
            for i in range(function_start, len(source_code)):
                if source_code[i] == '{':
                    if brace_count == 0:
                        body_start = i + 1
                    brace_count += 1
                elif source_code[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        body_end = i
                        break
            
            if body_start != -1 and body_end != -1:
                function_body = source_code[body_start:body_end]
                
                # Analyze patterns in the function body
                body.has_loops = bool(re.search(r'\b(for|while)\s*\(', function_body))
                body.has_conditionals = bool(re.search(r'\b(if|else|switch)\s*\(', function_body))
                body.has_arithmetic = bool(re.search(r'[\+\-\*/%]', function_body))
                body.has_comparisons = bool(re.search(r'[<>!=]=?', function_body))
                body.has_function_calls = bool(re.search(r'\w+\s*\(', function_body))
                body.has_returns = bool(re.search(r'\breturn\b', function_body))
                body.has_exceptions = bool(re.search(r'\b(throw|try|catch)\b', function_body))
                body.has_side_effects = bool(re.search(r'\b(cout|printf|fprintf|fopen|fclose|new|delete)\b', function_body))
                body.has_early_returns = len(re.findall(r'\breturn\b', function_body)) > 1
                
                # Enhanced pattern detection for intelligent analysis
                body.has_recursion = bool(re.search(rf'\b{re.escape(function_name)}\s*\(', function_body))
                body.has_regex = bool(re.search(r'\b(regex_match|regex_search|regex_replace)\b', function_body))
                body.has_api_calls = bool(re.search(r'\b(cout|cin|printf|scanf|fopen|fclose|fread|fwrite)\b', function_body))
                body.has_file_operations = bool(re.search(r'\b(fopen|fclose|fread|fwrite|remove|rename)\b', function_body))
                body.has_collections = bool(re.search(r'\b(vector|map|set|list|array|deque|queue|stack)\b', function_body))
                body.has_string_operations = bool(re.search(r'\b(cout|cin|printf|scanf|string|strlen|strcpy|strcat)\b', function_body))
                
                # Count complexity
                body.loop_count = len(re.findall(r'\b(for|while)\s*\(', function_body))
                body.conditional_count = len(re.findall(r'\b(if|else|switch)\s*\(', function_body))
                body.function_call_count = len(re.findall(r'\w+\s*\(', function_body))
                body.return_count = len(re.findall(r'\breturn\b', function_body))
            
            return body
            
        # If clang is available, this method shouldn't be called
        return FunctionBody()
    
    def _parse_parameters_regex(self, params_str: str) -> List[Parameter]:
        """
        Parse parameters using regex.
        
        Args:
            params_str: Parameters string
            
        Returns:
            List of Parameter objects
        """
        import re
        
        if not CLANG_AVAILABLE:
            parameters = []
            
            if not params_str.strip():
                return parameters
            
            # Split by comma, but be careful about template types
            param_parts = []
            current_param = ""
            bracket_count = 0
            
            for char in params_str:
                if char == '<':
                    bracket_count += 1
                elif char == '>':
                    bracket_count -= 1
                elif char == ',' and bracket_count == 0:
                    param_parts.append(current_param.strip())
                    current_param = ""
                    continue
                
                current_param += char
            
            if current_param.strip():
                param_parts.append(current_param.strip())
            
            for param_part in param_parts:
                # Extract type and name
                # Pattern: type name or type& name or type* name
                param_match = re.search(r'(\w+(?:\s*<[^>]*>)?(?:\s*[&*])?)\s+(\w+)', param_part)
                if param_match:
                    param_type = param_match.group(1).strip()
                    param_name = param_match.group(2).strip()
                    parameters.append(Parameter(name=param_name, type=param_type))
            
            return parameters
            
        parameters = []
        
        if not params_str.strip():
            return parameters
        
        # Split by comma, but be careful about template types
        param_parts = []
        current_param = ""
        bracket_count = 0
        
        for char in params_str:
            if char == '<':
                bracket_count += 1
            elif char == '>':
                bracket_count -= 1
            elif char == ',' and bracket_count == 0:
                param_parts.append(current_param.strip())
                current_param = ""
                continue
            
            current_param += char
        
        if current_param.strip():
            param_parts.append(current_param.strip())
        
        for param_part in param_parts:
            # Extract type and name
            # Pattern: type name or type& name or type* name
            param_match = re.search(r'(\w+(?:\s*<[^>]*>)?(?:\s*[&*])?)\s+(\w+)', param_part)
            if param_match:
                param_type = param_match.group(1).strip()
                param_name = param_match.group(2).strip()
                parameters.append(Parameter(name=param_name, type=param_type))
        
        return parameters 