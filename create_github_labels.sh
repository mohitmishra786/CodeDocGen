#!/bin/bash

# Script to create GitHub labels for CodeDocGen project
# Run this before creating issues

echo "Creating GitHub labels for CodeDocGen..."

# Enhancement labels
gh label create "enhancement" --description "New feature or request" --color "a2eeef" --force
gh label create "high-priority" --description "High priority task" --color "d93f0b" --force
gh label create "medium-priority" --description "Medium priority task" --color "fbca04" --force
gh label create "low-priority" --description "Low priority task" --color "0e8a16" --force

# Feature area labels
gh label create "ai-provider" --description "AI provider integration" --color "7057ff" --force
gh label create "vscode-extension" --description "VSCode extension related" --color "5319e7" --force
gh label create "configuration" --description "Configuration and setup" --color "d4c5f9" --force
gh label create "language-support" --description "Programming language support" --color "bfdadc" --force
gh label create "performance" --description "Performance improvements" --color "f9d0c4" --force
gh label create "ci-cd" --description "CI/CD integration" --color "0e8a16" --force
gh label create "metrics" --description "Metrics and reporting" --color "c2e0c6" --force
gh label create "ux" --description "User experience improvements" --color "bfd4f2" --force
gh label create "security" --description "Security related" --color "d73a4a" --force
gh label create "documentation" --description "Documentation improvements" --color "0075ca" --force
gh label create "testing" --description "Testing related" --color "d876e3" --force

# Status labels
gh label create "in-progress" --description "Currently being worked on" --color "fbca04" --force
gh label create "blocked" --description "Blocked by another issue" --color "d93f0b" --force
gh label create "needs-review" --description "Needs code review" --color "0e8a16" --force
gh label create "ready-for-release" --description "Ready to be released" --color "0e8a16" --force

# Size labels
gh label create "size:small" --description "Small task (1-3 days)" --color "c2e0c6" --force
gh label create "size:medium" --description "Medium task (1-2 weeks)" --color "fbca04" --force
gh label create "size:large" --description "Large task (2-4 weeks)" --color "d93f0b" --force
gh label create "size:xlarge" --description "Extra large task (1+ months)" --color "b60205" --force

# Type labels
gh label create "bug" --description "Something isn't working" --color "d73a4a" --force
gh label create "breaking-change" --description "Breaking API change" --color "b60205" --force
gh label create "good-first-issue" --description "Good for newcomers" --color "7057ff" --force
gh label create "help-wanted" --description "Extra attention is needed" --color "008672" --force

echo ""
echo "✓ All GitHub labels created successfully!"
echo ""
echo "Labels created:"
gh label list

