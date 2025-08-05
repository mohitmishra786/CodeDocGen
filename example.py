#!/usr/bin/env python3
"""
Enhanced Example for CodeDocGen AI-Powered Documentation Generation.

This script demonstrates advanced usage of CodeDocGen with AI-powered
comment generation, featuring complex algorithms and data structures.
"""

import tempfile
import os
import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math
import statistics
from dataclasses import dataclass
from enum import Enum

# Import CodeDocGen modules
from code_doc_gen import generate_docs, generate_cpp_docs, generate_python_docs


class SortAlgorithm(Enum):
    """Enumeration of available sorting algorithms."""
    BUBBLE = "bubble"
    QUICK = "quick"
    MERGE = "merge"
    HEAP = "heap"
    INSERTION = "insertion"


@dataclass
class DataPoint:
    """Represents a single data point with timestamp and value."""
    timestamp: datetime
    value: float
    metadata: Dict[str, str]


def quicksort_algorithm(arr: List[int], low: int = None, high: int = None) -> List[int]:
    """Implement quicksort algorithm with optimized pivot selection."""
    if low is None:
        low = 0
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pivot_index = _median_of_three(arr, low, high)
        arr[high], arr[pivot_index] = arr[pivot_index], arr[high]
        
        pivot = _partition(arr, low, high)
        quicksort_algorithm(arr, low, pivot - 1)
        quicksort_algorithm(arr, pivot + 1, high)
    
    return arr


def _median_of_three(arr: List[int], low: int, high: int) -> int:
    """Select pivot using median-of-three strategy."""
    mid = (low + high) // 2
    
    if arr[low] > arr[mid]:
        arr[low], arr[mid] = arr[mid], arr[low]
    if arr[low] > arr[high]:
        arr[low], arr[high] = arr[high], arr[low]
    if arr[mid] > arr[high]:
        arr[mid], arr[high] = arr[high], arr[mid]
    
    return mid


def _partition(arr: List[int], low: int, high: int) -> int:
    """Partition array around pivot element."""
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def fibonacci_memoization(n: int, memo: Dict[int, int] = None) -> int:
    """Calculate Fibonacci number using memoization for optimization."""
    if memo is None:
        memo = {}
    
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memoization(n - 1, memo) + fibonacci_memoization(n - 2, memo)
    return memo[n]


def dijkstra_shortest_path(graph: Dict[int, List[Tuple[int, float]]], 
                          start: int, 
                          end: int) -> Tuple[List[int], float]:
    """Find shortest path using Dijkstra's algorithm."""
    import heapq
    
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    pq = [(0, start)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        if current_distance > distances[current_node]:
            continue
        
        if current_node == end:
            break
        
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    
    return path, distances[end]


def knapsack_dynamic_programming(weights: List[int], 
                                values: List[int], 
                                capacity: int) -> Tuple[int, List[int]]:
    """Solve 0/1 knapsack problem using dynamic programming."""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(dp[i - 1][w], 
                              dp[i - 1][w - weights[i - 1]] + values[i - 1])
            else:
                dp[i][w] = dp[i - 1][w]
    
    selected_items = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected_items.append(i - 1)
            w -= weights[i - 1]
    
    return dp[n][capacity], selected_items[::-1]


def binary_search_rotated_array(nums: List[int], target: int) -> int:
    """Search for target in rotated sorted array."""
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:
            return mid
        
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1


def longest_common_subsequence(text1: str, text2: str) -> int:
    """Find length of longest common subsequence."""
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]


def rabin_karp_string_matching(text: str, pattern: str, prime: int = 101) -> List[int]:
    """Find all occurrences of pattern in text using Rabin-Karp algorithm."""
    def hash_string(s: str) -> int:
        hash_val = 0
        for char in s:
            hash_val = (hash_val * 256 + ord(char)) % prime
        return hash_val
    
    n, m = len(text), len(pattern)
    if m > n:
        return []
    
    pattern_hash = hash_string(pattern)
    text_hash = hash_string(text[:m])
    
    occurrences = []
    
    for i in range(n - m + 1):
        if pattern_hash == text_hash:
            if text[i:i + m] == pattern:
                occurrences.append(i)
        
        if i < n - m:
            text_hash = (text_hash * 256 - ord(text[i]) * pow(256, m, prime) + ord(text[i + m])) % prime
    
    return occurrences


def merge_k_sorted_lists(lists: List[List[int]]) -> List[int]:
    """Merge k sorted lists efficiently."""
    import heapq
    
    if not lists:
        return []
    
    heap = []
    result = []
    
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))
    
    while heap:
        val, list_idx, element_idx = heapq.heappop(heap)
        result.append(val)
        
        if element_idx + 1 < len(lists[list_idx]):
            next_val = lists[list_idx][element_idx + 1]
            heapq.heappush(heap, (next_val, list_idx, element_idx + 1))
    
    return result


def find_median_of_two_sorted_arrays(nums1: List[int], nums2: List[int]) -> float:
    """Find median of two sorted arrays in O(log(min(m,n))) time."""
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    
    m, n = len(nums1), len(nums2)
    left, right = 0, m
    
    while left <= right:
        partition_x = (left + right) // 2
        partition_y = (m + n + 1) // 2 - partition_x
        
        max_left_x = float('-inf') if partition_x == 0 else nums1[partition_x - 1]
        min_right_x = float('inf') if partition_x == m else nums1[partition_x]
        
        max_left_y = float('-inf') if partition_y == 0 else nums2[partition_y - 1]
        min_right_y = float('inf') if partition_y == n else nums2[partition_y]
        
        if max_left_x <= min_right_y and max_left_y <= min_right_x:
            if (m + n) % 2 == 0:
                return (max(max_left_x, max_left_y) + min(min_right_x, min_right_y)) / 2
            else:
                return max(max_left_x, max_left_y)
        elif max_left_x > min_right_y:
            right = partition_x - 1
        else:
            left = partition_x + 1
    
    raise ValueError("Input arrays are not sorted")


def word_ladder_bfs(begin_word: str, end_word: str, word_list: List[str]) -> int:
    """Find shortest transformation sequence from begin to end word."""
    if end_word not in word_list:
        return 0
    
    word_set = set(word_list)
    queue = [(begin_word, 1)]
    visited = {begin_word}
    
    while queue:
        current_word, level = queue.pop(0)
        
        if current_word == end_word:
            return level
        
        for i in range(len(current_word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = current_word[:i] + c + current_word[i + 1:]
                
                if next_word in word_set and next_word not in visited:
                    visited.add(next_word)
                    queue.append((next_word, level + 1))
    
    return 0


def sudoku_solver(board: List[List[str]]) -> bool:
    """Solve Sudoku puzzle using backtracking."""
    def is_valid(board: List[List[str]], row: int, col: int, num: str) -> bool:
        for x in range(9):
            if board[row][x] == num:
                return False
        
        for x in range(9):
            if board[x][col] == num:
                return False
        
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        
        return True
    
    def solve(board: List[List[str]]) -> bool:
        for i in range(9):
            for j in range(9):
                if board[i][j] == '.':
                    for num in '123456789':
                        if is_valid(board, i, j, num):
                            board[i][j] = num
                            if solve(board):
                                return True
                            board[i][j] = '.'
                    return False
        return True
    
    return solve(board)


def demonstrate_ai_powered_documentation():
    """Demonstrate AI-powered documentation generation."""
    print("=== AI-Powered Documentation Generation Demo ===\n")
    
    # Create a sample file with complex functions
    sample_dir = Path("ai_demo")
    sample_dir.mkdir(exist_ok=True)
    
    # Create a Python file with complex functions
    complex_file = sample_dir / "complex_algorithms.py"
    complex_content = '''#!/usr/bin/env python3
"""
Complex algorithms and data structures for AI documentation testing.
"""

import math
import statistics
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import heapq


def dijkstra_shortest_path(graph: Dict[int, List[Tuple[int, float]]], 
                          start: int, 
                          end: int) -> Tuple[List[int], float]:
    """Find shortest path using Dijkstra's algorithm."""
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    pq = [(0, start)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        if current_distance > distances[current_node]:
            continue
        
        if current_node == end:
            break
        
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    
    return path, distances[end]


def knapsack_dynamic_programming(weights: List[int], 
                                values: List[int], 
                                capacity: int) -> Tuple[int, List[int]]:
    """Solve 0/1 knapsack problem using dynamic programming."""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(dp[i - 1][w], 
                              dp[i - 1][w - weights[i - 1]] + values[i - 1])
            else:
                dp[i][w] = dp[i - 1][w]
    
    selected_items = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected_items.append(i - 1)
            w -= weights[i - 1]
    
    return dp[n][capacity], selected_items[::-1]


def binary_search_rotated_array(nums: List[int], target: int) -> int:
    """Search for target in rotated sorted array."""
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:
            return mid
        
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1


def longest_common_subsequence(text1: str, text2: str) -> int:
    """Find length of longest common subsequence."""
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]


def rabin_karp_string_matching(text: str, pattern: str, prime: int = 101) -> List[int]:
    """Find all occurrences of pattern in text using Rabin-Karp algorithm."""
    def hash_string(s: str) -> int:
        hash_val = 0
        for char in s:
            hash_val = (hash_val * 256 + ord(char)) % prime
        return hash_val
    
    n, m = len(text), len(pattern)
    if m > n:
        return []
    
    pattern_hash = hash_string(pattern)
    text_hash = hash_string(text[:m])
    
    occurrences = []
    
    for i in range(n - m + 1):
        if pattern_hash == text_hash:
            if text[i:i + m] == pattern:
                occurrences.append(i)
        
        if i < n - m:
            text_hash = (text_hash * 256 - ord(text[i]) * pow(256, m, prime) + ord(text[i + m])) % prime
    
    return occurrences


def merge_k_sorted_lists(lists: List[List[int]]) -> List[int]:
    """Merge k sorted lists efficiently."""
    if not lists:
        return []
    
    heap = []
    result = []
    
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))
    
    while heap:
        val, list_idx, element_idx = heapq.heappop(heap)
        result.append(val)
        
        if element_idx + 1 < len(lists[list_idx]):
            next_val = lists[list_idx][element_idx + 1]
            heapq.heappush(heap, (next_val, list_idx, element_idx + 1))
    
    return result


def find_median_of_two_sorted_arrays(nums1: List[int], nums2: List[int]) -> float:
    """Find median of two sorted arrays in O(log(min(m,n))) time."""
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    
    m, n = len(nums1), len(nums2)
    left, right = 0, m
    
    while left <= right:
        partition_x = (left + right) // 2
        partition_y = (m + n + 1) // 2 - partition_x
        
        max_left_x = float('-inf') if partition_x == 0 else nums1[partition_x - 1]
        min_right_x = float('inf') if partition_x == m else nums1[partition_x]
        
        max_left_y = float('-inf') if partition_y == 0 else nums2[partition_y - 1]
        min_right_y = float('inf') if partition_y == n else nums2[partition_y]
        
        if max_left_x <= min_right_y and max_left_y <= min_right_x:
            if (m + n) % 2 == 0:
                return (max(max_left_x, max_left_y) + min(min_right_x, min_right_y)) / 2
            else:
                return max(max_left_x, max_left_y)
        elif max_left_x > min_right_y:
            right = partition_x - 1
        else:
            left = partition_x + 1
    
    raise ValueError("Input arrays are not sorted")


def word_ladder_bfs(begin_word: str, end_word: str, word_list: List[str]) -> int:
    """Find shortest transformation sequence from begin to end word."""
    if end_word not in word_list:
        return 0
    
    word_set = set(word_list)
    queue = [(begin_word, 1)]
    visited = {begin_word}
    
    while queue:
        current_word, level = queue.pop(0)
        
        if current_word == end_word:
            return level
        
        for i in range(len(current_word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = current_word[:i] + c + current_word[i + 1:]
                
                if next_word in word_set and next_word not in visited:
                    visited.add(next_word)
                    queue.append((next_word, level + 1))
    
    return 0


def sudoku_solver(board: List[List[str]]) -> bool:
    """Solve Sudoku puzzle using backtracking."""
    def is_valid(board: List[List[str]], row: int, col: int, num: str) -> bool:
        for x in range(9):
            if board[row][x] == num:
                return False
        
        for x in range(9):
            if board[x][col] == num:
                return False
        
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        
        return True
    
    def solve(board: List[List[str]]) -> bool:
        for i in range(9):
            for j in range(9):
                if board[i][j] == '.':
                    for num in '123456789':
                        if is_valid(board, i, j, num):
                            board[i][j] = num
                            if solve(board):
                                return True
                            board[i][j] = '.'
                    return False
        return True
    
    return solve(board)
'''
    
    complex_file.write_text(complex_content)
    
    print("Created complex algorithms file for AI testing.")
    print("This file contains advanced algorithms that will benefit from AI-generated comments.")
    
    return sample_dir


def test_ai_documentation_generation():
    """Test AI-powered documentation generation."""
    print("\n=== Testing AI Documentation Generation ===\n")
    
    # Create demo directory
    demo_dir = demonstrate_ai_powered_documentation()
    
    # Test with AI enabled
    print("1. Testing with AI enabled (Phind with Groq fallback):")
    try:
        results = generate_docs(demo_dir, lang="python", inplace=True, 
                              enable_ai=True, ai_provider="phind")
        print("✅ AI documentation generation completed!")
        
        # Show some results
        complex_file = demo_dir / "complex_algorithms.py"
        if complex_file.exists():
            print(f"\n--- Generated documentation for {complex_file} ---")
            with open(complex_file, 'r') as f:
                content = f.read()
                # Show first few functions with their documentation
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('def ') and '"""' in line:
                        # Show function and its docstring
                        func_start = i
                        while func_start > 0 and not lines[func_start-1].strip().startswith('"""'):
                            func_start -= 1
                        
                        func_end = i + 1
                        while func_end < len(lines) and not lines[func_end].strip().startswith('"""'):
                            func_end += 1
                        
                        print('\n'.join(lines[func_start:func_end+1]))
                        print('-' * 50)
                        break
        
    except Exception as e:
        print(f"❌ AI documentation generation failed: {e}")
        print("This is expected if AI services are not available.")
    
    # Test without AI (fallback to NLTK)
    print("\n2. Testing without AI (NLTK fallback):")
    try:
        # Create a copy for testing
        test_dir = Path("ai_test_fallback")
        test_dir.mkdir(exist_ok=True)
        
        # Copy the complex file
        import shutil
        shutil.copy(demo_dir / "complex_algorithms.py", test_dir / "complex_algorithms.py")
        
        results = generate_docs(test_dir, lang="python", inplace=True, 
                              enable_ai=False)
        print("✅ NLTK fallback documentation generation completed!")
        
    except Exception as e:
        print(f"❌ NLTK fallback failed: {e}")


def main():
    """Main function to run the enhanced demonstration."""
    print("=== Enhanced CodeDocGen AI-Powered Documentation Demo ===\n")
    
    # Test AI documentation generation
    test_ai_documentation_generation()
    
    print("\n=== Summary ===")
    print("✅ Enhanced example with complex algorithms created")
    print("✅ AI-powered documentation generation tested")
    print("✅ Fallback mechanism tested")
    print("✅ Complex functions that benefit from AI analysis included")
    
    print("\n=== Usage Examples ===")
    print("To test AI documentation generation:")
    print("python -m code_doc_gen.main --repo . --files ai_demo/complex_algorithms.py --enable-ai --ai-provider phind --inplace")
    print()
    print("To test with Groq fallback:")
    print("python -m code_doc_gen.main --repo . --files ai_demo/complex_algorithms.py --enable-ai --ai-provider groq --inplace")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install -r requirements.txt") 