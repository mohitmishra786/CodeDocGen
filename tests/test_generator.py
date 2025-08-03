"""
Tests for the documentation generator module.
"""

import pytest
from pathlib import Path
from code_doc_gen.generator import DocumentationGenerator
from code_doc_gen.config import Config
from code_doc_gen.models import Function, Parameter, Exception


class TestDocumentationGenerator:
    """Test cases for DocumentationGenerator."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return Config()
    
    @pytest.fixture
    def generator(self, config):
        """Create a test generator."""
        return DocumentationGenerator(config)
    
    @pytest.fixture
    def sample_function(self):
        """Create a sample function for testing."""
        return Function(
            name="add",
            return_type="int",
            parameters=[
                Parameter(name="a", type="int"),
                Parameter(name="b", type="int")
            ],
            brief_description="Adds two integers.",
            detailed_description="Adds two integers and returns the sum."
        )

    # Language Inference Tests
    def test_infer_language_from_extension_python(self, generator):
        """Test language inference for Python files."""
        file_path = Path("test.py")
        lang = generator._infer_language_from_extension(file_path)
        assert lang == "python"
    
    def test_infer_language_from_extension_cpp(self, generator):
        """Test language inference for C++ files."""
        extensions = [".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"]
        for ext in extensions:
            file_path = Path(f"test{ext}")
            lang = generator._infer_language_from_extension(file_path)
            assert lang == "c++"
    
    def test_infer_language_from_extension_java(self, generator):
        """Test language inference for Java files."""
        file_path = Path("test.java")
        lang = generator._infer_language_from_extension(file_path)
        assert lang == "java"
    
    def test_infer_language_from_extension_unknown(self, generator):
        """Test language inference for unknown file types."""
        file_path = Path("test.txt")
        lang = generator._infer_language_from_extension(file_path)
        assert lang == "unknown"

    # Python Comment Detection Tests
    def test_find_existing_documentation_start_python_single_comment(self, generator):
        """Test finding single-line comment above Python function."""
        lines = [
            "# This is a comment\n",
            "def test_func():\n",
            "    pass\n"
        ]
        result = generator._find_existing_documentation_start(lines, 1, "python")
        assert result == 0
    
    def test_find_existing_documentation_start_python_docstring(self, generator):
        """Test finding docstring above Python function."""
        lines = [
            '"""This is a docstring"""\n',
            "def test_func():\n",
            "    pass\n"
        ]
        result = generator._find_existing_documentation_start(lines, 1, "python")
        assert result == 0
    
    def test_find_existing_documentation_start_python_triple_single_quotes(self, generator):
        """Test finding triple single quotes docstring above Python function."""
        lines = [
            "'''This is a docstring'''\n",
            "def test_func():\n",
            "    pass\n"
        ]
        result = generator._find_existing_documentation_start(lines, 1, "python")
        assert result == 0
    
    def test_find_existing_documentation_start_python_decorator(self, generator):
        """Test finding comment above decorator in Python."""
        lines = [
            "# This is a comment\n",
            "@decorator\n",
            "def test_func():\n",
            "    pass\n"
        ]
        result = generator._find_existing_documentation_start(lines, 2, "python")
        assert result == 0
    
    def test_find_existing_documentation_start_python_multiple_decorators(self, generator):
        """Test finding comment above multiple decorators in Python."""
        lines = [
            "# This is a comment\n",
            "@decorator1\n",
            "@decorator2\n",
            "def test_func():\n",
            "    pass\n"
        ]
        result = generator._find_existing_documentation_start(lines, 3, "python")
        assert result == 0
    
    def test_find_existing_documentation_start_python_comment_block(self, generator):
        """Test finding comment block above Python function."""
        lines = [
            "# Comment line 1\n",
            "# Comment line 2\n",
            "# Comment line 3\n",
            "def test_func():\n",
            "    pass\n"
        ]
        result = generator._find_existing_documentation_start(lines, 3, "python")
        assert result == 2  # Should return the last comment line in the block
    
    def test_find_existing_documentation_start_python_no_comment(self, generator):
        """Test finding no comment above Python function."""
        lines = [
            "def other_func():\n",
            "    pass\n",
            "\n",
            "def test_func():\n",
            "    pass\n"
        ]
        result = generator._find_existing_documentation_start(lines, 3, "python")
        assert result is None
    
    def test_find_existing_documentation_start_python_comment_between_functions(self, generator):
        """Test that comment belongs to correct function when functions are between."""
        lines = [
            "# Comment for func1\n",
            "def func1():\n",
            "    pass\n",
            "\n",
            "def func2():\n",
            "    pass\n",
            "\n",
            "def test_func():\n",
            "    pass\n"
        ]
        result = generator._find_existing_documentation_start(lines, 7, "python")
        assert result is None  # Comment belongs to func1, not test_func
    
    def test_has_inline_documentation_python_same_line(self, generator):
        """Test inline documentation detection on same line in Python."""
        lines = [
            "def test_func():  # This is a comment\n",
            "    pass\n"
        ]
        result = generator._has_inline_documentation(lines, 0, "python")
        assert result is True
    
    def test_has_inline_documentation_python_next_line(self, generator):
        """Test inline documentation detection on next line in Python."""
        lines = [
            "def test_func():\n",
            "    # This is a comment\n",
            "    pass\n"
        ]
        result = generator._has_inline_documentation(lines, 0, "python")
        assert result is True
    
    def test_has_inline_documentation_python_docstring_next_line(self, generator):
        """Test inline docstring detection on next line in Python."""
        lines = [
            "def test_func():\n",
            '    """This is a docstring"""\n',
            "    pass\n"
        ]
        result = generator._has_inline_documentation(lines, 0, "python")
        assert result is True
    
    def test_has_inline_documentation_python_no_inline(self, generator):
        """Test no inline documentation detection in Python."""
        lines = [
            "def test_func():\n",
            "    pass\n"
        ]
        result = generator._has_inline_documentation(lines, 0, "python")
        assert result is False

    # C++ Comment Detection Tests
    def test_find_existing_documentation_start_cpp_single_comment(self, generator):
        """Test finding single-line comment above C++ function."""
        lines = [
            "// This is a comment\n",
            "void test_func() {\n",
            "}\n"
        ]
        result = generator._find_existing_documentation_start(lines, 1, "c++")
        assert result == 0
    
    def test_find_existing_documentation_start_cpp_comment_block(self, generator):
        """Test finding comment block above C++ function."""
        lines = [
            "/* This is a comment block */\n",
            "void test_func() {\n",
            "}\n"
        ]
        result = generator._find_existing_documentation_start(lines, 1, "c++")
        assert result == 0
    
    def test_find_existing_documentation_start_cpp_doxygen_comment(self, generator):
        """Test finding Doxygen comment above C++ function."""
        lines = [
            "/** This is a Doxygen comment */\n",
            "void test_func() {\n",
            "}\n"
        ]
        result = generator._find_existing_documentation_start(lines, 1, "c++")
        assert result == 0
    
    def test_find_existing_documentation_start_cpp_multiline_comment(self, generator):
        """Test finding multi-line comment above C++ function."""
        lines = [
            "/* This is a multi-line\n",
            "   comment block */\n",
            "void test_func() {\n",
            "}\n"
        ]
        result = generator._find_existing_documentation_start(lines, 2, "c++")
        assert result == 1  # Should return the line with the closing comment
    
    def test_find_existing_documentation_start_cpp_contiguous_comments(self, generator):
        """Test finding contiguous single-line comments above C++ function."""
        lines = [
            "// Comment line 1\n",
            "// Comment line 2\n",
            "// Comment line 3\n",
            "void test_func() {\n",
            "}\n"
        ]
        result = generator._find_existing_documentation_start(lines, 3, "c++")
        assert result == 2  # Should return the last comment line in the contiguous block
    
    def test_find_existing_documentation_start_cpp_no_comment(self, generator):
        """Test finding no comment above C++ function."""
        lines = [
            "void other_func() {\n",
            "}\n",
            "\n",
            "void test_func() {\n",
            "}\n"
        ]
        result = generator._find_existing_documentation_start(lines, 3, "c++")
        assert result is None
    
    def test_find_existing_documentation_start_cpp_comment_between_functions(self, generator):
        """Test that comment belongs to correct function when functions are between."""
        lines = [
            "// Comment for func1\n",
            "void func1() {\n",
            "}\n",
            "\n",
            "void func2() {\n",
            "}\n",
            "\n",
            "void test_func() {\n",
            "}\n"
        ]
        result = generator._find_existing_documentation_start(lines, 7, "c++")
        assert result is None  # Comment belongs to func1, not test_func
    
    def test_has_inline_documentation_cpp_same_line(self, generator):
        """Test inline documentation detection on same line in C++."""
        lines = [
            "void test_func() { // This is a comment\n",
            "}\n"
        ]
        result = generator._has_inline_documentation(lines, 0, "c++")
        assert result is True
    
    def test_has_inline_documentation_cpp_next_line(self, generator):
        """Test inline documentation detection on next line in C++."""
        lines = [
            "void test_func() {\n",
            "    // This is a comment\n",
            "}\n"
        ]
        result = generator._has_inline_documentation(lines, 0, "c++")
        assert result is True
    
    def test_has_inline_documentation_cpp_no_inline(self, generator):
        """Test no inline documentation detection in C++."""
        lines = [
            "void test_func() {\n",
            "}\n"
        ]
        result = generator._has_inline_documentation(lines, 0, "c++")
        assert result is False

    # Edge Cases and Complex Scenarios
    def test_find_existing_documentation_start_python_mixed_content(self, generator):
        """Test finding comments in Python with mixed content."""
        lines = [
            "# Comment 1\n",
            "import os\n",
            "\n",
            "# Comment 2\n",
            "def func1():\n",
            "    pass\n",
            "\n",
            "def func2():\n",
            "    pass\n",
            "\n",
            "def test_func():\n",
            "    pass\n"
        ]
        result = generator._find_existing_documentation_start(lines, 9, "python")
        assert result is None  # No comment directly above test_func
    
    def test_find_existing_documentation_start_cpp_mixed_content(self, generator):
        """Test finding comments in C++ with mixed content."""
        lines = [
            "// Comment 1\n",
            "#include <iostream>\n",
            "\n",
            "// Comment 2\n",
            "void func1() {\n",
            "}\n",
            "\n",
            "void func2() {\n",
            "}\n",
            "\n",
            "void test_func() {\n",
            "}\n"
        ]
        result = generator._find_existing_documentation_start(lines, 9, "c++")
        assert result is None  # No comment directly above test_func
    
    def test_find_existing_documentation_start_python_empty_lines(self, generator):
        """Test finding comments with empty lines in Python."""
        lines = [
            "# Comment\n",
            "\n",
            "\n",
            "def test_func():\n",
            "    pass\n"
        ]
        result = generator._find_existing_documentation_start(lines, 3, "python")
        assert result == 0
    
    def test_find_existing_documentation_start_cpp_empty_lines(self, generator):
        """Test finding comments with empty lines in C++."""
        lines = [
            "// Comment\n",
            "\n",
            "\n",
            "void test_func() {\n",
            "}\n"
        ]
        result = generator._find_existing_documentation_start(lines, 3, "c++")
        assert result == 0
    
    def test_find_existing_documentation_start_unknown_language(self, generator):
        """Test comment detection for unknown language (fallback behavior)."""
        lines = [
            "// This should not be detected for unknown language\n",
            "function test_func() {\n",
            "}\n"
        ]
        result = generator._find_existing_documentation_start(lines, 1, "unknown")
        assert result is None  # Unknown language should not detect comments
    
    def test_has_inline_documentation_unknown_language(self, generator):
        """Test inline documentation detection for unknown language."""
        lines = [
            "function test_func() { // This should not be detected\n",
            "}\n"
        ]
        result = generator._has_inline_documentation(lines, 0, "unknown")
        assert result is False  # Unknown language should not detect inline comments

    # Integration Tests
    def test_apply_documentation_inplace_with_existing_comments_python(self, generator, tmp_path):
        """Test that in-place documentation doesn't overwrite existing comments in Python."""
        test_file = tmp_path / "test.py"
        test_content = """# Existing comment
def test_func():
    pass

def no_comment_func():
    pass
"""
        test_file.write_text(test_content)
        
        # Create function for documentation
        func = Function(name="no_comment_func", return_type="None")
        documentation = generator.generate_documentation([func], "python")
        
        # Apply documentation
        generator.apply_documentation_inplace(test_file, documentation)
        
        # Check that existing comment was preserved and new doc was added
        modified_content = test_file.read_text()
        assert "# Existing comment" in modified_content
        assert '"""' in modified_content  # New documentation should be added
    
    def test_apply_documentation_inplace_with_existing_comments_cpp(self, generator, tmp_path):
        """Test that in-place documentation doesn't overwrite existing comments in C++."""
        test_file = tmp_path / "test.cpp"
        test_content = """// Existing comment
void test_func() {
}

void no_comment_func() {
}
"""
        test_file.write_text(test_content)
        
        # Create function for documentation
        func = Function(name="no_comment_func", return_type="void")
        documentation = generator.generate_documentation([func], "c++")
        
        # Apply documentation
        generator.apply_documentation_inplace(test_file, documentation)
        
        # Check that existing comment was preserved and new doc was added
        modified_content = test_file.read_text()
        assert "// Existing comment" in modified_content
        assert "/**" in modified_content  # New documentation should be added
    
    def test_apply_documentation_inplace_with_decorators_python(self, generator, tmp_path):
        """Test that in-place documentation works correctly with decorators in Python."""
        test_file = tmp_path / "test.py"
        test_content = """@decorator
def test_func():
    pass

def no_comment_func():
    pass
"""
        test_file.write_text(test_content)
        
        # Create function for documentation
        func = Function(name="no_comment_func", return_type="None")
        documentation = generator.generate_documentation([func], "python")
        
        # Apply documentation
        generator.apply_documentation_inplace(test_file, documentation)
        
        # Check that decorator was preserved and new doc was added
        modified_content = test_file.read_text()
        assert "@decorator" in modified_content
        assert '"""' in modified_content  # New documentation should be added

    # Original Tests (keeping for backward compatibility)
    def test_generate_documentation(self, generator, sample_function):
        """Test documentation generation."""
        documentation = generator.generate_documentation([sample_function], "c++")
        
        assert "add" in documentation
        assert "adds" in documentation["add"].lower()
        assert "\\param" in documentation["add"]
        assert "\\return" in documentation["add"]
    
    def test_generate_brief_documentation_cpp(self, generator, sample_function):
        """Test brief documentation generation for C++."""
        doc = generator._generate_brief_documentation(sample_function, "c++")
        
        assert "\\brief" in doc
        assert "adds" in doc.lower()
    
    def test_generate_brief_documentation_python(self, generator, sample_function):
        """Test brief documentation generation for Python."""
        doc = generator._generate_brief_documentation(sample_function, "python")
        
        assert '"""' in doc
        assert "adds" in doc.lower()
    
    def test_generate_brief_documentation_java(self, generator, sample_function):
        """Test brief documentation generation for Java."""
        doc = generator._generate_brief_documentation(sample_function, "java")
        
        assert "/**" in doc
        assert "adds" in doc.lower()
    
    def test_generate_detailed_documentation(self, generator, sample_function):
        """Test detailed documentation generation."""
        doc = generator._generate_detailed_documentation(sample_function, "c++")
        
        assert "\\brief" in doc
        assert "\\param" in doc
        assert "\\return" in doc
    
    def test_generate_parameter_documentation(self, generator, sample_function):
        """Test parameter documentation generation."""
        param_docs = generator._generate_parameter_documentation(sample_function, "c++")
        
        assert "a" in param_docs
        assert "b" in param_docs
        assert "\\param" in param_docs["a"]
        assert "\\param" in param_docs["b"]
    
    def test_generate_parameter_documentation_text(self, generator, sample_function):
        """Test parameter documentation text generation."""
        text = generator._generate_parameter_documentation_text(sample_function, "c++")
        
        assert "\\param a" in text
        assert "\\param b" in text
    
    def test_generate_return_documentation(self, generator, sample_function):
        """Test return documentation generation."""
        doc = generator._generate_return_documentation(sample_function, "c++")
        
        assert doc is not None
        assert "\\return" in doc
        assert "integer" in doc.lower()
    
    def test_generate_return_documentation_void(self, generator):
        """Test return documentation generation for void functions."""
        void_function = Function(name="print", return_type="void")
        doc = generator._generate_return_documentation(void_function, "c++")
        
        assert doc is None
    
    def test_generate_return_description(self, generator):
        """Test return description generation."""
        # Test different return types
        function = Function(name="test", return_type="int")
        desc = generator._generate_return_description(function)
        assert "integer" in desc.lower()
        
        function.return_type = "bool"
        desc = generator._generate_return_description(function)
        assert "true or false" in desc.lower()
        
        function.return_type = "string"
        desc = generator._generate_return_description(function)
        assert "string" in desc.lower()
        
        function.return_type = "list"
        desc = generator._generate_return_description(function)
        assert "list" in desc.lower()
    
    def test_generate_exception_documentation(self, generator):
        """Test exception documentation generation."""
        function = Function(
            name="divide",
            return_type="float",
            exceptions=[
                Exception(name="ZeroDivisionError"),
                Exception(name="ValueError")
            ]
        )
        
        exception_docs = generator._generate_exception_documentation(function, "c++")
        
        assert "ZeroDivisionError" in exception_docs
        assert "ValueError" in exception_docs
        assert "\\throws" in exception_docs["ZeroDivisionError"]
        assert "\\throws" in exception_docs["ValueError"]
    
    def test_generate_exception_documentation_text(self, generator):
        """Test exception documentation text generation."""
        function = Function(
            name="divide",
            return_type="float",
            exceptions=[
                Exception(name="ZeroDivisionError")
            ]
        )
        
        text = generator._generate_exception_documentation_text(function, "c++")
        
        assert "\\throws ZeroDivisionError" in text
    
    def test_apply_documentation_inplace(self, generator, sample_function, tmp_path):
        """Test in-place documentation application."""
        # Create a test file
        test_file = tmp_path / "test.cpp"
        test_content = """int add(int a, int b) {
    return a + b;
}"""
        test_file.write_text(test_content)
        
        # Generate documentation
        documentation = generator.generate_documentation([sample_function], "c++")
        
        # Apply documentation
        generator.apply_documentation_inplace(test_file, documentation)
        
        # Check that backup was created
        backup_file = test_file.with_suffix(test_file.suffix + '.bak')
        assert backup_file.exists()
        
        # Check that file was modified
        modified_content = test_file.read_text()
        assert "\\brief" in modified_content
        assert "\\param" in modified_content
    
    def test_write_documentation_to_file(self, generator, sample_function, tmp_path):
        """Test writing documentation to a new file."""
        # Generate documentation
        documentation = generator.generate_documentation([sample_function], "c++")
        
        # Write to file
        output_file = tmp_path / "documentation.md"
        generator.write_documentation_to_file(output_file, documentation)
        
        # Check that file was created
        assert output_file.exists()
        
        # Check content
        content = output_file.read_text()
        assert "# Generated Documentation" in content
        assert "## Function: add" in content
        assert "\\brief" in content
    
    def test_generate_diff(self, generator, sample_function, tmp_path):
        """Test diff generation."""
        # Create a test file
        test_file = tmp_path / "test.cpp"
        test_content = """int add(int a, int b) {
    return a + b;
}"""
        test_file.write_text(test_content)
        
        # Generate documentation
        documentation = generator.generate_documentation([sample_function], "c++")
        
        # Generate diff
        diff = generator.generate_diff(test_file, documentation)
        
        # Check that diff contains expected content
        assert "---" in diff
        assert "+++" in diff
        assert "\\brief" in diff 