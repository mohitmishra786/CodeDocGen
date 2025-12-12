#!/bin/bash

# Script to create GitHub issues for CodeDocGen enhancements
# This will create issues systematically based on the enhancement plan

echo "Creating GitHub issues for CodeDocGen enhancements..."

# Issue 1: Azure OpenAI Integration
gh issue create \
  --title "Add Azure OpenAI Integration with Multiple Authentication Methods" \
  --label "enhancement,ai-provider,high-priority" \
  --body "## Overview
Integrate Azure OpenAI as a third AI provider alongside Groq and OpenAI, with support for multiple authentication methods.

## Requirements
- [ ] Add azure-openai package dependency
- [ ] Create AzureOpenAIProvider class in ai_analyzer.py
- [ ] Support API key authentication
- [ ] Support Azure CLI authentication (az login)
- [ ] Support Managed Identity authentication
- [ ] Implement credential chain: API Key → Azure CLI → Managed Identity
- [ ] Add configuration schema for Azure endpoints and deployments
- [ ] Support multiple deployment models per Azure subscription
- [ ] Add region detection and failover
- [ ] Integration with Azure Monitor for usage tracking
- [ ] Support for Azure Private Link endpoints
- [ ] Content filtering integration

## Configuration Example
\`\`\`yaml
ai:
  provider: \"azure_openai\"
  azure_openai:
    endpoint: \"https://your-resource.openai.azure.com/\"
    deployment_name: \"gpt-4\"
    api_version: \"2024-02-15-preview\"
    auth_method: \"azure_cli\"  # or \"api_key\" or \"managed_identity\"
\`\`\`

## CLI Usage Example
\`\`\`bash
# Using Azure CLI auth
code_doc_gen --repo /path/to/repo --enable-ai --ai-provider azure_openai --inplace

# Using API key
code_doc_gen --repo /path/to/repo --enable-ai --ai-provider azure_openai --azure-api-key YOUR_KEY --inplace
\`\`\`

## Dependencies
- azure-identity>=1.15.0
- azure-openai>=1.0.0

## Testing
- Unit tests for each auth method
- Integration tests with Azure OpenAI
- Error handling tests
- Fallback mechanism tests

## Documentation
- Update README.md with Azure setup instructions
- Add Azure authentication guide
- Update configuration documentation

## Estimated Effort
2-3 weeks

## Related
See ENHANCEMENT_PLAN.md Section 1"

# Issue 2: VSCode Extension
gh issue create \
  --title "Create VSCode Extension - DocGenius" \
  --label "enhancement,vscode-extension,high-priority" \
  --body "## Overview
Create a VSCode extension named \"DocGenius\" that provides seamless documentation generation directly within the IDE.

## Core Features
- [ ] Command palette integration for doc generation
- [ ] Hover provider showing documentation preview
- [ ] Code actions (Quick Fix) for missing documentation
- [ ] CodeLens showing \"Add Documentation\" above functions
- [ ] Inline diff view before applying changes
- [ ] Status bar integration with provider status
- [ ] Settings panel for AI provider configuration
- [ ] Token usage tracking
- [ ] Progress indicator during generation
- [ ] Multi-file workspace processing

## Commands
- \`DocGenius: Generate Documentation for Current File\`
- \`DocGenius: Generate Documentation for Selection\`
- \`DocGenius: Generate Documentation for Workspace\`
- \`DocGenius: Configure AI Provider\`
- \`DocGenius: Regenerate with Different Provider\`

## Technical Requirements
- TypeScript 5.0+
- Python bridge to CLI tool
- Support for all languages (C++, Python, Java, JavaScript/TypeScript)
- Configuration sync with CLI tool
- Error handling and user feedback

## Extension Structure
\`\`\`
docgenius-vscode/
├── package.json
├── src/
│   ├── extension.ts
│   ├── commands/
│   ├── providers/
│   ├── ui/
│   └── python/
└── media/
    └── docgenius.png (icon provided)
\`\`\`

## Configuration Schema
\`\`\`json
{
  \"docgenius.ai.provider\": \"azure_openai\",
  \"docgenius.azure.authMethod\": \"azureCli\",
  \"docgenius.autoGenerateOnSave\": false
}
\`\`\`

## Testing
- Unit tests for TypeScript code
- Integration tests with Python CLI
- E2E tests with VSCode API
- Manual testing on Windows/Linux/macOS

## Documentation
- README for extension marketplace
- Video walkthrough
- GIF demos for features
- Troubleshooting guide

## Publishing
- VSCode Marketplace
- Open VSX Registry
- Automated CI/CD for updates

## Estimated Effort
6-8 weeks

## Related
See ENHANCEMENT_PLAN.md Section 2"

# Issue 3: Configurable Parser Paths
gh issue create \
  --title "Add Configurable Parser Paths (Clang, Java, etc.)" \
  --label "enhancement,configuration,medium-priority" \
  --body "## Overview
Allow users to configure custom paths for language parsers (libclang, JavaParser, etc.) instead of relying solely on auto-detection.

## Requirements

### Clang/LLVM Configuration
- [ ] Add \`--clang-path\` CLI argument
- [ ] Add \`cpp.clang.library_path\` config option
- [ ] Add \`cpp.clang.library_file\` config option
- [ ] Support for multiple clang versions
- [ ] Automatic version detection and compatibility checking
- [ ] Better error messages when clang not found
- [ ] Fallback to regex parser when clang unavailable

### Java Parser Configuration
- [ ] Optional path to custom JavaParser installation
- [ ] Support for different Java versions
- [ ] JDK path configuration
- [ ] Fallback to regex parser

## Configuration Example
\`\`\`yaml
cpp:
  clang:
    library_path: \"/usr/local/opt/llvm/lib\"
    library_file: \"/usr/local/opt/llvm/lib/libclang.dylib\"
    version_preference: [\"14\", \"13\", \"12\"]
    fallback_to_regex: true

java:
  parser:
    jdk_path: \"/usr/lib/jvm/java-17-openjdk\"
    fallback_to_regex: true
\`\`\`

## CLI Usage
\`\`\`bash
code_doc_gen --repo /path/to/repo --lang c++ --clang-path /custom/path/to/libclang --inplace
\`\`\`

## Testing
- Test with various clang versions
- Test with custom paths
- Test fallback mechanisms
- Cross-platform testing

## Documentation
- Update installation guides
- Add troubleshooting section for parser issues
- Platform-specific instructions

## Estimated Effort
1-2 weeks

## Related
See ENHANCEMENT_PLAN.md Section 3"

# Issue 4: Enhanced TypeScript Support
gh issue create \
  --title "First-Class TypeScript Support with TSDoc Generation" \
  --label "enhancement,language-support,medium-priority" \
  --body "## Overview
Upgrade TypeScript support from regex-based parsing to first-class support with dedicated parser and TSDoc format.

## Requirements
- [ ] Dedicated TypeScript parser (separate from JavaScript)
- [ ] Support for TypeScript-specific syntax:
  - Decorators
  - Generics
  - Interfaces
  - Type aliases
  - Enums
  - Abstract classes
  - Access modifiers
- [ ] TSDoc format documentation generation
- [ ] Integration with TypeScript compiler API
- [ ] Type information in documentation
- [ ] Support for .ts, .tsx, .d.ts files

## TSDoc Format Example
\`\`\`typescript
/**
 * Calculates the sum of two numbers
 * 
 * @param x - The first number
 * @param y - The second number
 * @returns The sum of x and y
 * @throws {Error} If inputs are not valid numbers
 */
function add(x: number, y: number): number {
  return x + y;
}
\`\`\`

## Technical Implementation
- Use TypeScript Compiler API (ts.createSourceFile)
- Parse AST for all TypeScript constructs
- Generate TSDoc-compliant comments
- Preserve type annotations in documentation

## Testing
- Unit tests for TypeScript parser
- Test all TypeScript language features
- Compare with existing JavaScript parser
- Integration tests with real TypeScript projects

## Documentation
- Add TypeScript examples to README
- TypeScript-specific configuration guide
- TSDoc format documentation

## Estimated Effort
3-4 weeks

## Related
See ENHANCEMENT_PLAN.md Section 4.1"

# Issue 5: Additional Language Support (Go, Rust)
gh issue create \
  --title "Add Support for Go and Rust Languages" \
  --label "enhancement,language-support,medium-priority" \
  --body "## Overview
Extend CodeDocGen to support Go and Rust languages with native parsers and language-specific documentation formats.

## Go Support
- [ ] Create go_parser.py using go/ast
- [ ] Support for functions, methods, structs, interfaces
- [ ] GoDoc format documentation
- [ ] Package-level documentation
- [ ] Example tests documentation

### Go Example
\`\`\`go
// Add calculates the sum of two integers.
//
// Parameters:
//   - a: The first integer
//   - b: The second integer
//
// Returns:
//   - The sum of a and b
func Add(a, b int) int {
    return a + b
}
\`\`\`

## Rust Support
- [ ] Create rust_parser.py using syn crate or tree-sitter
- [ ] Support for functions, methods, traits, structs, enums
- [ ] RustDoc format documentation
- [ ] Lifetime annotations handling
- [ ] Macro documentation support

### Rust Example
\`\`\`rust
/// Calculates the sum of two integers.
///
/// # Arguments
///
/// * \`a\` - The first integer
/// * \`b\` - The second integer
///
/// # Returns
///
/// The sum of a and b
///
/// # Examples
///
/// \`\`\`
/// let result = add(2, 3);
/// assert_eq!(result, 5);
/// \`\`\`
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
\`\`\`

## Technical Requirements
- Go: Use subprocess to call go/ast tools
- Rust: Use tree-sitter-rust or call rust-analyzer
- File extension detection
- Language-specific templates

## Testing
- Parser unit tests for both languages
- Integration tests with real projects
- AI generation tests
- Template formatting tests

## Documentation
- Update README with Go and Rust examples
- Installation instructions for Go/Rust tools
- Best practices for each language

## Estimated Effort
4-5 weeks (2-2.5 weeks per language)

## Related
See ENHANCEMENT_PLAN.md Section 4.2"

# Issue 6: Performance Optimizations
gh issue create \
  --title "Implement Performance Optimizations for Large Codebases" \
  --label "enhancement,performance,medium-priority" \
  --body "## Overview
Optimize CodeDocGen performance for large codebases through parallel processing, caching, and resource management.

## Requirements

### Parallel Processing
- [ ] Multi-threaded file processing
- [ ] Async AI API calls
- [ ] Worker pool for parser operations
- [ ] Progress tracking with cancellation support
- [ ] Add \`--max-workers\` CLI option
- [ ] Smart batching of AI requests
- [ ] Thread-safe logging

### Caching System
- [ ] Cache AI responses for identical functions
- [ ] Cache parsed ASTs
- [ ] Incremental processing (only changed functions)
- [ ] Cache invalidation strategies
- [ ] Configurable cache directory
- [ ] Cache cleanup and maintenance
- [ ] Cache statistics

### Cache Structure
\`\`\`
.docgen_cache/
├── ai_responses/
│   └── {function_hash}.json
├── parsed_asts/
│   └── {file_hash}.pkl
└── metadata.json
\`\`\`

### Resource Management
- [ ] Memory usage optimization
- [ ] Streaming processing for huge files
- [ ] Smart pagination of AI requests
- [ ] Configurable batch sizes
- [ ] Memory profiling tools
- [ ] Resource limits configuration

## Configuration
\`\`\`yaml
performance:
  max_workers: 4
  cache_enabled: true
  cache_dir: \".docgen_cache\"
  cache_ttl: 2592000  # 30 days
  max_memory_mb: 2048
  batch_size: 10
\`\`\`

## CLI Options
\`\`\`bash
code_doc_gen --repo /path/to/repo --max-workers 8 --enable-cache --cache-dir /tmp/cache --inplace
\`\`\`

## Benchmarking
- [ ] Create performance benchmarking suite
- [ ] Test with various codebase sizes (100, 1K, 10K, 100K files)
- [ ] Measure improvement over baseline
- [ ] Memory usage profiling
- [ ] Compare single-threaded vs multi-threaded

## Performance Targets
- 10x improvement for large codebases (10K+ files)
- 50% reduction in AI API calls through caching
- < 100MB memory overhead for caching
- Linear scaling with worker count up to 8 workers

## Testing
- Unit tests for caching logic
- Integration tests for parallel processing
- Performance regression tests
- Load testing

## Documentation
- Performance tuning guide
- Caching configuration guide
- Best practices for large codebases

## Estimated Effort
4-5 weeks

## Related
See ENHANCEMENT_PLAN.md Section 6"

# Issue 7: GitHub Actions Workflow Templates
gh issue create \
  --title "Create GitHub Actions Workflow Templates for CI/CD Integration" \
  --label "enhancement,ci-cd,low-priority" \
  --body "## Overview
Provide ready-to-use GitHub Actions workflow templates for automated documentation generation in CI/CD pipelines.

## Requirements
- [ ] Create workflow template for PR documentation
- [ ] Create workflow template for commit documentation
- [ ] Create workflow template for release documentation
- [ ] Support for all AI providers
- [ ] Automatic commit of generated docs
- [ ] Documentation coverage reports
- [ ] Diff generation and PR comments
- [ ] Support for monorepos

## Workflow Templates

### PR Documentation Check
\`\`\`yaml
name: Documentation Check
on: [pull_request]
jobs:
  doc-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docgenius/setup-docgen@v1
      - name: Generate Documentation
        run: code_doc_gen --repo . --enable-ai --ai-provider azure_openai --diff
      - name: Post Results
        uses: docgenius/post-results@v1
\`\`\`

### Auto-Generate and Commit
\`\`\`yaml
name: Auto-Generate Documentation
on:
  push:
    branches: [main]
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docgenius/auto-docs@v1
        with:
          ai-provider: azure_openai
          auto-commit: true
\`\`\`

## Custom Actions to Create
- [ ] \`docgenius/setup-docgen\` - Install and configure DocGenius
- [ ] \`docgenius/auto-docs\` - Generate and optionally commit docs
- [ ] \`docgenius/post-results\` - Post diff/report as PR comment
- [ ] \`docgenius/coverage-report\` - Generate coverage report

## Features
- Configurable AI provider
- Secret management for API keys
- Azure authentication via OIDC
- Caching for faster runs
- Matrix builds for multiple languages
- Artifact upload for reports

## Documentation
- README for each action
- Usage examples
- Configuration reference
- Troubleshooting guide

## Additional CI/CD Platforms
- [ ] GitLab CI template
- [ ] Azure DevOps pipeline template
- [ ] CircleCI config example
- [ ] Jenkins pipeline example

## Testing
- Test workflows in real repositories
- Verify secret handling
- Test matrix builds
- Verify artifact uploads

## Estimated Effort
2-3 weeks

## Related
See ENHANCEMENT_PLAN.md Section 7.2"

# Issue 8: Documentation Coverage Metrics
gh issue create \
  --title "Implement Documentation Coverage Metrics and Reporting" \
  --label "enhancement,metrics,low-priority" \
  --body "## Overview
Add comprehensive metrics tracking and reporting for documentation coverage, quality, and AI usage.

## Requirements

### Coverage Metrics
- [ ] Calculate percentage of documented functions
- [ ] Track documentation coverage per file
- [ ] Track coverage per language
- [ ] Track coverage per module/package
- [ ] Identify undocumented functions
- [ ] Generate coverage reports

### Quality Metrics
- [ ] Documentation completeness score
- [ ] Documentation length/detail score
- [ ] Parameter documentation coverage
- [ ] Return type documentation coverage
- [ ] Exception documentation coverage
- [ ] Documentation freshness (last updated)

### AI Usage Metrics
- [ ] Track AI provider usage
- [ ] Track API call counts
- [ ] Estimate cost per provider
- [ ] Track success/failure rates
- [ ] Track response times
- [ ] Token usage tracking

### Report Formats
- [ ] JSON report
- [ ] HTML report with visualizations
- [ ] Markdown report
- [ ] Badge generation for README
- [ ] Console summary output

## CLI Commands
\`\`\`bash
# Generate coverage report
code_doc_gen --repo /path/to/repo --coverage-report --output coverage.json

# Generate HTML report
code_doc_gen --repo /path/to/repo --coverage-report --format html --output report.html

# Show coverage summary
code_doc_gen --repo /path/to/repo --coverage-summary
\`\`\`

## Report Structure
\`\`\`json
{
  \"overall_coverage\": 85.5,
  \"total_functions\": 1234,
  \"documented_functions\": 1055,
  \"undocumented_functions\": 179,
  \"by_language\": {
    \"python\": {\"coverage\": 90.5, \"functions\": 800},
    \"cpp\": {\"coverage\": 75.2, \"functions\": 400}
  },
  \"quality_score\": 8.5,
  \"ai_usage\": {
    \"groq_calls\": 450,
    \"openai_calls\": 50,
    \"estimated_cost\": 2.35
  }
}
\`\`\`

## HTML Report Features
- Interactive charts (Chart.js or D3.js)
- Sortable tables
- Filterable by language/module
- Drill-down to file level
- Trend graphs over time

## Badge Generation
\`\`\`markdown
![Documentation Coverage](https://img.shields.io/badge/docs-85%25-green)
\`\`\`

## Integration
- [ ] GitHub Actions integration
- [ ] Badge embedding in README
- [ ] Codecov integration
- [ ] SonarQube integration

## Configuration
\`\`\`yaml
metrics:
  enabled: true
  track_ai_usage: true
  track_costs: true
  report_format: \"html\"
  minimum_coverage: 80.0
\`\`\`

## Testing
- Unit tests for metric calculation
- Test report generation
- Verify accuracy of metrics
- Test with various codebase sizes

## Documentation
- Metrics documentation
- Report interpretation guide
- Integration guides

## Estimated Effort
3-4 weeks

## Related
See ENHANCEMENT_PLAN.md Section 7.3"

# Issue 9: Interactive Setup Wizard
gh issue create \
  --title "Create Interactive Setup Wizard for First-Time Users" \
  --label "enhancement,ux,low-priority" \
  --body "## Overview
Create an interactive setup wizard to help first-time users configure CodeDocGen with ease.

## Requirements
- [ ] Interactive CLI wizard
- [ ] VSCode extension setup wizard
- [ ] Language detection and configuration
- [ ] AI provider configuration
- [ ] Azure authentication flow
- [ ] Parser path detection
- [ ] Configuration file generation
- [ ] Dependency installation assistance
- [ ] Test configuration before saving

## CLI Wizard Flow
\`\`\`bash
code_doc_gen --setup

Welcome to CodeDocGen Setup Wizard!

1. Which languages do you want to document?
   [✓] Python
   [✓] C++
   [ ] Java
   [✓] JavaScript/TypeScript
   [ ] Go
   [ ] Rust

2. Do you want to use AI-powered documentation?
   [Yes] / No

3. Which AI provider?
   ( ) Groq
   (•) Azure OpenAI
   ( ) OpenAI
   ( ) None (NLTK only)

4. Azure OpenAI Configuration:
   Authentication method?
   ( ) API Key
   (•) Azure CLI (az login)
   ( ) Managed Identity
   
   Endpoint: [https://your-resource.openai.azure.com/]
   Deployment: [gpt-4]

5. Detecting parsers...
   ✓ Python: Built-in AST
   ✓ libclang found at: /usr/lib/libclang.so
   ⚠ JavaParser not found (will use regex fallback)
   
   Configure custom paths? [y/N]: n

6. Configuration Summary:
   Languages: Python, C++, JavaScript/TypeScript
   AI Provider: Azure OpenAI (Azure CLI auth)
   Parsers: Python (AST), C++ (libclang), JS (regex)
   
   Save configuration? [Y/n]: y
   
   Configuration saved to: config.yaml

7. Testing configuration...
   ✓ Azure authentication successful
   ✓ Python parser working
   ✓ C++ parser working
   ✓ JavaScript parser working
   
   Setup complete! Try running:
   code_doc_gen --repo /path/to/your/repo --inplace
\`\`\`

## VSCode Extension Wizard
- Welcome screen on first activation
- Step-by-step configuration
- Interactive authentication for Azure
- Provider status indicators
- Test generation button
- Settings sync with CLI tool

## Features
- Smart defaults based on environment
- Auto-detection of available parsers
- Validation of configuration
- Helpful error messages
- Link to documentation for each step
- Option to skip wizard and use defaults
- Re-run wizard command

## Configuration File Generation
Generate config.yaml with:
- Detected languages
- Configured AI providers
- Parser paths
- Recommended settings
- Comments explaining each option

## Testing
- Test wizard flow end-to-end
- Test with various scenarios (no clang, no azure, etc.)
- Test error handling
- Test configuration validation

## Documentation
- Wizard usage guide
- Configuration options reference
- Troubleshooting common issues

## Estimated Effort
2-3 weeks

## Related
See ENHANCEMENT_PLAN.md Section 9.2"

# Issue 10: Secure Credential Management
gh issue create \
  --title "Implement Secure Credential Management System" \
  --label "enhancement,security,medium-priority" \
  --body "## Overview
Implement secure credential management using system keychains and encryption instead of storing API keys in plain text.

## Requirements

### Credential Storage
- [ ] Integration with system keychains
  - macOS: Keychain
  - Windows: Credential Manager
  - Linux: Secret Service (GNOME Keyring, KWallet)
- [ ] Encrypted credential storage as fallback
- [ ] Support for multiple credentials per provider
- [ ] Credential naming and organization

### Security Features
- [ ] Never log credentials
- [ ] Credential rotation support
- [ ] Audit logging for credential access
- [ ] Encryption at rest
- [ ] Secure memory handling (clear after use)
- [ ] Rate limiting for credential retrieval
- [ ] Lockout after failed attempts

### CLI Interface
\`\`\`bash
# Store credentials
code_doc_gen --store-credentials azure_openai
Enter Azure OpenAI Endpoint: https://your-resource.openai.azure.com/
Enter API Key: ****
Credentials stored securely in system keychain.

# List stored credentials
code_doc_gen --list-credentials
- groq (stored in keychain)
- azure_openai (stored in keychain)
- openai (not configured)

# Remove credentials
code_doc_gen --remove-credentials azure_openai
Credentials removed.

# Rotate credentials
code_doc_gen --rotate-credentials groq
Enter new API Key: ****
Credentials updated.
\`\`\`

### VSCode Extension Integration
- Secure credential input UI
- Credential status indicators
- One-click credential management
- Sync with CLI credentials

## Technical Implementation
- Use \`keyring\` library for Python
- Fallback to encrypted local storage
- AES-256 encryption for fallback
- Master password for encryption
- Environment variable override still supported

## Configuration
\`\`\`yaml
security:
  use_keychain: true
  fallback_encryption: true
  credential_audit_log: true
  audit_log_path: \"~/.docgen/audit.log\"
\`\`\`

## Privacy Features
- [ ] No telemetry by default
- [ ] Opt-in for usage statistics
- [ ] PII detection in code before AI submission
- [ ] Ability to mask sensitive patterns
- [ ] Local-only mode (no network calls)

## Compliance
- [ ] GDPR compliance checklist
- [ ] SOC 2 readiness
- [ ] Security audit logging
- [ ] Data residency options for Azure

## Testing
- Unit tests for encryption/decryption
- Integration tests with keychains
- Security penetration testing
- Credential rotation testing
- Fallback mechanism testing

## Documentation
- Security best practices guide
- Credential management guide
- Compliance documentation
- Audit log interpretation

## Estimated Effort
3-4 weeks

## Related
See ENHANCEMENT_PLAN.md Section 10"

echo ""
echo "✓ All enhancement issues created successfully!"
echo ""
echo "To view issues, run: gh issue list"
echo "To view a specific issue, run: gh issue view <number>"

