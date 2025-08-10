"""
JavaScript parser for CodeDocGen.

Uses regex-based parsing to extract function and method signatures from .js files,
including function declarations, function expressions, arrow functions, and class methods.
"""

import re
from pathlib import Path
from typing import List, Optional

from . import BaseParser
from ..models import Function, Parameter, FunctionBody, ParsedFile, FunctionType
from ..config import Config


class JavaScriptParser(BaseParser):
    """Parser for JavaScript source files (.js, .mjs, .cjs)."""

    def __init__(self, config: Config):
        super().__init__(config)

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in {'.js', '.mjs', '.cjs', '.ts', '.tsx'}

    def parse_file(self, file_path: Path) -> ParsedFile:
        try:
            source = file_path.read_text(encoding='utf-8')
        except Exception:
            source = ''

        parsed_file = ParsedFile(file_path=str(file_path), language='javascript')

        try:
            # Collect functions from various patterns
            functions: List[Function] = []

            # 1) Function declarations: function name(a, b) { ... }
            for m in re.finditer(r"\bfunction\s+([a-zA-Z_$][\w$]*)\s*\(([^)]*)\)", source):
                name = m.group(1)
                params = self._parse_params(m.group(2))
                func = self._create_function(name, params, 'any', None)
                func.source_code = source
                functions.append(func)

            # 2) Function expressions: const name = function(a, b) { ... }
            for m in re.finditer(r"(?:^|\b)(?:const|let|var)\s+([a-zA-Z_$][\w$]*)\s*=\s*function\s*\(([^)]*)\)", source):
                name = m.group(1)
                params = self._parse_params(m.group(2))
                func = self._create_function(name, params, 'any', None)
                func.source_code = source
                functions.append(func)

            # 3) Arrow functions: const name = (a, b): Ret => { ... } or name = a: T => a*2
            for m in re.finditer(r"(?:^|\b)(?:const|let|var)?\s*([a-zA-Z_$][\w$]*)\s*=\s*\(?([^)=]*)\)?\s*(?::\s*[^=]+?)?\s*=>", source):
                name = m.group(1)
                params = self._parse_params(m.group(2))
                func = self._create_function(name, params, 'any', None)
                func.source_code = source
                functions.append(func)

            # 4) Class methods: class A { method(a,b) { ... } static method() {} }
            for class_match in re.finditer(r"class\s+([A-Za-z_$][\w$]*)\s*\{([\s\S]*?)\}", source):
                class_name = class_match.group(1)
                body = class_match.group(2)
                for m in re.finditer(r"(?:(?:public|private|protected|readonly|static|async)\s+)*([A-Za-z_$][\w$]*)\s*(?:<[^>]+>)?\s*\(([^)]*)\)\s*(?::\s*[^ {]+)?\s*\{", body):
                    method_name = m.group(1)
                    params = self._parse_params(m.group(2))
                    func = self._create_function(method_name, params, 'any', class_name)
                    func.source_code = source
                    functions.append(func)

            for f in functions:
                parsed_file.add_function(f)

        except Exception:
            # On parser error, return what we have
            pass

        return parsed_file

    def _parse_params(self, params_str: str) -> List[Parameter]:
        params_str = (params_str or '').strip()
        if not params_str:
            return []
        # Split by comma ignoring default values with commas (simple heuristic)
        parts: List[str] = []
        current = ''
        depth = 0
        for ch in params_str:
            if ch in '([{':
                depth += 1
            elif ch in ')]}':
                depth -= 1
            if ch == ',' and depth == 0:
                parts.append(current.strip())
                current = ''
            else:
                current += ch
        if current.strip():
            parts.append(current.strip())

        params: List[Parameter] = []
        for p in parts:
            # Handle patterns like: a, b = 2, {x,y}, [a,b], x?: T, x: T
            name = p.split('=')[0].strip()
            # Remove TypeScript type annotation
            name = name.split(':')[0].strip()
            # Remove optional marker
            name = name.replace('?', '').strip()
            # Strip destructuring braces for a name placeholder
            name_clean = re.sub(r"[\{\}\[\]\s]+", '', name) or 'param'
            params.append(Parameter(name=name_clean, type='any'))
        return params

    def _create_function(self, name: str, params: List[Parameter], return_type: str, class_name: Optional[str]) -> Function:
        body = FunctionBody()
        return Function(
            name=name,
            parameters=params,
            return_type=return_type,
            function_type=FunctionType.METHOD if class_name else FunctionType.FUNCTION,
            class_name=class_name or "",
            body=body,
        )

