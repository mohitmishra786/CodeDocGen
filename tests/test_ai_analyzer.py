"""
Tests for AI analyzer functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from code_doc_gen.ai_analyzer import AIAnalyzer
from code_doc_gen.config import Config
from code_doc_gen.models import Function, Parameter


class TestAIAnalyzer:
    """Test cases for AI analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.analyzer = AIAnalyzer(self.config)
        
        # Create a sample function for testing
        self.sample_function = Function(
            name="calculate_sum",
            parameters=[
                Parameter("a", "int", "First number"),
                Parameter("b", "int", "Second number")
            ],
            return_type="int",
            source_code="return a + b"
        )
    
    def test_ai_disabled_by_default(self):
        """Test that AI is disabled by default."""
        assert not self.analyzer.ai_enabled
        assert not self.analyzer.is_available()
    
    def test_enable_ai_phind(self):
        """Test enabling AI with Phind provider."""
        self.config.config['ai']['enabled'] = True
        self.config.config['ai']['provider'] = 'phind'
        
        analyzer = AIAnalyzer(self.config)
        assert analyzer.ai_enabled
        assert analyzer.ai_provider == 'phind'
        assert analyzer.is_available()
    
    def test_enable_ai_groq_without_key(self):
        """Test enabling AI with Groq but no API key."""
        self.config.config['ai']['enabled'] = True
        self.config.config['ai']['provider'] = 'groq'
        self.config.config['ai']['groq_api_key'] = ''  # Explicitly set empty key
        
        analyzer = AIAnalyzer(self.config)
        assert analyzer.ai_enabled
        assert analyzer.ai_provider == 'groq'
        assert not analyzer.is_available()  # No API key
    
    def test_enable_ai_groq_with_key(self):
        """Test enabling AI with Groq and API key."""
        self.config.config['ai']['enabled'] = True
        self.config.config['ai']['provider'] = 'groq'
        self.config.config['ai']['groq_api_key'] = 'test-key'
        
        with patch('code_doc_gen.ai_analyzer.GROQ_AVAILABLE', True):
            analyzer = AIAnalyzer(self.config)
            assert analyzer.ai_enabled
            assert analyzer.ai_provider == 'groq'
            assert analyzer.is_available()
    
    def test_create_python_prompt(self):
        """Test Python prompt creation."""
        self.config.config['ai']['enabled'] = True
        analyzer = AIAnalyzer(self.config)
        
        prompt = analyzer._create_python_prompt(
            "def calculate_sum(a: int, b: int) -> int:",
            "return a + b"
        )
        
        assert "Python function" in prompt
        assert "PEP 257 docstring" in prompt
        assert "def calculate_sum(a: int, b: int) -> int:" in prompt
        assert "return a + b" in prompt
    
    def test_create_cpp_prompt(self):
        """Test C++ prompt creation."""
        self.config.config['ai']['enabled'] = True
        analyzer = AIAnalyzer(self.config)
        
        prompt = analyzer._create_cpp_java_prompt(
            "int calculate_sum(int a, int b)",
            "return a + b;",
            "c++"
        )
        
        assert "C++ function" in prompt
        assert "Doxygen-style" in prompt
        assert "int calculate_sum(int a, int b)" in prompt
        assert "return a + b;" in prompt
    
    def test_get_function_signature_python(self):
        """Test Python function signature extraction."""
        signature = self.analyzer._get_function_signature(self.sample_function, "python")
        assert signature == "def calculate_sum(a: int, b: int) -> int:"
    
    def test_get_function_signature_cpp(self):
        """Test C++ function signature extraction."""
        signature = self.analyzer._get_function_signature(self.sample_function, "c++")
        assert signature == "int calculate_sum(int a, int b)"
    
    @patch('code_doc_gen.ai_analyzer.requests.post')
    def test_call_phind_success(self, mock_post):
        """Test successful Phind API call."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '"""Adds two numbers together."""'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        self.config.config['ai']['enabled'] = True
        self.config.config['ai']['provider'] = 'phind'
        analyzer = AIAnalyzer(self.config)
        
        response = analyzer._call_phind("test prompt")
        assert response == '"""Adds two numbers together."""'
    
    @patch('code_doc_gen.ai_analyzer.requests.post')
    def test_call_phind_failure(self, mock_post):
        """Test failed Phind API call."""
        mock_post.side_effect = Exception("Network error")
        
        self.config.config['ai']['enabled'] = True
        self.config.config['ai']['provider'] = 'phind'
        analyzer = AIAnalyzer(self.config)
        
        response = analyzer._call_phind("test prompt")
        assert response is None
    
    @patch('code_doc_gen.ai_analyzer.groq')
    def test_call_groq_success(self, mock_groq):
        """Test successful Groq API call."""
        # Mock Groq client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '"""Adds two numbers together."""'
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq.Groq.return_value = mock_client
        
        self.config.config['ai']['enabled'] = True
        self.config.config['ai']['provider'] = 'groq'
        self.config.config['ai']['groq_api_key'] = 'test-key'
        
        with patch('code_doc_gen.ai_analyzer.GROQ_AVAILABLE', True):
            analyzer = AIAnalyzer(self.config)
            response = analyzer._call_groq("test prompt")
            assert response == '"""Adds two numbers together."""'
    
    def test_parse_ai_response_python(self):
        """Test parsing AI response for Python."""
        response = '"""Adds two numbers together."""'
        parsed = self.analyzer._parse_ai_response(response, "python")
        assert parsed == '"""Adds two numbers together."""'
    
    def test_parse_ai_response_cpp(self):
        """Test parsing AI response for C++."""
        response = 'Adds two numbers together.'
        parsed = self.analyzer._parse_ai_response(response, "c++")
        assert parsed == "/**\n * Adds two numbers together.\n */"
    
    def test_parse_ai_response_with_markdown(self):
        """Test parsing AI response with markdown formatting."""
        response = '```\n"""Adds two numbers together."""\n```'
        parsed = self.analyzer._parse_ai_response(response, "python")
        assert parsed == '"""Adds two numbers together."""'
    
    def test_analyze_function_ai_disabled(self):
        """Test function analysis when AI is disabled."""
        result = self.analyzer.analyze_function(self.sample_function, "python")
        assert result is None
    
    @patch('code_doc_gen.ai_analyzer.requests.post')
    def test_analyze_function_ai_success(self, mock_post):
        """Test successful AI function analysis."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '"""Adds two numbers together."""'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        self.config.config['ai']['enabled'] = True
        self.config.config['ai']['provider'] = 'phind'
        analyzer = AIAnalyzer(self.config)
        
        result = analyzer.analyze_function(self.sample_function, "python")
        assert result == '"""Adds two numbers together."""'
    
    @patch('code_doc_gen.ai_analyzer.requests.post')
    def test_analyze_function_ai_failure_fallback(self, mock_post):
        """Test AI function analysis with fallback on failure."""
        # Mock failed response
        mock_post.side_effect = Exception("Network error")
        
        self.config.config['ai']['enabled'] = True
        self.config.config['ai']['provider'] = 'phind'
        analyzer = AIAnalyzer(self.config)
        
        result = analyzer.analyze_function(self.sample_function, "python")
        assert result is None  # Should return None for fallback
    
    def test_get_provider_info(self):
        """Test getting provider information."""
        self.config.config['ai']['enabled'] = True
        self.config.config['ai']['provider'] = 'phind'
        analyzer = AIAnalyzer(self.config)
        
        info = analyzer.get_provider_info()
        assert info['enabled'] is True
        assert info['provider'] == 'phind'
        assert info['available'] is True
    
    def test_get_provider_info_groq(self):
        """Test getting provider information for Groq."""
        self.config.config['ai']['enabled'] = True
        self.config.config['ai']['provider'] = 'groq'
        self.config.config['ai']['groq_api_key'] = 'test-key'
        
        with patch('code_doc_gen.ai_analyzer.GROQ_AVAILABLE', True):
            analyzer = AIAnalyzer(self.config)
            info = analyzer.get_provider_info()
            
            assert info['enabled'] is True
            assert info['provider'] == 'groq'
            assert info['available'] is True
            assert info['groq_available'] is True
            assert info['api_key_configured'] is True 