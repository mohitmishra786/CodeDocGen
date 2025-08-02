"""
NLTK-based analyzer for CodeDocGen.

Uses natural language processing to generate human-readable descriptions
from function names, parameters, and code patterns.
"""

import re
import nltk
from typing import List, Dict, Optional, Tuple
from .models import Function, Parameter, FunctionBody, Exception
from .config import Config


class NLTKAnalyzer:
    """NLTK-based analyzer for generating human-readable descriptions."""
    
    def __init__(self, config: Config):
        """
        Initialize the analyzer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self._ensure_nltk_data()
        
        # Common patterns for function name analysis
        self.camel_case_pattern = re.compile(r'([A-Z][a-z0-9]+)')
        self.snake_case_pattern = re.compile(r'_([a-z0-9])')
        self.underscore_pattern = re.compile(r'_+')
        
        # Common prefixes and their meanings
        self.prefix_patterns = {
            'get': 'retrieves',
            'set': 'sets',
            'is': 'checks if',
            'has': 'checks if contains',
            'add': 'adds',
            'remove': 'removes',
            'delete': 'deletes',
            'create': 'creates',
            'update': 'updates',
            'validate': 'validates',
            'compute': 'computes',
            'calculate': 'calculates',
            'process': 'processes',
            'handle': 'handles',
            'parse': 'parses',
            'format': 'formats',
            'convert': 'converts',
            'transform': 'transforms',
            'filter': 'filters',
            'sort': 'sorts',
            'find': 'finds',
            'search': 'searches',
            'load': 'loads',
            'save': 'saves',
            'read': 'reads',
            'write': 'writes',
            'send': 'sends',
            'receive': 'receives',
            'connect': 'connects',
            'disconnect': 'disconnects',
            'start': 'starts',
            'stop': 'stops',
            'init': 'initializes',
            'reset': 'resets',
            'clear': 'clears',
            'copy': 'copies',
            'move': 'moves',
            'merge': 'merges',
            'split': 'splits',
            'join': 'joins',
            'reverse': 'reverses',
            'rotate': 'rotates',
            'shuffle': 'shuffles',
            'randomize': 'randomizes',
            'encrypt': 'encrypts',
            'decrypt': 'decrypts',
            'hash': 'hashes',
            'encode': 'encodes',
            'decode': 'decodes',
            'compress': 'compresses',
            'decompress': 'decompresses',
            'serialize': 'serializes',
            'deserialize': 'deserializes',
            'export': 'exports',
            'import': 'imports',
            'generate': 'generates',
            'build': 'builds',
            'compile': 'compiles',
            'link': 'links',
            'install': 'installs',
            'uninstall': 'uninstalls',
            'configure': 'configures',
            'setup': 'sets up',
            'teardown': 'tears down',
            'cleanup': 'cleans up',
            'finalize': 'finalizes',
            'destroy': 'destroys',
            'release': 'releases',
            'allocate': 'allocates',
            'deallocate': 'deallocates',
            'free': 'frees',
            'lock': 'locks',
            'unlock': 'unlocks',
            'acquire': 'acquires',
            'release': 'releases',
            'wait': 'waits',
            'notify': 'notifies',
            'signal': 'signals',
            'broadcast': 'broadcasts',
            'subscribe': 'subscribes',
            'unsubscribe': 'unsubscribes',
            'publish': 'publishes',
            'consume': 'consumes',
            'produce': 'produces',
            'consume': 'consumes',
            'buffer': 'buffers',
            'cache': 'caches',
            'flush': 'flushes',
            'sync': 'synchronizes',
            'async': 'asynchronizes',
            'queue': 'queues',
            'dequeue': 'dequeues',
            'enqueue': 'enqueues',
            'pop': 'pops',
            'push': 'pushes',
            'peek': 'peeks',
            'poll': 'polls',
            'offer': 'offers',
            'take': 'takes',
            'put': 'puts',
            'get': 'gets',
            'set': 'sets',
            'put': 'puts',
            'take': 'takes',
            'offer': 'offers',
            'poll': 'polls',
            'peek': 'peeks',
            'push': 'pushes',
            'pop': 'pops',
            'enqueue': 'enqueues',
            'dequeue': 'dequeues',
            'queue': 'queues',
            'async': 'asynchronizes',
            'sync': 'synchronizes',
            'flush': 'flushes',
            'cache': 'caches',
            'buffer': 'buffers',
            'consume': 'consumes',
            'produce': 'produces',
            'publish': 'publishes',
            'unsubscribe': 'unsubscribes',
            'subscribe': 'subscribes',
            'broadcast': 'broadcasts',
            'signal': 'signals',
            'notify': 'notifies',
            'wait': 'waits',
            'release': 'releases',
            'acquire': 'acquires',
            'unlock': 'unlocks',
            'lock': 'locks',
            'free': 'frees',
            'deallocate': 'deallocates',
            'allocate': 'allocates',
            'release': 'releases',
            'destroy': 'destroys',
            'finalize': 'finalizes',
            'cleanup': 'cleans up',
            'teardown': 'tears down',
            'setup': 'sets up',
            'configure': 'configures',
            'uninstall': 'uninstalls',
            'install': 'installs',
            'link': 'links',
            'compile': 'compiles',
            'build': 'builds',
            'generate': 'generates',
            'import': 'imports',
            'export': 'exports',
            'deserialize': 'deserializes',
            'serialize': 'serializes',
            'decompress': 'decompresses',
            'compress': 'compresses',
            'decode': 'decodes',
            'encode': 'encodes',
            'hash': 'hashes',
            'decrypt': 'decrypts',
            'encrypt': 'encrypts',
            'randomize': 'randomizes',
            'shuffle': 'shuffles',
            'rotate': 'rotates',
            'reverse': 'reverses',
            'join': 'joins',
            'split': 'splits',
            'merge': 'merges',
            'move': 'moves',
            'copy': 'copies',
            'clear': 'clears',
            'reset': 'resets',
            'init': 'initializes',
            'stop': 'stops',
            'start': 'starts',
            'disconnect': 'disconnects',
            'connect': 'connects',
            'receive': 'receives',
            'send': 'sends',
            'write': 'writes',
            'read': 'reads',
            'save': 'saves',
            'load': 'loads',
            'search': 'searches',
            'find': 'finds',
            'sort': 'sorts',
            'filter': 'filters',
            'transform': 'transforms',
            'convert': 'converts',
            'format': 'formats',
            'parse': 'parses',
            'handle': 'handles',
            'process': 'processes',
            'calculate': 'calculates',
            'compute': 'computes',
            'validate': 'validates',
            'update': 'updates',
            'create': 'creates',
            'delete': 'deletes',
            'remove': 'removes',
            'add': 'adds',
            'has': 'checks if contains',
            'is': 'checks if',
            'set': 'sets',
            'get': 'retrieves'
        }
    
    def _ensure_nltk_data(self) -> None:
        """Ensure required NLTK data is downloaded."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
    
    def analyze_function(self, function: Function) -> None:
        """
        Analyze a function and generate descriptions.
        
        Args:
            function: Function to analyze
        """
        # Generate brief description from function name
        function.brief_description = self._generate_brief_description(function)
        
        # Generate detailed description
        function.detailed_description = self._generate_detailed_description(function)
        
        # Analyze function body
        if function.body:
            self._analyze_function_body(function.body)
    
    def _generate_brief_description(self, function: Function) -> str:
        """
        Generate a brief description from the function name.
        
        Args:
            function: Function to analyze
            
        Returns:
            Brief description string
        """
        # Check custom rules first
        rules = self.config.get_rules()
        for rule in rules:
            pattern = rule.get("pattern", "")
            if re.match(pattern, function.name, re.IGNORECASE):
                template = rule.get("brief", "")
                return self._fill_template(template, function)
        
        # Use prefix patterns
        for prefix, verb in self.prefix_patterns.items():
            if function.name.lower().startswith(prefix.lower()):
                noun = self._extract_noun_from_name(function.name[len(prefix):])
                if function.has_parameters():
                    param_names = function.get_parameter_names()
                    return f"{verb.capitalize()} the {noun} based on {', '.join(param_names)}."
                else:
                    return f"{verb.capitalize()} the {noun}."
        
        # Fallback: convert function name to sentence
        return self._name_to_sentence(function.name)
    
    def _generate_detailed_description(self, function: Function) -> str:
        """
        Generate a detailed description of the function.
        
        Args:
            function: Function to analyze
            
        Returns:
            Detailed description string
        """
        parts = []
        
        # Start with brief description
        if function.brief_description:
            parts.append(function.brief_description)
        
        # Add behavior description
        if function.body:
            behavior = function.body.get_behavior_description()
            if behavior:
                parts.append(behavior)
        
        # Add parameter information
        if function.has_parameters():
            param_desc = self._describe_parameters(function.parameters)
            if param_desc:
                parts.append(param_desc)
        
        # Add return information
        if function.return_type.lower() != 'void':
            return_desc = self._describe_return_type(function)
            if return_desc:
                parts.append(return_desc)
        
        return " ".join(parts)
    
    def _extract_noun_from_name(self, name: str) -> str:
        """
        Extract a noun from a function name.
        
        Args:
            name: Function name
            
        Returns:
            Extracted noun
        """
        if not name:
            return "value"
        
        # Convert camelCase to words
        words = self.camel_case_pattern.findall(name)
        if words:
            # Use the first word as the noun
            return words[0].lower()
        
        # Convert snake_case to words
        words = name.split('_')
        if words:
            # For snake_case, take the second part if it exists
            if len(words) > 1:
                return words[1].lower()
            else:
                return words[0].lower()
        
        return name.lower()
    
    def _name_to_sentence(self, name: str) -> str:
        """
        Convert a function name to a readable sentence.
        
        Args:
            name: Function name
            
        Returns:
            Sentence describing the function
        """
        # Convert camelCase to words
        words = self.camel_case_pattern.findall(name)
        if not words:
            # Convert snake_case to words
            words = name.split('_')
        
        if not words:
            return f"Performs {name} operation."
        
        # Tokenize and tag parts of speech
        try:
            tokens = nltk.word_tokenize(' '.join(words))
            pos_tags = nltk.pos_tag(tokens)
            
            # Find verbs and nouns
            verbs = [word for word, tag in pos_tags if tag.startswith('VB')]
            nouns = [word for word, tag in pos_tags if tag.startswith('NN')]
            
            if verbs and nouns:
                verb = verbs[0].lower()
                noun = nouns[0].lower()
                return f"{verb.capitalize()} the {noun}."
            elif verbs:
                verb = verbs[0].lower()
                return f"{verb.capitalize()} the specified value."
            elif nouns:
                noun = nouns[0].lower()
                return f"Processes the {noun}."
            else:
                return f"Performs {name.lower()} operation."
                
        except (LookupError, OSError, ImportError):
            # Fallback to simple conversion
            return f"Performs {name.lower()} operation."
    
    def _fill_template(self, template: str, function: Function) -> str:
        """
        Fill a template with function information.
        
        Args:
            template: Template string with placeholders
            function: Function to use for filling
            
        Returns:
            Filled template string
        """
        # Extract noun from function name
        noun = self._extract_noun_from_name(function.name)
        
        # Get parameter names
        params = function.get_parameter_names()
        params_str = ', '.join(params) if params else "input"
        
        # Replace placeholders
        result = template.replace("{noun}", noun)
        result = result.replace("{params}", params_str)
        result = result.replace("{name}", function.name)
        
        return result
    
    def _describe_parameters(self, parameters: List[Parameter]) -> str:
        """
        Generate a description of function parameters.
        
        Args:
            parameters: List of parameters
            
        Returns:
            Parameter description string
        """
        if not parameters:
            return ""
        
        param_names = [p.name for p in parameters]
        if len(param_names) == 1:
            return f"Takes {param_names[0]} as input."
        else:
            return f"Takes {', '.join(param_names[:-1])} and {param_names[-1]} as input."
    
    def _describe_return_type(self, function: Function) -> str:
        """
        Generate a description of the return type.
        
        Args:
            function: Function to analyze
            
        Returns:
            Return type description string
        """
        return_type = function.return_type.lower()
        
        if return_type == 'bool':
            return "Returns true or false."
        elif return_type in ['int', 'integer']:
            return "Returns an integer value."
        elif return_type in ['float', 'double']:
            return "Returns a floating-point value."
        elif return_type in ['string', 'str']:
            return "Returns a string value."
        elif return_type in ['list', 'array']:
            return "Returns a list of values."
        elif return_type in ['dict', 'map']:
            return "Returns a dictionary of values."
        elif return_type == 'void':
            return "Returns nothing."
        else:
            return f"Returns a {return_type} value."
    
    def _analyze_function_body(self, body: FunctionBody) -> None:
        """
        Analyze function body for patterns and behaviors.
        
        Args:
            body: Function body to analyze
        """
        # This method would analyze the actual function body
        # For now, we'll set some default behaviors based on common patterns
        # In a real implementation, this would parse the AST and detect patterns
        
        # Example analysis (this would be done by the parsers)
        # body.has_loops = self._detect_loops(ast_node)
        # body.has_conditionals = self._detect_conditionals(ast_node)
        # body.has_exceptions = self._detect_exceptions(ast_node)
        # etc.
        pass
    
    def analyze_parameter(self, parameter: Parameter) -> None:
        """
        Analyze a parameter and generate description.
        
        Args:
            parameter: Parameter to analyze
        """
        if not parameter.description:
            parameter.description = self._generate_parameter_description(parameter)
    
    def _generate_parameter_description(self, parameter: Parameter) -> str:
        """
        Generate a description for a parameter.
        
        Args:
            parameter: Parameter to describe
            
        Returns:
            Parameter description string
        """
        type_desc = self._get_type_description(parameter.type)
        return f"The {parameter.name} {type_desc}."
    
    def _get_type_description(self, type_name: str) -> str:
        """
        Get a human-readable description of a type.
        
        Args:
            type_name: Type name
            
        Returns:
            Type description string
        """
        type_mapping = {
            'int': 'integer value',
            'float': 'floating-point number',
            'double': 'double-precision floating-point number',
            'char': 'character',
            'string': 'string value',
            'str': 'string value',
            'bool': 'boolean value',
            'boolean': 'boolean value',
            'void': 'void value',
            'list': 'list of values',
            'array': 'array of values',
            'dict': 'dictionary of key-value pairs',
            'map': 'map of key-value pairs',
            'tuple': 'tuple of values',
            'set': 'set of unique values',
            'bytes': 'bytes data',
            'object': 'object instance',
            'None': 'None value'
        }
        
        return type_mapping.get(type_name.lower(), f"value of type {type_name}")
    
    def analyze_exception(self, exception: Exception) -> None:
        """
        Analyze an exception and generate description.
        
        Args:
            exception: Exception to analyze
        """
        if not exception.description:
            exception.description = self._generate_exception_description(exception)
    
    def _generate_exception_description(self, exception: Exception) -> str:
        """
        Generate a description for an exception.
        
        Args:
            exception: Exception to describe
            
        Returns:
            Exception description string
        """
        return f"Thrown when {exception.name.lower()} occurs." 