#!/usr/bin/env python3
"""
Setup script for CodeDocGen.

Installation script for the CodeDocGen package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="code_doc_gen",
    version="1.1.6",
    author="Mohit Mishra",
    author_email="mohitmishra786687@gmail.com",
    description="Intelligent automatic documentation generation for Python and C++ codebases using AST analysis and NLTK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mohitmishra786/CodeDocGen",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "nltk>=3.8",
        "pyyaml>=6.0",
        "pytest>=7.0.0",
        "typing-extensions>=4.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "cpp": [
            "clang>=6.0.0",
        ],
        "ai": [
            "groq>=0.4.0",
            "openai>=1.0.0",
        ],
        "all": [
            "clang>=6.0.0",
            "groq>=0.4.0",
            "openai>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "code_doc_gen=code_doc_gen.main:cli_main",
        ],
    },
    include_package_data=True,
    package_data={
        "code_doc_gen": ["*.yaml", "*.yml"],
    },
    keywords=[
        "documentation",
        "code-generation",
        "nltk",
        "ast",
        "parser",
        "c++",
        "python",
        "doxygen",
        "docstring",
    ],
    project_urls={
        "Bug Reports": "https://github.com/mohitmishra786/CodeDocGen/issues",
        "Source": "https://github.com/mohitmishra786/CodeDocGen",
        "Documentation": "https://github.com/mohitmishra786/CodeDocGen#readme",
    },
) 