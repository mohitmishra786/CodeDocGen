"""
AST Analyzer for intelligent function analysis.
"""

import ast
from typing import List, Set, Optional


class ASTAnalyzer(ast.NodeVisitor):
    """Analyzes AST nodes to understand function behavior patterns."""
    
    def __init__(self):
        self.characteristics: Set[str] = set()
        self.function_name: str = ""
        self.recursion_detected: bool = False
        self.regex_detected: bool = False
        self.api_calls: Set[str] = set()
        self.file_operations: Set[str] = set()
        self.collection_operations: Set[str] = set()
        self.string_operations: Set[str] = set()
    
    def analyze(self, node: ast.AST, function_name: str = "") -> List[str]:
        """
        Analyze an AST node and return list of characteristics.
        
        Args:
            node: AST node to analyze
            function_name: Name of the function being analyzed
            
        Returns:
            List of behavior characteristics
        """
        self.characteristics.clear()
        self.function_name = function_name
        self.recursion_detected = False
        self.regex_detected = False
        self.api_calls.clear()
        self.file_operations.clear()
        self.collection_operations.clear()
        self.string_operations.clear()
        
        self.visit(node)
        return list(self.characteristics)
    
    def visit_For(self, node: ast.For) -> None:
        """Analyze for loops."""
        self.characteristics.add("iterating through collections")
        self.generic_visit(node)
    
    def visit_While(self, node: ast.While) -> None:
        """Analyze while loops."""
        self.characteristics.add("looping until condition met")
        self.generic_visit(node)
    
    def visit_If(self, node: ast.If) -> None:
        """Analyze conditional statements."""
        self.characteristics.add("making conditional decisions")
        self.generic_visit(node)
    
    def visit_IfExp(self, node: ast.IfExp) -> None:
        """Analyze conditional expressions."""
        self.characteristics.add("making conditional decisions")
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Analyze function calls."""
        # Check for recursion
        if isinstance(node.func, ast.Name) and node.func.id == self.function_name:
            self.recursion_detected = True
            self.characteristics.add("using recursion")
        
        # Check for regex operations
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['match', 'search', 'findall', 'sub', 'split']:
                if self._is_regex_module(node.func.value):
                    self.regex_detected = True
                    self.characteristics.add("using regular expressions")
            
            # Check for API calls
            if node.func.attr in ['get', 'post', 'put', 'delete', 'request']:
                if self._is_requests_module(node.func.value):
                    self.api_calls.add(node.func.attr)
                    self.characteristics.add("making API calls")
            
            # Check for file operations
            if node.func.attr in ['open', 'read', 'write', 'close']:
                self.file_operations.add(node.func.attr)
                self.characteristics.add("performing file operations")
            
            # Check for collection operations
            if node.func.attr in ['append', 'extend', 'insert', 'remove', 'pop', 'clear']:
                self.collection_operations.add(node.func.attr)
                self.characteristics.add("manipulating collections")
            
            # Check for string operations
            if node.func.attr in ['split', 'join', 'replace', 'strip', 'upper', 'lower']:
                self.string_operations.add(node.func.attr)
                self.characteristics.add("performing string operations")
        
        self.generic_visit(node)
    
    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Analyze binary operations."""
        self.characteristics.add("performing mathematical operations")
        self.generic_visit(node)
    
    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        """Analyze unary operations."""
        if isinstance(node.op, (ast.UAdd, ast.USub, ast.Invert)):
            self.characteristics.add("performing mathematical operations")
        self.generic_visit(node)
    
    def visit_Return(self, node: ast.Return) -> None:
        """Analyze return statements."""
        if node.value is not None:
            self.characteristics.add("returning computed result")
        else:
            self.characteristics.add("returning early")
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Analyze assignments."""
        self.characteristics.add("modifying state")
        self.generic_visit(node)
    
    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Analyze augmented assignments."""
        self.characteristics.add("modifying state")
        if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)):
            self.characteristics.add("performing mathematical operations")
        self.generic_visit(node)
    
    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Analyze list comprehensions."""
        self.characteristics.add("creating collections")
        self.generic_visit(node)
    
    def visit_DictComp(self, node: ast.DictComp) -> None:
        """Analyze dictionary comprehensions."""
        self.characteristics.add("creating collections")
        self.generic_visit(node)
    
    def visit_SetComp(self, node: ast.SetComp) -> None:
        """Analyze set comprehensions."""
        self.characteristics.add("creating collections")
        self.generic_visit(node)
    
    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        """Analyze generator expressions."""
        self.characteristics.add("creating iterators")
        self.generic_visit(node)
    
    def visit_Try(self, node: ast.Try) -> None:
        """Analyze try-except blocks."""
        self.characteristics.add("handling exceptions")
        self.generic_visit(node)
    
    def visit_Raise(self, node: ast.Raise) -> None:
        """Analyze raise statements."""
        self.characteristics.add("raising exceptions")
        self.generic_visit(node)
    
    def visit_With(self, node: ast.With) -> None:
        """Analyze with statements."""
        self.characteristics.add("managing resources")
        self.generic_visit(node)
    
    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        """Analyze async for loops."""
        self.characteristics.add("iterating asynchronously")
        self.generic_visit(node)
    
    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        """Analyze async with statements."""
        self.characteristics.add("managing resources asynchronously")
        self.generic_visit(node)
    
    def _is_regex_module(self, node: ast.expr) -> bool:
        """Check if the node represents the re module."""
        if isinstance(node, ast.Name):
            return node.id == 're'
        elif isinstance(node, ast.Attribute):
            return node.attr == 're'
        return False
    
    def _is_requests_module(self, node: ast.expr) -> bool:
        """Check if the node represents the requests module."""
        if isinstance(node, ast.Name):
            return node.id == 'requests'
        elif isinstance(node, ast.Attribute):
            return node.attr == 'requests'
        return False
    
    def get_detailed_characteristics(self) -> dict:
        """Get detailed analysis results."""
        return {
            'characteristics': list(self.characteristics),
            'recursion_detected': self.recursion_detected,
            'regex_detected': self.regex_detected,
            'api_calls': list(self.api_calls),
            'file_operations': list(self.file_operations),
            'collection_operations': list(self.collection_operations),
            'string_operations': list(self.string_operations)
        } 