# CodeDocGen

A command-line tool and library that automatically generates Doxygen-style comments and documentation for functions and methods in codebases. Uses rule-based analysis and NLTK for natural language processing to create human-readable documentation without AI/ML.

## Features

- **Rule-based Analysis**: Deterministic documentation generation using AST analysis and pattern matching
- **Multi-language Support**: C/C++ (using libclang), Python (using ast), Java (using javaparser)
- **Smart Inference**: Analyzes function bodies to detect loops, conditionals, exceptions, and operations
- **NLTK Integration**: Uses natural language processing for humanizing function names and descriptions
- **Flexible Output**: In-place file modification, diff generation, or new file creation
- **Configurable**: YAML-based configuration for custom rules and templates

## Installation

### Prerequisites

- Python 3.8+
- Clang (for C/C++ parsing)
- Java (for Java parsing, if using javaparser)

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
code_doc_gen --repo /path/to/repo --lang java --config custom_rules.yaml
```

### Library Usage

```python
from code_doc_gen import generate_docs

# Generate documentation for a repository
results = generate_docs('/path/to/repo', lang='c++')

# Process specific files
results = generate_docs('/path/to/repo', lang='python', files=['src/main.py'])
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

### Python
- Uses built-in `ast` module
- Generates docstring-style documentation
- Analyzes function bodies for behavior inference

### Java
- Uses javaparser for AST parsing
- Generates Javadoc-style comments
- Supports class methods and constructors

## Examples

### Input (C++)
```cpp
int add(int a, int b) {
    return a + b;
}
```

### Output
```cpp
/**
 * \brief Adds two integers.
 * \param a First integer.
 * \param b Second integer.
 * \return The sum of the two integers.
 */
int add(int a, int b) {
    return a + b;
}
```

### Input (Python)
```python
def validate_email(email):
    if '@' not in email:
        raise ValueError("Invalid email")
    return True
```

### Output
```python
def validate_email(email):
    """
    Validates the email address.
    
    :param email: The email address to validate.
    :return: True if valid.
    :raises ValueError: If email format is invalid.
    """
    if '@' not in email:
        raise ValueError("Invalid email")
    return True
```

## Project Structure

```
code_doc_gen/
├── __init__.py
├── main.py              # CLI entrypoint
├── scanner.py           # Repository scanning
├── parsers/             # Language-specific parsers
│   ├── __init__.py
│   ├── cpp_parser.py
│   ├── python_parser.py
│   └── java_parser.py
├── analyzer.py          # NLTK-based inference
├── generator.py         # Comment formatting
├── config.py           # YAML configuration
└── tests/              # Unit tests
    ├── __init__.py
    ├── test_scanner.py
    ├── test_parsers.py
    ├── test_analyzer.py
    └── test_generator.py
```

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Languages

1. Create a new parser in `parsers/`
2. Implement the `BaseParser` interface
3. Add language-specific templates to configuration
4. Update the main scanner to recognize new file extensions

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Roadmap

- [ ] JavaScript/TypeScript support
- [ ] Go support
- [ ] Rust support
- [ ] Better error handling and recovery
- [ ] Performance optimizations for large codebases
- [ ] IDE integration plugins 