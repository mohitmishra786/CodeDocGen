# CodeDocGen

A command-line tool and library that automatically generates Doxygen-style comments and documentation for functions and methods in codebases. Uses AI-powered analysis with fallback to NLTK for intelligent, context-aware documentation generation.

## Features

- **AI-Powered Comment Generation**: Uses Groq, OpenAI, Anthropic (Claude), Mistral, or Azure OpenAI for intelligent, context-aware documentation
- **Smart Fallback System**: Falls back to NLTK/SpaCy-based analysis when AI is unavailable or fails
- **Multi-language Support**: C/C++ (using libclang), Python (using ast), Java (regex/AI), JavaScript (regex/AI), TypeScript (regex/AI), Go (regex/AI), Rust (regex/AI)
- **Smart Function Analysis**: Analyzes function bodies to detect recursion, loops, conditionals, regex usage, API calls, and file operations
- **Git Integration**: Process only changed files with `--changes-only` flag and auto-commit documentation with `--auto-commit`
- **Context-Aware Descriptions**: Generates specific, meaningful descriptions instead of generic templates
- **Flexible Output**: In-place file modification, diff generation, or new file creation
- **Configurable**: YAML-based configuration for custom rules, templates, and AI settings
- **Cross-Platform**: Full support for Windows, macOS, and Linux
- **Scalable**: Progress bars and optimized parallel processing for large repositories

## Installation

### Prerequisites

- Python 3.8+
- Clang (for C/C++ parsing) - Optional but recommended

### Setup

1. **Activate the virtual environment:**
   ```bash
   source codedocgen/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # Install optional NLP/AI extras
   pip install -e .[ai,nlp]
   ```

3. **Download NLTK/SpaCy data:**
   ```python
   # NLTK (Required)
   python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"
   
   # SpaCy (Optional - for enhanced analysis)
   python -m spacy download en_core_web_sm
   ```

### From TestPyPI (Latest Version)
```bash
pip install --index-url https://test.pypi.org/simple/ code_doc_gen==1.2.0
```

### From PyPI (Stable Version)
```bash
pip install code-doc-gen
```

### OS-specific setup guides (highly recommended)
- Windows: [usage/windows.md](usage/windows.md)
- Linux: [usage/linux.md](usage/linux.md)
- macOS: [usage/macos.md](usage/macos.md)

## Usage

### Command Line Interface

```bash
# Generate documentation (automatically detects language from file extensions)
code_doc_gen --repo /path/to/repo --inplace

# Generate documentation for a C++ repository (preserves existing comments)
code_doc_gen --repo /path/to/cpp/repo --lang c++ --inplace --clang-path /usr/lib/llvm-14/lib/libclang.so

# Generate documentation for Python files with custom output
code_doc_gen --repo /path/to/python/repo --lang python --output-dir ./docs

# Enable AI-powered documentation generation (Groq/OpenAI/Anthropic/Mistral)
code_doc_gen --repo /path/to/repo --enable-ai --ai-provider anthropic --inplace

# Use enhanced SpaCy analysis
code_doc_gen --repo /path/to/repo --enable-spacy --inplace

# Process only changed files in a Git repository
code_doc_gen --repo /path/to/repo --changes-only --inplace
```

### Library Usage

```python
from code_doc_gen import generate_docs

# Generate documentation (automatically detects language)
results = generate_docs('/path/to/repo', inplace=True)
```

## Configuration

Create a `config.yaml` file to customize documentation generation:

```yaml
# AI configuration
ai:
  enabled: true
  provider: "groq"  # groq, openai, anthropic, mistral, azure_openai
  fallback_providers: ["openai", "anthropic"]
  groq_api_key: ""      # Or set GROQ_API_KEY env var
  openai_api_key: ""    # Or set OPENAI_API_KEY env var
  anthropic_api_key: "" # Or set ANTHROPIC_API_KEY env var
  mistral_api_key: ""   # Or set MISTRAL_API_KEY env var
  azure_openai_api_key: "" # Or set AZURE_OPENAI_API_KEY env var
  azure_endpoint: ""    # Or set AZURE_OPENAI_ENDPOINT env var
  azure_deployment: ""  # Or set AZURE_OPENAI_DEPLOYMENT_NAME env var
  models:
    groq: ["llama3-8b-8192", "llama3.1-8b-instant"]
    openai: "gpt-4o-mini"
    anthropic: "claude-3-haiku-20240307"
    mistral: "mistral-small-latest"
    azure_openai: "gpt-4" # Placeholder, usually uses azure_deployment

# C++ Configuration
cpp:
  libclang:
    library_file: "/path/to/libclang.so"  # Can also be set via --clang-path

# NLP Configuration
nltk:
  enable_spacy: true  # Use SpaCy for better analysis
```

## Environment Variables (Recommended for API Keys)

```bash
GROQ_API_KEY=your_key
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
MISTRAL_API_KEY=your_key
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

## Supported Languages

### C/C++
- Uses libclang for AST parsing (robust) with regex fallback
- Customizable libclang path via `--clang-path` or config

### Python
- Uses built-in ast module

### Java/JavaScript
- Enhanced regex-based parsing
- AI-powered context understanding

### TypeScript/Go/Rust
- Regex-based parsing
- AI-powered context understanding

## AI Providers

CodeDocGen supports:
1. **Groq** (Fastest, Free tier)
2. **OpenAI** (GPT-4o, GPT-3.5)
3. **Anthropic** (Claude 3 Haiku/Opus/Sonnet)
4. **Mistral** (Mistral Small/Large)
5. **Azure OpenAI** (Enterprise)

## VSCode Extension

This repository includes a VSCode extension (`docgenius-vscode`) that integrates CodeDocGen directly into your editor.
To install:
1. Download `docgenius-1.2.1.vsix`
2. Run `code --install-extension docgenius-1.2.1.vsix` or install from VSIX in VSCode.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request