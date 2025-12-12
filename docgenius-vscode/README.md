# DocGenius - VSCode Extension

Intelligent automatic documentation generation for multiple programming languages using AI and AST analysis.

## Features

- Generate documentation for Python, C/C++, Java, and JavaScript/TypeScript
- AI-powered comment generation with multiple providers (Groq, OpenAI, Azure OpenAI)
- NLTK-based local analysis (no API key required)
- Support for Azure CLI authentication (az login)
- Diff preview before applying changes
- Keyboard shortcuts for quick generation
- Status bar integration showing current AI provider

## Supported Languages

- Python (.py) - PEP 257 docstrings
- C/C++ (.c, .cpp, .h, .hpp) - Doxygen-style comments
- Java (.java) - Javadoc-style comments
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx) - JSDoc-style comments

## Installation

1. Install from VSCode Marketplace
2. Install the Python CLI tool:
   ```bash
   pip install code-doc-gen
   ```

## Usage

### Commands

- **DocGenius: Generate Documentation for Current File** - Generate docs for the active file
- **DocGenius: Generate Documentation for Selection** - Generate docs for selected functions
- **DocGenius: Generate Documentation for Workspace** - Generate docs for entire workspace
- **DocGenius: Configure AI Provider** - Set up your AI provider
- **DocGenius: Show Status** - Display current configuration

### Keyboard Shortcuts

- `Ctrl+Alt+D` (Mac: `Cmd+Alt+D`) - Generate documentation for current file
- `Ctrl+Alt+S` (Mac: `Cmd+Alt+S`) - Generate documentation for selection

### Context Menu

Right-click in the editor to access DocGenius commands.

## Configuration

### AI Providers

**NLTK (Default)**
- Local analysis, no API key required
- Good for basic documentation
- Works offline

**Groq**
- Fast and efficient
- Requires API key from https://console.groq.com/keys

**OpenAI**
- High quality documentation
- Requires API key from https://platform.openai.com/account/api-keys

**Azure OpenAI**
- Enterprise-grade AI
- Multiple authentication methods:
  - Azure CLI (az login) - Recommended for developers
  - API Key
  - Managed Identity - For production deployments

### Settings

- `docgenius.ai.enabled` - Enable AI-powered documentation
- `docgenius.ai.provider` - AI provider (nltk, groq, openai, azure_openai)
- `docgenius.azure.authMethod` - Azure authentication method
- `docgenius.azure.endpoint` - Azure OpenAI endpoint
- `docgenius.azure.deploymentName` - Azure deployment name
- `docgenius.autoGenerateOnSave` - Auto-generate on file save
- `docgenius.showPreviewBeforeApplying` - Show diff before applying
- `docgenius.pythonPath` - Path to Python interpreter
- `docgenius.clangPath` - Path to libclang library
- `docgenius.maxWorkers` - Number of worker threads
- `docgenius.enableCache` - Enable caching for performance

## Azure OpenAI Setup

1. Open Command Palette (Ctrl+Shift+P)
2. Run "DocGenius: Configure AI Provider"
3. Select "Azure OpenAI"
4. Choose authentication method:
   - **Azure CLI**: Run `az login` in terminal first
   - **API Key**: Enter your endpoint and API key
   - **Managed Identity**: For Azure-hosted deployments

## Examples

### Python Documentation

```python
def add(a: int, b: int) -> int:
    return a + b
```

After running DocGenius:

```python
def add(a: int, b: int) -> int:
    """
    Adds two integers and returns their sum.
    
    Parameters:
        a: The first integer to add.
        b: The second integer to add.
    
    Returns:
        The sum of a and b.
    """
    return a + b
```

### C++ Documentation

```cpp
int multiply(int x, int y) {
    return x * y;
}
```

After running DocGenius:

```cpp
/**
 * \brief Multiplies two integers and returns the product.
 * 
 * \param x The first integer to multiply.
 * \param y The second integer to multiply.
 * \return The product of x and y.
 */
int multiply(int x, int y) {
    return x * y;
}
```

## Requirements

- VSCode 1.80.0 or higher
- Python 3.8 or higher
- code-doc-gen Python package

## Known Issues

- Large files may take longer to process
- libclang required for optimal C++ parsing

## Release Notes

### 1.2.1

- Initial release
- Support for Python, C/C++, Java, JavaScript/TypeScript
- Multiple AI provider support
- Azure OpenAI integration with multiple auth methods
- Diff preview functionality
- Status bar integration

## Contributing

Contributions are welcome! Please visit our [GitHub repository](https://github.com/mohitmishra786/CodeDocGen).

## License

MIT License - see [LICENSE](https://github.com/mohitmishra786/CodeDocGen/blob/main/LICENSE)

## Support

- Report issues: https://github.com/mohitmishra786/CodeDocGen/issues
- Documentation: https://github.com/mohitmishra786/CodeDocGen#readme

