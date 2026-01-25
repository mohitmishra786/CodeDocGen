"""
TypeScript parser for CodeDocGen.
"""
import re
from pathlib import Path
from typing import List, Optional
from . import BaseParser
from ..models import Function, Parameter, FunctionBody, ParsedFile, FunctionType
from ..config import Config

class TypeScriptParser(BaseParser):
    """
    Parser for TypeScript source files (.ts, .tsx).
    
    Note: Basic regex-based extraction is used. Complex patterns like
    destructuring parameters or nested generics in types may not be 
    fully supported.
    """

    def __init__(self, config: Config):
        super().__init__(config)

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in {'.ts', '.tsx'}

    def _extract_function_source(self, source: str, start_index: int) -> str:
        """
        Extract the full function source by matching braces.
        
        Args:
            source: Full source code
            start_index: Index where the function definition starts
            
        Returns:
            Extracted function source code
        """
        brace_count = 0
        in_brace = False
        
        # Find the opening brace first
        current_idx = start_index
        while current_idx < len(source):
            if source[current_idx] == '{':
                brace_count += 1
                in_brace = True
                current_idx += 1
                break
            current_idx += 1
            
        if not in_brace:
            return "" # Could not find opening brace
            
        # Count braces until balanced
        while current_idx < len(source):
            char = source[current_idx]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                
            current_idx += 1
            
            if brace_count == 0:
                break
                
        return source[start_index:current_idx]

    def parse_file(self, file_path: Path) -> ParsedFile:
        try:
            source = file_path.read_text(encoding='utf-8')
        except Exception:
            return ParsedFile(file_path=str(file_path), language='typescript')

        parsed_file = ParsedFile(file_path=str(file_path), language='typescript')
        
        # Regex patterns for TypeScript functions
        patterns = [
            # Function declaration: function name(params): Ret {
            r"function\s+([a-zA-Z_$][\w$]*)\s*\(([^)]*)\)(?:\s*:\s*[^ {]+)?\s*\{",
            # Const arrow/expression: const name = (params): Ret =>
            r"(?:const|let|var)\s+([a-zA-Z_$][\w$]*)\s*=\s*(?:async\s*)?\(?([^)=]*)\)?(?:\s*:\s*[^=]+)?\s*=>",
            # Class method: public name(params): Ret {
            r"(?:public|private|protected|static|async|abstract)*\s+([a-zA-Z_$][\w$]*)\s*\(([^)]*)\)(?:\s*:\s*[^ {]+)?\s*\{"
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, source):
                name = match.group(1)
                # Skip reserved keywords if matched by mistake
                if name in ['if', 'for', 'switch', 'while', 'catch', 'constructor']:
                    continue
                    
                params_str = match.group(2)
                params = self._parse_params(params_str)
                
                # Simple return type extraction could be improved, default to 'any' or parsed
                return_type = 'any'
                
                # Extract actual source code
                func_source = self._extract_function_source(source, match.start())
                if not func_source:
                    func_source = match.group(0) # Fallback to match only if extraction fails
                
                func = Function(
                    name=name,
                    parameters=params,
                    return_type=return_type,
                    function_type=FunctionType.FUNCTION,
                    body=FunctionBody(),
                    source_code=func_source
                )
                parsed_file.add_function(func)

        return parsed_file

    def _parse_params(self, params_str: str) -> List[Parameter]:
        if not params_str.strip():
            return []
            
        params = []
        # Naive split by comma, handling nested generics/objects is complex with regex
        # This is a basic implementation
        raw_params = params_str.split(',')
        
        for p in raw_params:
            p = p.strip()
            if not p:
                continue
                
            # Handle "name: Type"
            if ':' in p:
                parts = p.split(':')
                name = parts[0].strip().replace('?', '') # Remove optional marker
                type_name = parts[1].strip().split('=')[0].strip() # Remove default value
            else:
                name = p.split('=')[0].strip()
                type_name = 'any'
                
            params.append(Parameter(name=name, type=type_name))
            
        return params
