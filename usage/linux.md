## CodeDocGen on Linux — Step-by-step Guide

This guide helps you install and use CodeDocGen on Ubuntu/Debian/Fedora/Arch-like systems.

### What you need
- Linux with Python 3.8+
- Terminal access

### 1) Install Python and pip
Your distro likely has Python 3 already:

```bash
python3 --version
```

If missing, install via your package manager (e.g., `sudo apt install python3 python3-venv python3-pip`).

### 2) Create a project folder
```bash
mkdir -p ~/code-docgen-demo
cd ~/code-docgen-demo
```

### 3) Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4) Install CodeDocGen from TestPyPI (latest build)
```bash
python -m pip install -U pip
pip install -i https://test.pypi.org/simple/ code_doc_gen==1.1.7
```

### 5) Install libclang for C/C++ support
Install your distro’s LLVM/Clang packages. Examples:

- Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y clang libclang-dev
```

- Fedora:
```bash
sudo dnf install -y clang llvm-devel
```

- Arch:
```bash
sudo pacman -S --needed clang llvm
```

CodeDocGen auto-detects libclang. If detection fails, set an environment variable with the full path to the library file:

```bash
# Common locations vary by distro/version. Examples:
export LIBCLANG_LIBRARY_FILE=/usr/lib/llvm-18/lib/libclang.so    # Ubuntu example
# or
export LIBCLANG_LIBRARY_FILE=/usr/lib/libclang.so                # Fedora/Arch example
```

You can also put this in a `.env` file in your project folder:
```
LIBCLANG_LIBRARY_FILE=/usr/lib/llvm-18/lib/libclang.so
```

Note: libclang is only needed for C/C++ projects. Pure Python projects do not require it.

### 6) (Optional) AI setup for better comments
- Get a Groq API key: https://console.groq.com/keys
- (Optional) OpenAI API key: https://platform.openai.com/account/api-keys

Create a `.env` file in your project folder:
```
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 7) Prepare a test project
```bash
mkdir demo_repo
cat > demo_repo/math.cpp <<'CPP'
int mul(int a, int b) { return a * b; }
CPP

cat > demo_repo/utils.py <<'PY'
def square(x: int) -> int:
    return x * x
PY
```

### 8) Run CodeDocGen
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

### 9) Results
- Files are updated in place; a `.bak` backup is created on first edit.

### 10) Troubleshooting
- libclang not found:
  - Verify `libclang` is installed by your package manager.
  - Use `ldconfig -p | grep libclang` to see available versions/paths.
  - Set `LIBCLANG_LIBRARY_FILE` to the exact `.so` path if needed.

- ABI mismatch / symbol errors:
  - Ensure Python `clang` bindings match your system libclang version. If needed:
    ```bash
    pip install "clang==18.1.8"
    ```

- AI authentication errors:
  - Double-check `GROQ_API_KEY`/`OPENAI_API_KEY` in `.env`.

### 11) Upgrade / Uninstall
```bash
pip install -U -i https://test.pypi.org/simple/ code_doc_gen==1.1.7
pip uninstall code_doc_gen
```

You’re ready to generate documentation on Linux!

