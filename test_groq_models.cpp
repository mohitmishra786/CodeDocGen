#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <map>
#include <set>
#include <queue>
#include <stack>
#include <sstream>

/**
 * \brief Adds two integers
 * 
 * \param a The first integer to add
 * \param b The second integer to add
 * \return The sum of the two input integers
 */
int add_numbers(int a, int b) {
    return a + b;
}

std::vector<int> filter_even_numbers(const std::vector<int>& numbers) {
    std::vector<int> result;
    for (int num : numbers) {
        if (num % 2 == 0) {
            result.push_back(num);
        }
    }
    return result;
}

std::string reverse_string(const std::string& input) {
    std::string result = input;
    std::reverse(result.begin(), result.end());
    return result;
}

std::vector<int> bubble_sort(std::vector<int> arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                std::swap(arr[j], arr[j + 1]);
            }
        }
    }
    return arr;
}

/**
 * \brief Calculates the nth Fibonacci number
 * 
 * \param n The position of the Fibonacci number to calculate
 * \return The nth Fibonacci number
 */
int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

/**
 * \brief Checks if a given string is a palindrome
 * 
 * \param str A string to check for palindrome
 * \return True if the string is a palindrome, False otherwise
 */
bool is_palindrome(const std::string& str) {
    int left = 0;
    int right = str.length() - 1;
    while (left < right) {
        if (str[left] != str[right]) {
            return false;
        }
        left++;
        right--;
    }
    return true;
}

std::vector<int> merge_sorted_arrays(const std::vector<int>& arr1, const std::vector<int>& arr2) {
    std::vector<int> result;
    int i = 0, j = 0;
    
    while (i < arr1.size() && j < arr2.size()) {
        if (arr1[i] <= arr2[j]) {
            result.push_back(arr1[i]);
            i++;
        } else {
            result.push_back(arr2[j]);
            j++;
        }
    }
    
    while (i < arr1.size()) {
        result.push_back(arr1[i]);
        i++;
    }
    
    while (j < arr2.size()) {
        result.push_back(arr2[j]);
        j++;
    }
    
    return result;
}

std::map<char, int> count_characters(const std::string& text) {
    std::map<char, int> char_count;
    for (char c : text) {
        char_count[c]++;
    }
    return char_count;
}

/**
 * \brief Checks whether a given integer is a prime number
 * 
 * \param n The integer to check for primality
 * \return True if the number is prime, False otherwise
 */
bool is_prime(int n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;
    
    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) {
            return false;
        }
    }
    return true;
}

std::vector<int> find_primes_up_to(int limit) {
    std::vector<int> primes;
    for (int i = 2; i <= limit; i++) {
        if (is_prime(i)) {
            primes.push_back(i);
        }
    }
    return primes;
}

std::string remove_duplicates(const std::string& str) {
    std::set<char> seen;
    std::string result;
    for (char c : str) {
        if (seen.find(c) == seen.end()) {
            seen.insert(c);
            result += c;
        }
    }
    return result;
}

/**
 * \brief Searches for a target value in a sorted array using binary search
 * 
 * \param arr A sorted list of integers
 * \param target The value to search for
 * \return The index of the target value if found, -1 otherwise
 */
int binary_search(const std::vector<int>& arr, int target) {
    int left = 0;
    int right = arr.size() - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}

std::vector<std::string> split_string(const std::string& str, char delimiter) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(str);
    
    while (std::getline(tokenStream, token, delimiter)) {
        tokens.push_back(token);
    }
    return tokens;
}

/**
 * \brief Checks if a string contains balanced parentheses
 * 
 * \param str A string containing parentheses
 * \return True if the string has balanced parentheses, False otherwise
 */
bool is_balanced_parentheses(const std::string& str) {
    std::stack<char> stack;
    std::map<char, char> pairs = {{')', '('}, {']', '['}, {'}', '{'}};
    
    for (char c : str) {
        if (c == '(' || c == '[' || c == '{') {
            stack.push(c);
        } else if (c == ')' || c == ']' || c == '}') {
            if (stack.empty() || stack.top() != pairs[c]) {
                return false;
            }
            stack.pop();
        }
    }
    return stack.empty();
}

std::vector<int> topological_sort(const std::map<int, std::vector<int>>& graph) {
    std::map<int, int> in_degree;
    std::queue<int> queue;
    std::vector<int> result;
    
    for (const auto& pair : graph) {
        in_degree[pair.first] = 0;
    }
    
    for (const auto& pair : graph) {
        for (int neighbor : pair.second) {
            in_degree[neighbor]++;
        }
    }
    
    for (const auto& pair : in_degree) {
        if (pair.second == 0) {
            queue.push(pair.first);
        }
    }
    
    while (!queue.empty()) {
        int node = queue.front();
        queue.pop();
        result.push_back(node);
        
        for (int neighbor : graph.at(node)) {
            in_degree[neighbor]--;
            if (in_degree[neighbor] == 0) {
                queue.push(neighbor);
            }
        }
    }
    
    return result;
}

/**
 * \brief Testing various algorithms and functions
 * 
 * \param 10 First number to add
 * \param 20 Second number to add
 * \param numbers A list of integers
 * \return The sum of the input numbers and a list of even numbers
 */
int main() {
    std::cout << "Testing various algorithms..." << std::endl;
    
    int sum = add_numbers(10, 20);
    std::cout << "Sum: " << sum << std::endl;
    
    std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    std::vector<int> evens = filter_even_numbers(numbers);
    std::cout << "Even numbers: ";
    for (int num : evens) std::cout << num << " ";
    std::cout << std::endl;
    
    std::string text = "Hello World";
    std::string reversed = reverse_string(text);
    std::cout << "Reversed: " << reversed << std::endl;
    
    std::vector<int> unsorted = {64, 34, 25, 12, 22, 11, 90};
    std::vector<int> sorted = bubble_sort(unsorted);
    std::cout << "Sorted: ";
    for (int num : sorted) std::cout << num << " ";
    std::cout << std::endl;
    
    int fib = fibonacci(10);
    std::cout << "Fibonacci(10): " << fib << std::endl;
    
    bool palindrome = is_palindrome("racecar");
    std::cout << "Is palindrome: " << palindrome << std::endl;
    
    return 0;
} 