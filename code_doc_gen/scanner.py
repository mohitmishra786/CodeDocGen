"""
Repository scanner for CodeDocGen.

Handles scanning repositories for source files and coordinating
the parsing and analysis of code files.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from multiprocessing import Pool, cpu_count

from .parsers import ParserFactory
from .analyzer import IntelligentAnalyzer
from .models import Function, ParsedFile
from .config import Config
from .git_integration import GitIntegration


class RepositoryScanner:
    """Scans repositories for source files and coordinates parsing."""
    
    def __init__(self, config: Config):
        """
        Initialize the repository scanner.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.parser_factory = ParserFactory(config)
        self.analyzer = IntelligentAnalyzer(config)
        
        # Get logger (logging configuration is handled centrally in main.py)
        self.logger = logging.getLogger(__name__)
    
    """
        Performs scan_repository operation. Function iterates over data, conditionally processes input, may throw exceptions, may return early, has side effects, performs arithmetic operations. Takes self, repo_path, lang and files as input. Returns a list[path] value.
        :param self: The self object.
        :param repo_path: The repo_path value of type Path.
        :param lang: The lang value of type Optional[str].
        :param files: The files value of type Optional[List[str]].
        :return: Value of type List[Path]
        :raises Call: Thrown when call occurs.

    """
    def scan_repository(
        self, 
        repo_path: Path, 
        lang: Optional[str] = None, 
        files: Optional[List[str]] = None,
        changes_only: bool = False
    ) -> List[Path]:
        """
        Scan a repository for source files.
        
        Args:
            repo_path: Path to the repository
            lang: Programming language to filter by
            files: Specific files to process
            changes_only: Whether to only process changed files (requires Git)
            
        Returns:
            List of file paths to process
        """
        repo_path = Path(repo_path)
        
        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        # Handle changes-only mode
        if changes_only:
            git_integration = GitIntegration(repo_path)
            if not git_integration.is_git_repo:
                self.logger.warning("Changes-only mode requires a Git repository")
                return []
            
            # Get all supported file extensions
            all_extensions = []
            for lang_name in ['c++', 'python', 'java']:
                all_extensions.extend(self.config.get_file_extensions(lang_name))
            
            # Get changed files and filter to source files
            changed_files = git_integration.get_changed_files()
            source_files = git_integration.filter_source_files(changed_files, all_extensions)
            
            self.logger.info(f"Found {len(source_files)} changed source files")
            return source_files
        
        if files:
            # Process specific files
            file_paths = []
            for file_str in files:
                file_path = repo_path / file_str
                if file_path.exists():
                    file_paths.append(file_path)
                else:
                    self.logger.warning(f"File not found: {file_path}")
            return file_paths
        
        # Scan the entire repository
        file_paths = []
        
        for root, dirs, filenames in os.walk(repo_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore_directory(Path(root) / d)]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                # Skip ignored files
                if self.config.should_ignore_file(file_path):
                    continue
                
                # Check if we can parse this file
                if lang:
                    # Use specific language parser
                    try:
                        parser = self.parser_factory.get_parser(lang)
                        if parser.can_parse(file_path):
                            file_paths.append(file_path)
                    except ValueError:
                        self.logger.warning(f"No parser available for language: {lang}")
                else:
                    # Try to find appropriate parser
                    try:
                        parser = self.parser_factory.get_parser_for_file(file_path)
                        file_paths.append(file_path)
                    except ValueError:
                        # Skip files we can't parse
                        continue
        
        self.logger.info(f"Found {len(file_paths)} files to process")
        return file_paths
    
    def _should_ignore_directory(self, dir_path: Path) -> bool:
        """
        Check if a directory should be ignored.
        
        Args:
            dir_path: Directory path
            
        Returns:
            True if directory should be ignored
        """
        dir_name = dir_path.name
        
        # Common directories to ignore
        ignore_dirs = {
            '.git', '.svn', '.hg', '.bzr',  # Version control
            '__pycache__', '.pytest_cache',  # Python cache
            'node_modules', 'bower_components',  # Node.js
            'build', 'dist', 'target',  # Build artifacts
            '.idea', '.vscode',  # IDE files
            'venv', 'env', '.venv', '.env', 'codedocgen',  # Virtual environments
            'vendor', 'deps',  # Dependencies
            'tmp', 'temp', 'cache',  # Temporary files
            'site-packages',  # Python packages
        }
        
        return dir_name in ignore_dirs
    
    def parse_file(self, file_path: Path, lang: Optional[str] = None) -> List[Function]:
        """
        Parse a single file and extract functions.
        
        Args:
            file_path: Path to the file to parse
            lang: Programming language (if None, auto-detect)
            
        Returns:
            List of Function objects
        """
        try:
            # Get appropriate parser
            if lang:
                parser = self.parser_factory.get_parser(lang)
            else:
                parser = self.parser_factory.get_parser_for_file(file_path)
            
            # Parse the file
            parsed_file = parser.parse_file(file_path)
            
            # Determine language for AI analysis
            detected_lang = lang or self._detect_language_from_file(file_path)
            
            # Analyze functions
            for function in parsed_file.functions:
                self.analyzer.analyze_function(function, detected_lang)
                
                # Analyze parameters
                for parameter in function.parameters:
                    self.analyzer.analyze_parameter(parameter)
                
                # Analyze exceptions
                for exception in function.exceptions:
                    self.analyzer.analyze_exception(exception)
            
            self.logger.info(f"Parsed {len(parsed_file.functions)} functions from {file_path}")
            return parsed_file.functions
            
        except (Exception, OSError, ImportError) as e:
            self.logger.error(f"Error parsing file {file_path}: {e}")
            return []
    
    """
        Parses the files based on self, file_paths, lang, max_workers. Function iterates over data, conditionally processes input, has side effects. Takes self, file_paths, lang and max_workers as input. Returns a dict[(path, list[function])] value.
        :param self: The self object.
        :param file_paths: The file_paths value of type List[Path].
        :param lang: The lang value of type Optional[str].
        :param max_workers: The max_workers value of type Optional[int].
        :return: Value of type Dict[(Path, List[Function])]

    """
    def parse_files_parallel(
        self, 
        file_paths: List[Path], 
        lang: Optional[str] = None,
        max_workers: Optional[int] = None
    ) -> Dict[Path, List[Function]]:
        """
        Parse multiple files in parallel.
        
        Args:
            file_paths: List of file paths to parse
            lang: Programming language (if None, auto-detect)
            max_workers: Maximum number of worker processes
            
        Returns:
            Dictionary mapping file paths to lists of functions
        """
        if not max_workers:
            max_workers = min(cpu_count(), len(file_paths))
        
        self.logger.info(f"Parsing {len(file_paths)} files with {max_workers} workers")
        
        # Prepare arguments for parallel processing
        args = [(file_path, lang) for file_path in file_paths]
        
        # Use multiprocessing to parse files in parallel
        with Pool(processes=max_workers) as pool:
            results = pool.starmap(self._parse_file_worker, args)
        
        # Combine results
        file_functions = {}
        for file_path, functions in zip(file_paths, results):
            file_functions[file_path] = functions
        
        return file_functions
    
    def _parse_file_worker(self, file_path: Path, lang: Optional[str] = None) -> List[Function]:
        """
        Worker function for parallel file parsing.
        
        Args:
            file_path: Path to the file to parse
            lang: Programming language
            
        Returns:
            List of Function objects
        """
        try:
            return self.parse_file(file_path, lang)
        except (Exception, OSError, ImportError) as e:
            self.logger.error(f"Error in worker parsing {file_path}: {e}")
            return []
    
    """
        Performs scan_and_parse operation. Function iterates over data, conditionally processes input, may return early, has side effects. Takes self, repo_path, lang, files and parallel as input. Returns a dict[(path, list[function])] value.
        :param self: The self object.
        :param repo_path: The repo_path value of type Path.
        :param lang: The lang value of type Optional[str].
        :param files: The files value of type Optional[List[str]].
        :param parallel: The parallel boolean value.
        :return: Value of type Dict[(Path, List[Function])]

    """
    def scan_and_parse(
        self, 
        repo_path: Path, 
        lang: Optional[str] = None,
        files: Optional[List[str]] = None,
        parallel: bool = True
    ) -> Dict[Path, List[Function]]:
        """
        Scan repository and parse all files.
        
        Args:
            repo_path: Path to the repository
            lang: Programming language to filter by
            files: Specific files to process
            parallel: Whether to use parallel processing
            
        Returns:
            Dictionary mapping file paths to lists of functions
        """
        # Scan for files
        file_paths = self.scan_repository(repo_path, lang, files)
        
        if not file_paths:
            self.logger.warning("No files found to process")
            return {}
        
        # Parse files
        if parallel and len(file_paths) > 1:
            return self.parse_files_parallel(file_paths, lang)
        else:
            file_functions = {}
            for file_path in file_paths:
                functions = self.parse_file(file_path, lang)
                file_functions[file_path] = functions
            return file_functions
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages.
        
        Returns:
            List of supported language names
        """
        return self.parser_factory.get_supported_languages()
    
    def get_file_extensions(self, lang: str) -> List[str]:
        """
        Get file extensions for a language.
        
        Args:
            lang: Programming language
            
        Returns:
            List of file extensions
        """
        return self.config.get_file_extensions(lang)
    
    def _detect_language_from_file(self, file_path: Path) -> str:
        """
        Detect programming language from file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected language string
        """
        suffix = file_path.suffix.lower()
        
        if suffix in ['.py', '.pyx', '.pxd']:
            return 'python'
        elif suffix in ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hh', '.hxx']:
            return 'c++'
        elif suffix == '.java':
            return 'java'
        else:
            return 'python'  # Default fallback 