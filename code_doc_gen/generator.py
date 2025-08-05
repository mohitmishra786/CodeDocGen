"""
Documentation generator for CodeDocGen.

Formats and generates documentation comments for functions
in various programming languages.
"""

import re
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from difflib import unified_diff

from .models import Function, DocumentationResult, FunctionType
from .config import Config


class DocumentationGenerator:
    """Generates documentation comments for functions."""
    
    def __init__(self, config: Config):
        """
        Initialize the documentation generator.
        
        Args:
            config: Configuration object
        """
        self.config = config
    
    """
        Generates the documentation based on self, functions, lang. Function iterates over data, conditionally processes input, has side effects. Takes self, functions and lang as input. Returns a dict[(str, str)] value.
        :param self: The self object.
        :param functions: The functions value of type List[Function].
        :param lang: The lang string.
        :return: Value of type Dict[(str, str)]

    """
    def generate_documentation(
        self, 
        functions: List[Function], 
        lang: str
    ) -> Dict[str, str]:
        """
        Generate documentation for a list of functions.
        
        Args:
            functions: List of functions to document
            lang: Programming language
            
        Returns:
            Dictionary mapping function names to documentation strings
        """
        documentation = {}
        
        for function in functions:
            try:
                # Check if function already has AI-generated documentation
                if function.brief_description and function.brief_description.strip():
                    # Function already has AI-generated documentation, use it directly
                    # But ensure it's properly formatted
                    if function.brief_description.startswith('"""') or function.brief_description.startswith('/**'):
                        # Already formatted as docstring, use as-is
                        documentation[function.get_full_name()] = function.brief_description
                    else:
                        # Raw description, format it properly
                        doc_result = self._generate_function_documentation(function, lang)
                        if doc_result:
                            documentation[function.get_full_name()] = doc_result.get_full_documentation()
                else:
                    # Generate template-based documentation only if no AI documentation exists
                    doc_result = self._generate_function_documentation(function, lang)
                    if doc_result:
                        documentation[function.get_full_name()] = doc_result.get_full_documentation()
            except Exception as e:
                print(f"Error generating documentation for {function.name}: {e}")
                continue
        
        return documentation
    
    def _generate_function_documentation(self, function: Function, lang: str) -> Optional[DocumentationResult]:
        """
        Generate documentation for a single function.
        
        Args:
            function: Function to document
            lang: Programming language
            
        Returns:
            DocumentationResult object or None if generation fails
        """
        # Generate brief documentation
        brief_doc = self._generate_brief_documentation(function, lang)
        
        # Generate detailed documentation
        detailed_doc = self._generate_detailed_documentation(function, lang)
        
        # Generate parameter documentation
        param_docs = self._generate_parameter_documentation(function, lang)
        
        # Generate return documentation
        return_doc = self._generate_return_documentation(function, lang)
        
        # Generate exception documentation
        exception_docs = self._generate_exception_documentation(function, lang)
        
        return DocumentationResult(
            function=function,
            brief_doc=brief_doc,
            detailed_doc=detailed_doc,
            param_docs=param_docs,
            return_doc=return_doc,
            exception_docs=exception_docs
        )
    
    def _generate_brief_documentation(self, function: Function, lang: str) -> str:
        """
        Generate brief documentation for a function.
        
        Args:
            function: Function to document
            lang: Programming language
            
        Returns:
            Brief documentation string
        """
        template = self.config.get_template(lang, "brief")
        
        if not template:
            # Fallback templates
            if lang == "c++":
                template = "/**\n * \\brief {description}\n */"
            elif lang == "python":
                template = '""" {description} """'
            elif lang == "java":
                template = "/**\n * {description}\n */"
            else:
                template = "/** {description} */"
        
        description = function.brief_description or function.detailed_description or f"Function {function.name}"
        
        return template.format(description=description)
    
    def _generate_detailed_documentation(self, function: Function, lang: str) -> str:
        """
        Generate detailed documentation for a function.
        
        Args:
            function: Function to document
            lang: Programming language
            
        Returns:
            Detailed documentation string
        """
        template = self.config.get_template(lang, "detailed")
        
        if not template:
            # Fallback templates
            if lang == "c++":
                template = "/**\n * \\brief {description}{params}{returns}{throws}\n */"
            elif lang == "python":
                template = '"""\n    {description}\n{params}{returns}{raises}\n    """'
            elif lang == "java":
                template = "/**\n * {description}\n *\n{params}{returns}{throws}\n */"
            else:
                template = "/**\n * {description}\n *\n{params}{returns}{throws}\n */"
        
        # Generate parameter documentation
        params_doc = self._generate_parameter_documentation_text(function, lang)
        
        # Generate return documentation
        returns_doc = self._generate_return_documentation_text(function, lang)
        
        # Generate exception documentation
        throws_doc = self._generate_exception_documentation_text(function, lang)
        
        description = function.detailed_description or function.brief_description or f"Function {function.name}"
        
        if lang == "c++":
            # Only add newlines if the section is non-empty
            params_doc = ("\n" + params_doc) if params_doc else ""
            returns_doc = ("\n" + returns_doc) if returns_doc else ""
            throws_doc = ("\n" + throws_doc) if throws_doc else ""
            template = "/**\n * \\brief {description}{params}{returns}{throws}\n */"
            return template.format(
                description=description,
                params=params_doc,
                returns=returns_doc,
                throws=throws_doc,
                raises=throws_doc  # For Python compatibility
            )
        elif lang == "python":
            # Check if we have any sections before processing
            has_sections = any([params_doc, returns_doc, throws_doc])
            
            # Determine if this is a class method
            is_class_method = function.function_type in [FunctionType.METHOD, FunctionType.CONSTRUCTOR, FunctionType.DESTRUCTOR] or function.class_name is not None
            
            if has_sections:
                # Add newlines for sections
                params_doc = ("\n" + params_doc) if params_doc else ""
                returns_doc = ("\n" + returns_doc) if returns_doc else ""
                throws_doc = ("\n" + throws_doc) if throws_doc else ""
                
                if is_class_method:
                    template = '"""\n    {description}{params}{returns}{raises}\n"""'
                else:
                    template = '"""\n    {description}{params}{returns}{raises}\n"""'
            else:
                # No sections, no extra newlines
                if is_class_method:
                    template = '"""\n    {description}\n"""'
                else:
                    template = '"""\n    {description}\n"""'
            
            return template.format(
                description=description,
                params=params_doc,
                returns=returns_doc,
                throws=throws_doc,
                raises=throws_doc  # For Python compatibility
            )
        else:
            # Only add newlines if the section is non-empty
            params_doc = ("\n" + params_doc) if params_doc else ""
            returns_doc = ("\n" + returns_doc) if returns_doc else ""
            throws_doc = ("\n" + throws_doc) if throws_doc else ""
            return template.format(
                description=description,
                params=params_doc,
                returns=returns_doc,
                throws=throws_doc,
                raises=throws_doc  # For Python compatibility
            )
    
    def _generate_parameter_documentation(self, function: Function, lang: str) -> Dict[str, str]:
        """
        Generate parameter documentation for a function.
        
        Args:
            function: Function to document
            lang: Programming language
            
        Returns:
            Dictionary mapping parameter names to documentation strings
        """
        param_docs = {}
        
        for parameter in function.parameters:
            template = self.config.get_template(lang, "param")
            
            if not template:
                # Fallback templates
                if lang == "c++":
                    template = " * \\param {name} {description}"
                elif lang == "python":
                    template = "    :param {name}: {description}"
                elif lang == "java":
                    template = " * @param {name} {description}"
                else:
                    template = " * @param {name} {description}"
            
            description = parameter.description or f"Parameter {parameter.name}"
            
            param_docs[parameter.name] = template.format(
                name=parameter.name,
                description=description
            )
        
        return param_docs
    
    def _generate_parameter_documentation_text(self, function: Function, lang: str) -> str:
        """
        Generate parameter documentation as text.
        
        Args:
            function: Function to document
            lang: Programming language
            
        Returns:
            Parameter documentation text
        """
        param_docs = self._generate_parameter_documentation(function, lang)
        
        if not param_docs:
            return ""
        
        # Join parameter documentation with newlines
        return "\n".join(param_docs.values())
    
    def _generate_return_documentation(self, function: Function, lang: str) -> Optional[str]:
        """
        Generate return documentation for a function.
        
        Args:
            function: Function to document
            lang: Programming language
            
        Returns:
            Return documentation string or None
        """
        if function.return_type.lower() == "void":
            return None
        
        template = self.config.get_template(lang, "return")
        
        if not template:
            # Fallback templates
            if lang == "c++":
                template = " * \\return {description}"
            elif lang == "python":
                template = "    :return: {description}"
            elif lang == "java":
                template = " * @return {description}"
            else:
                template = " * @return {description}"
        
        # Generate return description based on type
        description = self._generate_return_description(function)
        
        return template.format(description=description)
    
    def _generate_return_documentation_text(self, function: Function, lang: str) -> str:
        """
        Generate return documentation as text.
        
        Args:
            function: Function to document
            lang: Programming language
            
        Returns:
            Return documentation text
        """
        return_doc = self._generate_return_documentation(function, lang)
        
        if not return_doc:
            return ""
        
        return return_doc
    
    def _generate_return_description(self, function: Function) -> str:
        """
        Generate a description for the return value.
        
        Args:
            function: Function to document
            
        Returns:
            Return description string
        """
        return_type = function.return_type.lower()
        
        if return_type == "bool":
            return "True or false"
        elif return_type in ["int", "integer"]:
            return "Integer value"
        elif return_type in ["float", "double"]:
            return "Floating-point value"
        elif return_type in ["string", "str"]:
            return "String value"
        elif return_type in ["list", "array"]:
            return "List of values"
        elif return_type in ["dict", "map"]:
            return "Dictionary of values"
        else:
            return f"Value of type {function.return_type}"
    
    def _generate_exception_documentation(self, function: Function, lang: str) -> Dict[str, str]:
        """
        Generate exception documentation for a function.
        
        Args:
            function: Function to document
            lang: Programming language
            
        Returns:
            Dictionary mapping exception names to documentation strings
        """
        exception_docs = {}
        
        for exception in function.exceptions:
            template = self.config.get_template(lang, "throws")
            
            if not template:
                # Fallback templates
                if lang == "c++":
                    template = " * \\throws {exception} {description}"
                elif lang == "python":
                    template = "    :raises {exception}: {description}"
                elif lang == "java":
                    template = " * @throws {exception} {description}"
                else:
                    template = " * @throws {exception} {description}"
            
            description = exception.description or f"Thrown when {exception.name.lower()} occurs"
            
            exception_docs[exception.name] = template.format(
                exception=exception.name,
                description=description
            )
        
        return exception_docs
    
    def _generate_exception_documentation_text(self, function: Function, lang: str) -> str:
        """
        Generate exception documentation as text.
        
        Args:
            function: Function to document
            lang: Programming language
            
        Returns:
            Exception documentation text
        """
        exception_docs = self._generate_exception_documentation(function, lang)
        
        if not exception_docs:
            return ""
        
        # Join exception documentation with newlines
        return "\n".join(exception_docs.values())
    
    def apply_documentation_inplace(self, file_path: Path, documentation: Dict[str, str]) -> None:
        """
        Apply documentation to a file in place.
        
        Args:
            file_path: Path to the file to modify
            documentation: Dictionary mapping function names to documentation strings
        """
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        shutil.copy2(file_path, backup_path)
        
        try:
            # Read the original file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Infer language from file extension
            lang = self._infer_language_from_extension(file_path)
            
            # Apply documentation
            modified_lines = self._insert_documentation(lines, documentation, lang)
            
            # Write the modified file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(modified_lines)
            
            print(f"Applied documentation to {file_path}")
            
        except Exception as e:
            # Restore from backup
            shutil.copy2(backup_path, file_path)
            raise e
    
    def _infer_language_from_extension(self, file_path: Path) -> str:
        """
        Infer programming language from file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Language string ('python', 'c++', 'java', or 'unknown')
        """
        ext = file_path.suffix.lower()
        if ext == '.py':
            return 'python'
        elif ext in ['.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx']:
            return 'c++'
        elif ext == '.java':
            return 'java'
        else:  # Fallback for other languages
            return 'unknown'
    
    def _insert_documentation(self, lines: List[str], documentation: Dict[str, str], lang: str) -> List[str]:
        """
        Insert documentation into file lines.
        """
        modified_lines = []
        processed_functions = set()
        i = 0
        
        while i < len(lines):
            line = lines[i]
            inserted = False
            for qualified_name, doc_string in documentation.items():
                # Split qualified name for class methods
                if '::' in qualified_name:
                    class_name, func_name = qualified_name.split('::', 1)
                    match = re.match(r'^(\s*)def\s+' + re.escape(func_name) + r'\s*\(', line)
                    if not match:
                        match = re.match(r'^(\s*)(?:\w+\s+)*' + re.escape(class_name) + r'::' + re.escape(func_name) + r'\s*\(', line)
                else:
                    func_name = qualified_name
                    match = re.match(r'^(\s*)(?:async\s+)?def\s+' + re.escape(func_name) + r'\s*\(', line)
                    if not match:
                        match = re.match(r'^(\s*)(?:\w+\s+)*\b' + re.escape(func_name) + r'\s*\([^)]*\)\s*(?:const\s*)?\s*\{?\s*$', line)
                        if not match:
                            match = re.match(r'^(\s*)(?:\w+\s+)*\b' + re.escape(func_name) + r'\s*\([^)]*\)\s*$', line)
                if match and qualified_name not in processed_functions:
                    indent = match.group(1) or ''
                    # Check for actual documentation immediately before the function
                    doc_blocking = False
                    j = len(modified_lines) - 1
                    while j >= 0 and not modified_lines[j].strip():
                        j -= 1
                    if j >= 0:
                        prev_line = modified_lines[j].strip()
                        if (prev_line.startswith('/**') or prev_line.startswith('/*') or prev_line.startswith('///') or prev_line.startswith('*')):
                            doc_blocking = True
                        if prev_line.startswith('//') and any(keyword in prev_line.lower() for keyword in ['@brief', '@param', '@return', 'brief', 'param', 'return']):
                            doc_blocking = True
                    if not doc_blocking:
                        doc_lines = doc_string.split('\n')
                        for doc_line in doc_lines:
                            if doc_line.strip():
                                modified_lines.append(indent + doc_line + '\n')
                            elif doc_line == '':
                                modified_lines.append('\n')
                        processed_functions.add(qualified_name)
                        inserted = True
                        break
                    else:
                        processed_functions.add(qualified_name)
                        inserted = True
                        break
            modified_lines.append(line)
            i += 1
        return modified_lines

    def _find_existing_documentation_start(self, lines: List[str], function_line_index: int, lang: str, is_first_function: bool = False) -> Optional[int]:
        """
        Find the start of existing documentation before a function.
        If is_first_function is True, ignore file-level docstrings at the top of the file.
        """
        if function_line_index <= 0:
            return None
        i = function_line_index - 1
        while i >= 0 and not lines[i].strip():
            i -= 1
        if i < 0:
            return None
        line = lines[i].strip()
        if lang == 'python':
            if (line.startswith('"""') or line.startswith("'''") or line.startswith('#')):
                # If this is the first function and the docstring is at the very top, skip it
                if is_first_function and i < 5:
                    return None
                return i
        else:
            while i >= 0:
                line = lines[i].strip()
                # Only treat actual documentation comments as blocking insertion
                if (line.startswith('/**') or line.startswith('/*') or line.startswith('///') or line.startswith('*')):
                    return i
                # Only treat // comments as documentation if they contain documentation keywords
                if line.startswith('//') and any(keyword in line.lower() for keyword in ['@brief', '@param', '@return', 'brief', 'param', 'return']):
                    return i
                # Otherwise, skip non-documentation comments and keep looking further up
                i -= 1
            return None
    
    def _has_inline_documentation(self, lines: List[str], function_line_index: int, lang: str) -> bool:
        """
        Check if a function has inline documentation (docstring on the same line or immediately after).
        
        Args:
            lines: All lines in the file
            function_line_index: Index of the function definition line
            lang: Programming language
            
        Returns:
            True if the function has inline documentation, False otherwise
        """
        if function_line_index >= len(lines):
            return False
        
        function_line = lines[function_line_index]
        
        # Language-specific checks
        if lang == 'python':
            # Same-line checks
            if any(marker in function_line for marker in ['#', '"""', "'''"]):
                return True
            
            # Next-line checks
            if function_line_index + 1 < len(lines):
                next_line = lines[function_line_index + 1].strip()
                if any(next_line.startswith(marker) for marker in ['"""', "'''", '#']):
                    return True
        
        elif lang == 'c++':
            # Same-line checks
            if any(marker in function_line for marker in ['//', '/*', '/**']):
                return True
            
            # Next-line checks
            if function_line_index + 1 < len(lines):
                next_line = lines[function_line_index + 1].strip()
                if any(next_line.startswith(marker) for marker in ['//', '/*', '/**', '*']):
                    return True
        
        # Fallback for other languages
        elif lang == 'java':
            # Same-line checks for Java
            if any(marker in function_line for marker in ['//', '/*', '/**']):
                return True
            
            # Next-line checks for Java
            if function_line_index + 1 < len(lines):
                next_line = lines[function_line_index + 1].strip()
                if any(next_line.startswith(marker) for marker in ['//', '/*', '/**', '*']):
                    return True
        
        # For unknown languages, don't detect any comments
        # This prevents false positives for languages we don't support
        
        return False
    
    def _has_decorators_before(self, lines: List[str], function_line_index: int) -> bool:
        """
        Check if there are decorators before a function definition.
        
        Args:
            lines: All lines in the file
            function_line_index: Index of the function definition line
            
        Returns:
            True if there are decorators before the function, False otherwise
        """
        if function_line_index <= 0:
            return False
        
        # Look backwards from the function definition
        i = function_line_index - 1
        
        # Skip empty lines
        while i >= 0 and not lines[i].strip():
            i -= 1
        
        if i < 0:
            return False
        
        # Check if the line before the function is a decorator
        line = lines[i].strip()
        
        # Python decorators start with @
        if line.startswith('@'):
            return True
        
        # Check for multiple decorators by looking backwards
        while i >= 0:
            line = lines[i].strip()
            
            # If we hit a non-empty line that's not a decorator, stop
            if line and not line.startswith('@'):
                break
            
            # If we found a decorator, return True
            if line.startswith('@'):
                return True
            
            i -= 1
        
        return False
    
    def write_documentation_to_file(self, output_path: Path, documentation: Dict[str, str]) -> None:
        """
        Write documentation to a new file.
        
        Args:
            output_path: Path to the output file
            documentation: Dictionary mapping function names to documentation strings
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Generated Documentation\n\n")
            
            for func_name, doc_string in documentation.items():
                f.write(f"## Function: {func_name}\n\n")
                f.write("```\n")
                f.write(doc_string)
                f.write("\n```\n\n")
        
        print(f"Wrote documentation to {output_path}")
    
    def generate_diff(self, file_path: Path, documentation: Dict[str, str]) -> str:
        """
        Generate a diff showing the documentation changes.
        
        Args:
            file_path: Path to the file
            documentation: Dictionary mapping function names to documentation strings
            
        Returns:
            Diff string
        """
        try:
            # Read the original file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
            
            # Infer language from file extension
            lang = self._infer_language_from_extension(file_path)
            
            # Generate modified lines
            modified_lines = self._insert_documentation(original_lines, documentation, lang)
            
            # Generate diff
            diff = list(unified_diff(
                original_lines,
                modified_lines,
                fromfile=str(file_path),
                tofile=str(file_path),
                lineterm=''
            ))
            
            return '\n'.join(diff)
            
        except Exception as e:
            return f"Error generating diff: {e}" 