#!/usr/bin/env python3
"""
Command-line interface for CodeDocGen.

Main entry point for the CodeDocGen tool that provides both CLI and library interfaces.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from . import generate_docs, generate_cpp_docs, generate_python_docs
from .scanner import RepositoryScanner
from .config import Config


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def validate_args(args: argparse.Namespace) -> None:
    """
    Validate command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Raises:
        ValueError: If arguments are invalid
    """
    repo_path = Path(args.repo)
    if not repo_path.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")
    
    if not repo_path.is_dir():
        raise ValueError(f"Repository path must be a directory: {repo_path}")
    
    if args.lang and args.lang not in ['c++', 'python']:
        raise ValueError(f"Unsupported language: {args.lang}")
    
    if args.config and not Path(args.config).exists():
        raise ValueError(f"Configuration file does not exist: {args.config}")
    
    if args.output_dir and args.inplace:
        raise ValueError("Cannot specify both --output-dir and --inplace")


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="CodeDocGen - Automatic documentation generation for codebases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate documentation for a C++ repository
  code_doc_gen --repo /path/to/cpp/repo --lang c++ --inplace

  # Generate documentation for Python files with custom output
  code_doc_gen --repo /path/to/python/repo --lang python --output-dir ./docs

  # Use custom configuration
  code_doc_gen --repo /path/to/repo --lang c++ --config custom_rules.yaml

  # Process specific files only
  code_doc_gen --repo /path/to/repo --lang python --files src/main.py src/utils.py
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--repo',
        required=True,
        help='Path to the repository to scan'
    )
    
    # Optional arguments
    parser.add_argument(
        '--lang',
        choices=['c++', 'python'],
        help='Programming language (auto-detect if not specified)'
    )
    
    parser.add_argument(
        '--files',
        nargs='+',
        help='Specific files to process (relative to repo path)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to custom configuration file (YAML)'
    )
    
    parser.add_argument(
        '--inplace',
        action='store_true',
        help='Modify files in place (creates backups)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Directory to output modified files (if not using --inplace)'
    )
    
    parser.add_argument(
        '--diff',
        action='store_true',
        help='Show diff of changes instead of applying them'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'CodeDocGen {__import__("code_doc_gen").__version__}'
    )
    
    args = parser.parse_args()
    
    try:
        # Set up logging
        setup_logging(args.verbose)
        logger = logging.getLogger(__name__)
        
        # Validate arguments
        validate_args(args)
        
        logger.info("Starting CodeDocGen")
        logger.info(f"Repository: {args.repo}")
        logger.info(f"Language: {args.lang or 'auto-detect'}")
        
        # Load configuration
        config_path = Path(args.config) if args.config else None
        config = Config(config_path)
        
        # Initialize scanner
        scanner = RepositoryScanner(config)
        
        # Check supported languages
        supported_langs = scanner.get_supported_languages()
        logger.info(f"Supported languages: {', '.join(supported_langs)}")
        
        if args.lang and args.lang not in supported_langs:
            logger.error(f"Language '{args.lang}' is not supported")
            logger.error(f"Available languages: {', '.join(supported_langs)}")
            return 1
        
        # Scan repository
        logger.info("Scanning repository for source files...")
        file_paths = scanner.scan_repository(Path(args.repo), args.lang, args.files)
        
        if not file_paths:
            logger.warning("No source files found to process")
            return 0
        
        logger.info(f"Found {len(file_paths)} files to process")
        
        # Process files
        total_functions = 0
        processed_files = 0
        
        for file_path in file_paths:
            try:
                logger.info(f"Processing {file_path}")
                
                # Parse file
                functions = scanner.parse_file(file_path, args.lang)
                
                if not functions:
                    logger.warning(f"No functions found in {file_path}")
                    continue
                
                logger.info(f"Found {len(functions)} functions in {file_path}")
                total_functions += len(functions)
                
                # Generate documentation
                from .generator import DocumentationGenerator
                generator = DocumentationGenerator(config)
                
                # Determine language for this file
                file_lang = args.lang
                if not file_lang:
                    # Auto-detect language based on file extension
                    if file_path.suffix.lower() in ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hh', '.hxx']:
                        file_lang = 'c++'
                    elif file_path.suffix.lower() in ['.py', '.pyx', '.pxd']:
                        file_lang = 'python'
                    elif file_path.suffix.lower() == '.java':
                        file_lang = 'java'
                    else:
                        logger.warning(f"Could not determine language for {file_path}")
                        continue
                
                documentation = generator.generate_documentation(functions, file_lang)
                
                if not documentation:
                    logger.warning(f"No documentation generated for {file_path}")
                    continue
                
                # Apply or output documentation
                if args.diff:
                    # Show diff
                    diff = generator.generate_diff(file_path, documentation)
                    if diff:
                        print(f"\n--- Diff for {file_path} ---")
                        print(diff)
                    else:
                        print(f"\nNo changes for {file_path}")
                
                elif args.inplace:
                    # Apply in place
                    generator.apply_documentation_inplace(file_path, documentation)
                    processed_files += 1
                
                elif args.output_dir:
                    # Write to output directory
                    output_path = Path(args.output_dir) / file_path.name
                    generator.write_documentation_to_file(output_path, documentation)
                    processed_files += 1
                
                else:
                    # Just show what would be generated
                    print(f"\n--- Documentation for {file_path} ---")
                    for func_name, doc_string in documentation.items():
                        print(f"\nFunction: {func_name}")
                        print(doc_string)
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue
        
        # Summary
        logger.info(f"Processing complete!")
        logger.info(f"Processed {processed_files} files")
        logger.info(f"Found {total_functions} functions")
        
        if args.inplace:
            logger.info("Files have been modified in place (backups created with .bak extension)")
        elif args.output_dir:
            logger.info(f"Modified files written to {args.output_dir}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cli_main() -> None:
    """Entry point for command-line usage."""
    sys.exit(main())


if __name__ == '__main__':
    cli_main() 