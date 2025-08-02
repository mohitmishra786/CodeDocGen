"""
Data models for CodeDocGen.

Defines the structure for representing functions, parameters, and other code elements.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class FunctionType(Enum):
    """Types of functions."""
    FUNCTION = "function"
    METHOD = "method"
    CONSTRUCTOR = "constructor"
    DESTRUCTOR = "destructor"


class ParameterType(Enum):
    """Types of parameters."""
    INPUT = "input"
    OUTPUT = "output"
    INOUT = "inout"


@dataclass
class Parameter:
    """Represents a function parameter."""
    
    name: str
    type: str
    default_value: Optional[str] = None
    param_type: ParameterType = ParameterType.INPUT
    description: Optional[str] = None
    
    def __post_init__(self):
        """Generate description if not provided."""
        if not self.description:
            self.description = self._generate_description()
    
    def _generate_description(self) -> str:
        """Generate a basic description for the parameter."""
        type_desc = self._get_type_description()
        return f"The {self.name} {type_desc}."
    
    def _get_type_description(self) -> str:
        """Get a human-readable description of the type."""
        type_mapping = {
            "int": "integer",
            "float": "floating-point number",
            "double": "double-precision floating-point number",
            "char": "character",
            "string": "string",
            "bool": "boolean value",
            "void": "void",
            "list": "list",
            "dict": "dictionary",
            "tuple": "tuple",
            "set": "set",
            "str": "string",
            "bytes": "bytes",
            "object": "object",
            "None": "None value"
        }
        
        return type_mapping.get(self.type.lower(), f"value of type {self.type}")


@dataclass
class Exception:
    """Represents an exception that can be thrown/raised."""
    
    name: str
    description: Optional[str] = None
    
    def __post_init__(self):
        """Generate description if not provided."""
        if not self.description:
            self.description = f"Thrown when {self.name.lower()} occurs."


@dataclass
class FunctionBody:
    """Represents analysis of a function body."""
    
    has_loops: bool = False
    has_conditionals: bool = False
    has_exceptions: bool = False
    has_returns: bool = False
    has_early_returns: bool = False
    has_side_effects: bool = False
    has_arithmetic: bool = False
    has_string_operations: bool = False
    has_file_operations: bool = False
    has_network_operations: bool = False
    complexity_score: int = 0
    
    def get_behavior_description(self) -> str:
        """Generate a description of the function's behavior."""
        behaviors = []
        
        if self.has_loops:
            behaviors.append("iterates over data")
        if self.has_conditionals:
            behaviors.append("conditionally processes input")
        if self.has_exceptions:
            behaviors.append("may throw exceptions")
        if self.has_early_returns:
            behaviors.append("may return early")
        if self.has_side_effects:
            behaviors.append("has side effects")
        if self.has_arithmetic:
            behaviors.append("performs arithmetic operations")
        if self.has_string_operations:
            behaviors.append("manipulates strings")
        if self.has_file_operations:
            behaviors.append("performs file operations")
        if self.has_network_operations:
            behaviors.append("performs network operations")
        
        if behaviors:
            return f"Function {', '.join(behaviors)}."
        return ""


@dataclass
class Function:
    """Represents a function or method."""
    
    name: str
    return_type: str
    parameters: List[Parameter] = field(default_factory=list)
    exceptions: List[Exception] = field(default_factory=list)
    body: Optional[FunctionBody] = None
    function_type: FunctionType = FunctionType.FUNCTION
    class_name: Optional[str] = None
    namespace: Optional[str] = None
    line_number: int = 0
    end_line: int = 0
    description: Optional[str] = None
    brief_description: Optional[str] = None
    detailed_description: Optional[str] = None
    
    def __post_init__(self):
        """Initialize body if not provided."""
        if self.body is None:
            self.body = FunctionBody()
    
    def get_full_name(self) -> str:
        """Get the full name including namespace and class."""
        parts = []
        if self.namespace:
            parts.append(self.namespace)
        if self.class_name:
            parts.append(self.class_name)
        parts.append(self.name)
        return "::".join(parts)
    
    def get_signature(self) -> str:
        """Get the function signature as a string."""
        params = ", ".join([f"{p.type} {p.name}" for p in self.parameters])
        return f"{self.return_type} {self.name}({params})"
    
    def has_parameters(self) -> bool:
        """Check if function has parameters."""
        return len(self.parameters) > 0
    
    def has_exceptions(self) -> bool:
        """Check if function throws/raises exceptions."""
        return len(self.exceptions) > 0
    
    def get_parameter_names(self) -> List[str]:
        """Get list of parameter names."""
        return [p.name for p in self.parameters]
    
    def get_parameter_types(self) -> List[str]:
        """Get list of parameter types."""
        return [p.type for p in self.parameters]


@dataclass
class ParsedFile:
    """Represents a parsed source file."""
    
    file_path: str
    language: str
    functions: List[Function] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    namespaces: List[str] = field(default_factory=list)
    includes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    
    def add_function(self, function: Function) -> None:
        """Add a function to the file."""
        self.functions.append(function)
    
    def get_functions_by_class(self, class_name: str) -> List[Function]:
        """Get all functions belonging to a specific class."""
        return [f for f in self.functions if f.class_name == class_name]
    
    def get_functions_by_namespace(self, namespace: str) -> List[Function]:
        """Get all functions belonging to a specific namespace."""
        return [f for f in self.functions if f.namespace == namespace]


@dataclass
class DocumentationResult:
    """Represents the result of documentation generation."""
    
    function: Function
    brief_doc: str
    detailed_doc: str
    param_docs: Dict[str, str] = field(default_factory=dict)
    return_doc: Optional[str] = None
    exception_docs: Dict[str, str] = field(default_factory=dict)
    
    def get_full_documentation(self) -> str:
        """Get the complete documentation string."""
        # This will be implemented by the generator
        return self.detailed_doc 