"""
Go parser for CodeDocGen.
"""
import re
from pathlib import Path
from typing import List, Optional
from .. import BaseParser
from ...models import Function, Parameter, FunctionBody, ParsedFile, FunctionType
from ...config import Config

class GoParser(BaseParser):
    """Parser for Go source files (.go)."""

    def __init__(self, config: Config):
        super().__init__(config)

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == '.go'

    def parse_file(self, file_path: Path) -> ParsedFile:
        try:
            source = file_path.read_text(encoding='utf-8')
        except Exception:
            return ParsedFile(file_path=str(file_path), language='go')

        parsed_file = ParsedFile(file_path=str(file_path), language='go')
        
        # Regex patterns for Go functions
        # 1. Standard function: func Name(params) (returns) {
        # 2. Method: func (r Receiver) Name(params) (returns) {
        
        # Capture method receiver if present
        pattern = r"func\s+(?:\(([^)]+)\)\s+)?([a-zA-Z_]\w*)\s*\(([^)]*)\)\s*(?:\(?([^){]*)\)?)?\s*\{"
        
        for match in re.finditer(pattern, source):
            receiver = match.group(1)
            name = match.group(2)
            params_str = match.group(3)
            return_str = match.group(4)
            
            params = self._parse_params(params_str)
            
            # Basic return type handling
            return_type = return_str.strip() if return_str else "void"
            
            func_type = FunctionType.METHOD if receiver else FunctionType.FUNCTION
            class_name = ""
            if receiver:
                # Extract receiver type for class name simulation
                # e.g., "s *Server" -> "Server"
                parts = receiver.split()
                if len(parts) > 1:
                    class_name = parts[-1].replace('*', '')
                else:
                    class_name = parts[0].replace('*', '')

            func = Function(
                name=name,
                parameters=params,
                return_type=return_type,
                function_type=func_type,
                class_name=class_name,
                body=FunctionBody(),
                source_code=source # Simplified, ideally slice the function body
            )
            parsed_file.add_function(func)

        return parsed_file

    def _parse_params(self, params_str: str) -> List[Parameter]:
        if not params_str.strip():
            return []
            
        params = []
        # Go params: "a, b int, c string" -> a int, b int, c string
        # This naive parser handles simple cases
        parts = params_str.split(',')
        
        # This logic is tricky for Go because types come after names and can be grouped
        # e.g. "x, y int"
        # We'll use a simplified split for now
        
        # Better approach: split by comma, but need to handle type association
        # For prototype, we'll just extract names if possible or full string
        
        # Let's try to normalize "x, y int" to "x int, y int" logic roughly?
        # Actually complex regex needed. 
        # Fallback: Just separate by commas and take the first word as name
        
        current_names = []
        
        # Rough tokenization
        tokens = params_str.split()
        # This is hard without a proper parser. 
        # Let's just create generic parameters for now from comma split
        
        for part in params_str.split(','):
            part = part.strip()
            if not part:
                continue
            
            # If it has a space, likely "name type"
            if ' ' in part:
                subparts = part.split()
                name = subparts[0]
                type_name = " ".join(subparts[1:])
                params.append(Parameter(name=name, type=type_name))
            else:
                # Just a name (part of a group like x, y int) - type is unknown until later
                params.append(Parameter(name=part, type="unknown"))
                
        return params
