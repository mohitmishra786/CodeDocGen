"""
C++ parser for CodeDocGen.

Uses libclang to parse C++ code and extract function signatures,
parameters, and analyze function bodies.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional

from . import BaseParser
from ..models import Function, Parameter, FunctionBody, Exception, ParsedFile, FunctionType
from ..config import Config

# Try to import clang, but don't fail if it's not available
try:
    import clang.cindex
    CLANG_AVAILABLE = True
except ImportError:
    CLANG_AVAILABLE = False


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
            clang.cindex.Config.set_library_file('/System/Volumes/Data/Library/Developer/CommandLineTools/usr/lib/libclang.dylib')
        except Exception:
            # Try alternative paths
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
            
        except:
            # Fallback to regex-based parsing for C++
            return self._parse_with_regex_fallback(file_path)
    
    def _extract_functions(self, cursor: clang.cindex.Cursor, parsed_file: ParsedFile) -> None:
        """
        Extract functions from the AST cursor.
        
        Args:
            cursor: libclang cursor
            parsed_file: ParsedFile object to populate
        """
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
    
    def _parse_function_decl(self, cursor: clang.cindex.Cursor) -> Optional[Function]:
        """
        Parse a function declaration.
        
        Args:
            cursor: Function declaration cursor
            
        Returns:
            Function object or None if parsing fails
        """
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
            
            # Get line numbers
            line_number = cursor.location.line
            end_line = self._get_end_line(cursor)
            
            function = Function(
                name=name,
                return_type=return_type,
                parameters=parameters,
                exceptions=exceptions,
                body=body,
                function_type=FunctionType.FUNCTION,
                line_number=line_number,
                end_line=end_line
            )
            
            return function
            
        except Exception as e:
            print(f"Error parsing function {cursor.spelling}: {e}")
            return None
    
    def _parse_method_decl(self, cursor: clang.cindex.Cursor) -> Optional[Function]:
        """
        Parse a method declaration.
        
        Args:
            cursor: Method declaration cursor
            
        Returns:
            Function object or None if parsing fails
        """
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
            
            # Get line numbers
            line_number = cursor.location.line
            end_line = self._get_end_line(cursor)
            
            function = Function(
                name=name,
                return_type=return_type,
                parameters=parameters,
                exceptions=exceptions,
                body=body,
                function_type=FunctionType.METHOD,
                class_name=class_name,
                line_number=line_number,
                end_line=end_line
            )
            
            return function
            
        except Exception as e:
            print(f"Error parsing method {cursor.spelling}: {e}")
            return None
    
    def _parse_constructor_decl(self, cursor: clang.cindex.Cursor) -> Optional[Function]:
        """
        Parse a constructor declaration.
        
        Args:
            cursor: Constructor declaration cursor
            
        Returns:
            Function object or None if parsing fails
        """
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
    
    def _parse_destructor_decl(self, cursor: clang.cindex.Cursor) -> Optional[Function]:
        """
        Parse a destructor declaration.
        
        Args:
            cursor: Destructor declaration cursor
            
        Returns:
            Function object or None if parsing fails
        """
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
    
    def _parse_parameters(self, cursor: clang.cindex.Cursor) -> List[Parameter]:
        """
        Parse function parameters.
        
        Args:
            cursor: Function cursor
            
        Returns:
            List of Parameter objects
        """
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
    
    def _parse_exceptions(self, cursor: clang.cindex.Cursor) -> List[Exception]:
        """
        Parse exceptions that can be thrown by the function.
        
        Args:
            cursor: Function cursor
            
        Returns:
            List of Exception objects
        """
        exceptions = []
        
        # This is a simplified implementation
        # In a real implementation, you would need to analyze the function body
        # and look for throw statements or exception specifications
        
        # For now, we'll look for common exception patterns in the function body
        for child in cursor.get_children():
            if child.kind == clang.cindex.CursorKind.COMPOUND_STMT:
                self._find_exceptions_in_body(child, exceptions)
        
        return exceptions
    
    def _find_exceptions_in_body(self, cursor: clang.cindex.Cursor, exceptions: List[Exception]) -> None:
        """
        Find exceptions in function body.
        
        Args:
            cursor: Function body cursor
            exceptions: List to populate with exceptions
        """
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
    
    def _analyze_function_body(self, cursor: clang.cindex.Cursor) -> FunctionBody:
        """
        Analyze the function body for patterns and behaviors.
        
        Args:
            cursor: Function cursor
            
        Returns:
            FunctionBody object with analysis results
        """
        body = FunctionBody()
        
        # Find the function body (compound statement)
        for child in cursor.get_children():
            if child.kind == clang.cindex.CursorKind.COMPOUND_STMT:
                self._analyze_compound_statement(child, body)
                break
        
        return body
    
    def _analyze_compound_statement(self, cursor: clang.cindex.Cursor, body: FunctionBody) -> None:
        """
        Analyze a compound statement for patterns.
        
        Args:
            cursor: Compound statement cursor
            body: FunctionBody object to update
        """
        for child in cursor.get_children():
            if child.kind == clang.cindex.CursorKind.FOR_STMT:
                body.has_loops = True
            elif child.kind == clang.cindex.CursorKind.WHILE_STMT:
                body.has_loops = True
            elif child.kind == clang.cindex.CursorKind.DO_STMT:
                body.has_loops = True
            elif child.kind == clang.cindex.CursorKind.IF_STMT:
                body.has_conditionals = True
            elif child.kind == clang.cindex.CursorKind.SWITCH_STMT:
                body.has_conditionals = True
            elif child.kind == clang.cindex.CursorKind.RETURN_STMT:
                body.has_returns = True
            elif child.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
                # Check for arithmetic operations
                op = child.spelling
                if op in ['+', '-', '*', '/', '%', '<<', '>>', '&', '|', '^']:
                    body.has_arithmetic = True
            elif child.kind == clang.cindex.CursorKind.CALL_EXPR:
                body.has_side_effects = True
                # Check for specific function calls
                func_name = child.spelling
                if func_name in ['printf', 'cout', 'cerr', 'fprintf']:
                    body.has_string_operations = True
                elif func_name in ['fopen', 'fclose', 'fread', 'fwrite']:
                    body.has_file_operations = True
            
            # Recursively analyze nested compound statements
            if child.kind == clang.cindex.CursorKind.COMPOUND_STMT:
                self._analyze_compound_statement(child, body)
    
    def _get_type_string(self, type_obj: clang.cindex.Type) -> str:
        """
        Get a string representation of a type.
        
        Args:
            type_obj: libclang type object
            
        Returns:
            Type string
        """
        return type_obj.spelling
    
    def _get_class_name(self, cursor: clang.cindex.Cursor) -> Optional[str]:
        """
        Get the class name for a method.
        
        Args:
            cursor: Method cursor
            
        Returns:
            Class name or None
        """
        # Find the parent class
        parent = cursor.semantic_parent
        if parent and parent.kind == clang.cindex.CursorKind.CLASS_DECL:
            return parent.spelling
        return None
    
    def _get_end_line(self, cursor: clang.cindex.Cursor) -> int:
        """
        Get the end line number of the function.
        
        Args:
            cursor: Function cursor
            
        Returns:
            End line number
        """
        # This is a simplified implementation
        # In a real implementation, you would need to traverse the AST
        # to find the actual end of the function
        
        # For now, we'll use a reasonable estimate
        return cursor.location.line + 10  # Assume 10 lines for the function
    
    def _parse_with_regex_fallback(self, file_path: Path) -> ParsedFile:
        """
        Fallback regex-based parsing for C++ files when libclang fails.
        
        Args:
            file_path: Path to the C++ file
            
        Returns:
            ParsedFile object with extracted functions
        """
        import re
        
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
        Extract functions using regex patterns.
        
        Args:
            source_code: C++ source code
            
        Returns:
            List of Function objects
        """
        import re
        
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
                params = self._parse_parameters_regex(params_str)
                parameters = params
            
            # Create function body (simplified)
            body = FunctionBody()
            
            function = Function(
                name=function_name,
                return_type=return_type,
                parameters=parameters,
                body=body,
                function_type=FunctionType.FUNCTION
            )
            
            functions.append(function)
        
        return functions
    
    def _parse_parameters_regex(self, params_str: str) -> List[Parameter]:
        """
        Parse parameters using regex.
        
        Args:
            params_str: Parameters string
            
        Returns:
            List of Parameter objects
        """
        import re
        
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