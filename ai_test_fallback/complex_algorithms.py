#!/usr/bin/env python3
"""
Complex algorithms and data structures for AI documentation testing.
"""

import math
import statistics
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import heapq


"""
    Function dijkstra_shortest_path
    :param graph: The graph of type dict[(int, list[tuple[(int, float)]])].
    :param start: The start of type int.
    :param end: The end of type int.
    :return: Value of type Tuple[(List[int], float)]
"""
"""
    Function dijkstra_shortest_path
    :param graph: The graph of type dict[(int, list[tuple[(int, float)]])].
    :param start: The start of type int.
    :param end: The end of type int.
    :return: Value of type Tuple[(List[int], float)]
"""
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


"""
    Function knapsack_dynamic_programming
    :param weights: The weight of type list[int].
    :param values: The values of type list[int].
    :param capacity: The capacity of type int.
    :return: Value of type Tuple[(int, List[int])]
"""
"""
    Function knapsack_dynamic_programming
    :param weights: The weight of type list[int].
    :param values: The values of type list[int].
    :param capacity: The capacity of type int.
    :return: Value of type Tuple[(int, List[int])]
"""
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


"""
    Function binary_search_rotated_array
    :param nums: The nums parameter.
    :param target: The target of type int.
    :return: Integer value
"""
"""
    Function binary_search_rotated_array
    :param nums: The nums parameter.
    :param target: The target of type int.
    :return: Integer value
"""
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


"""
    Function longest_common_subsequence
    :param text1: The text1 parameter.
    :param text2: The text2 parameter.
    :return: Integer value
"""
"""
    Function longest_common_subsequence
    :param text1: The text1 parameter.
    :param text2: The text2 parameter.
    :return: Integer value
"""
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


"""
    Function rabin_karp_string_matching
    :param text: The text to process.
    :param pattern: The form of type str.
    :param prime: The prime of type int.
    :return: Value of type List[int]
"""
"""
    Function rabin_karp_string_matching
    :param text: The text to process.
    :param pattern: The form of type str.
    :param prime: The prime of type int.
    :return: Value of type List[int]
"""
def rabin_karp_string_matching(text: str, pattern: str, prime: int = 101) -> List[int]:
    """Find all occurrences of pattern in text using Rabin-Karp algorithm."""
    """
        Processes the hash string by iterating through collections, modifying state, returning computed result and performing mathematical operations
        :param s: The s parameter.
        :return: Integer value
    """
    """
        Processes the hash string by iterating through collections, modifying state, returning computed result and performing mathematical operations
        :param s: The s parameter.
        :return: Integer value
    """
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


"""
    Function merge_k_sorted_lists
    :param lists: The list of type list[list[int]].
    :return: Value of type List[int]
"""
"""
    Function merge_k_sorted_lists
    :param lists: The list of type list[list[int]].
    :return: Value of type List[int]
"""
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


"""
    Function find_median_of_two_sorted_arrays
    :param nums1: The nums1 parameter.
    :param nums2: The nums2 parameter.
    :return: Floating-point value
    :raises Call: Thrown when call occurs.
"""
"""
    Function find_median_of_two_sorted_arrays
    :param nums1: The nums1 parameter.
    :param nums2: The nums2 parameter.
    :return: Floating-point value
    :raises Call: Thrown when call occurs.
"""
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


"""
    Function word_ladder_bfs
    :param begin_word: The begin_word parameter.
    :param end_word: The end_word parameter.
    :param word_list: The word_list parameter.
    :return: Integer value
"""
"""
    Function word_ladder_bfs
    :param begin_word: The begin_word parameter.
    :param end_word: The end_word parameter.
    :param word_list: The word_list parameter.
    :return: Integer value
"""
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


"""
    Function sudoku_solver
    :param board: The board of type list[list[str]].
    :return: True or false
"""
"""
    Function sudoku_solver
    :param board: The board of type list[list[str]].
    :return: True or false
"""
def sudoku_solver(board: List[List[str]]) -> bool:
    """Solve Sudoku puzzle using backtracking."""
    """
        Is the valid by returning computed result, making conditional decisions, performing mathematical operations, modifying state and iterating through collections
        :param board: The board of type list[list[str]].
        :param row: The row of type int.
        :param col: The col of type int.
        :param num: The number to calculate for.
        :return: True or false
    """
    """
        Function is_valid
        :param board: The board of type list[list[str]].
        :param row: The row of type int.
        :param col: The col of type int.
        :param num: The number to calculate for.
        :return: True or false
    """
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
    
    """
        Processes the solve by returning computed result, making conditional decisions, modifying state, using recursion and iterating through collections
        :param board: The board of type list[list[str]].
        :return: True or false
    """
    """
        Processes the solve by returning computed result, making conditional decisions, modifying state, using recursion and iterating through collections
        :param board: The board of type list[list[str]].
        :return: True or false
    """
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
