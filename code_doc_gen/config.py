"""
Configuration management for CodeDocGen.

Handles loading and validation of YAML configuration files with default settings.
"""

import os
import copy
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Load .env from current working directory (where user runs the command)
    # Try multiple locations to find the .env file
    import os
    cwd = os.getcwd()
    env_path = os.path.join(cwd, '.env')
    
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
    else:
        # Fallback: try to load from current directory
        load_dotenv(override=True)
except ImportError:
    # python-dotenv not installed, continue without .env support
    pass


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
            },
            "javascript": {
                "brief": "/**\n * {description}\n */",
                "param": " * @param {name} {description}",
                "return": " * @returns {description}",
                "detailed": "/**\n * {description}\n *\n{params}{returns}\n */"
            },
            "typescript": {
                "brief": "/**\n * {description}\n */",
                "param": " * @param {name} {description}",
                "return": " * @returns {description}",
                "detailed": "/**\n * {description}\n *\n{params}{returns}\n */"
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
            "java": [".java"],
            "javascript": [".js", ".mjs", ".cjs", ".ts", ".tsx"]
        },
        "ignore_patterns": [
            "*/node_modules/*",
            "*/__pycache__/*",
            "*/build/*",
            "*/dist/*",
            "*.pyc",
            "*.o",
            "*.so",
            "*.dll",
            "*.exe",
            "*/venv/*",
            "*/env/*",
            "*/target/*",
            "*/bin/*",
            "*/obj/*"
        ],
        "nltk": {
            "download_data": True,
            "corpora": ["punkt", "averaged_perceptron_tagger"]
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "ai": {
            "enabled": False,
            "provider": "groq",
            "groq_api_key": "",  # Will be loaded from environment variable
            "openai_api_key": "",  # Will be loaded from environment variable
            "azure_openai_api_key": "",  # Will be loaded from environment variable
            "azure_endpoint": "",  # Will be loaded from environment variable
            "azure_deployment": "gpt-4",  # Default deployment name
            "azure_api_version": "2023-05-15",
            "max_retries": 3,
            "retry_delay": 1.0,
            "models": {
                "groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
                "openai": "gpt-4o-mini",
                "azure_openai": "gpt-4", # Placeholder, usually uses azure_deployment
                "anthropic": "claude-3-haiku-20240307",
                "mistral": "mistral-small-latest"
            }
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to custom configuration file
        """
        # Use deep copy to avoid cross-test/shared-mutation of nested dicts
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        
        if config_path and config_path.exists():
            self.load_config(config_path)
        
        # Load API keys from environment variables (highest priority)
        self._load_env_api_keys()
    
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
    
    def get_ai_config(self) -> Dict[str, Any]:
        """
        Get AI configuration.
        
        Returns:
            AI configuration dictionary
        """
        return self.config.get("ai", {}) 
    
    def _load_env_api_keys(self) -> None:
        """Load API keys from environment variables or secure credential store."""
        
        # 1. Try Environment variables (Highest priority)
        env_keys = {
            'groq_api_key': os.getenv('GROQ_API_KEY'),
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'azure_openai_api_key': os.getenv('AZURE_OPENAI_API_KEY'),
            'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
            'mistral_api_key': os.getenv('MISTRAL_API_KEY')
        }
        
        # 2. Try Credential Manager (Keyring) if not in env
        try:
            from .credential_manager import CredentialManager
            cred_manager = CredentialManager()
            
            providers_map = {
                'groq_api_key': 'groq',
                'openai_api_key': 'openai',
                'azure_openai_api_key': 'azure_openai',
                'anthropic_api_key': 'anthropic',
                'mistral_api_key': 'mistral'
            }
            
            for config_key, provider_name in providers_map.items():
                if not env_keys.get(config_key):
                    stored_key = cred_manager.get_key(provider_name)
                    if stored_key:
                        env_keys[config_key] = stored_key
                        
        except ImportError:
            pass
        except Exception as e:
            print(f"Warning: Failed to access credential manager: {e}")

        # Update config
        if env_keys['groq_api_key']:
            self.config['ai']['groq_api_key'] = env_keys['groq_api_key']
        
        if env_keys['openai_api_key']:
            self.config['ai']['openai_api_key'] = env_keys['openai_api_key']
            
        if env_keys['azure_openai_api_key']:
            self.config['ai']['azure_openai_api_key'] = env_keys['azure_openai_api_key']
            
        if os.getenv('AZURE_OPENAI_ENDPOINT'):
            self.config['ai']['azure_endpoint'] = os.getenv('AZURE_OPENAI_ENDPOINT')
            
        if os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'):
            self.config['ai']['azure_deployment'] = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
            
        if env_keys['anthropic_api_key']:
            self.config['ai']['anthropic_api_key'] = env_keys['anthropic_api_key']
            
        if env_keys['mistral_api_key']:
            self.config['ai']['mistral_api_key'] = env_keys['mistral_api_key']
 