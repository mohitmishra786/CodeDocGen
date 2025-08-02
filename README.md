# CodeDocGen

A command-line tool and library that automatically generates Doxygen-style comments and documentation for functions and methods in codebases. Uses rule-based analysis and NLTK for natural language processing to create human-readable documentation without AI/ML.

## Features

- **Rule-based Analysis**: Deterministic documentation generation using AST analysis and pattern matching
- **Multi-language Support**: C/C++ (using libclang), Python (using ast)
- **Smart Inference**: Analyzes function bodies to detect loops, conditionals, exceptions, and operations
- **NLTK Integration**: Uses natural language processing for humanizing function names and descriptions
- **Flexible Output**: In-place file modification, diff generation, or new file creation
- **Configurable**: YAML-based configuration for custom rules and templates

## Installation

### Prerequisites

- Python 3.8+
- Clang (for C/C++ parsing)

### Setup

1. **Activate the virtual environment:**
   ```bash
   source codedocgen/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download NLTK data:**
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
   ```

## Usage

### Command Line Interface

```bash
# Generate documentation for a C++ repository
code_doc_gen --repo /path/to/cpp/repo --lang c++ --inplace

# Generate documentation for Python files with custom output
code_doc_gen --repo /path/to/python/repo --lang python --output-dir ./docs

# Use custom configuration
code_doc_gen --repo /path/to/repo --lang c++ --config custom_rules.yaml

# Process specific files only
code_doc_gen --repo /path/to/repo --lang python --files src/main.py src/utils.py

# Show diff without applying changes
code_doc_gen --repo /path/to/repo --lang c++ --diff

# Enable verbose logging
code_doc_gen --repo /path/to/repo --lang python --verbose
```

### Library Usage

```python
from code_doc_gen import generate_docs

# Generate documentation for a repository
results = generate_docs('/path/to/repo', lang='c++')

# Process specific files
results = generate_docs('/path/to/repo', lang='python', files=['src/main.py'])

# Generate in-place documentation
generate_docs('/path/to/repo', lang='python', inplace=True)

# Generate to output directory
generate_docs('/path/to/repo', lang='c++', output_dir='./docs')
```

## Configuration

Create a `config.yaml` file to customize documentation generation:

```yaml
# Language-specific templates
templates:
  c++:
    brief: "/** \brief {description} */"
    param: " * \param {name} {description}"
    return: " * \return {description}"
    throws: " * \throws {exception} {description}"
  
  python:
    brief: '""" {description} """'
    param: "    :param {name}: {description}"
    return: "    :return: {description}"
    raises: "    :raises {exception}: {description}"

# Custom inference rules
rules:
  - pattern: "^validate.*"
    brief: "Validates the input {params}."
  - pattern: "^compute.*"
    brief: "Computes the {noun} based on {params}."
  - pattern: "^get.*"
    brief: "Retrieves the {noun}."
```

## Supported Languages

### C/C++
- Uses libclang for AST parsing
- Generates Doxygen-style comments
- Detects function signatures, parameters, return types, and exceptions
- Supports both .c and .cpp files

### Python
- Uses built-in ast module for parsing
- Generates PEP 257 compliant docstrings
- Detects function signatures, parameters, return types, and exceptions
- Supports .py files

## Project Structure

```
CodeDocGen/
├── code_doc_gen/
│   ├── __init__.py          # Main package interface
│   ├── main.py              # CLI entry point
│   ├── scanner.py           # Repository scanning
│   ├── analyzer.py          # NLTK-based analysis
│   ├── generator.py         # Documentation generation
│   ├── config.py            # Configuration management
│   ├── models.py            # Data models
│   └── parsers/             # Language-specific parsers
│       ├── __init__.py
│       ├── cpp_parser.py    # C/C++ parser (libclang)
│       └── python_parser.py # Python parser (ast)
├── tests/                   # Unit tests
├── requirements.txt         # Dependencies
├── setup.py                # Package setup
├── README.md               # This file
└── example.py              # Usage examples
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_analyzer.py -v
```

### Installing in Development Mode

```bash
pip install -e .
```

## Roadmap

### Version 1.1 (Next Release)
- **Java Support**: Add Java parser using javaparser or regex fallback
- **Enhanced Templates**: More customization options for documentation styles
- **Better Error Handling**: Improved error messages and recovery
- **Performance Optimizations**: Parallel processing improvements

### Version 1.2
- **JavaScript/TypeScript Support**: Add support for JS/TS files
- **IDE Integration**: VSCode and IntelliJ plugin support
- **Batch Processing**: Support for processing multiple repositories
- **Documentation Quality**: Enhanced analysis for better documentation

### Version 1.3
- **Go Support**: Add Go language parser
- **Rust Support**: Add Rust language parser
- **Web Interface**: Simple web UI for documentation generation
- **CI/CD Integration**: GitHub Actions and GitLab CI templates

### Future Versions
- **C# Support**: Add C# language parser
- **PHP Support**: Add PHP language parser
- **Ruby Support**: Add Ruby language parser
- **Advanced Analysis**: More sophisticated code analysis and inference
- **Documentation Standards**: Support for various documentation standards

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **NLTK**: For natural language processing capabilities
- **libclang**: For C/C++ AST parsing
- **Python ast module**: For Python code analysis 