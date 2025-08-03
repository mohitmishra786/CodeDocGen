# CodeDocGen

A command-line tool and library that automatically generates Doxygen-style comments and documentation for functions and methods in codebases. Uses rule-based analysis and NLTK for natural language processing to create human-readable documentation without AI/ML.

## Features

- **Rule-based Analysis**: Deterministic documentation generation using AST analysis and pattern matching
- **Multi-language Support**: C/C++ (using libclang), Python (using ast), Java (basic support)
- **Smart Inference**: Analyzes function bodies to detect loops, conditionals, exceptions, and operations
- **NLTK Integration**: Uses natural language processing for humanizing function names and descriptions
- **Flexible Output**: In-place file modification, diff generation, or new file creation
- **Configurable**: YAML-based configuration for custom rules and templates
- **Language-Aware Comment Detection**: Prevents duplicate documentation by detecting existing comments

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

### From TestPyPI (Latest Version)
```bash
pip install --index-url https://test.pypi.org/simple/ code_doc_gen==1.0.16
```

### From PyPI (Stable Version)
```bash
pip install code_doc_gen
```

## Usage

### Command Line Interface

```bash
# Generate documentation (automatically detects language from file extensions)
code_doc_gen --repo /path/to/repo --inplace

# Generate documentation for a C++ repository (preserves existing comments)
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

# Generate documentation (automatically detects language)
results = generate_docs('/path/to/repo', inplace=True)

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
- **NEW**: Recognizes existing comments (`//`, `/* */`, `/** */`) to prevent duplicates

### Python
- Uses built-in ast module for parsing
- Generates PEP 257 compliant docstrings
- Detects function signatures, parameters, return types, and exceptions
- Supports .py files
- **NEW**: Recognizes existing comments (`#`, `"""`, `'''`) and decorators to prevent duplicates

### Java
- **NEW**: Basic Java comment detection support
- Recognizes Javadoc-style comments with `@param`, `@return`, `@throws`
- Fallback to regex-based parsing when javaparser is not available
- Supports .java files

## Language-Aware Comment Detection

CodeDocGen v1.0.16 introduces intelligent comment detection that prevents duplicate documentation:

### Python Comment Detection
```python
# Existing comment above function
@decorator
def commented_func():
    """This function has a docstring"""
    return True

def inline_commented_func():  # Inline comment
    return True

def next_line_commented_func():
    # Comment on next line
    return True
```

### C++ Comment Detection
```cpp
// Existing comment above function
int add(int a, int b) {
    return a + b;
}

void inline_commented_func() { // Inline comment
    std::cout << "Hello" << std::endl;
}

/* Multi-line comment above function */
void multi_line_func() {
    std::cout << "Multi-line" << std::endl;
}

/** Doxygen comment */
void doxygen_func() {
    std::cout << "Doxygen" << std::endl;
}
```

### Java Comment Detection
```java
/**
 * Existing Javadoc comment
 * @param input The input parameter
 * @return The result
 */
public String processInput(String input) {
    return input.toUpperCase();
}
```

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
│       ├── python_parser.py # Python parser (ast)
│       └── java_parser.py   # Java parser (regex fallback)
├── tests/                   # Unit tests (76 tests)
├── requirements.txt         # Dependencies
├── setup.py                # Package setup
├── README.md               # This file
└── example.py              # Usage examples
```

## Development

### Running Tests

```bash
# Run all tests (76 tests)
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_generator.py -v

# Run tests with coverage
python -m pytest tests/ --cov=code_doc_gen
```

### Installing in Development Mode

```bash
pip install -e .
```

## Roadmap

### Version 1.1 (Next Release)
- **Enhanced Java Support**: Full javaparser integration for better Java parsing
- **JavaScript/TypeScript Support**: Add support for JS/TS files
- **Enhanced Templates**: More customization options for documentation styles
- **Performance Optimizations**: Parallel processing improvements

### Version 1.2
- **Go and Rust Support**: Add support for Go and Rust files
- **IDE Integration**: VSCode and IntelliJ plugin support
- **Batch Processing**: Support for processing multiple repositories
- **Documentation Quality**: Enhanced analysis for better documentation

### Version 1.3
- **C# Support**: Add C# language parser
- **PHP Support**: Add PHP language parser
- **Web Interface**: Simple web UI for documentation generation
- **CI/CD Integration**: GitHub Actions and GitLab CI templates

### Future Versions
- **Ruby Support**: Add Ruby language parser
- **Advanced Analysis**: More sophisticated code analysis and inference
- **Documentation Standards**: Support for various documentation standards
- **Machine Learning**: Optional ML-based documentation suggestions

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
- **Community**: For feedback and contributions 