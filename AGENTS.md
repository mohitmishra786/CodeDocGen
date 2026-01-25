# Agent Guidelines for CodeDocGen

Welcome! This document provides essential information for agentic coding agents working on the CodeDocGen repository.

## Project Overview
CodeDocGen is an AI-powered documentation generator for Python, C++, Java, and JavaScript. It uses AST analysis (libclang for C++, `ast` for Python) and NLTK for intelligent fallback analysis.

## Development Environment
- **Language**: Python 3.8+ (Primary), C++17 (Secondary)
- **Main Tooling**: `pytest`, `black`, `flake8`, `mypy`, `libclang`

### Essential Commands
- **Install Dependencies**: `pip install -r requirements.txt`
- **Install in Dev Mode**: `pip install -e .[dev,all]`
- **Run All Tests**: `python -m pytest tests/ -v`
- **Run Single Test**: `python -m pytest tests/test_generator.py -v`
- **Run with Coverage**: `python -m pytest tests/ --cov=code_doc_gen`
- **Format Code**: `black .`
- **Lint Code**: `flake8 .`
- **Type Checking**: `mypy code_doc_gen`
- **Build C++ components**: `mkdir build && cd build && cmake .. && make`

## Code Style & Conventions

### Python Style
- **Formatting**: Strictly follow `black` (88 characters, double quotes).
- **Imports**: Group in the following order:
    1. Standard library imports
    2. Third-party library imports (e.g., `nltk`, `yaml`, `clang`)
    3. Local module imports (relative or absolute)
- **Naming**:
    - Classes: `PascalCase`
    - Functions/Variables: `snake_case`
    - Constants: `UPPER_CASE`
- **Typing**: Use type hints for all public functions and methods. Import complex types from `typing`.
- **Docstrings**: Use PEP 257 compliant triple-double quotes. Include `Args:`, `Returns:`, and `Raises:` sections.
- **Path Handling**: Always use `pathlib.Path` instead of `os.path`.

### Error Handling & Logging
- Use the standard `logging` module.
- Root logger is configured in `code_doc_gen/main.py`.
- Prefer `try...except` blocks with informative error messages and logging.
- Use `logger.debug()` for detailed execution flow and `logger.error()` for failures.

### Repository Structure
- `code_doc_gen/`: Main package.
    - `parsers/`: Language-specific parsers.
    - `main.py`: CLI entry point.
    - `models.py`: Data models (Function, Parameter, etc.).
    - `scanner.py`: Repository and file scanning logic.
    - `generator.py`: Documentation generation and file modification.
    - `ai_analyzer.py`: Integration with AI providers (Groq, OpenAI).
    - `analyzer.py`: NLTK-based intelligent analysis.
- `tests/`: Extensive test suite.
- `usage/`: OS-specific setup guides.

## Feature Implementation Guidelines

### 1. New Language Support
- Inherit from `BaseParser` in `code_doc_gen/parsers/`.
- Implement `can_parse()` (file extension check) and `parse_file()`.
- Add the new parser to `RepositoryScanner.get_supported_languages()`.
- Ensure regex fallback is implemented for environments where AST tools are missing.

### 2. AI Analysis & Fallback
- Logic resides in `code_doc_gen/ai_analyzer.py`.
- All AI calls must handle timeouts and retries using the configured settings.
- Ensure fallback to NLTK analysis in `code_doc_gen/analyzer.py` is always maintained as a safety net.

### 3. AST Analysis
- Use `ast` module for Python.
- Use `libclang` for C++. Note that `libclang` resolution is complex; check `CppParser._configure_libclang()` for details.
- Always provide source code context to the AI for better analysis.

## Testing Conventions
- **New Features**: Must include unit tests in `tests/`.
- **Mocking**: Mock all network calls and AI responses in tests using `unittest.mock` or `pytest-mock`.
- **Regression**: Ensure `pytest` passes 100% before any PR.

## Verification Workflow
Before submitting any changes:
1. Run `black .` to ensure formatting.
2. Run `flake8 .` and `mypy code_doc_gen` to check for linting/type errors.
3. Execute relevant tests using `pytest`.
4. If modifying CLI, verify with `python -m code_doc_gen.main --repo . --diff`.

## Security
- NEVER hardcode API keys. Use environment variables (loaded via `python-dotenv`).
- API keys are prioritized: Environment > CLI Args > Config File.
- Ensure `.env` is never committed (checked by `.gitignore`).

## Git Integration
- Process changed files only: `--changes-only`.
- Auto-commit functionality: `--auto-commit` (implemented in `git_integration.py`).
- Always verify the Git state before performing auto-commits.

---
*This file is intended for agentic use. Keep it updated with new tools or architectural changes.*
