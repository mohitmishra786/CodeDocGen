"""
CodeDocGen - Intelligent automatic documentation generation for codebases.

An AI-powered tool that generates intelligent Doxygen-style comments and documentation
for functions and methods using AST analysis and NLTK for natural language processing.
Features context-aware parameter descriptions and function-specific return type analysis.
"""

from typing import Dict, List, Optional, Union
from pathlib import Path

from .scanner import RepositoryScanner
from .config import Config
from .generator import DocumentationGenerator

__version__ = "1.1.0"
__author__ = "Mohit Mishra"
__license__ = "MIT"


"""
    Generates the docs based on repo_path, lang, files, config_path, inplace, output_dir. Function iterates over data, conditionally processes input, has side effects, performs arithmetic operations. Takes repo_path, lang, files, config_path, inplace and output_dir as input. Returns a dict[(str, str)] value.
    :param repo_path: The repo_path value of type Union[(str, Path)].
    :param lang: The lang string.
    :param files: The files value of type Optional[List[str]].
    :param config_path: The config_path value of type Optional[Union[(str, Path)]].
    :param inplace: The inplace boolean value.
    :param output_dir: The output_dir value of type Optional[Union[(str, Path)]].
    :return: Value of type Dict[(str, str)]

"""
def generate_docs(
    repo_path: Union[str, Path],
    lang: str = "c++",
    files: Optional[List[str]] = None,
    config_path: Optional[Union[str, Path]] = None,
    inplace: bool = False,
    output_dir: Optional[Union[str, Path]] = None
) -> Dict[str, str]:
    """
    Generate documentation for functions and methods in a repository.
    
    Args:
        repo_path: Path to the repository to scan
        lang: Programming language ('c++', 'python')
        files: Specific files to process (if None, processes all files)
        config_path: Path to custom configuration file
        inplace: Whether to modify files in place
        output_dir: Directory to output modified files (if not inplace)
        
    Returns:
        Dictionary mapping file paths to generated documentation strings
    """
    config = Config(config_path) if config_path else Config()
    scanner = RepositoryScanner(config)
    generator = DocumentationGenerator(config)
    
    # Scan repository for files
    file_paths = scanner.scan_repository(repo_path, lang, files)
    
    results = {}
    for file_path in file_paths:
        try:
            # Parse and analyze the file
            functions = scanner.parse_file(file_path, lang)
            
            # Generate documentation
            doc_strings = generator.generate_documentation(functions, lang)
            
            if inplace:
                # Modify file in place
                generator.apply_documentation_inplace(file_path, doc_strings)
            elif output_dir:
                # Write to output directory
                output_path = Path(output_dir) / Path(file_path).name
                generator.write_documentation_to_file(output_path, doc_strings)
            
            results[str(file_path)] = doc_strings
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    return results


# Convenience functions for specific languages
def generate_cpp_docs(repo_path: Union[str, Path], **kwargs) -> Dict[str, str]:
    """Generate documentation for C++ code."""
    return generate_docs(repo_path, lang="c++", **kwargs)


def generate_python_docs(repo_path: Union[str, Path], **kwargs) -> Dict[str, str]:
    """Generate documentation for Python code."""
    return generate_docs(repo_path, lang="python", **kwargs)


# Java support will be added in future versions
# def generate_java_docs(repo_path: Union[str, Path], **kwargs) -> Dict[str, str]:
#     """Generate documentation for Java code."""
#     return generate_docs(repo_path, lang="java", **kwargs)


__all__ = [
    'generate_docs',
    'generate_cpp_docs',
    'generate_python_docs', 
    'RepositoryScanner',
    'Config',
    'DocumentationGenerator'
] 