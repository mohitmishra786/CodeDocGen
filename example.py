#!/usr/bin/env python3
"""
Example usage of CodeDocGen.

This script demonstrates how to use the CodeDocGen library
to generate documentation for code files.
"""

import tempfile
import os
from pathlib import Path
from code_doc_gen import generate_docs, generate_cpp_docs, generate_python_docs


def create_sample_files():
    """Create sample code files for demonstration."""
    sample_dir = Path("sample_code")
    sample_dir.mkdir(exist_ok=True)
    
    # Create a sample C++ file
    cpp_file = sample_dir / "math.cpp"
    cpp_content = """
#include <iostream>

int add(int a, int b) {
    return a + b;
}

float multiply(float x, float y) {
    return x * y;
}

bool isPositive(int value) {
    return value > 0;
}

void printResult(int result) {
    std::cout << "Result: " << result << std::endl;
}
"""
    cpp_file.write_text(cpp_content)
    
    # Create a sample Python file
    python_file = sample_dir / "utils.py"
    python_content = """
def validate_email(email):
    if '@' not in email:
        raise ValueError("Invalid email format")
    return True

def get_user_info(user_id):
    return {"id": user_id, "name": "John Doe"}

def compute_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def is_valid_password(password):
    return len(password) >= 8

def process_data(data):
    # This function calls other functions - these should NOT get comments
    result = validate_email(data.get('email', ''))
    user = get_user_info(data.get('user_id'))
    avg = compute_average(data.get('scores', []))
    return {
        'valid': result,
        'user': user,
        'average': avg
    }

def main():
    # This function also calls other functions
    data = {
        'email': 'test@example.com',
        'user_id': 123,
        'scores': [85, 90, 78, 92]
    }
    
    # These function calls should NOT get comments
    result = process_data(data)
    print(f"Processed: {result}")
    
    # Test password validation
    is_valid = is_valid_password("secure123")
    print(f"Password valid: {is_valid}")
"""
    python_file.write_text(python_content)
    
    # Create a sample Python file with class methods
    class_file = sample_dir / "class_example.py"
    class_content = """
class Calculator:
    def __init__(self, initial_value=0):
        self.value = initial_value
    
    def add(self, x):
        self.value += x
        return self.value
    
    def subtract(self, x):
        self.value -= x
        return self.value
    
    def multiply(self, x):
        self.value *= x
        return self.value
    
    def get_value(self):
        return self.value

class DataProcessor:
    def process_data(self, data):
        # This should NOT get a comment - it's a function call
        result = self.validate_data(data)
        return result
    
    def validate_data(self, data):
        if not data:
            return False
        return True
"""
    class_file.write_text(class_content)
    
    return sample_dir


def create_sample_files_with_existing_docs():
    """Create sample files with existing documentation to test the fix."""
    sample_dir = Path("sample_code")
    sample_dir.mkdir(exist_ok=True)
    
    # Create a Python file with existing docstrings
    existing_docs_file = sample_dir / "existing_docs.py"
    existing_docs_content = '''#!/usr/bin/env python3
"""
Test Real Repository Animation

This script tests our ManimGL system with real GitHub repositories
to generate animations from actual code.
"""

import os
import sys
import logging
from pathlib import Path
import argparse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import logging utilities
from advanced_animation.utils.logging_config import setup_logging_for_run, get_logger

# Setup logging for this run
logging_manager = setup_logging_for_run("logs", logging.INFO)
logger = get_logger(__name__)

from advanced_animation import AdvancedAnimationSystem
from code_analysis import EnhancedCodeAnalyzer
from repo_fetcher import RepoFetcher
import tempfile
import subprocess

def fetch_repository(repo_url: str) -> str:
    """Wrapper function to fetch a repository."""
    # Create a temporary directory for the repository
    temp_dir = tempfile.mkdtemp(prefix="repo_")
    
    # Clone the repository using git
    try:
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True, capture_output=True)
        return temp_dir
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to clone repository: {e}")

def analyze_repository(repo_path: str):
    """Wrapper function to analyze a repository."""
    analyzer = EnhancedCodeAnalyzer(repo_path)
    return analyzer.analyze_project()

def analyze_github_repo(repo_url: str, output_dir: str = "real_repo_output"):
    """Analyze a GitHub repository and create animations."""
    print(f"🎬 Testing Real Repository: {repo_url}")
    print("=" * 60)
    
    try:
        # Initialize the advanced animation system
        system = AdvancedAnimationSystem(output_dir=output_dir)
        
        # Fetch and analyze the repository
        print("📥 Fetching repository...")
        repo_path = fetch_repository(repo_url)
        print(f"✅ Repository fetched to: {repo_path}")
        
        print("\\n🔍 Analyzing repository...")
        code_analysis = analyze_repository(repo_path)
        print(f"✅ Analysis complete: {len(code_analysis.get('files', []))} files analyzed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing repository: {e}")
        return False

class StoryboardManager:
    """Manages storyboard operations."""
    
    @staticmethod
    def save_storyboard(storyboard, output_path: str) -> str:
        """Save storyboard to JSON file."""
        try:
            # Convert storyboard to JSON and save
            import json
            with open(output_path, 'w') as f:
                json.dump(storyboard.__dict__, f, indent=2)
            return output_path
        except Exception as e:
            raise IOError(f"Failed to save storyboard: {e}")
    
    @staticmethod
    def load_storyboard(file_path: str):
        """Load storyboard from JSON file."""
        try:
            import json
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            raise IOError(f"Failed to load storyboard: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test ManimGL system with real repositories")
    parser.add_argument("repo_url", help="GitHub repository URL (e.g., https://github.com/user/repo)")
    parser.add_argument("--output", "-o", default="real_repo_output", 
                       help="Output directory (default: real_repo_output)")
    
    args = parser.parse_args()
    
    # Validate repository URL
    if not args.repo_url.startswith("https://github.com/"):
        print("❌ Please provide a valid GitHub repository URL")
        return
    
    # Process the repository
    success = analyze_github_repo(args.repo_url, args.output)
    
    if success:
        print("\\n🎊 Repository animation test completed successfully!")
    else:
        print("\\n⚠️ Some issues encountered. Check the logs above.")

if __name__ == "__main__":
    main()
'''
    existing_docs_file.write_text(existing_docs_content)
    
    return sample_dir


def demonstrate_library_usage():
    """Demonstrate the library usage."""
    print("=== CodeDocGen Library Usage Example ===\n")
    
    # Create sample files
    sample_dir = create_sample_files()
    
    # Example 1: Generate documentation for Python files
    print("1. Generating documentation for Python files:")
    results = generate_python_docs(sample_dir, inplace=False)
    
    for file_path, doc_strings in results.items():
        print(f"\nFile: {file_path}")
        for func_name, doc_string in doc_strings.items():
            print(f"\nFunction: {func_name}")
            print(doc_string)
    
    # Example 2: Generate documentation for C++ files
    print("\n\n2. Generating documentation for C++ files:")
    results = generate_cpp_docs(sample_dir, inplace=False)
    
    for file_path, doc_strings in results.items():
        print(f"\nFile: {file_path}")
        for func_name, doc_string in doc_strings.items():
            print(f"\nFunction: {func_name}")
            print(doc_string)
    
    # Example 3: Generate documentation with custom output
    print("\n\n3. Generating documentation to output directory:")
    output_dir = Path("generated_docs")
    # Generate Python docs
    generate_docs(sample_dir, lang="python", output_dir=output_dir)
    # Generate C++ docs
    generate_docs(sample_dir, lang="c++", output_dir=output_dir)
    print(f"Documentation written to: {output_dir}")
    
    # Example 4: Show diff without applying changes
    print("\n\n4. Showing diff of changes:")
    for file_path in sample_dir.glob("*.py"):
        results = generate_python_docs(sample_dir, files=[file_path.name], inplace=False)
        if results:
            from code_doc_gen.generator import DocumentationGenerator
            from code_doc_gen.config import Config
            
            config = Config()
            generator = DocumentationGenerator(config)
            
            for file_path_str, doc_strings in results.items():
                diff = generator.generate_diff(Path(file_path_str), doc_strings)
                if diff:
                    print(f"\n--- Diff for {file_path_str} ---")
                    print(diff)
    
    # Cleanup
    # print("\n\n=== Cleanup ===")
    # print("Removing sample files...")
    # import shutil
    # shutil.rmtree(sample_dir)
    # if output_dir.exists():
    #     shutil.rmtree(output_dir)
    # print("Cleanup complete!")


def demonstrate_cli_usage():
    """Demonstrate CLI usage instructions."""
    print("\n=== CLI Usage Examples ===\n")
    
    print("To use the command-line interface:")
    print()
    print("1. Generate documentation for a C++ repository:")
    print("   code_doc_gen --repo /path/to/cpp/repo --lang c++ --inplace")
    print()
    print("2. Generate documentation for Python files with custom output:")
    print("   code_doc_gen --repo /path/to/python/repo --lang python --output-dir ./docs")
    print()
    print("3. Use custom configuration:")
    print("   code_doc_gen --repo /path/to/repo --lang java --config custom_rules.yaml")
    print()
    print("4. Process specific files only:")
    print("   code_doc_gen --repo /path/to/repo --lang python --files src/main.py src/utils.py")
    print()
    print("5. Show diff without applying changes:")
    print("   code_doc_gen --repo /path/to/repo --lang c++ --diff")
    print()
    print("6. Enable verbose logging:")
    print("   code_doc_gen --repo /path/to/repo --lang python --verbose")


def print_file_contents(file_path):
    print(f"\n--- {file_path} ---")
    with open(file_path, "r", encoding="utf-8") as f:
        print(f.read())

def demonstrate_existing_documentation_fix():
    """Demonstrate that the tool doesn't break existing documentation."""
    print("\n=== Testing Existing Documentation Preservation ===")
    
    # Create sample files with existing documentation
    sample_dir = create_sample_files_with_existing_docs()
    
    # Test in-place documentation generation
    print("Testing in-place documentation generation on files with existing docs...")
    generate_docs(sample_dir, lang="python", inplace=True)
    
    # Show the results
    print("\n--- existing_docs.py (after processing) ---")
    print_file_contents(sample_dir / "existing_docs.py")
    
    print("\n✅ Test completed: Existing documentation should be preserved!")

def demonstrate_inplace_for_all_languages():
    sample_dir = Path("sample_code")
    # In-place for Python
    print("=== In-place documentation for Python ===")
    generate_docs(sample_dir, lang="python", inplace=True)
    print_file_contents(sample_dir / "utils.py")
    
    # Test class methods
    print("\n=== In-place documentation for Python Classes ===")
    print_file_contents(sample_dir / "class_example.py")

    # In-place for C++ (also works for .c files)
    print("\n=== In-place documentation for C++ ===")
    generate_docs(sample_dir, lang="c++", inplace=True)
    print_file_contents(sample_dir / "math.cpp")

    # If you have Java files, do the same:
    # print("\n=== In-place documentation for Java ===")
    # generate_docs(sample_dir, lang="java", inplace=True)
    # print_file_contents(sample_dir / "Example.java")

def demo():
    """Run the complete demonstration."""
    print("=== CodeDocGen Library Usage Example ===\n")
    
    # Create sample files
    sample_dir = create_sample_files()
    
    # 1. Generate documentation for Python files
    print("1. Generating documentation for Python files:")
    result = generate_docs(sample_dir, lang="python")
    
    for file_path, functions in result.items():
        print(f"\nFile: {file_path}\n")
        for func_name, doc_string in functions.items():
            print(f"Function: {func_name}")
            print(doc_string)
    
    # 2. Generate documentation for C++ files
    print("\n2. Generating documentation for C++ files:")
    result = generate_docs(sample_dir, lang="c++")
    
    for file_path, functions in result.items():
        print(f"\nFile: {file_path}\n")
        for func_name, doc_string in functions.items():
            print(f"Function: {func_name}")
            print(doc_string)
    
    # 3. Generate documentation to output directory
    print("\n3. Generating documentation to output directory:")
    output_dir = Path("generated_docs")
    generate_docs(sample_dir, lang="python", output_dir=output_dir)
    generate_docs(sample_dir, lang="c++", output_dir=output_dir)
    print(f"Documentation written to: {output_dir}")
    
    # 4. Test existing documentation preservation
    demonstrate_existing_documentation_fix()
    
    # 5. Test in-place documentation
    demonstrate_inplace_for_all_languages()
    
    print("\n=== CLI Usage Examples ===")
    print("To use the command-line interface:")
    print("1. Generate documentation for a C++ repository:")
    print("   code_doc_gen --repo /path/to/cpp/repo --lang c++ --inplace")
    print("2. Generate documentation for Python files with custom output:")
    print("   code_doc_gen --repo /path/to/python/repo --lang python --output-dir ./docs")
    print("3. Use custom configuration:")
    print("   code_doc_gen --repo /path/to/repo --lang java --config custom_rules.yaml")
    print("4. Process specific files only:")
    print("   code_doc_gen --repo /path/to/repo --lang python --files src/main.py src/utils.py")
    print("5. Show diff without applying changes:")
    print("   code_doc_gen --repo /path/to/repo --lang c++ --diff")
    print("6. Enable verbose logging:")
    print("   code_doc_gen --repo /path/to/repo --lang python --verbose")

if __name__ == "__main__":
    try:
        demo()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install -r requirements.txt")
        print("python -c \"import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')\"") 