## CodeDocGen on Windows — Step-by-step Guide

This guide shows exactly how to install and use CodeDocGen on Windows. Follow each step in order. No prior experience required.

### What you need
- A Windows 10/11 PC with internet
- Python 3.8 or newer
- About 5–10 minutes

### 1) Install Python
1. Go to the official Python website: https://www.python.org/downloads/
2. Download the latest Python 3 release for Windows.
3. Run the installer. Important: check “Add Python to PATH” during installation.

To verify, open PowerShell and run:

```powershell
python --version
```

You should see something like `Python 3.11.x`.

### 2) Create a project folder and open a terminal
1. Make a folder anywhere, for example `C:\Users\You\code-docgen-demo`.
2. Right-click inside the folder → “Open in Terminal” (or open PowerShell and `cd` into the folder).

### 3) Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run PowerShell “as Administrator” and execute this once:
```powershell
Set-ExecutionPolicy RemoteSigned
```
Then try activation again.

### 4) Install CodeDocGen from TestPyPI (latest build)
```powershell
python -m pip install -U pip
pip install -i https://test.pypi.org/simple/ code_doc_gen==1.1.7
```

This installs the `code_doc_gen` CLI and library.

### 5) Install LLVM (libclang) for C/C++ support
CodeDocGen uses libclang to understand C/C++ code.

1. Download LLVM for Windows from: https://github.com/llvm/llvm-project/releases (look for “LLVM-win64.exe”).
2. Install LLVM (default location is `C:\Program Files\LLVM`).

CodeDocGen auto-detects common locations, but you can also set an environment variable to point to the library file explicitly.

- Typical library file: `C:\\Program Files\\LLVM\\bin\\libclang.dll`

Set `LIBCLANG_LIBRARY_FILE` permanently (recommended):
```powershell
setx LIBCLANG_LIBRARY_FILE "C:\\Program Files\\LLVM\\bin\\libclang.dll"
```
Close and reopen your terminal after using `setx`.

Alternatively, create a `.env` file in your project folder:
```
LIBCLANG_LIBRARY_FILE=C:\\Program Files\\LLVM\\bin\\libclang.dll
```

Note: If you only work with Python files, libclang is not required.

### 6) (Optional) AI setup for better comments
CodeDocGen can use AI to generate higher-quality docstrings.

- Get a Groq API key: https://console.groq.com/keys
- (Optional) Get an OpenAI API key: https://platform.openai.com/account/api-keys

Create a `.env` file in your project folder and add:
```
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
```

You can also pass keys via CLI flags, but `.env` is simpler.

### 7) Prepare a test project
Create a folder with some code, for example:
```
demo_repo
├─ math.cpp
└─ utils.py
```

Example `math.cpp`:
```cpp
int add(int a, int b) { return a + b; }
```

Example `utils.py`:
```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

### 8) Run CodeDocGen
Basic run (auto-detect language and write in place):
```powershell
code_doc_gen --repo .\demo_repo --inplace
```

With AI enabled (Groq):
```powershell
code_doc_gen --repo .\demo_repo --enable-ai --ai-provider groq --inplace
```

You can also run via Python directly:
```powershell
python -m code_doc_gen.main --repo .\demo_repo --inplace
```

### 9) Where do the comments go?
- The tool updates your files in place.
- It creates backups with `.bak` suffix the first time it edits a file.

### 10) Troubleshooting
- “libclang not found” or “could not load library”:
  - Make sure LLVM is installed.
  - Verify the file exists: `C:\\Program Files\\LLVM\\bin\\libclang.dll`.
  - Set `LIBCLANG_LIBRARY_FILE` to that exact path and reopen your terminal.

- “symbol not found” or ABI mismatch errors:
  - Ensure Python bindings and the system libclang are compatible.
  - If needed, install matching Python bindings: `pip install "clang==18.1.8"`.

- AI errors (401/403):
  - Check `GROQ_API_KEY` is correct in `.env`.
  - Try a simple request again later.

### 11) Upgrading / Uninstalling
- Upgrade:
```powershell
pip install -U -i https://test.pypi.org/simple/ code_doc_gen==1.1.7
```

- Uninstall:
```powershell
pip uninstall code_doc_gen
```

That’s it! You’re ready to generate documentation on Windows.

