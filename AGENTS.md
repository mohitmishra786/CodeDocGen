# Agent Guidelines for CodeDocGen

Welcome! This document provides essential information for agentic coding agents working on the CodeDocGen repository. It outlines project conventions, tooling, and workflows to ensure high-quality contributions.

## Project Overview
CodeDocGen is an AI-powered documentation generator for Python, C++, Java, JavaScript, TypeScript, Go, and Rust. It uses AST analysis (libclang for C++, `ast` for Python) and NLTK for intelligent fallback analysis. The goal is to produce Doxygen-style documentation automatically.

## Development Environment
- **Language**: Python 3.8+ (Primary), C++17 (Secondary)
- **Main Tooling**: `pytest`, `black`, `flake8`, `mypy`, `libclang`

### Essential Commands

#### Setup & Installation
- **Install Dependencies**: `pip install -r requirements.txt`
- **Install with Dev Tools**: `pip install -e .[dev,all]`
- **Download NLP Data**:
  ```bash
  python -c "import nltk; nltk.download(['punkt', 'averaged_perceptron_tagger', 'wordnet'])"
  python -m spacy download en_core_web_sm
  ```

#### Testing
- **Run All Tests**: `python -m pytest tests/ -v`
- **Run Single Test File**: `python -m pytest tests/test_generator.py -v`
- **Run Specific Test Case**: `python -m pytest tests/test_generator.py -k "test_generate_python" -v`
- **Run with Coverage**: `python -m pytest tests/ --cov=code_doc_gen --cov-report=term-missing`

#### Code Quality
- **Format Code**: `black .`
- **Lint Code**: `flake8 .`
- **Type Checking**: `mypy code_doc_gen`
- **Build C++ Components**: `mkdir -p build && cd build && cmake .. && make`

## Code Style & Conventions

### Python Style Guidelines
- **Formatting**: Strictly follow `black` (88 characters, double quotes).
- **Imports**: Group in the following order, separated by a blank line:
  1. Standard library imports (e.g., `os`, `sys`, `pathlib`)
  2. Third-party library imports (e.g., `nltk`, `yaml`, `clang`, `groq`)
  3. Local module imports (e.g., `from .models import Function`)
- **Naming Conventions**:
  - **Classes**: `PascalCase` (e.g., `PythonParser`)
  - **Functions/Variables**: `snake_case` (e.g., `extract_functions`)
  - **Constants**: `UPPER_CASE` (e.g., `MAX_RETRY_COUNT`)
  - **Private Members**: Prefix with underscore (e.g., `_analyze_body`)
- **Typing**: Mandatory type hints for all public functions, methods, and complex variables. Use `typing` module for generics.
- **Docstrings**: PEP 257 compliant triple-double quotes. Use Google style for arguments:
  ```python
  def process_file(file_path: Path) -> bool:
      """
      Brief description of the function.

      Args:
          file_path: Path to the source file to process.

      Returns:
          True if processing succeeded, False otherwise.
      """
  ```
- **Path Handling**: ALWAYS use `pathlib.Path` instead of `os.path` for filesystem operations.

### Error Handling & Logging
- **Logging**: Use the standard `logging` module. Use `logger.debug()` for execution flow and `logger.error()` for failures.
- **Exceptions**: Prefer specific exception types. Always provide informative error messages that help debug the root cause.
- **Context**: Wrap risky operations (I/O, API calls) in `try...except` blocks with appropriate logging.

## Architectural Patterns

### 1. Parser Implementation
- All language parsers must inherit from `BaseParser` in `code_doc_gen/parsers/base.py`.
- Implement `can_parse(file_path)` and `parse_file(file_path)`.
- Use AST analysis where possible (e.g., `ast` for Python, `libclang` for C++).
- Implement regex-based fallbacks for environments without specialized AST tools.

### 2. AI & Fallback Logic
- AI provider logic is isolated in `code_doc_gen/ai_providers/`.
- The `AIAnalyzer` in `code_doc_gen/ai_analyzer.py` manages the fallback chain.
- Ensure the NLTK analyzer (`code_doc_gen/analyzer.py`) remains functional as the ultimate fallback.

### 3. Data Models
- Use the central models in `code_doc_gen/models.py` (`Function`, `Parameter`, `FunctionBody`) to pass data between components.
- **FunctionBody**: Contains metadata about code complexity, loops, conditionals, and side effects.
- **Function**: Represents a single function/method with its signature and analyzed body.

## Repository Structure
- `code_doc_gen/`: Core package logic.
  - `ai_providers/`: Implementation of different AI models (OpenAI, Groq, etc.).
  - `parsers/`: Language-specific code parsing logic.
  - `config.py`: Configuration management.
  - `generator.py`: Main documentation generation engine.
  - `models.py`: Shared data structures.
  - `git_integration.py`: Logic for processing changed files and auto-commits.
- `tests/`: Unit and integration tests.
- `usage/`: Platform-specific setup and usage guides.
- `docgenius-vscode/`: Source code for the VSCode extension.

## Verification Workflow
Before submitting any changes or completing a task:
1. **Format**: Run `black .` to ensure consistent formatting.
2. **Lint**: Run `flake8 .` and resolve all warnings.
3. **Types**: Run `mypy code_doc_gen` to verify type safety.
4. **Test**: Execute relevant tests and ensure 100% pass rate.
5. **CLI Check**: If CLI flags were changed, verify with:
   `python -m code_doc_gen.main --repo . --diff`

## Security & Secrets
- **Environment Variables**: Use `.env` files for API keys (loaded via `python-dotenv`).
- **Prioritization**: API keys follow the hierarchy: Environment > CLI Arguments > Config File.
- **Safety**: NEVER commit `.env` files or hardcode keys in source code.

## Handling Optional Dependencies
Many components (libclang, groq, spacy) are optional. When working on these:
- Use `try...except ImportError` blocks.
- Check if the dependency is enabled in the configuration before usage.
- Provide clear error messages if a user tries to use a feature without its dependency.

## Common Task: Adding a New AI Provider
1. Create a new file in `code_doc_gen/ai_providers/`.
2. Inherit from `BaseAIProvider`.
3. Implement `generate_documentation()` and `is_available()`.
4. Register the new provider in `AIAnalyzer`.
5. Update `requirements.txt` and `setup.py` if new libraries are needed.

## Common Task: Adding a New Language Parser
1. Create a new file in `code_doc_gen/parsers/`.
2. Inherit from `BaseParser`.
3. Implement `can_parse()` and `parse_file()`.
4. Register the new parser in `RepositoryScanner`.
5. Add unit tests in `tests/` for the new language.

## Git Workflow
- **Changes Only**: Process only modified files with `--changes-only`.
- **Auto-Commit**: Automatically commit generated docs with `--auto-commit`.
- **Pre-commit Hooks**: Ensure all code passes linting before committing.

---
*This file is intended for agentic use. It should be updated whenever new patterns or tools are introduced.*
