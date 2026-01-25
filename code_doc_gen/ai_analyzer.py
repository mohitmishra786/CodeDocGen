"""
AI-powered analyzer for CodeDocGen.

Provides AI-powered comment generation using multiple AI providers,
with robust fallback mechanisms and intelligent response parsing.
"""

import json
import logging
import time
import re
from typing import Dict, Optional, List, Any
from pathlib import Path

from .models import Function, Parameter
from .config import Config
from .ai_providers import AIProvider, GroqProvider, OpenAIProvider, AnthropicProvider, MistralProvider

class AIAnalyzer:
    """AI-powered analyzer for generating intelligent function comments."""
    
    def __init__(self, config: Config):
        """
        Initialize the AI analyzer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # AI configuration
        ai_config = config.get_ai_config()
        self.ai_enabled = ai_config.get('enabled', False)
        self.ai_provider_name = ai_config.get('provider', 'groq')
        self.fallback_providers_names = ai_config.get('fallback_providers', ['openai'])
        self.max_retries = ai_config.get('max_retries', 5)
        self.retry_delay = ai_config.get('retry_delay', 1.0)
        
        # Load API keys
        self.api_keys = {
            'groq': ai_config.get('groq_api_key', ''),
            'openai': ai_config.get('openai_api_key', ''),
            'azure_openai': ai_config.get('azure_openai_api_key', ''),
            'anthropic': ai_config.get('anthropic_api_key', ''),
            'mistral': ai_config.get('mistral_api_key', '')
        }
        
        # Azure specific config
        self.azure_config = {
            'endpoint': ai_config.get('azure_endpoint', ''),
            'deployment': ai_config.get('azure_deployment', 'gpt-4'),
            'api_version': ai_config.get('azure_api_version', '2023-05-15')
        }
        
        # Models configuration
        self.models_config = ai_config.get('models', {
            'groq': ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768'],
            'openai': 'gpt-4o-mini',
            'azure_openai': self.azure_config['deployment'],
            'anthropic': 'claude-3-haiku-20240307',
            'mistral': 'mistral-small-latest'
        })
        
        # Initialize providers map
        self.providers: Dict[str, AIProvider] = {}
        
    def _get_provider(self, name: str) -> Optional[AIProvider]:
        """Lazy load provider instance."""
        if name in self.providers:
            return self.providers[name]
            
        key = self.api_keys.get(name, "")
        model = self.models_config.get(name)
        
        provider: Optional[AIProvider] = None
        if name == 'groq':
            provider = GroqProvider(key, model)
        elif name == 'openai':
            provider = OpenAIProvider(key, model)
        elif name == 'azure_openai':
            from .ai_providers.azure_openai import AzureOpenAIProvider
            provider = AzureOpenAIProvider(
                api_key=key, 
                endpoint=self.azure_config['endpoint'],
                deployment_name=self.azure_config['deployment'],
                api_version=self.azure_config['api_version']
            )
        elif name == 'anthropic':
            provider = AnthropicProvider(key, model)
        elif name == 'mistral':
            provider = MistralProvider(key, model)
            
        if provider:
            self.providers[name] = provider
            
        return provider

    def analyze_function(self, function: Function, language: str) -> Optional[str]:
        """
        Analyze a function using AI and return a cleaned, provider-style response.
        """
        if not self.ai_enabled:
            return None
        # Double-check live config
        if not self.config.get_ai_config().get('enabled', False):
            return None
            
        if not self.is_available():
            return None

        try:
            prompt = self._create_ai_prompt(function, language)
            raw_response = self._get_ai_response(prompt)
            if not raw_response:
                return None
            return self._parse_ai_response(raw_response, language)
        except (ValueError, AttributeError, RuntimeError) as e:
            self.logger.warning(f"AI analysis failed for function {function.name}: {e}")
            return None
        except Exception:
            self.logger.exception(f"Unexpected error during AI analysis for {function.name}")
            return None

    def _get_ai_response(self, prompt: str) -> Optional[str]:
        """
        Get response from AI provider with comprehensive fallback.
        """
        # Define provider order: primary + fallbacks
        providers_to_try = [self.ai_provider_name] + [p for p in self.fallback_providers_names if p != self.ai_provider_name]
        
        for provider_name in providers_to_try:
            provider = self._get_provider(provider_name)
            if provider and provider.is_available():
                self.logger.info(f"Trying {provider_name} as {'primary' if provider_name == self.ai_provider_name else 'fallback'}...")
                
                # Retry logic
                for attempt in range(self.max_retries):
                    try:
                        response = provider.generate_documentation(prompt)
                        if response:
                            self.logger.debug(f"{provider_name} response received")
                            return response
                    except Exception as e:
                        self.logger.warning(f"{provider_name} call attempt {attempt + 1} failed: {e}")
                        if attempt < self.max_retries - 1:
                            delay = self.retry_delay * (2 ** attempt)
                            time.sleep(delay)
                            
        self.logger.warning("All AI providers failed")
        return None

    def is_available(self) -> bool:
        """Check if AI analysis is available."""
        if not self.ai_enabled:
            return False
            
        # Check primary
        p = self._get_provider(self.ai_provider_name)
        if p and p.is_available():
            return True
            
        # Check fallbacks
        for name in self.fallback_providers_names:
            p = self._get_provider(name)
            if p and p.is_available():
                return True
                
        return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available AI providers."""
        available = self.is_available()
        info: Dict[str, Any] = {
            'enabled': self.ai_enabled,
            'provider': self.ai_provider_name,
            'available': available,
        }
        # Backward compatibility for tests
        if self.ai_provider_name == 'groq':
            p = self._get_provider('groq')
            info['groq_available'] = p.is_available() if p else False
            info['api_key_configured'] = bool(self.api_keys.get('groq'))
        return info

    # -------------------------------------------------------------------------
    # Prompt Creation & Parsing Logic (Preserved from original)
    # -------------------------------------------------------------------------

    def _create_ai_prompt(self, function: Function, language: str) -> str:
        signature = self._get_function_signature(function, language)
        body = function.source_code or ""
        
        if language == 'python':
            return self._create_python_prompt(signature, body)
        elif language in ['c++', 'java']:
            return self._create_cpp_java_prompt(signature, body, language)
        else:
            return self._create_generic_prompt(signature, body, language)

    def _create_python_prompt(self, signature: str, body: str) -> str:
        if len(body) > 2000:
            body = body[:2000] + "..."
        return f"""Generate a concise, professional PEP 257 docstring for this Python function.
Focus on the function's intent, key operations, and make it context-aware.

Function:
{signature}

Function body:
{body}

CRITICAL INSTRUCTIONS:
1. Output ONLY the raw docstring content that goes INSIDE the triple quotes
2. Do NOT include any triple quotes in your response
3. Do NOT include any introductory text like "Here is the docstring:"
4. Do NOT include any parameter annotations like ":param name: description" at the end
5. Do NOT include any formatting markers or code blocks
6. Do NOT include any artifacts or extra text

EXACT FORMAT TO FOLLOW:
Brief description of what the function does.

Parameters:
    param_name (type): Description of the parameter.

Returns:
    type: Description of the return value.

Raises:
    ExceptionType: Description of when this exception is raised.

Example output (without triple quotes):
Searches for a target value in a sorted array using binary search.

Parameters:
    arr (List[int]): A sorted list of integers.
    target (int): The value to search for.

Returns:
    Optional[int]: The index of the target value if found, None otherwise."""

    def _create_cpp_java_prompt(self, signature: str, body: str, language: str) -> str:
        comment_style = "Doxygen-style" if language == 'c++' else "Javadoc-style"
        tag_prefix = "\\" if language == 'c++' else "@"
        
        if len(body) > 2000:
            body = body[:2000] + "..."
        
        return f"""Generate a concise, professional {comment_style} comment for this {language.upper()} function.
Focus on the function's intent, key operations, and make it context-aware.

Function:
{signature}

Function body:
{body}

CRITICAL INSTRUCTIONS:
1. Output ONLY the raw comment content that goes INSIDE the comment markers
2. Do NOT include any comment markers in your response
3. Do NOT include any introductory text like "Here is the comment:"
4. Do NOT include any parameter annotations like "{tag_prefix}param name description" at the end
5. Do NOT include any formatting markers or code blocks
6. Do NOT include any artifacts or extra text

EXACT FORMAT TO FOLLOW:
{tag_prefix}brief Brief description of what the function does.

{tag_prefix}param param_name Description of the parameter.
{tag_prefix}return Description of the return value.
{tag_prefix}throws ExceptionType Description of when this exception is raised.

Example output (without comment markers):
{tag_prefix}brief Computes the greatest common divisor of two integers using Euclidean algorithm.

{tag_prefix}param a The first integer.
{tag_prefix}param b The second integer.
{tag_prefix}return The greatest common divisor of a and b."""

    def _create_generic_prompt(self, signature: str, body: str, language: str) -> str:
        if len(body) > 2000:
            body = body[:2000] + "..."
        
        return f"""Generate a concise, professional comment for this {language} function.
Include a brief description, parameter details, return value, and exceptions if applicable.
Focus on the function's intent, key operations, and make it context-aware.

Function:
{signature}

Function body:
{body}

IMPORTANT: Output ONLY the comment block without any additional text, explanations, or code.
Do NOT include introductory text like "Here is the comment:" or similar."""

    def _get_function_signature(self, function: Function, language: str) -> str:
        params = []
        for param in function.parameters:
            if language == 'python':
                params.append(f"{param.name}: {param.type}")
            else:
                params.append(f"{param.type} {param.name}")
        
        param_str = ", ".join(params)
        
        if language == 'python':
            return f"def {function.name}({param_str}) -> {function.return_type}:"
        else:
            return f"{function.return_type} {function.name}({param_str})"

    def _parse_ai_response(self, response: str, language: str) -> str:
        raw = response.strip()
        if language == 'python':
            # Handle code-fenced docstring
            fenced = re.search(r'^```(?:\w+\n)?(.*?)```$', raw, flags=re.DOTALL)
            if fenced:
                inner = fenced.group(1).strip()
                if inner.startswith('"""') and inner.endswith('"""'):
                    return inner
                raw = inner
            if raw.startswith('"""') and raw.endswith('"""'):
                return raw

        cleaned = self._remove_boundary_markers(raw, language)
        cleaned = re.sub(r'^```.*?```$', '', cleaned, flags=re.DOTALL)

        content = self._extract_clean_content(cleaned)
        if not content.strip():
            return self._generate_fallback_docstring(language)
        if language == 'python':
            return self._format_python_docstring(content)
        else:
            return self._format_cpp_java_comment(content, language)

    def _remove_boundary_markers(self, response: str, language: str) -> str:
        if language == 'python':
            response = re.sub(r'"""', '', response)
            response = re.sub(r"'''", '', response)
        else:
            response = re.sub(r'/\*\*?', '', response)
            response = re.sub(r'\*/', '', response)
        return response.strip()

    def _extract_clean_content(self, response: str) -> str:
        artifact_patterns = [
            r'^Here is (the|a) (docstring|comment):?',
            r'^Output( should be)?:?',
            r'^Example( format)?:?',
            r'^For example:',
            r'^Note:',
            r'^IMPORTANT( NOTE)?:?',
            r'^Do NOT include',
            r'^Just provide',
            r'^CRITICAL:',
            r'^Follow( these instructions)?:?',
            r'^(The|Your) (output|response) (should|must)',
            r'^Raises: None$',
            r'^Exceptions: None$',
            r'^Parameters: None$',
            r'^Returns: None$',
            r'^\s*[`*]{3,}\s*$',
            r'^\s*None\s*$'
        ]
        
        response = re.sub(
            r'(Here is (the|a) (docstring|comment):).*?(?=(\n\s*[A-Z]|$))', 
            '', 
            response, 
            flags=re.DOTALL|re.IGNORECASE
        )
        
        lines = response.split('\n')
        clean_lines = []
        
        preserved_patterns = [
            r'^\s*:param\b',
            r'^\s*:return\b',
            r'^\s*:raises?\b',
            r'^\s*\\param\b',
            r'^\s*\\return\b',
            r'^\s*\\throws\b',
            r'^\s*@param\b',
            r'^\s*@return\b',
            r'^\s*@throws\b'
        ]
        
        for line in lines:
            line = line.strip()
            
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in artifact_patterns):
                continue
            
            if any(re.match(p, line) for p in preserved_patterns):
                clean_lines.append(line)
                continue
            
            if (line.startswith('Here is') or
                line.startswith('Generate') or
                line.startswith('Output') or
                line.startswith('Follow') or
                line.startswith('Use') or
                line.startswith('IMPORTANT') or
                line.startswith('Do NOT') or
                line.startswith('Just provide') or
                line.startswith('Example format') or
                line.startswith('CRITICAL') or
                line == 'None' or
                line == '"' or
                line == '*' or
                line.startswith('Raises: None') or
                line.startswith('Exceptions: None')):
                continue
            
            line = re.sub(r'^\s*:\s*param\s+\w+:\s*.*$', '', line)
            line = re.sub(r'^\s*:\s*return:\s*.*$', '', line)
            line = re.sub(r'^\s*:\s*raises?\s+\w+:\s*.*$', '', line)
            
            if line and not line.isspace():
                clean_lines.append(line)
        
        content = '\n'.join(clean_lines)
        content = content.strip()
        
        content = re.sub(r'^\s*(:param|@param|\\param)\s*\w+\s*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'(Raises|Exceptions):\s*\n\s*', '', content)
        content = re.sub(r'(\n\s*){3,}', '\n\n', content)
        
        content = content.strip()
        
        if not content or content.isspace():
            content = "Function documentation."
        
        return content

    def _generate_fallback_docstring(self, language: str) -> str:
        if language == 'python':
            return '"""\n    Function documentation\n    """'
        else:
            return '/**\n * Function documentation\n */'

    def _format_python_docstring(self, content: str) -> str:
        content = re.sub(r'(?<!""")(""")(?!""")', r'\"\"\"', content)
        content = re.sub(r"(?<!''')(''')(?!''')", r"\'\'\'", content)
        
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.isspace():
                cleaned_lines.append(line)
        
        if cleaned_lines:
            docstring_content = '\n    '.join(cleaned_lines)
            return f'"""\n    {docstring_content}\n"""'
        else:
            return '"""\n    Function documentation.\n"""'

    def _format_cpp_java_comment(self, content: str, language: str) -> str:
        if language == 'javascript':
            content = self._normalize_js_content(content)
        
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            line = re.sub(r'^\*+\s*', '', line)
            if language == 'javascript':
                line = re.sub(r'^@return(\b)', r'@returns\1', line)
            if line and not line.isspace():
                cleaned_lines.append(line)
        
        if cleaned_lines:
            comment_content = '\n * '.join(cleaned_lines)
            return f"/**\n * {comment_content}\n */"
        else:
            return "/**\n * Function documentation.\n */"

    def _normalize_js_content(self, content: str) -> str:
        lines = [re.sub(r'^\*+\s*', '', ln.strip()) for ln in content.split('\n')]
        result_lines: List[str] = []
        param_lines: List[str] = []
        returns_line: str = ''
        mode = None
        i = 0
        while i < len(lines):
            ln = lines[i]
            if not ln or ln.lower() in {'none', '*'}:
                i += 1
                continue
            low = ln.lower()
            if low.startswith('parameters:') or low.startswith('parameters'):
                mode = 'params'
                i += 1
                continue
            if low.startswith('returns:') or low.startswith('return value:') or low.startswith('return:'):
                mode = 'returns'
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    desc = re.sub(r'^\*+\s*', '', lines[i].strip())
                    returns_line = f"@returns {desc}"
                    i += 1
                continue
            if ln.startswith('@param') or ln.startswith('@return') or ln.startswith('@returns'):
                if ln.startswith('@return'):
                    ln = re.sub(r'^@return(\b)', r'@returns\1', ln)
                if ln.startswith('@returns') and not returns_line:
                    returns_line = ln
                elif ln.startswith('@param'):
                    param_lines.append(ln)
                i += 1
                continue
            if mode == 'params':
                m = re.match(r'^([A-Za-z_$][\w$]*)\s*[:\-\u2013\u2014]\s*(.+)$', ln)
                if m:
                    name, desc = m.group(1), m.group(2)
                    param_lines.append(f"@param {name} {desc}")
                    i += 1
                    continue
                mode = None
            if not result_lines:
                result_lines.append(ln)
            i += 1
        result_lines.extend(param_lines)
        if returns_line:
            result_lines.append(returns_line)
        return '\n'.join(result_lines)
