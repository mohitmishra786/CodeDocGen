"""
Java parser for CodeDocGen.

Uses javaparser to parse Java code and extract function signatures,
parameters, and analyze function bodies.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from . import BaseParser
from ..models import Function, Parameter, FunctionBody, Exception, ParsedFile, FunctionType
from ..config import Config


class JavaParser(BaseParser):
    """Parser for Java source files."""
    
    def __init__(self, config: Config):
        """
        Initialize the Java parser.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        # Try to import javaparser
        try:
            import javaparser
            self.javaparser = javaparser
        except ImportError:
            self.javaparser = None
            print("Warning: javaparser not available, using regex-based parsing")
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the parser can handle this file
        """
        return file_path.suffix.lower() == '.java'
    
    def parse_file(self, file_path: Path) -> ParsedFile:
        """
        Parse a Java source file and extract functions.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            ParsedFile object containing extracted functions
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            parsed_file = ParsedFile(
                file_path=str(file_path),
                language='java'
            )
            
            if self.javaparser:
                # Use javaparser if available
                return self._parse_with_javaparser(source_code, parsed_file)
            else:
                # Fallback to regex-based parsing
                return self._parse_with_regex(source_code, parsed_file)
            
        except Exception as e:
            print(f"Error parsing Java file {file_path}: {e}")
            return ParsedFile(file_path=str(file_path), language='java')
    
    def _parse_with_javaparser(self, source_code: str, parsed_file: ParsedFile) -> ParsedFile:
        """
        Parse Java code using javaparser.
        
        Args:
            source_code: Java source code
            parsed_file: ParsedFile object to populate
            
        Returns:
            Updated ParsedFile object
        """
        try:
            # Parse the source code
            compilation_unit = self.javaparser.parse(source_code)
            
            # Extract imports
            parsed_file.imports = self._extract_imports_javaparser(compilation_unit)
            
            # Extract classes
            parsed_file.classes = self._extract_classes_javaparser(compilation_unit)
            
            # Extract methods
            methods = self._extract_methods_javaparser(compilation_unit)
            for method in methods:
                parsed_file.add_function(method)
            
            return parsed_file
            
        except Exception as e:
            print(f"Error with javaparser: {e}")
            # Fallback to regex parsing
            return self._parse_with_regex(source_code, parsed_file)
    
    def _parse_with_regex(self, source_code: str, parsed_file: ParsedFile) -> ParsedFile:
        """
        Parse Java code using regex patterns.
        
        Args:
            source_code: Java source code
            parsed_file: ParsedFile object to populate
            
        Returns:
            Updated ParsedFile object
        """
        # Extract imports
        parsed_file.imports = self._extract_imports_regex(source_code)
        
        # Extract classes
        parsed_file.classes = self._extract_classes_regex(source_code)
        
        # Extract methods
        methods = self._extract_methods_regex(source_code)
        for method in methods:
            parsed_file.add_function(method)
        
        return parsed_file
    
    def _extract_imports_javaparser(self, compilation_unit) -> List[str]:
        """
        Extract imports using javaparser.
        
        Args:
            compilation_unit: javaparser compilation unit
            
        Returns:
            List of import statements
        """
        imports = []
        try:
            for import_decl in compilation_unit.getImports():
                imports.append(import_decl.toString())
        except:
            pass
        return imports
    
    def _extract_imports_regex(self, source_code: str) -> List[str]:
        """
        Extract imports using regex.
        
        Args:
            source_code: Java source code
            
        Returns:
            List of import statements
        """
        imports = []
        import_pattern = r'import\s+([^;]+);'
        matches = re.findall(import_pattern, source_code)
        for match in matches:
            imports.append(f"import {match.strip()};")
        return imports
    
    def _extract_classes_javaparser(self, compilation_unit) -> List[str]:
        """
        Extract class names using javaparser.
        
        Args:
            compilation_unit: javaparser compilation unit
            
        Returns:
            List of class names
        """
        classes = []
        try:
            for type_decl in compilation_unit.getTypes():
                if hasattr(type_decl, 'getName'):
                    classes.append(type_decl.getName())
        except:
            pass
        return classes
    
    def _extract_classes_regex(self, source_code: str) -> List[str]:
        """
        Extract class names using regex.
        
        Args:
            source_code: Java source code
            
        Returns:
            List of class names
        """
        classes = []
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)'
        matches = re.findall(class_pattern, source_code)
        classes.extend(matches)
        
        # Also find interfaces
        interface_pattern = r'(?:public\s+)?interface\s+(\w+)'
        matches = re.findall(interface_pattern, source_code)
        classes.extend(matches)
        
        return classes
    
    def _extract_methods_javaparser(self, compilation_unit) -> List[Function]:
        """
        Extract methods using javaparser.
        
        Args:
            compilation_unit: javaparser compilation unit
            
        Returns:
            List of Function objects
        """
        methods = []
        try:
            for type_decl in compilation_unit.getTypes():
                if hasattr(type_decl, 'getMethods'):
                    for method_decl in type_decl.getMethods():
                        function = self._parse_method_javaparser(method_decl, type_decl.getName())
                        if function:
                            methods.append(function)
        except:
            pass
        return methods
    
    def _extract_methods_regex(self, source_code: str) -> List[Function]:
        """
        Extract methods using regex.
        
        Args:
            source_code: Java source code
            
        Returns:
            List of Function objects
        """
        methods = []
        
        # Method pattern: modifiers return_type method_name(parameters) throws exceptions
        method_pattern = r'(?:public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *[^\{]*\{'
        
        matches = re.finditer(method_pattern, source_code)
        for match in matches:
            method_name = match.group(1)
            
            # Get the method signature
            start = match.start()
            end = source_code.find('{', start)
            if end == -1:
                continue
            
            signature = source_code[start:end].strip()
            function = self._parse_method_signature(signature, method_name)
            if function:
                methods.append(function)
        
        return methods
    
    def _parse_method_javaparser(self, method_decl, class_name: str) -> Optional[Function]:
        """
        Parse a method using javaparser.
        
        Args:
            method_decl: javaparser method declaration
            class_name: Name of the containing class
            
        Returns:
            Function object or None if parsing fails
        """
        try:
            # Get method name
            name = method_decl.getName()
            
            # Get return type
            return_type = method_decl.getType().toString()
            
            # Get parameters
            parameters = []
            for param in method_decl.getParameters():
                param_name = param.getName()
                param_type = param.getType().toString()
                parameters.append(Parameter(name=param_name, type=param_type))
            
            # Get exceptions
            exceptions = []
            for exception in method_decl.getThrownExceptions():
                exceptions.append(Exception(name=exception.toString()))
            
            # Determine function type
            function_type = FunctionType.METHOD
            if name == class_name:
                function_type = FunctionType.CONSTRUCTOR
            elif name == f"~{class_name}":
                function_type = FunctionType.DESTRUCTOR
            
            # Analyze function body
            body = self._analyze_method_body_javaparser(method_decl)
            
            function = Function(
                name=name,
                return_type=return_type,
                parameters=parameters,
                exceptions=exceptions,
                body=body,
                function_type=function_type,
                class_name=class_name
            )
            
            return function
            
        except Exception as e:
            print(f"Error parsing method {method_decl.getName()}: {e}")
            return None
    
    def _parse_method_signature(self, signature: str, method_name: str) -> Optional[Function]:
        """
        Parse a method signature using regex.
        
        Args:
            signature: Method signature string
            method_name: Method name
            
        Returns:
            Function object or None if parsing fails
        """
        try:
            # Extract return type
            return_type_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s+' + re.escape(method_name), signature)
            return_type = return_type_match.group(1) if return_type_match else "void"
            
            # Extract parameters
            params_match = re.search(r'\(([^)]*)\)', signature)
            parameters = []
            if params_match:
                params_str = params_match.group(1).strip()
                if params_str:
                    params = self._parse_parameters_regex(params_str)
                    parameters = params
            
            # Extract exceptions
            exceptions = []
            throws_match = re.search(r'throws\s+([^{]+)', signature)
            if throws_match:
                throws_str = throws_match.group(1).strip()
                exceptions = [Exception(name=exc.strip()) for exc in throws_str.split(',')]
            
            # Determine function type
            function_type = FunctionType.METHOD
            if method_name == "main":
                function_type = FunctionType.FUNCTION
            
            # Create function body (simplified)
            body = FunctionBody()
            
            function = Function(
                name=method_name,
                return_type=return_type,
                parameters=parameters,
                exceptions=exceptions,
                body=body,
                function_type=function_type
            )
            
            return function
            
        except Exception as e:
            print(f"Error parsing method signature {method_name}: {e}")
            return None
    
    def _parse_parameters_regex(self, params_str: str) -> List[Parameter]:
        """
        Parse parameters using regex.
        
        Args:
            params_str: Parameters string
            
        Returns:
            List of Parameter objects
        """
        parameters = []
        
        # Split by comma, but be careful about generic types
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
            param_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_<>\[\]]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)', param_part)
            if param_match:
                param_type = param_match.group(1)
                param_name = param_match.group(2)
                parameters.append(Parameter(name=param_name, type=param_type))
        
        return parameters
    
    def _analyze_method_body_javaparser(self, method_decl) -> FunctionBody:
        """
        Analyze method body using javaparser.
        
        Args:
            method_decl: javaparser method declaration
            
        Returns:
            FunctionBody object with analysis results
        """
        body = FunctionBody()
        
        try:
            # Get the method body
            method_body = method_decl.getBody()
            if method_body:
                # Analyze the body for patterns
                body_text = method_body.toString()
                
                # Check for loops
                if any(keyword in body_text for keyword in ['for', 'while', 'do']):
                    body.has_loops = True
                
                # Check for conditionals
                if any(keyword in body_text for keyword in ['if', 'switch']):
                    body.has_conditionals = True
                
                # Check for exceptions
                if 'throw' in body_text:
                    body.has_exceptions = True
                
                # Check for returns
                if 'return' in body_text:
                    body.has_returns = True
                
                # Check for arithmetic operations
                if any(op in body_text for op in ['+', '-', '*', '/', '%']):
                    body.has_arithmetic = True
                
                # Check for string operations
                if any(method in body_text for method in ['.length()', '.substring(', '.indexOf(', '.charAt(']):
                    body.has_string_operations = True
                
                # Check for file operations
                if any(keyword in body_text for keyword in ['File', 'InputStream', 'OutputStream', 'Reader', 'Writer']):
                    body.has_file_operations = True
                
                # Check for side effects
                if '=' in body_text or '(' in body_text:
                    body.has_side_effects = True
                
        except:
            pass
        
        return body 