"""
Rust parser for CodeDocGen.
"""
import re
from pathlib import Path
from typing import List, Optional
from .. import BaseParser
from ...models import Function, Parameter, FunctionBody, ParsedFile, FunctionType
from ...config import Config

class RustParser(BaseParser):
    """Parser for Rust source files (.rs)."""

    def __init__(self, config: Config):
        super().__init__(config)

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == '.rs'

    def parse_file(self, file_path: Path) -> ParsedFile:
        try:
            source = file_path.read_text(encoding='utf-8')
        except Exception:
            return ParsedFile(file_path=str(file_path), language='rust')

        parsed_file = ParsedFile(file_path=str(file_path), language='rust')
        
        # Regex for Rust functions
        # fn name(params) -> Type {
        # pub fn name<T>(params) -> Type where T: Bound {
        
        pattern = r"fn\s+([a-zA-Z_]\w*)\s*(?:<[^>]*>)?\s*\(([^)]*)\)\s*(?:->\s*([^{]+))?\s*(?:where\s+[^{]+)?\s*\{"
        
        for match in re.finditer(pattern, source):
            name = match.group(1)
            params_str = match.group(2)
            return_str = match.group(3)
            
            params = self._parse_params(params_str)
            
            # Clean return type
            return_type = return_str.strip() if return_str else "void"
            
            func = Function(
                name=name,
                parameters=params,
                return_type=return_type,
                function_type=FunctionType.FUNCTION,
                body=FunctionBody(),
                source_code=source
            )
            parsed_file.add_function(func)

        return parsed_file

    def _parse_params(self, params_str: str) -> List[Parameter]:
        if not params_str.strip():
            return []
            
        params = []
        # Rust params: "name: Type, name2: &Type"
        # Handles "self", "&self", "mut self"
        
        for part in params_str.split(','):
            part = part.strip()
            if not part:
                continue
                
            if part == 'self' or part == '&self' or part == '&mut self':
                params.append(Parameter(name='self', type='Self'))
                continue
                
            if ':' in part:
                name_part, type_part = part.split(':', 1)
                params.append(Parameter(name=name_part.strip(), type=type_part.strip()))
            else:
                # Fallback
                params.append(Parameter(name=part, type='unknown'))
                
        return params
