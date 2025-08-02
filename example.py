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
"""
    python_file.write_text(python_content)
    
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

def demonstrate_inplace_for_all_languages():
    sample_dir = Path("sample_code")
    # In-place for Python
    print("=== In-place documentation for Python ===")
    generate_docs(sample_dir, lang="python", inplace=True)
    print_file_contents(sample_dir / "utils.py")

    # In-place for C++ (also works for .c files)
    print("\n=== In-place documentation for C++ ===")
    generate_docs(sample_dir, lang="c++", inplace=True)
    print_file_contents(sample_dir / "math.cpp")

    # If you have Java files, do the same:
    # print("\n=== In-place documentation for Java ===")
    # generate_docs(sample_dir, lang="java", inplace=True)
    # print_file_contents(sample_dir / "Example.java")

if __name__ == "__main__":
    try:
        demonstrate_library_usage()
        demonstrate_cli_usage()
        demonstrate_inplace_for_all_languages()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install -r requirements.txt")
        print("python -c \"import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')\"") 