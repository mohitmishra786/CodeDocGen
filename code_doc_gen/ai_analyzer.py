"""
AI-powered analyzer for CodeDocGen.

Provides AI-powered comment generation using multiple AI providers (Phind, Groq, OpenAI),
with robust fallback mechanisms and intelligent response parsing.
"""

import json
import logging
import time
import re
import uuid
import requests
from typing import Dict, Optional, List, Any
from pathlib import Path

try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .models import Function, Parameter
from .config import Config


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
        self.ai_provider = ai_config.get('provider', 'phind')
        self.groq_api_key = ai_config.get('groq_api_key', '')
        self.openai_api_key = ai_config.get('openai_api_key', '')
        self.fallback_providers = ai_config.get('fallback_providers', ['groq', 'openai'])
        self.max_retries = ai_config.get('max_retries', 5)
        self.retry_delay = ai_config.get('retry_delay', 1.0)
        self.models = ai_config.get('models', {
            'phind': 'gpt-3.5-turbo',
            'groq': ['llama3-8b-8192', 'llama3.1-8b-instant', 'llama3-70b-8192'],
            'openai': 'gpt-4o-mini'
        })
        
        # Initialize clients
        self.groq_client = None
        self.openai_client = None
        
        if GROQ_AVAILABLE and self.groq_api_key:
            try:
                self.groq_client = groq.Groq(api_key=self.groq_api_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize Groq client: {e}")
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI client: {e}")
    
    def analyze_function(self, function: Function, language: str) -> Optional[str]:
        """
        Analyze a function using AI to generate intelligent comments.
        
        Args:
            function: Function to analyze
            language: Programming language (c++, python, java)
            
        Returns:
            Generated comment string or None if AI analysis fails
        """
        if not self.ai_enabled:
            return None
        
        try:
            self.logger.debug(f"=== Starting AI analysis for function: {function.name} ===")
            # Use template-based generation for more reliable output
            result = self._generate_template_based_comment(function, language)
            self.logger.debug(f"=== Final result for {function.name}: ===\n{result}\n=== End result ===")
            return result
        except Exception as e:
            self.logger.warning(f"AI analysis failed for function {function.name}: {e}")
            return None
    
    def _generate_template_based_comment(self, function: Function, language: str) -> str:
        """
        Generate comments using AI + template approach for reliable formatting.
        
        Args:
            function: Function to analyze
            language: Programming language
            
        Returns:
            Generated comment string
        """
        self.logger.debug(f"=== Template-based generation for {function.name} ===")
        
        # Step 1: Extract information using AI
        self.logger.debug("Step 1: Extracting function info from AI...")
        ai_info = self._extract_function_info(function, language)
        
        if not ai_info:
            self.logger.debug("AI extraction failed, using basic template")
            # Fallback to basic template
            result = self._generate_basic_template(function, language)
            self.logger.debug(f"Basic template result: {result}")
            return result
        
        self.logger.debug(f"AI info extracted: {ai_info}")
        
        # Step 2: Apply information to language-specific template
        self.logger.debug("Step 2: Applying template...")
        result = self._apply_template(ai_info, language)
        self.logger.debug(f"Template result: {result}")
        return result
    
    def _extract_function_info(self, function: Function, language: str) -> Optional[Dict[str, Any]]:
        """
        Extract function information using AI.
        
        Args:
            function: Function to analyze
            language: Programming language
            
        Returns:
            Dictionary with extracted information or None if failed
        """
        try:
            self.logger.debug(f"=== Extracting function info for {function.name} ===")
            
            # Create a simple extraction prompt
            self.logger.debug("Creating extraction prompt...")
            prompt = self._create_extraction_prompt(function, language)
            self.logger.debug(f"Extraction prompt: {prompt}")
            
            # Get AI response
            self.logger.debug("Getting AI response...")
            response = self._get_ai_response(prompt)
            
            if not response:
                self.logger.debug("No AI response received")
                return None
            
            self.logger.debug(f"Raw AI response: {response}")
            
            # Parse the response into structured information
            self.logger.debug("Parsing extraction response...")
            result = self._parse_extraction_response(response, language)
            self.logger.debug(f"Parsed result: {result}")
            return result
            
        except Exception as e:
            self.logger.warning(f"Failed to extract function info: {e}")
            return None
    
    def _create_extraction_prompt(self, function: Function, language: str) -> str:
        """Create a prompt for extracting function information."""
        signature = self._get_function_signature(function, language)
        body = function.source_code[:1000] if function.source_code else ""
        
        return f"""Analyze this {language} function and extract key information.

Function: {signature}
Body: {body}

Extract and return ONLY a JSON object with these fields:
- "description": Brief description of what the function does
- "parameters": List of parameter descriptions [{{"name": "param_name", "description": "param_desc"}}]
- "returns": Description of return value
- "exceptions": List of exceptions that might be raised [{{"type": "ExceptionType", "description": "when raised"}}]

Example output:
{{
  "description": "Searches for a target value in a sorted array using binary search",
  "parameters": [
    {{"name": "arr", "description": "A sorted list of integers"}},
    {{"name": "target", "description": "The value to search for"}}
  ],
  "returns": "The index of the target value if found, None otherwise",
  "exceptions": [
    {{"type": "ValueError", "description": "If the input array is not sorted"}}
  ]
}}

Return ONLY the JSON object, no other text."""
    
    def _parse_extraction_response(self, response: str, language: str) -> Optional[Dict[str, Any]]:
        """Parse AI response into structured information."""
        try:
            self.logger.debug(f"=== Parsing extraction response ===")
            self.logger.debug(f"Input response: {response}")
            
            # Clean the response
            response = response.strip()
            self.logger.debug(f"Stripped response: {response}")
            
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                self.logger.debug(f"Found JSON: {json_str}")
                result = json.loads(json_str)
                self.logger.debug(f"Parsed JSON: {result}")
                return result
            
            # If no JSON found, try to extract information manually
            self.logger.debug("No JSON found, trying manual extraction...")
            result = self._extract_info_manually(response, language)
            self.logger.debug(f"Manual extraction result: {result}")
            return result
            
        except Exception as e:
            self.logger.warning(f"Failed to parse extraction response: {e}")
            return None
    
    def _extract_info_manually(self, response: str, language: str) -> Dict[str, Any]:
        """Extract information manually from AI response."""
        self.logger.debug(f"=== Manual extraction ===")
        self.logger.debug(f"Input response: {repr(response)}")  # Using repr to see exact content
        
        info = {
            "description": "Function documentation",
            "parameters": [],
            "returns": "Function result",
            "exceptions": []
        }
        
        # Try to extract description
        desc_match = re.search(r'"description":\s*"([^"]+)"', response)
        if desc_match:
            info["description"] = desc_match.group(1)
            self.logger.debug(f"Extracted description: {info['description']}")
        
        # Try to extract parameters
        param_matches = re.findall(r'"name":\s*"([^"]+)",\s*"description":\s*"([^"]+)"', response)
        for name, desc in param_matches:
            info["parameters"].append({"name": name, "description": desc})
            self.logger.debug(f"Extracted parameter: {name} = {desc}")
        
        # Try to extract return value
        return_match = re.search(r'"returns":\s*"([^"]+)"', response)
        if return_match:
            info["returns"] = return_match.group(1)
            self.logger.debug(f"Extracted returns: {info['returns']}")
        
        # Try to extract exceptions
        exception_matches = re.findall(r'"type":\s*"([^"]+)",\s*"description":\s*"([^"]+)"', response)
        for exc_type, desc in exception_matches:
            info["exceptions"].append({"type": exc_type, "description": desc})
            self.logger.debug(f"Extracted exception: {exc_type} = {desc}")
        
        self.logger.debug(f"Final manual extraction result: {info}")
        return info
    
    def _apply_template(self, info: Dict[str, Any], language: str) -> str:
        """Apply extracted information to language-specific template."""
        self.logger.debug(f"=== Applying template for {language} ===")
        self.logger.debug(f"Input info: {info}")
        
        if language == 'python':
            result = self._apply_python_template(info)
        else:
            result = self._apply_cpp_java_template(info, language)
        
        self.logger.debug(f"Template result: {result}")
        return result
    
    def _apply_python_template(self, info: Dict[str, Any]) -> str:
        """Apply Python PEP 257 template."""
        self.logger.debug(f"=== Applying Python template ===")
        self.logger.debug(f"Input info: {info}")
        
        lines = []
        
        # Description
        description = info.get("description", "Function documentation")
        lines.append(description)
        lines.append("")
        self.logger.debug(f"Added description: {description}")
        
        # Parameters
        params = info.get("parameters", [])
        if params:
            lines.append("Parameters:")
            for param in params:
                param_line = f"    {param['name']}: {param['description']}"
                lines.append(param_line)
                self.logger.debug(f"Added parameter: {param_line}")
            lines.append("")
        
        # Returns
        returns = info.get("returns", "")
        if returns:
            lines.append("Returns:")
            return_line = f"    {returns}"
            lines.append(return_line)
            self.logger.debug(f"Added returns: {return_line}")
            lines.append("")
        
        # Exceptions
        exceptions = info.get("exceptions", [])
        if exceptions:
            lines.append("Raises:")
            for exc in exceptions:
                exc_line = f"    {exc['type']}: {exc['description']}"
                lines.append(exc_line)
                self.logger.debug(f"Added exception: {exc_line}")
        
        # Format as docstring - CLEAN FORMAT
        content = "\n".join(lines).strip()
        self.logger.debug(f"Content before formatting: {repr(content)}")
        
        result = f'"""\n    {content}\n"""'
        self.logger.debug(f"Final Python template result: {repr(result)}")
        return result
    
    def _apply_cpp_java_template(self, info: Dict[str, Any], language: str) -> str:
        """Apply C++/Java Doxygen/Javadoc template."""
        self.logger.debug(f"=== Applying {language} template ===")
        self.logger.debug(f"Input info: {info}")
        
        tag_prefix = "\\" if language == 'c++' else "@"
        lines = []
        
        # Brief description
        description = info.get('description', 'Function documentation')
        brief_line = f"{tag_prefix}brief {description}"
        lines.append(brief_line)
        lines.append("")
        self.logger.debug(f"Added brief: {brief_line}")
        
        # Parameters
        params = info.get("parameters", [])
        for param in params:
            param_line = f"{tag_prefix}param {param['name']} {param['description']}"
            lines.append(param_line)
            self.logger.debug(f"Added parameter: {param_line}")
        
        # Return value
        returns = info.get("returns", "")
        if returns:
            return_line = f"{tag_prefix}return {returns}"
            lines.append(return_line)
            self.logger.debug(f"Added return: {return_line}")
        
        # Exceptions
        exceptions = info.get("exceptions", [])
        for exc in exceptions:
            exc_line = f"{tag_prefix}throws {exc['type']} {exc['description']}"
            lines.append(exc_line)
            self.logger.debug(f"Added exception: {exc_line}")
        
        # Format as comment - CLEAN FORMAT
        content = "\n * ".join(lines)
        self.logger.debug(f"Content before formatting: {content}")
        
        result = f"/**\n * {content}\n */"
        self.logger.debug(f"Final {language} template result: {result}")
        return result
    
    def _generate_basic_template(self, function: Function, language: str) -> str:
        """Generate a basic template when AI extraction fails."""
        if language == 'python':
            return f'"""\n    {function.name} function\n"""'
        else:
            return f"/**\n * {function.name} function\n */"
    
    def _create_ai_prompt(self, function: Function, language: str) -> str:
        """
        Create a prompt for AI analysis.
        
        Args:
            function: Function to analyze
            language: Programming language
            
        Returns:
            Formatted prompt string
        """
        # Extract function signature and body
        signature = self._get_function_signature(function, language)
        body = function.source_code or ""
        
        # Create language-specific prompt
        if language == 'python':
            return self._create_python_prompt(signature, body)
        elif language in ['c++', 'java']:
            return self._create_cpp_java_prompt(signature, body, language)
        else:
            return self._create_generic_prompt(signature, body, language)
    
    def _create_python_prompt(self, signature: str, body: str) -> str:
        """Create a Python-specific prompt."""
        # Truncate body if too long
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
        """Create a C++/Java-specific prompt."""
        comment_style = "Doxygen-style" if language == 'c++' else "Javadoc-style"
        tag_prefix = "\\" if language == 'c++' else "@"
        
        # Truncate body if too long
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
        """Create a generic prompt for other languages."""
        # Truncate body if too long
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
        """
        Extract function signature for AI analysis.
        
        Args:
            function: Function to analyze
            language: Programming language
            
        Returns:
            Function signature string
        """
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
    
    def _get_ai_response(self, prompt: str) -> Optional[str]:
        """
        Get response from AI provider with comprehensive fallback.
        
        Args:
            prompt: Prompt to send to AI
            
        Returns:
            AI response string or None if failed
        """
        # Define provider order: primary + fallbacks
        providers_to_try = [self.ai_provider] + self.fallback_providers
        
        for provider in providers_to_try:
            if provider == 'phind':
                response = self._try_provider_with_retries('phind', self._call_phind, prompt)
                if response:
                    self.logger.debug(f"Phind response: {repr(response)}")
                    return response
                    
            elif provider == 'groq' and GROQ_AVAILABLE and self.groq_api_key:
                self.logger.info(f"Trying Groq as {'primary' if provider == self.ai_provider else 'fallback'}...")
                response = self._try_provider_with_retries('groq', self._call_groq, prompt)
                if response:
                    self.logger.debug(f"Groq response: {repr(response)}")
                    return response
                    
            elif provider == 'openai' and OPENAI_AVAILABLE and self.openai_api_key:
                self.logger.info(f"Trying OpenAI as {'primary' if provider == self.ai_provider else 'fallback'}...")
                response = self._try_provider_with_retries('openai', self._call_openai, prompt)
                if response:
                    self.logger.debug(f"OpenAI response: {repr(response)}")
                    return response
        
        self.logger.warning("All AI providers failed")
        return None
    
    def _try_provider_with_retries(self, provider_name: str, provider_func, prompt: str) -> Optional[str]:
        """
        Try a provider with exponential backoff retries.
        
        Args:
            provider_name: Name of the provider for logging
            provider_func: Function to call the provider
            prompt: Input prompt
            
        Returns:
            Response or None if all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                response = provider_func(prompt)
                if response:
                    return response
            except Exception as e:
                self.logger.warning(f"{provider_name} call attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
        
        return None
    
    def _call_phind(self, prompt: str) -> Optional[str]:
        """
        Call Phind API with streaming support.
        
        Args:
            prompt: Prompt to send
            
        Returns:
            Response string or None if failed
        """
        try:
            url = "https://api.phind.com/agent/"
            
            headers = {
                'Content-Type': 'application/json',
                'Origin': 'https://www.phind.com',
                'Referer': 'https://www.phind.com/',
                'Accept': 'text/event-stream',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'User-Agent': 'CodeDocGen/1.0'
            }
            
            data = {
                "requested_model": self.models.get('phind', 'gpt-3.5-turbo'),
                "user_input": prompt,
                "message_history": [],
                "anon_user_id": str(uuid.uuid4()),
                "challenge": 0
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60, stream=True)
            response.raise_for_status()
            
            # Handle streaming response
            content = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data_str = line_str[6:]  # Remove 'data: ' prefix
                            if data_str.strip() == '[DONE]':
                                break
                            
                            event_data = json.loads(data_str)
                            if 'choices' in event_data and len(event_data['choices']) > 0:
                                choice = event_data['choices'][0]
                                if 'delta' in choice and 'content' in choice['delta']:
                                    content += choice['delta']['content']
                        except json.JSONDecodeError:
                            continue
            
            return content.strip() if content else None
            
        except requests.exceptions.Timeout:
            self.logger.warning("Phind API call timed out")
        except requests.exceptions.ConnectionError:
            self.logger.warning("Phind API connection error")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                self.logger.warning("Phind API rate limited")
            else:
                self.logger.warning(f"Phind API HTTP error: {e}")
        except Exception as e:
            self.logger.warning(f"Phind API call failed: {e}")
        
        return None
    
    def _call_groq(self, prompt: str) -> Optional[str]:
        """
        Call Groq API with multiple model fallback.
        
        Args:
            prompt: Prompt to send
            
        Returns:
            Response string or None if failed
        """
        if not self.groq_client:
            # Try to initialize the client if we have an API key
            if self.groq_api_key:
                try:
                    self.groq_client = groq.Groq(api_key=self.groq_api_key)
                except Exception as e:
                    self.logger.warning(f"Failed to initialize Groq client: {e}")
                    return None
            else:
                self.logger.warning("Groq client not available")
                return None
        
        # Get Groq models - handle both string and list formats
        groq_models = self.models.get('groq', ['llama3-8b-8192', 'llama3.1-8b-instant', 'llama3-70b-8192'])
        if isinstance(groq_models, str):
            groq_models = [groq_models]
        
        # Try each model in order
        for model in groq_models:
            try:
                self.logger.debug(f"Trying Groq model: {model}")
                response = self.groq_client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                
                if response.choices and len(response.choices) > 0:
                    self.logger.debug(f"Groq model {model} succeeded")
                    return response.choices[0].message.content.strip()
                
            except Exception as e:
                self.logger.warning(f"Groq model {model} failed: {e}")
                continue
        
        self.logger.warning("All Groq models failed")
        return None
    
    def _call_openai(self, prompt: str) -> Optional[str]:
        """
        Call OpenAI API.
        
        Args:
            prompt: Prompt to send
            
        Returns:
            Response string or None if failed
        """
        if not self.openai_client:
            # Try to initialize the client if we have an API key
            if self.openai_api_key:
                try:
                    self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                except Exception as e:
                    self.logger.warning(f"Failed to initialize OpenAI client: {e}")
                    return None
            else:
                self.logger.warning("OpenAI client not available")
                return None
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.models.get('openai', 'gpt-4o-mini'),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.warning(f"OpenAI API call failed: {e}")
        
        return None
    
    def _remove_boundary_markers(self, response: str, language: str) -> str:
        """
        Remove boundary markers from AI response.
        
        Args:
            response: Raw AI response
            language: Programming language
            
        Returns:
            Response with boundary markers removed
        """
        # Remove Python triple quotes - handle nested quotes
        if language == 'python':
            # Remove all triple quotes (both """ and ''')
            response = re.sub(r'"""', '', response)
            response = re.sub(r"'''", '', response)
        # Remove C++/Java comment markers - handle nested markers
        else:
            # Remove all /** and */ markers
            response = re.sub(r'/\*\*?', '', response)  # /** or /*
            response = re.sub(r'\*/', '', response)     # */
        return response.strip()
    
    def _parse_ai_response(self, response: str, language: str) -> str:
        """
        Parse and clean AI response with robust extraction and formatting.
        
        Args:
            response: Raw AI response
            language: Programming language
            
        Returns:
            Cleaned comment string
        """
        # Step 1: Remove boundary markers
        response = self._remove_boundary_markers(response, language)
        
        # Step 2: Remove code blocks
        response = re.sub(r'^```.*?```', '', response, flags=re.DOTALL)
        response = re.sub(r'^```\w*\n', '', response)
        response = re.sub(r'\n```$', '', response)
        
        # Step 3: Extract clean content
        content = self._extract_clean_content(response)
        
        # Step 4: Check for empty content and use fallback
        if not content.strip():
            self.logger.warning("AI returned empty content - using fallback")
            return self._generate_fallback_docstring(language)
        
        # Step 5: Format for target language
        if language == 'python':
            return self._format_python_docstring(content)
        else:
            return self._format_cpp_java_comment(content, language)
    
    def _generate_fallback_docstring(self, language: str) -> str:
        """
        Generate a fallback docstring when AI returns empty content.
        
        Args:
            language: Programming language
            
        Returns:
            Fallback docstring string
        """
        if language == 'python':
            return '"""\n    Function documentation\n    """'
        else:
            return '/**\n * Function documentation\n */'
    
    def _extract_clean_content(self, response: str) -> str:
        """
        Extract clean content from AI response by removing all artifacts.
        
        Args:
            response: Raw AI response
            
        Returns:
            Clean content without artifacts
        """
        # Define comprehensive artifact patterns
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
            r'^\s*[`*]{3,}\s*$',  # Markdown code blocks
            r'^\s*None\s*$'
        ]
        
        # Remove multi-line artifacts
        response = re.sub(
            r'(Here is (the|a) (docstring|comment):).*?(?=(\n\s*[A-Z]|$))', 
            '', 
            response, 
            flags=re.DOTALL|re.IGNORECASE
        )
        
        # Split into lines and process each line
        lines = response.split('\n')
        clean_lines = []
        
        # Define preserved patterns for valid tags
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
            
            # Check if line matches any artifact pattern
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in artifact_patterns):
                continue
            
            # Check if line should be preserved (valid tags)
            if any(re.match(p, line) for p in preserved_patterns):
                clean_lines.append(line)
                continue
            
            # Skip lines that are just artifacts
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
            
            # Remove any remaining artifacts from the line
            line = re.sub(r'^\s*:\s*param\s+\w+:\s*.*$', '', line)
            line = re.sub(r'^\s*:\s*return:\s*.*$', '', line)
            line = re.sub(r'^\s*:\s*raises?\s+\w+:\s*.*$', '', line)
            
            if line and not line.isspace():
                clean_lines.append(line)
        
        content = '\n'.join(clean_lines)
        content = content.strip()
        
        # Edge case handling
        # Remove orphaned tags without content
        content = re.sub(r'^\s*(:param|@param|\\param)\s*\w+\s*$', '', content, flags=re.MULTILINE)
        
        # Remove empty sections
        content = re.sub(r'(Raises|Exceptions):\s*\n\s*', '', content)
        
        # Ensure proper newlines between sections
        content = re.sub(r'(\n\s*){3,}', '\n\n', content)
        
        content = content.strip()
        
        # If content is empty, provide a default
        if not content or content.isspace():
            content = "Function documentation."
        
        return content
    
    def _format_python_docstring(self, content: str) -> str:
        """
        Format content as a proper Python docstring.
        
        Args:
            content: Cleaned content
            
        Returns:
            Properly formatted Python docstring
        """
        # Escape internal triple quotes
        content = re.sub(r'(?<!""")(""")(?!""")', r'\"\"\"', content)
        content = re.sub(r"(?<!''')(''')(?!''')", r"\'\'\'", content)
        
        # Split content into lines and clean each line
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.isspace():
                cleaned_lines.append(line)
        
        # Join lines and create proper docstring
        if cleaned_lines:
            docstring_content = '\n    '.join(cleaned_lines)
            return f'"""\n    {docstring_content}\n    """'
        else:
            return '"""\n    Function documentation.\n    """'
    
    def _format_cpp_java_comment(self, content: str, language: str) -> str:
        """
        Format content as a proper C++/Java comment.
        
        Args:
            content: Cleaned content
            language: Programming language (c++ or java)
            
        Returns:
            Properly formatted comment
        """
        # Split content into lines and clean each line
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.isspace():
                cleaned_lines.append(line)
        
        # Join lines and create proper comment
        if cleaned_lines:
            comment_content = '\n * '.join(cleaned_lines)
            return f"/**\n * {comment_content}\n */"
        else:
            return "/**\n * Function documentation.\n */"
    
    def _clean_docstring_content(self, content: str) -> str:
        """
        Clean up docstring content by removing all formatting artifacts.
        
        Args:
            content: Raw docstring content
            
        Returns:
            Cleaned content
        """
        # Remove any remaining docstring markers
        content = content.replace('"""', '').replace("'''", '').replace('/**', '').replace('*/', '')
        
        # Remove common AI response artifacts
        content = re.sub(r'Here is the.*?docstring.*?:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Here is a.*?docstring.*?:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Here is the.*?comment.*?:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Here is the.*?PEP 257.*?:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Generate.*?docstring.*?:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Output.*?comment.*?:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Follow.*?PEP 257.*?:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Use.*?template.*?:', '', content, flags=re.IGNORECASE)
        
        # Remove all parameter annotations at the end
        content = re.sub(r'\s*:\s*param\s+\w+:\s*.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s*:\s*return:\s*.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s*:\s*raises?\s+\w+:\s*.*$', '', content, flags=re.MULTILINE)
        
        # Remove any remaining \commands and artifacts
        content = re.sub(r'\\\w+\s*', '', content)
        content = re.sub(r'\*\s*\\\w+\s*', '', content)  # Remove * \param patterns
        content = re.sub(r'\*\s*@\w+\s*', '', content)   # Remove * @param patterns
        
        # Remove any remaining artifacts at the end
        content = re.sub(r'\s*:\s*param\s+\w+:\s*.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s*:\s*return:\s*.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s*:\s*raises?\s+\w+:\s*.*$', '', content, flags=re.MULTILINE)
        
        # Clean up whitespace and formatting
        content = re.sub(r'\n\s*\n', '\n', content)  # Remove empty lines
        content = re.sub(r'^\s*"\s*$', '', content, flags=re.MULTILINE)  # Remove standalone quotes
        content = re.sub(r'^\s*\*\s*$', '', content, flags=re.MULTILINE)  # Remove standalone asterisks
        content = re.sub(r'^\s*None\s*$', '', content, flags=re.MULTILINE)  # Remove standalone "None"
        content = re.sub(r'^\s*Raises:\s*None\s*$', '', content, flags=re.MULTILINE | re.IGNORECASE)
        content = re.sub(r'^\s*Exceptions:\s*None\s*$', '', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove any trailing artifacts
        content = re.sub(r'\s*Raises:\s*None\s*$', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\s*Exceptions:\s*None\s*$', '', content, flags=re.IGNORECASE)
        
        # Remove any lines that are just artifacts
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip lines that are just artifacts
            if (line.startswith(':param') or 
                line.startswith(':return') or 
                line.startswith(':raises') or
                line.startswith('\\param') or
                line.startswith('\\return') or
                line.startswith('\\throws') or
                line.startswith('@param') or
                line.startswith('@return') or
                line.startswith('@throws') or
                line == 'None' or
                line == '"' or
                line == '*' or
                line.startswith('Raises: None') or
                line.startswith('Exceptions: None')):
                continue
            if line and not line.isspace():
                cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        content = content.strip()
        
        # If content is empty or just whitespace, provide a default
        if not content or content.isspace():
            content = "Function documentation."
        
        return content
    
    def is_available(self) -> bool:
        """
        Check if AI analysis is available.
        
        Returns:
            True if AI is enabled and at least one provider is available
        """
        if not self.ai_enabled:
            return False
        
        # Check primary provider
        if self.ai_provider == 'phind':
            return True  # Phind is always available (no API key required)
        elif self.ai_provider == 'groq':
            return GROQ_AVAILABLE and bool(self.groq_api_key)
        elif self.ai_provider == 'openai':
            return OPENAI_AVAILABLE and bool(self.openai_api_key)
        
        # Check fallback providers
        for provider in self.fallback_providers:
            if provider == 'groq' and GROQ_AVAILABLE and self.groq_api_key:
                return True
            elif provider == 'openai' and OPENAI_AVAILABLE and self.openai_api_key:
                return True
        
        return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about available AI providers.
        
        Returns:
            Dictionary with provider information
        """
        info = {
            'enabled': self.ai_enabled,
            'primary_provider': self.ai_provider,
            'fallback_providers': self.fallback_providers,
            'providers': {}
        }
        
        # Phind info
        info['providers']['phind'] = {
            'available': True,  # Always available
            'requires_key': False,
            'model': self.models.get('phind', 'gpt-3.5-turbo'),
            'note': 'Unofficial API - may be rate-limited or change'
        }
        
        # Groq info
        groq_models = self.models.get('groq', ['llama3-8b-8192', 'llama3.1-8b-instant', 'llama3-70b-8192'])
        if isinstance(groq_models, str):
            groq_models = [groq_models]
        
        info['providers']['groq'] = {
            'available': GROQ_AVAILABLE and bool(self.groq_api_key),
            'requires_key': True,
            'has_key': bool(self.groq_api_key),
            'models': groq_models,
            'primary_model': groq_models[0] if groq_models else 'llama3-8b-8192'
        }
        
        # OpenAI info
        info['providers']['openai'] = {
            'available': OPENAI_AVAILABLE and bool(self.openai_api_key),
            'requires_key': True,
            'has_key': bool(self.openai_api_key),
            'model': self.models.get('openai', 'gpt-4o-mini')
        }
        
        return info 