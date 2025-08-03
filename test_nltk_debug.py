#!/usr/bin/env python3
"""
Test script to debug NLTK usage in CodeDocGen
"""

import nltk
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from code_doc_gen.analyzer import NLTKAnalyzer
from code_doc_gen.config import Config
from code_doc_gen.models import Function, Parameter

def test_nltk_usage():
    """Test if NLTK is being used correctly"""
    
    # Create a config
    config = Config()
    
    # Create an analyzer
    analyzer = NLTKAnalyzer(config)
    
    # Create test functions
    dfs_function = Function(
        name="dfs",
        parameters=[Parameter(name="curr", type="int")],
        return_type="void",
        class_name=None,
        function_type="FUNCTION"
    )
    
    main_function = Function(
        name="main",
        parameters=[],
        return_type="int",
        class_name=None,
        function_type="FUNCTION"
    )
    
    # Test NLTK tokenization
    print("Testing NLTK tokenization...")
    try:
        tokens = nltk.word_tokenize("dfs")
        pos_tags = nltk.pos_tag(tokens)
        print(f"Tokens: {tokens}")
        print(f"POS tags: {pos_tags}")
    except Exception as e:
        print(f"NLTK error: {e}")
    
    # Test analyzer
    print("\nTesting analyzer...")
    analyzer.analyze_function(dfs_function)
    analyzer.analyze_function(main_function)
    
    print(f"DFS brief: {dfs_function.brief_description}")
    print(f"DFS detailed: {dfs_function.detailed_description}")
    print(f"Main brief: {main_function.brief_description}")
    print(f"Main detailed: {main_function.detailed_description}")

if __name__ == "__main__":
    test_nltk_usage() 