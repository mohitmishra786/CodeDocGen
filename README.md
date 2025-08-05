# CodeDocGen

A command-line tool and library that automatically generates Doxygen-style comments and documentation for functions and methods in codebases. Uses AI-powered analysis with fallback to NLTK for intelligent, context-aware documentation generation.

## Features

- **AI-Powered Comment Generation**: Uses Phind (free, no API key) or Groq for intelligent, context-aware documentation
- **Smart Fallback System**: Falls back to NLTK-based analysis when AI is unavailable or fails
- **Multi-language Support**: C/C++ (using libclang), Python (using ast), Java (basic support)
- **Smart Function Analysis**: Analyzes function bodies to detect recursion, loops, conditionals, regex usage, API calls, and file operations
- **Git Integration**: Process only changed files with `--changes-only` flag and auto-commit documentation with `--auto-commit`
- **Context-Aware Descriptions**: Generates specific, meaningful descriptions instead of generic templates
- **Flexible Output**: In-place file modification, diff generation, or new file creation
- **Configurable**: YAML-based configuration for custom rules, templates, and AI settings
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
pip install --index-url https://test.pypi.org/simple/ code_doc_gen==1.1.0
```

### From PyPI (Stable Version)
```bash
pip install code-doc-gen==1.1.0
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

# Enable AI-powered documentation generation (using Phind - free, no API key)
code_doc_gen --repo /path/to/repo --lang python --enable-ai --ai-provider phind --inplace

# Use Groq AI provider (requires API key)
code_doc_gen --repo /path/to/repo --lang c++ --enable-ai --ai-provider groq --groq-api-key YOUR_API_KEY --inplace

# Process only changed files in a Git repository
code_doc_gen --repo /path/to/repo --lang python --changes-only --inplace

# Auto-commit generated documentation
code_doc_gen --repo /path/to/repo --lang python --enable-ai --inplace --auto-commit
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

# AI configuration for intelligent comment generation
ai:
  enabled: false  # Set to true to enable AI-powered analysis
  provider: "phind"  # Options: "phind" (free, no API key) or "groq" (requires API key)
  groq_api_key: ""  # Get from https://console.groq.com/keys or set GROQ_API_KEY environment variable
  openai_api_key: ""  # Get from https://platform.openai.com/account/api-keys or set OPENAI_API_KEY environment variable
  max_retries: 3  # Number of retries for AI API calls
  retry_delay: 1.0  # Delay between retries in seconds
```

## Environment Variables (Recommended for API Keys)

For security and ease of use, it's recommended to use environment variables for API keys instead of hardcoding them in config files.

### Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file and add your API keys:**
   ```bash
   # Groq API Key (get from https://console.groq.com/keys)
   GROQ_API_KEY=your_groq_api_key_here
   
   # OpenAI API Key (get from https://platform.openai.com/account/api-keys)
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Add `.env` to your `.gitignore` file:**
   ```bash
   echo ".env" >> .gitignore
   ```

### Priority Order

The tool loads API keys in the following priority order:
1. **Environment variables** (from `.env` file) - **Highest priority**
2. **Command line arguments** (if provided)
3. **Config file values** (from `config.yaml`) - **Lowest priority**

This ensures your API keys are secure and not accidentally committed to version control.

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

## AI-Powered Comment Generation

CodeDocGen now supports AI-powered comment generation with intelligent fallback to NLTK-based analysis:

### AI Providers

#### Phind (Recommended - Free)
- **No API key required** - completely free to use
- Uses Phind-70B model for high-quality comment generation
- Automatic fallback to NLTK if AI is unavailable
- Perfect for getting started with AI-powered documentation

#### Groq (Alternative)
- **Requires API key** from https://console.groq.com/keys
- Uses Mixtral-8x7b-32768 model
- Fast response times with generous free tier
- Install with: `pip install groq`

### Setup

1. **Enable AI in configuration:**
   ```yaml
   ai:
     enabled: true
     provider: "phind"  # or "groq"
   ```

2. **For Groq/OpenAI users:**
   - Get API keys from:
     - Groq: https://console.groq.com/keys
     - OpenAI: https://platform.openai.com/account/api-keys
   - **Option 1: Use .env file (Recommended)**
     ```bash
     # Copy the example file
     cp .env.example .env
     
     # Edit .env and add your API keys
     GROQ_API_KEY=your_groq_api_key_here
     OPENAI_API_KEY=your_openai_api_key_here
     ```
   - **Option 2: Add to config.yaml**
     ```yaml
     groq_api_key: "your-api-key-here"
     openai_api_key: "your-openai-api-key-here"
     ```
   - **Note**: Environment variables (from .env) take precedence over config file values

3. **Command line usage:**
   ```bash
   # Enable AI with Phind (free)
   code_doc_gen --repo /path/to/repo --enable-ai --ai-provider phind --inplace
   
   # Enable AI with Groq (using .env file)
   code_doc_gen --repo /path/to/repo --enable-ai --ai-provider groq --inplace
   
   # Enable AI with OpenAI (using .env file)
   code_doc_gen --repo /path/to/repo --enable-ai --ai-provider openai --inplace
   
   # Or pass API keys directly (not recommended for security)
   code_doc_gen --repo /path/to/repo --enable-ai --ai-provider groq --groq-api-key YOUR_KEY --inplace
   ```

### Fallback System

The tool uses a smart fallback system:
1. **AI Analysis**: Try AI-powered comment generation first
2. **NLTK Analysis**: Fall back to NLTK-based intelligent analysis if AI fails
3. **Rule-based**: Final fallback to pattern-based rules

This ensures the tool always works, even when AI services are unavailable.

## Intelligent Comment Generation (NLTK-based)

CodeDocGen v1.1.3 introduces intelligent comment generation with AST analysis and NLTK-powered descriptions:

### Key Improvements
- **Context-Aware Parameter Descriptions**: Smart parameter descriptions based on names and context
- **Function-Specific Return Types**: Intelligent return type descriptions based on function purpose
- **Behavioral Detection**: Detects recursion, loops, conditionals, regex usage, API calls, and file operations
- **Specific Actions**: Generates specific action verbs instead of generic "processes" descriptions
- **Complete Coverage**: All functions receive intelligent, meaningful comments

### Language-Aware Comment Detection

CodeDocGen v1.1.3 maintains intelligent comment detection that prevents duplicate documentation:

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

### Version 1.1 (Current Release)
- **Intelligent Comment Generation**: AST analysis and NLTK-powered documentation
- **Context-Aware Descriptions**: Smart parameter and return type descriptions
- **Behavioral Detection**: Recursion, loops, conditionals, regex, API calls, file operations
- **Specific Actions**: Meaningful action verbs instead of generic descriptions
- **Complete Coverage**: All functions receive intelligent comments

### Version 1.2 (Next Release)
- **Enhanced Java Support**: Full javaparser integration for better Java parsing
- **JavaScript/TypeScript Support**: Add support for JS/TS files
- **Enhanced Templates**: More customization options for documentation styles
- **Performance Optimizations**: Parallel processing improvements

### Version 1.3
- **Go and Rust Support**: Add support for Go and Rust files
- **IDE Integration**: VSCode and IntelliJ plugin support
- **Batch Processing**: Support for processing multiple repositories
- **Documentation Quality**: Enhanced analysis for better documentation

### Version 1.4
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

## AI Providers Setup

CodeDocGen supports multiple AI providers for intelligent documentation generation. You can configure one primary provider and set up fallback providers for reliability.

### Available Providers

#### 1. Phind (Free, No API Key Required)
- **Status**: Unofficial API - use with caution
- **Cost**: Free
- **Setup**: No configuration required
- **Warning**: This is an unofficial API that may be rate-limited, change, or violate terms of service. Use only for personal projects.

#### 2. Groq (Free API Key Required)
- **Status**: Official API
- **Cost**: Free tier available
- **Setup**: 
  1. Visit [Groq Console](https://console.groq.com/keys)
  2. Sign up for a free account
  3. Generate an API key
  4. Add to `config.yaml`:
     ```yaml
     ai:
       groq_api_key: "your_groq_api_key_here"
     ```

#### 3. OpenAI (Paid API Key Required)
- **Status**: Official API
- **Cost**: Pay-per-use
- **Setup**:
  1. Visit [OpenAI Platform](https://platform.openai.com/account/api-keys)
  2. Create an account and add billing information
  3. Generate an API key
  4. Add to `config.yaml`:
     ```yaml
     ai:
       openai_api_key: "your_openai_api_key_here"
     ```

### Configuration

Configure AI providers in your `config.yaml`:

```yaml
ai:
  enabled: true
  provider: "phind"  # Primary provider: phind, groq, or openai
  fallback_providers: ["groq", "openai"]  # Fallback order
  groq_api_key: "your_groq_key"
  openai_api_key: "your_openai_key"
  max_retries: 5
  retry_delay: 1.0
  models:
    phind: "gpt-3.5-turbo"
    groq: ["llama3-8b-8192", "llama3.1-8b-instant", "llama3-70b-8192"]
    openai: "gpt-4o-mini"
```

### Usage Examples

```bash
# Use Phind (free, no key required)
python -m code_doc_gen.main --repo . --files src/ --enable-ai --ai-provider phind

# Use Groq with fallback to OpenAI
python -m code_doc_gen.main --repo . --files src/ --enable-ai --ai-provider groq

# Use OpenAI directly
python -m code_doc_gen.main --repo . --files src/ --enable-ai --ai-provider openai
```

### Fallback Behavior

The system automatically tries providers in this order:
1. Primary provider (from config)
2. Fallback providers (in order specified)

If all AI providers fail, the system falls back to NLTK-based analysis.

### Rate Limiting and Reliability

- **Phind**: May be rate-limited; exponential backoff retry
- **Groq**: Official rate limits; exponential backoff retry  
- **OpenAI**: Official rate limits; exponential backoff retry

All providers use intelligent retry logic with exponential backoff to handle temporary failures. 