"""
Language-specific parsers for CodeDocGen.

Provides parsers for different programming languages that extract function
signatures, parameters, and analyze function bodies.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path

from ..models import Function, ParsedFile
from ..config import Config


class BaseParser(ABC):
    """Base class for language-specific parsers."""
    
    def __init__(self, config: Config):
        """
        Initialize the parser.
        
        Args:
            config: Configuration object
        """
        self.config = config
    
    @abstractmethod
    def parse_file(self, file_path: Path) -> ParsedFile:
        """
        Parse a source file and extract functions.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            ParsedFile object containing extracted functions
        """
        pass
    
    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the parser can handle this file
        """
        pass


class ParserFactory:
    """Factory for creating language-specific parsers."""
    
    def __init__(self, config: Config):
        """
        Initialize the parser factory.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self._parsers = {}
        self._load_parsers()
    
    def _load_parsers(self) -> None:
        """Load available parsers."""
        try:
            from .cpp_parser import CppParser
            self._parsers['c++'] = CppParser(self.config)
        except (ImportError, NameError, Exception) as e:
            print(f"Warning: C++ parser not available: {e}")
        
        try:
            from .python_parser import PythonParser
            self._parsers['python'] = PythonParser(self.config)
        except ImportError:
            print("Warning: Python parser not available")
        
        try:
            from .java_parser import JavaParser
            self._parsers['java'] = JavaParser(self.config)
        except ImportError:
            print("Warning: Java parser not available")
    
    def get_parser(self, language: str) -> BaseParser:
        """
        Get a parser for the specified language.
        
        Args:
            language: Programming language
            
        Returns:
            Parser instance
            
        Raises:
            ValueError: If no parser is available for the language
        """
        if language not in self._parsers:
            raise ValueError(f"No parser available for language: {language}")
        
        return self._parsers[language]
    
    def get_parser_for_file(self, file_path: Path) -> BaseParser:
        """
        Get the appropriate parser for a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Parser instance
            
        Raises:
            ValueError: If no parser can handle the file
        """
        for language, parser in self._parsers.items():
            if parser.can_parse(file_path):
                return parser
        
        raise ValueError(f"No parser available for file: {file_path}")
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages.
        
        Returns:
            List of supported language names
        """
        return list(self._parsers.keys())


__all__ = ['BaseParser', 'ParserFactory'] 