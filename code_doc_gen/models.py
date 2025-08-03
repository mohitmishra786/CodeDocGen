"""
Data models for CodeDocGen.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
import ast


class FunctionType(Enum):
    """Types of functions."""
    FUNCTION = "function"
    METHOD = "method"
    CONSTRUCTOR = "constructor"
    DESTRUCTOR = "destructor"


class Parameter:
    """Represents a function parameter."""
    
    def __init__(self, name: str, type: str, description: str = ""):
        self.name = name
        self.type = type
        self.description = description
    
    def __str__(self) -> str:
        return f"{self.name}: {self.type}"


class FunctionException:
    """Represents an exception that can be thrown."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description


class FunctionBody:
    """Represents analysis of a function's body."""
    
    def __init__(self):
        self.has_loops = False
        self.has_conditionals = False
        self.has_exceptions = False
        self.has_side_effects = False
        self.has_arithmetic = False
        self.has_early_returns = False
        self.has_recursion = False
        self.has_regex = False
        self.has_api_calls = False
        self.has_file_operations = False
        self.has_collections = False
        self.has_string_operations = False
    
    def get_behavior_description(self) -> str:
        """Get a description of the function's behavior."""
        behaviors = []
        
        if self.has_loops:
            behaviors.append("iterates over data")
        if self.has_conditionals:
            behaviors.append("has conditional logic")
        if self.has_side_effects:
            behaviors.append("has side effects")
        if self.has_arithmetic:
            behaviors.append("performs calculations")
        if self.has_exceptions:
            behaviors.append("may throw exceptions")
        if self.has_early_returns:
            behaviors.append("may return early")
        if self.has_recursion:
            behaviors.append("uses recursion")
        if self.has_regex:
            behaviors.append("uses regular expressions")
        if self.has_api_calls:
            behaviors.append("makes API calls")
        if self.has_file_operations:
            behaviors.append("performs file operations")
        if self.has_collections:
            behaviors.append("manipulates collections")
        if self.has_string_operations:
            behaviors.append("performs string operations")
        
        if behaviors:
            return f"Function {', '.join(behaviors)}."
        return ""


class Function:
    """Represents a function in the codebase."""
    
    def __init__(self, 
                 name: str,
                 parameters: List[Parameter],
                 return_type: str,
                 function_type: FunctionType = FunctionType.FUNCTION,
                 class_name: str = "",
                 brief_description: str = "",
                 detailed_description: str = "",
                 exceptions: List[FunctionException] = None,
                 body: Optional[FunctionBody] = None,
                 ast_node: Optional[ast.AST] = None,
                 source_code: str = ""):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.function_type = function_type
        self.class_name = class_name
        self.brief_description = brief_description
        self.detailed_description = detailed_description
        self.exceptions = exceptions or []
        self.body = body or FunctionBody()
        self.ast_node = ast_node
        self.source_code = source_code
    
    def has_parameters(self) -> bool:
        """Check if the function has parameters."""
        return len(self.parameters) > 0
    
    def get_parameter_names(self) -> List[str]:
        """Get the names of all parameters."""
        return [p.name for p in self.parameters]
    
    def __str__(self) -> str:
        params_str = ", ".join([str(p) for p in self.parameters])
        return f"{self.name}({params_str}) -> {self.return_type}"
    
    def get_full_name(self) -> str:
        """Get the full name including class if applicable."""
        if self.class_name:
            return f"{self.class_name}.{self.name}"
        return self.name


class ParsedFile:
    """Represents a parsed source file."""
    
    def __init__(self, file_path: str, language: str):
        self.file_path = file_path
        self.language = language
        self.functions: List[Function] = []
        self.classes: List[str] = []
        self.namespaces: List[str] = []
        self.includes: List[str] = []
        self.imports: List[str] = []
    
    def add_function(self, function: Function) -> None:
        """Add a function to the file."""
        self.functions.append(function)
    
    def get_functions_by_class(self, class_name: str) -> List[Function]:
        """Get all functions belonging to a specific class."""
        return [f for f in self.functions if f.class_name == class_name]
    
    def get_functions_by_namespace(self, namespace: str) -> List[Function]:
        """Get all functions belonging to a specific namespace."""
        return [f for f in self.functions if hasattr(f, 'namespace') and f.namespace == namespace]


class DocumentationResult:
    """Represents the result of documentation generation."""
    
    def __init__(self, function: Function, brief_doc: str, detailed_doc: str, 
                 param_docs: Dict[str, str] = None, return_doc: str = None, 
                 exception_docs: Dict[str, str] = None):
        self.function = function
        self.brief_doc = brief_doc
        self.detailed_doc = detailed_doc
        self.param_docs = param_docs or {}
        self.return_doc = return_doc
        self.exception_docs = exception_docs or {}
    
    def get_full_documentation(self) -> str:
        """Get the complete documentation string."""
        # This will be implemented by the generator
        return self.detailed_doc 