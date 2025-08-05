# CodeDocGen Package Distribution Guide

This guide covers how to distribute CodeDocGen to various package managers and repositories.

## Python Package Distribution (PyPI)

### Prerequisites
1. Create accounts on PyPI and TestPyPI:
   - **TestPyPI**: https://test.pypi.org/account/register/
   - **PyPI**: https://pypi.org/account/register/

2. Create API tokens:
   - Go to Account Settings → API tokens
   - Create a token with upload permissions
   - Save the token securely

### Upload to TestPyPI (Recommended First Step)
```bash
# Test the upload on TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ code-doc-gen
```

### Upload to PyPI
```bash
# Upload to production PyPI
twine upload dist/*

# Install from PyPI
pip install code-doc-gen
```

### Automated Upload with GitHub Actions
Create `.github/workflows/publish.yml`:
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## C++ Package Distribution

### 1. vcpkg (Microsoft's C++ Package Manager)

#### Prerequisites
- Install vcpkg: https://github.com/microsoft/vcpkg

#### Add to vcpkg Registry
1. Fork the vcpkg repository
2. Add your package to `ports/codedocgen/`
3. Create a pull request

#### Local Installation
```bash
# Install locally
vcpkg install codedocgen

# Use in CMake project
find_package(codedocgen CONFIG REQUIRED)
target_link_libraries(your_target PRIVATE CodeDocGen::codedocgen_cpp)
```

### 2. Conan Package Manager

#### Prerequisites
- Install Conan: `pip install conan`

#### Create and Upload Package
```bash
# Create package
conan create . codedocgen/1.0.0

# Upload to Conan Center (requires approval)
conan upload codedocgen/1.0.0 --all -r=conancenter

# Or upload to your own remote
conan remote add my-remote https://your-conan-server.com
conan upload codedocgen/1.0.0 --all -r=my-remote
```

#### Use in Project
```bash
# Install package
conan install codedocgen/1.0.0

# Use in CMake
find_package(codedocgen REQUIRED)
target_link_libraries(your_target PRIVATE codedocgen::codedocgen_cpp)
```

### 3. Homebrew (macOS)

#### Create Formula
Create `Formula/codedocgen.rb`:
```ruby
class Codedocgen < Formula
  desc "Automatic documentation generation for C++ codebases"
  homepage "https://github.com/mohitmishra786/CodeDocGen"
  url "https://github.com/mohitmishra786/CodeDocGen/archive/v1.0.0.tar.gz"
  sha256 "YOUR_SHA256_HERE"
  license "MIT"

  depends_on "cmake" => :build
  depends_on "llvm" => :build

  def install
    system "cmake", "-S", ".", "-B", "build", *std_cmake_args
    system "cmake", "--build", "build"
    system "cmake", "--install", "build"
  end

  test do
    system "codedocgen", "--version"
  end
end
```

#### Submit to Homebrew
```bash
# Fork homebrew-core
# Add your formula
# Submit pull request
```

### 4. Chocolatey (Windows)

#### Create Package
Create `codedocgen.nuspec`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd">
  <metadata>
    <id>codedocgen</id>
    <version>1.0.0</version>
    <title>CodeDocGen</title>
    <authors>Mohit Mishra</authors>
    <projectUrl>https://github.com/mohitmishra786/CodeDocGen</projectUrl>
    <licenseUrl>https://github.com/mohitmishra786/CodeDocGen/blob/main/LICENSE</licenseUrl>
    <requireLicenseAcceptance>false</requireLicenseAcceptance>
    <description>Automatic documentation generation for C++ codebases</description>
    <releaseNotes>Initial release with Python and C++ support</releaseNotes>
    <tags>documentation code-generation cpp</tags>
  </metadata>
  <files>
    <file src="tools\**" target="tools" />
  </files>
</package>
```

#### Submit to Chocolatey
```bash
# Create package
choco pack

# Submit to Chocolatey Community Repository
choco push codedocgen.1.0.0.nupkg
```

### 5. Snap (Linux)

#### Create snapcraft.yaml
```yaml
name: codedocgen
version: '1.0.0'
summary: Automatic documentation generation for codebases
description: |
  CodeDocGen is a tool that automatically generates documentation
  for Python and C++ codebases using rule-based analysis.

grade: stable
confinement: strict

parts:
  codedocgen:
    source: .
    plugin: cmake
    build-packages:
      - cmake
      - build-essential
    stage-packages:
      - python3
      - python3-pip

apps:
  codedocgen:
    command: bin/codedocgen
    plugs:
      - home
```

#### Build and Publish
```bash
# Build snap
snapcraft

# Install locally
sudo snap install codedocgen_1.0.0_amd64.snap --dangerous

# Publish to Snap Store
snapcraft upload --release=stable codedocgen_1.0.0_amd64.snap
```

## GitHub Actions for Automated Distribution

Create `.github/workflows/distribute.yml`:
```yaml
name: Distribute Package

on:
  release:
    types: [published]

jobs:
  distribute:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
          - name: PyPI
            command: |
              pip install twine
              twine upload dist/*
          - name: Homebrew
            command: |
              # Update Homebrew formula
          - name: Chocolatey
            command: |
              # Update Chocolatey package
          - name: Snap
            command: |
              # Update Snap package

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Build and distribute
      run: |
        pip install build
        python -m build
        ${{ matrix.command }}
```

## Package Status

| Package Manager | Status | Installation Command |
|----------------|--------|---------------------|
| PyPI | ✅ Released v1.1.6 | `pip install code-doc-gen==1.1.6` |
| vcpkg | Configured | `vcpkg install codedocgen` |
| Conan | Configured | `conan install codedocgen/1.0.0` |
| Homebrew | Pending | `brew install codedocgen` |
| Chocolatey | Pending | `choco install codedocgen` |
| Snap | Pending | `snap install codedocgen` |

## Next Steps

1. **PyPI**: Complete the upload process with your API tokens
2. **vcpkg**: Submit pull request to vcpkg repository
3. **Conan**: Upload to Conan Center or create your own remote
4. **Homebrew**: Submit formula to homebrew-core
5. **Chocolatey**: Submit package to Chocolatey Community Repository
6. **Snap**: Publish to Snap Store

## Maintenance

- Update version numbers in all package files
- Test packages before distribution
- Monitor for issues and feedback
- Keep documentation updated 