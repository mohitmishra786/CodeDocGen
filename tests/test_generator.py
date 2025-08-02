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