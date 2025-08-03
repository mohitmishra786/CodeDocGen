"""
Configuration management for CodeDocGen.

Handles loading and validation of YAML configuration files with default settings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class Config:
    """Configuration manager for CodeDocGen."""
    
    # Default configuration
    DEFAULT_CONFIG = {
        "templates": {
            "c++": {
                "brief": "/**\n * \\brief {description}\n */",
                "param": " * \\param {name} {description}",
                "return": " * \\return {description}",
                "throws": " * \\throws {exception} {description}",
                "detailed": "/**\n * \\brief {description}\n{params}{returns}{throws}\n */"
            },
            "python": {
                "brief": '"""\n    {description}\n"""',
                "param": "    :param {name}: {description}",
                "return": "    :return: {description}",
                "raises": "    :raises {exception}: {description}",
                "detailed": '"""\n    {description}\n{params}{returns}{raises}\n"""'
            },
            "java": {
                "brief": "/**\n * {description}\n */",
                "param": " * @param {name} {description}",
                "return": " * @return {description}",
                "throws": " * @throws {exception} {description}",
                "detailed": "/**\n * {description}\n *\n{params}{returns}{throws}\n */"
            }
        },
        "rules": [
            {
                "pattern": "^validate.*",
                "brief": "Validates the input {params}.",
                "priority": 10
            },
            {
                "pattern": "^compute.*",
                "brief": "Computes the {noun} based on {params}.",
                "priority": 9
            },
            {
                "pattern": "^get.*",
                "brief": "Retrieves the {noun}.",
                "priority": 8
            },
            {
                "pattern": "^set.*",
                "brief": "Sets the {noun} to the specified value.",
                "priority": 8
            },
            {
                "pattern": "^is.*",
                "brief": "Checks if the {noun} meets the specified condition.",
                "priority": 7
            },
            {
                "pattern": "^has.*",
                "brief": "Checks if the {noun} contains the specified element.",
                "priority": 7
            },
            {
                "pattern": "^add.*",
                "brief": "Adds the {noun} to the collection.",
                "priority": 6
            },
            {
                "pattern": "^remove.*",
                "brief": "Removes the {noun} from the collection.",
                "priority": 6
            },
            {
                "pattern": "^create.*",
                "brief": "Creates a new {noun} instance.",
                "priority": 5
            },
            {
                "pattern": "^delete.*",
                "brief": "Deletes the {noun} from the system.",
                "priority": 5
            },
            {
                "pattern": "^update.*",
                "brief": "Updates the {noun} with new information.",
                "priority": 4
            },
            {
                "pattern": "^process.*",
                "brief": "Processes the {noun} according to the specified logic.",
                "priority": 3
            },
            {
                "pattern": "^handle.*",
                "brief": "Handles the {noun} event or request.",
                "priority": 2
            }
        ],
        "file_extensions": {
            "c++": [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hh", ".hxx"],
            "python": [".py", ".pyx", ".pxd"],
            "java": [".java"]
        },
        "ignore_patterns": [
            "*/node_modules/*",
            "*/__pycache__/*",
            "*/build/*",
            "*/dist/*",
            "*/codedocgen/*",
            "*/venv/*",
            "*/env/*",
            "*/\.venv/*",
            "*/\.env/*",
            "*/site-packages/*",
            "*.pyc",
            "*.o",
            "*.so",
            "*.dll",
            "*.exe"
        ],
        "nltk": {
            "download_data": True,
            "corpora": ["punkt", "averaged_perceptron_tagger"]
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to custom configuration file
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and config_path.exists():
            self.load_config(config_path)
    
    def load_config(self, config_path: Path) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                custom_config = yaml.safe_load(f)
            
            # Merge custom configuration with defaults
            self._merge_config(self.config, custom_config)
            
        except Exception as e:
            print(f"Warning: Could not load configuration from {config_path}: {e}")
    
    def _merge_config(self, base: Dict[str, Any], custom: Dict[str, Any]) -> None:
        """
        Recursively merge custom configuration with base configuration.
        
        Args:
            base: Base configuration dictionary
            custom: Custom configuration dictionary
        """
        for key, value in custom.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get_template(self, lang: str, template_type: str) -> str:
        """
        Get template for specific language and type.
        
        Args:
            lang: Programming language
            template_type: Type of template (brief, param, return, etc.)
            
        Returns:
            Template string
        """
        return self.config["templates"].get(lang, {}).get(template_type, "")
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """
        Get inference rules sorted by priority.
        
        Returns:
            List of rules sorted by priority (highest first)
        """
        rules = self.config.get("rules", [])
        return sorted(rules, key=lambda x: x.get("priority", 0), reverse=True)
    
    def get_file_extensions(self, lang: str) -> List[str]:
        """
        Get file extensions for a language.
        
        Args:
            lang: Programming language
            
        Returns:
            List of file extensions
        """
        return self.config["file_extensions"].get(lang, [])
    
    def get_ignore_patterns(self) -> List[str]:
        """
        Get patterns to ignore during scanning.
        
        Returns:
            List of ignore patterns
        """
        return self.config.get("ignore_patterns", [])
    
    def should_ignore_file(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored based on patterns.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file should be ignored
        """
        file_str = str(file_path)
        
        # Check for virtual environment directories
        if any(venv_dir in file_str for venv_dir in ['codedocgen/', 'venv/', 'env/', '.venv/', '.env/', 'site-packages/']):
            return True
        
        # Check for other common ignore patterns
        ignore_patterns = [
            'node_modules',
            '__pycache__',
            'build',
            'dist',
            '.pyc',
            '.o',
            '.so',
            '.dll',
            '.exe'
        ]
        
        for pattern in ignore_patterns:
            if pattern in file_str:
                return True
        
        return False
    
    def get_nltk_config(self) -> Dict[str, Any]:
        """
        Get NLTK configuration.
        
        Returns:
            NLTK configuration dictionary
        """
        return self.config.get("nltk", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration.
        
        Returns:
            Logging configuration dictionary
        """
        return self.config.get("logging", {}) 