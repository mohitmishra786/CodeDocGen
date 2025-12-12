# Change Log

All notable changes to the "docgenius" extension will be documented in this file.

## [1.2.1] - 2025-12-13

### Added
- Initial release of DocGenius VSCode extension
- Support for Python, C/C++, Java, and JavaScript/TypeScript
- AI-powered documentation generation with multiple providers:
  - NLTK (local, no API key)
  - Groq
  - OpenAI
  - Azure OpenAI
- Azure OpenAI authentication methods:
  - Azure CLI (az login)
  - API Key
  - Managed Identity
- Diff preview before applying changes
- Keyboard shortcuts for quick generation
- Context menu integration
- Status bar showing current AI provider
- Configuration UI for AI provider setup
- Auto-generate on save option
- Configurable Python and clang paths
- Caching support for improved performance
- Multi-worker parallel processing

### Features
- Generate documentation for current file
- Generate documentation for selection
- Generate documentation for entire workspace
- Configure AI provider through command palette
- Show status and configuration

### Settings
- Comprehensive configuration options for all AI providers
- Customizable paths for Python and libclang
- Performance tuning options
- Preview and auto-save options

## [Unreleased]

### Planned
- Code lens showing "Add Documentation" above functions
- Hover provider for documentation preview
- Quick fix actions for missing documentation
- Inline diff view
- Real-time token usage tracking
- Go and Rust language support
- Enhanced TypeScript support with TSDoc
- Documentation coverage metrics

