## CodeDocGen on macOS — Step-by-step Guide

This guide makes it easy to install and use CodeDocGen on macOS (Intel or Apple Silicon).

### What you need
- macOS 12+ recommended
- Python 3.8+
- Terminal app

### 1) Install Python
On macOS, you can install Python via python.org or Homebrew.

Option A: python.org installer (simple)
1. Visit https://www.python.org/downloads/
2. Download the latest Python 3 macOS installer and run it.

Option B: Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
```

Verify:
```bash
python3 --version
```

### 2) Create a project folder and virtual environment
```bash
mkdir -p ~/code-docgen-demo
cd ~/code-docgen-demo
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
```

### 3) Install CodeDocGen from TestPyPI (latest build)
```bash
pip install -i https://test.pypi.org/simple/ code_doc_gen==1.1.7
```

### 4) Install libclang for C/C++ support
CodeDocGen uses libclang to parse C/C++ code. There are two easy setups:

Option A: Xcode Command Line Tools (recommended, simple)
```bash
xcode-select --install   # if not already installed
```
Then install Python bindings compatible with CLT 18.x:
```bash
pip install 'clang==18.1.8'
```
Auto-detection usually finds `/Library/Developer/CommandLineTools/usr/lib/libclang.dylib` with no extra setup.

Option B: Homebrew LLVM (latest toolchain)
```bash
brew install llvm
```
Then create a `.env` file in your project folder to point to the library file explicitly:
```
# Apple Silicon (most common on M1/M2/M3)
LIBCLANG_LIBRARY_FILE=/opt/homebrew/opt/llvm/lib/libclang.dylib

# Intel Macs (older)
# LIBCLANG_LIBRARY_FILE=/usr/local/opt/llvm/lib/libclang.dylib
```

Note: If you only work with Python files, libclang is not required.

### 5) (Optional) AI setup for better comments
- Get a Groq API key: https://console.groq.com/keys
- (Optional) OpenAI API key: https://platform.openai.com/account/api-keys

Create a `.env` file in your project folder:
```
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 6) Prepare a test project
```bash
mkdir demo_repo
cat > demo_repo/geometry.cpp <<'CPP'
int add(int a, int b) { return a + b; }
CPP

cat > demo_repo/analysis.py <<'PY'
def greet(name: str) -> str:
    return f"Hello, {name}!"
PY
```

### 7) Run CodeDocGen
Basic run (auto-detect language and write in place):
```bash
code_doc_gen --repo ./demo_repo --inplace
```

With AI enabled (Groq):
```bash
code_doc_gen --repo ./demo_repo --enable-ai --ai-provider groq --inplace
```

Or via Python module:
```bash
python -m code_doc_gen.main --repo ./demo_repo --inplace
```

### 8) Results
- Files are updated in place; `.bak` backup files are created on first edit.

### 9) Troubleshooting
- libclang not found:
  - Xcode CLT: make sure CLT is installed and try `pip install 'clang==18.1.8'`.
  - Homebrew: confirm the path in `.env` matches your system.

- ABI mismatch / dlsym symbol not found:
  - Install Python bindings matching CLT: `pip install 'clang==18.1.8'`.
  - Re-run and confirm `clang.cindex.Index.create()` works (the tool auto-probes this).

- AI errors (401/403):
  - Check `.env` has `GROQ_API_KEY` and you restarted the terminal in the venv.

### 10) Upgrade / Uninstall
```bash
pip install -U -i https://test.pypi.org/simple/ code_doc_gen==1.1.7
pip uninstall code_doc_gen
```

You’re all set to generate documentation on macOS!

