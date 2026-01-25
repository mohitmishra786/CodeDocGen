<div align="center">

# CodeDocGen

*"Automatic documentation generation powered by AI."*

Intelligent documentation generator for Python, C++, Java, JavaScript, TypeScript, Go, and Rust.

[![Twitter Follow](https://img.shields.io/twitter/follow/chessMan786?style=social)](https://x.com/chessMan786)
[![Marketplace](https://img.shields.io/badge/Marketplace-DocGenius-blue)](https://marketplace.visualstudio.com/items?itemName=mohitmishra.docgenius)

</div>

---

## Tech Stack

| Category | Tools |
| :--- | :--- |
| **Languages** | Python, C++, Java, JavaScript, TypeScript, Go, Rust |
| **AI Models** | Groq, OpenAI, Anthropic, Mistral, Azure OpenAI |
| **Parsing** | AST (ast, libclang), NLTK, SpaCy |
| **Quality** | Pytest, Black, Flake8, Mypy |
| **IDE** | VSCode (DocGenius Extension) |

---

## Features

- **AI-Powered Comment Generation**: Uses Groq, OpenAI, Anthropic (Claude), Mistral, or Azure OpenAI for intelligent, context-aware documentation.
- **Smart Fallback System**: Falls back to NLTK/SpaCy-based analysis when AI is unavailable or fails.
- **Multi-language Support**: C/C++ (using libclang), Python (using ast), Java (regex/AI), JavaScript (regex/AI), TypeScript (regex/AI), Go (regex/AI), Rust (regex/AI).
- **Smart Function Analysis**: Analyzes function bodies to detect recursion, loops, conditionals, regex usage, API calls, and file operations.
- **Git Integration**: Process only changed files with `--changes-only` flag and auto-commit documentation with `--auto-commit`.
- **Context-Aware Descriptions**: Generates specific, meaningful descriptions instead of generic templates.
- **Flexible Output**: In-place file modification, diff generation, or new file creation.

## Installation

### Prerequisites

- Python 3.8+
- Clang (for C/C++ parsing) - Optional but recommended

### Setup

1. **Activate the virtual environment**:
   ```bash
   source codedocgen/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # Install optional NLP/AI extras
   pip install -e .[ai,nlp]
   ```

3. **Download NLP data**:
   ```python
   # NLTK (Required)
   python -c "import nltk; nltk.download(['punkt', 'averaged_perceptron_tagger', 'wordnet'])"
   
   # SpaCy (Optional - for enhanced analysis)
   python -m spacy download en_core_web_sm
   ```

## Usage

### Command Line Interface

```bash
# Generate documentation (automatically detects language from file extensions)
code_doc_gen --repo /path/to/repo --inplace

# Generate documentation for a C++ repository
code_doc_gen --repo /path/to/cpp/repo --lang c++ --inplace

# Enable AI-powered documentation generation
code_doc_gen --repo /path/to/repo --enable-ai --ai-provider anthropic --inplace

# Process only changed files in a Git repository
code_doc_gen --repo /path/to/repo --changes-only --inplace
```

### Library Usage

```python
from code_doc_gen import generate_docs

# Generate documentation (automatically detects language)
results = generate_docs('/path/to/repo', inplace=True)
```

## VSCode Extension

DocGenius is available on the VSCode Marketplace. It integrates CodeDocGen directly into your editor for a seamless documentation experience.

[Install DocGenius from Marketplace](https://marketplace.visualstudio.com/items?itemName=mohitmishra.docgenius)

---

MIT License
