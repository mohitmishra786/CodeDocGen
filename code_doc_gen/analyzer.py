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
            
        # Also ensure punkt_tab is available for word_tokenize
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
    
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
        
        # Add intelligent behavior description
        if function.body:
            behavior = self._generate_intelligent_behavior_description(function)
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
    
    def _generate_intelligent_behavior_description(self, function: Function) -> str:
        """
        Generate intelligent behavior description using NLTK analysis.
        
        Args:
            function: Function to analyze
            
        Returns:
            Intelligent behavior description
        """
        if not function.body:
            return ""
        
        # Use NLTK to analyze function name and understand its purpose
        func_name = function.name.lower()
        param_names = [p.name.lower() for p in function.parameters]
        param_types = [p.type.lower() for p in function.parameters]
        
        try:
            # Tokenize and analyze function name
            tokens = nltk.word_tokenize(func_name)
            pos_tags = nltk.pos_tag(tokens)
            
            behaviors = []
            
            # Analyze the semantic meaning of the function name
            verbs = [word for word, tag in pos_tags if tag.startswith('VB')]
            nouns = [word for word, tag in pos_tags if tag.startswith('NN')]
            adjectives = [word for word, tag in pos_tags if tag.startswith('JJ')]
            
            # Understand function purpose from name structure
            if len(tokens) == 1:
                word = tokens[0]
                tag = pos_tags[0][1]
                
                if tag.startswith('VB'):
                    # Single verb - understand the action
                    if word in ['traverse', 'visit', 'explore']:
                        behaviors.append("traverses data structures systematically")
                    elif word in ['calculate', 'compute', 'evaluate']:
                        behaviors.append("performs mathematical computations")
                    elif word in ['validate', 'check', 'verify']:
                        behaviors.append("validates input against criteria")
                    elif word in ['process', 'transform', 'convert']:
                        behaviors.append("transforms input data")
                    elif word in ['get', 'retrieve', 'fetch']:
                        behaviors.append("retrieves data from storage")
                    elif word in ['set', 'assign', 'update']:
                        behaviors.append("modifies data or state")
                    else:
                        behaviors.append(f"performs {word} operations")
                
                elif tag.startswith('NN'):
                    # Single noun - understand what it processes
                    if word in ['main', 'entry']:
                        behaviors.append("serves as program entry point")
                    elif word in ['init', 'setup', 'start']:
                        behaviors.append("initializes system or component")
                    elif word in ['cleanup', 'teardown', 'stop']:
                        behaviors.append("cleans up resources")
                    else:
                        behaviors.append(f"processes {word} data")
            
            elif len(tokens) >= 2:
                # Multi-word function names - understand the relationship
                if verbs and nouns:
                    verb = verbs[0]
                    noun = nouns[0]
                    
                    if verb in ['get', 'retrieve', 'fetch']:
                        behaviors.append(f"retrieves {noun} information")
                    elif verb in ['set', 'assign', 'update']:
                        behaviors.append(f"modifies {noun} data")
                    elif verb in ['validate', 'check', 'verify']:
                        behaviors.append(f"validates {noun} format or content")
                    elif verb in ['process', 'transform']:
                        behaviors.append(f"transforms {noun} data")
                    elif verb in ['calculate', 'compute']:
                        behaviors.append(f"calculates {noun} values")
                    else:
                        behaviors.append(f"performs {verb} operations on {noun}")
                
                elif adjectives and nouns:
                    adj = adjectives[0]
                    noun = nouns[0]
                    behaviors.append(f"implements {adj} {noun} algorithm")
                
                elif len(nouns) >= 2:
                    # Noun + Noun patterns like "userManager", "dataProcessor"
                    behaviors.append(f"manages {nouns[0]} {nouns[1]} operations")
            
            # Analyze function body patterns to understand behavior
            if function.body.has_loops:
                if any('list' in t or 'array' in t for t in param_types):
                    behaviors.append("iterates through collection elements")
                elif any('string' in t for t in param_types):
                    behaviors.append("processes string content sequentially")
                elif any('graph' in t or 'tree' in t for t in param_types):
                    behaviors.append("traverses graph or tree structure")
                else:
                    behaviors.append("iterates through data structures")
            
            if function.body.has_conditionals:
                if any('validate' in n or 'check' in n for n in param_names):
                    behaviors.append("evaluates conditions for validation")
                elif any('search' in n for n in param_names):
                    behaviors.append("compares elements during search")
                else:
                    behaviors.append("makes conditional decisions")
            
            if function.body.has_side_effects:
                if any('init' in n or 'setup' in n for n in param_names):
                    behaviors.append("initializes state or resources")
                elif any('add' in n or 'append' in n for n in param_names):
                    behaviors.append("modifies collections")
                else:
                    behaviors.append("modifies internal or external state")
            
            if function.body.has_arithmetic:
                behaviors.append("performs mathematical operations")
            
            if function.body.has_exceptions:
                behaviors.append("handles error conditions with exceptions")
            
            if function.body.has_early_returns:
                behaviors.append("may return early based on conditions")
            
            if behaviors:
                return f"Function {', '.join(behaviors)}."
            return ""
            
        except (LookupError, OSError, ImportError):
            # Fallback to basic analysis without NLTK
            behaviors = []
            
            if function.body.has_loops:
                behaviors.append("iterates through data structures")
            if function.body.has_conditionals:
                behaviors.append("makes conditional decisions")
            if function.body.has_side_effects:
                behaviors.append("modifies state or data")
            if function.body.has_arithmetic:
                behaviors.append("performs calculations")
            if function.body.has_exceptions:
                behaviors.append("handles exceptions")
            if function.body.has_early_returns:
                behaviors.append("may return early")
            
            if behaviors:
                return f"Function {', '.join(behaviors)}."
            return ""
    
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
        Convert a function name to a readable sentence using NLTK.
        
        Args:
            name: Function name
            
        Returns:
            Sentence describing the function
        """
        # Special case for main function
        if name.lower() == 'main':
            return "Entry point of the program."
        
        # Convert camelCase to words
        words = self.camel_case_pattern.findall(name)
        if not words:
            # Convert snake_case to words
            words = name.split('_')
        
        if not words:
            return f"Performs {name} operation."
        
        # Use NLTK for intelligent analysis
        try:
            # Tokenize the words
            tokens = nltk.word_tokenize(' '.join(words))
            pos_tags = nltk.pos_tag(tokens)
            
            # Analyze the structure
            verbs = [word for word, tag in pos_tags if tag.startswith('VB')]
            nouns = [word for word, tag in pos_tags if tag.startswith('NN')]
            adjectives = [word for word, tag in pos_tags if tag.startswith('JJ')]
            
            # Handle different patterns
            if len(tokens) == 1:
                word = tokens[0].lower()
                tag = pos_tags[0][1]
                
                if tag.startswith('VB'):
                    # Single verb - describe the action
                    return f"Executes {word} operation."
                elif tag.startswith('NN'):
                    # Single noun - describe what it processes
                    if word in ['dfs', 'bfs', 'dijkstra', 'kruskal', 'prim']:
                        return f"Implements {word.upper()} algorithm."
                    elif word in ['sort', 'filter', 'map', 'reduce', 'search']:
                        return f"Applies {word} operation to data."
                    elif word in ['init', 'setup', 'start']:
                        return f"Initializes the system or component."
                    elif word in ['cleanup', 'teardown', 'stop']:
                        return f"Cleans up resources and terminates."
                    else:
                        return f"Processes {word} data or operations."
                else:
                    return f"Handles {word} operations."
            
            elif len(tokens) == 2:
                # Two-word patterns
                word1, tag1 = pos_tags[0]
                word2, tag2 = pos_tags[1]
                
                if tag1.startswith('VB') and tag2.startswith('NN'):
                    # Verb + Noun: "getUser", "setValue"
                    return f"{word1.capitalize()} the {word2}."
                elif tag1.startswith('JJ') and tag2.startswith('NN'):
                    # Adjective + Noun: "quickSort", "binarySearch"
                    return f"Implements {word1} {word2} algorithm."
                elif tag1.startswith('NN') and tag2.startswith('NN'):
                    # Noun + Noun: "userManager", "dataProcessor"
                    return f"Manages {word1} {word2} operations."
            
            elif len(tokens) >= 3:
                # Multi-word patterns - use NLTK to understand structure
                if verbs and nouns:
                    verb = verbs[0].lower()
                    noun = nouns[0].lower()
                    return f"{verb.capitalize()} the {noun}."
                elif verbs:
                    verb = verbs[0].lower()
                    return f"{verb.capitalize()} the specified data or values."
                elif nouns:
                    noun = nouns[0].lower()
                    return f"Processes {noun} data or operations."
                else:
                    # Fallback for complex names
                    return f"Handles {name.lower()} operations."
            
            else:
                return f"Processes {name.lower()} operations."
                
        except (LookupError, OSError, ImportError) as e:
            # Fallback to intelligent pattern matching
            word = name.lower()
            
            # Common algorithm patterns
            if word in ['dfs', 'bfs', 'dijkstra', 'kruskal', 'prim', 'bellmanford']:
                return f"Implements {word.upper()} algorithm."
            elif word in ['quicksort', 'mergesort', 'heapsort', 'bubblesort']:
                return f"Implements {word} sorting algorithm."
            elif word in ['binarysearch', 'linearsearch']:
                return f"Implements {word} search algorithm."
            elif word in ['main', 'init', 'setup']:
                return "Initializes or starts the program."
            elif word in ['cleanup', 'teardown', 'destroy']:
                return "Cleans up resources and terminates."
            else:
                return f"Processes {word} operations."
    
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
        Generate a description of the return type using NLTK analysis.
        
        Args:
            function: Function to analyze
            
        Returns:
            Return type description string
        """
        return_type = function.return_type.lower()
        func_name = function.name.lower()
        
        try:
            # Use NLTK to understand function purpose and return type
            tokens = nltk.word_tokenize(func_name)
            pos_tags = nltk.pos_tag(tokens)
            
            verbs = [word for word, tag in pos_tags if tag.startswith('VB')]
            nouns = [word for word, tag in pos_tags if tag.startswith('NN')]
            
            # Understand return type based on function purpose
            if return_type == 'bool':
                if verbs and any(v in ['validate', 'check', 'verify', 'is', 'has'] for v in verbs):
                    return "Returns true if the condition is met, false otherwise."
                else:
                    return "Returns a boolean result of the operation."
            
            elif return_type in ['int', 'integer']:
                if verbs and any(v in ['calculate', 'compute', 'count', 'sum'] for v in verbs):
                    return "Returns the calculated integer result."
                elif nouns and any(n in ['index', 'position', 'size', 'length'] for n in nouns):
                    return "Returns the position, index, or count value."
                else:
                    return "Returns an integer value from the operation."
            
            elif return_type in ['float', 'double']:
                if verbs and any(v in ['calculate', 'compute', 'average', 'mean'] for v in verbs):
                    return "Returns the calculated floating-point result."
                else:
                    return "Returns a floating-point value from the calculation."
            
            elif return_type in ['string', 'str']:
                if verbs and any(v in ['format', 'convert', 'toString'] for v in verbs):
                    return "Returns the formatted or converted string."
                elif verbs and any(v in ['get', 'retrieve'] for v in verbs):
                    return "Returns the retrieved string data."
                else:
                    return "Returns a string value from the operation."
            
            elif return_type in ['list', 'array']:
                if verbs and any(v in ['get', 'retrieve', 'fetch'] for v in verbs):
                    return "Returns the retrieved list of items."
                elif verbs and any(v in ['process', 'filter', 'transform'] for v in verbs):
                    return "Returns the processed list of results."
                else:
                    return "Returns a list of processed values."
            
            elif return_type in ['dict', 'map']:
                if verbs and any(v in ['get', 'retrieve'] for v in verbs):
                    return "Returns the retrieved data as key-value pairs."
                else:
                    return "Returns a dictionary containing structured data."
            
            elif return_type == 'void':
                if verbs and any(v in ['traverse', 'visit', 'explore'] for v in verbs):
                    return "Returns nothing (performs traversal operations)."
                elif verbs and any(v in ['set', 'update', 'modify'] for v in verbs):
                    return "Returns nothing (modifies state or data)."
                else:
                    return "Returns nothing (performs side effects only)."
            
            else:
                return f"Returns a {return_type} value from the operation."
                
        except (LookupError, OSError, ImportError):
            # Fallback to basic type descriptions
            if return_type == 'bool':
                return "Returns true or false based on the operation result."
            elif return_type in ['int', 'integer']:
                return "Returns an integer value from the calculation."
            elif return_type in ['float', 'double']:
                return "Returns a floating-point value from the calculation."
            elif return_type in ['string', 'str']:
                return "Returns a string value or formatted text."
            elif return_type in ['list', 'array']:
                return "Returns a list or array of processed values."
            elif return_type in ['dict', 'map']:
                return "Returns a dictionary containing key-value pairs."
            elif return_type == 'void':
                return "Returns nothing (performs side effects only)."
            else:
                return f"Returns a {return_type} value from the operation."
    
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
        Generate a description for a parameter using NLTK analysis.
        
        Args:
            parameter: Parameter to describe
            
        Returns:
            Parameter description string
        """
        param_name = parameter.name.lower()
        param_type = parameter.type.lower()
        
        try:
            # Use NLTK to understand parameter meaning
            tokens = nltk.word_tokenize(param_name)
            pos_tags = nltk.pos_tag(tokens)
            
            # Analyze parameter name structure
            if len(tokens) == 1:
                word = tokens[0]
                tag = pos_tags[0][1]
                
                if tag.startswith('NN'):
                    # Noun - understand what it represents
                    if word in ['node', 'vertex']:
                        return f"The {word} to process in graph/tree structure."
                    elif word in ['data', 'input', 'value']:
                        return f"The {word} to be processed."
                    elif word in ['result', 'output']:
                        return f"The {word} to store results."
                    elif word in ['list', 'array', 'collection']:
                        return f"The {word} of items to process."
                    elif word in ['count', 'number', 'size']:
                        return f"The {word} value for calculations."
                    elif word in ['id', 'key', 'index']:
                        return f"The {word} for identification."
                    else:
                        return f"The {word} parameter."
                
                elif tag.startswith('JJ'):
                    # Adjective - describe the type
                    return f"The {word} parameter."
                
                else:
                    # Other parts of speech
                    return f"The {word} parameter."
            
            elif len(tokens) >= 2:
                # Multi-word parameter names
                if any(tag.startswith('NN') for _, tag in pos_tags):
                    # Contains nouns - understand the object
                    nouns = [word for word, tag in pos_tags if tag.startswith('NN')]
                    if 'id' in nouns or 'identifier' in nouns:
                        return f"The identifier for the {' '.join(nouns)}."
                    elif 'list' in nouns or 'array' in nouns:
                        return f"The {' '.join(nouns)} to process."
                    else:
                        return f"The {' '.join(nouns)} parameter."
                else:
                    return f"The {param_name} parameter."
            
            else:
                return f"The {param_name} parameter."
                
        except (LookupError, OSError, ImportError):
            # Fallback to type-based description
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