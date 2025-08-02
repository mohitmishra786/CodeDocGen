"""
Tests for the NLTK analyzer module.
"""

import pytest
from code_doc_gen.analyzer import NLTKAnalyzer
from code_doc_gen.config import Config
from code_doc_gen.models import Function, Parameter, FunctionBody


class TestNLTKAnalyzer:
    """Test cases for NLTKAnalyzer."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return Config()
    
    @pytest.fixture
    def analyzer(self, config):
        """Create a test analyzer."""
        return NLTKAnalyzer(config)
    
    @pytest.fixture
    def sample_function(self):
        """Create a sample function for testing."""
        return Function(
            name="add",
            return_type="int",
            parameters=[
                Parameter(name="a", type="int"),
                Parameter(name="b", type="int")
            ]
        )
    
    def test_analyze_function(self, analyzer, sample_function):
        """Test function analysis."""
        analyzer.analyze_function(sample_function)
        
        assert sample_function.brief_description is not None
        assert sample_function.detailed_description is not None
        assert "add" in sample_function.brief_description.lower()
    
    def test_analyze_parameter(self, analyzer):
        """Test parameter analysis."""
        parameter = Parameter(name="count", type="int")
        analyzer.analyze_parameter(parameter)
        
        assert parameter.description is not None
        assert "count" in parameter.description.lower()
        assert "integer" in parameter.description.lower()
    
    def test_analyze_exception(self, analyzer):
        """Test exception analysis."""
        from code_doc_gen.models import Exception
        exception = Exception(name="ValueError")
        analyzer.analyze_exception(exception)
        
        assert exception.description is not None
        assert "valueerror" in exception.description.lower()
    
    def test_generate_brief_description_with_prefix(self, analyzer):
        """Test brief description generation for functions with common prefixes."""
        # Test get prefix
        get_function = Function(name="getValue", return_type="string")
        analyzer.analyze_function(get_function)
        assert "retrieves" in get_function.brief_description.lower()
        
        # Test set prefix
        set_function = Function(name="setValue", return_type="void")
        analyzer.analyze_function(set_function)
        assert "sets" in set_function.brief_description.lower()
        
        # Test is prefix
        is_function = Function(name="isValid", return_type="bool")
        analyzer.analyze_function(is_function)
        assert "checks if" in is_function.brief_description.lower()
    
    def test_generate_brief_description_with_parameters(self, analyzer):
        """Test brief description generation for functions with parameters."""
        function = Function(
            name="computeSum",
            return_type="int",
            parameters=[
                Parameter(name="a", type="int"),
                Parameter(name="b", type="int")
            ]
        )
        analyzer.analyze_function(function)
        
        assert "computes" in function.brief_description.lower()
        assert "a" in function.brief_description.lower()
        assert "b" in function.brief_description.lower()
    
    def test_extract_noun_from_name(self, analyzer):
        """Test noun extraction from function names."""
        # Test camelCase
        assert analyzer._extract_noun_from_name("getValue") == "value"
        assert analyzer._extract_noun_from_name("computeSum") == "sum"
        
        # Test snake_case
        assert analyzer._extract_noun_from_name("get_value") == "value"
        assert analyzer._extract_noun_from_name("compute_sum") == "sum"
        
        # Test empty name
        assert analyzer._extract_noun_from_name("") == "value"
    
    def test_name_to_sentence(self, analyzer):
        """Test conversion of function names to sentences."""
        # Test simple names
        result = analyzer._name_to_sentence("add")
        assert "add" in result.lower() or "performs" in result.lower()
        
        # Test camelCase
        result = analyzer._name_to_sentence("computeSum")
        assert "compute" in result.lower() or "performs" in result.lower()
    
    def test_get_type_description(self, analyzer):
        """Test type description generation."""
        assert "integer" in analyzer._get_type_description("int")
        assert "floating-point" in analyzer._get_type_description("float")
        assert "string" in analyzer._get_type_description("string")
        assert "boolean" in analyzer._get_type_description("bool")
        assert "list" in analyzer._get_type_description("list")
        assert "dictionary" in analyzer._get_type_description("dict")
    
    def test_describe_parameters(self, analyzer):
        """Test parameter description generation."""
        # Single parameter
        params = [Parameter(name="value", type="int")]
        result = analyzer._describe_parameters(params)
        assert "takes value as input" in result.lower()
        
        # Multiple parameters
        params = [
            Parameter(name="a", type="int"),
            Parameter(name="b", type="int")
        ]
        result = analyzer._describe_parameters(params)
        assert "takes a and b as input" in result.lower()
        
        # No parameters
        result = analyzer._describe_parameters([])
        assert result == ""
    
    def test_describe_return_type(self, analyzer):
        """Test return type description generation."""
        function = Function(name="test", return_type="int")
        result = analyzer._describe_return_type(function)
        assert "integer" in result.lower()
        
        function.return_type = "bool"
        result = analyzer._describe_return_type(function)
        assert "true or false" in result.lower()
        
        function.return_type = "void"
        result = analyzer._describe_return_type(function)
        assert "returns nothing" in result.lower()
    
    def test_fill_template(self, analyzer):
        """Test template filling."""
        function = Function(
            name="getValue",
            return_type="string",
            parameters=[
                Parameter(name="key", type="string")
            ]
        )
        
        template = "Retrieves the {noun} based on {params}."
        result = analyzer._fill_template(template, function)
        
        assert "retrieves" in result.lower()
        assert "key" in result.lower() 