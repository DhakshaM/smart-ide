import ast
import unittest
import timeit

def extract_function_info(code):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            args = []
            for arg in node.args.args:
                if arg.annotation:
                    if isinstance(arg.annotation, ast.Name):
                        arg_type = arg.annotation.id
                    elif isinstance(arg.annotation, ast.Subscript):
                        # Handle Subscript (e.g., List[int])
                        # Extract the base type (e.g., List) and the parameters (e.g., int)
                        if isinstance(arg.annotation.value, ast.Name):
                             base_type = arg.annotation.value.id
                        else:
                             base_type = "Unknown"

                        if isinstance(arg.annotation.slice, ast.Index) and isinstance(arg.annotation.slice.value, ast.Name):
                            parameter_type = arg.annotation.slice.value.id
                        else:
                            parameter_type = "Unknown"

                        arg_type = f"{base_type}[{parameter_type}]" #creates a string representation
                    else:
                        arg_type = "Unknown"  # Handle other annotation types if needed
                else:
                    arg_type = 'Any'
                args.append((arg.arg, arg_type))
            docstring = ast.get_docstring(node)
            return function_name, args, docstring
    return None, None, None

def extract_test_class_name(test_code):
    """Extracts the name of the first class that inherits from unittest.TestCase."""
    tree = ast.parse(test_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == 'TestCase' or (isinstance(base, ast.Attribute) and base.attr == 'TestCase'):
                    return node.name
    return None

# Smarter Edge Case Detection (Basic)
def suggest_edge_cases(arg_types):
    edge_cases = {}
    for arg_name, arg_type in arg_types:
        if arg_type == 'int' or arg_type == 'float':
            edge_cases[arg_name] = [-1, 0, 1, 100, -100, float('inf'), float('-inf'), float('nan')]  # Added infinities and NaN
        elif arg_type == 'str':
            edge_cases[arg_name] = ["", " ", "long string", "\n", "\t",  "`~!@#$%^&*()_+=-`"]  # Added whitespace variations
        elif arg_type == 'bool':
            edge_cases[arg_name] = [True, False]
        elif arg_type == 'list':
            edge_cases[arg_name] = [[], [1, 2, 3], [None]]  #Empty list, numbers, and None
        elif arg_type == 'dict':
            edge_cases[arg_name] = [{}, {"a": 1}, {1: "a"}]
        else:
            edge_cases[arg_name] = []  # Add 'Any', or list, dictionary
    return edge_cases

# Exception Handling
def generate_exception_test(function_name, arg_values, exception_type="ValueError"):
    args_str = ", ".join(map(repr, arg_values))
    test_code = f"""
    def test_exception_{function_name}_{args_str.replace(', ', '_')}(self):
        with self.assertRaises({exception_type}):
            {function_name}({args_str})
    """
    return test_code

def analyze_complexity(code):
    """Analyzes code complexity and suggests potential optimizations."""
    tree = ast.parse(code)
    analyzer = ComplexityAnalyzer()
    analyzer.visit(tree)
    return analyzer.get_results()

# Class to analyze code complexity
class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.results = []
        self.loop_depth = 0

    def visit_For(self, node):
        self.loop_depth += 1
        self.generic_visit(node)  # Visit inner nodes
        self.loop_depth -= 1

    def visit_While(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_FunctionDef(self, node): # Function definition
        self.results.append({"message": f"Analyzing Function: {node.name}"}) #add to result

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'sum':
            self.results.append({"message": "Potential O(n) complexity due to `sum` function."})

        self.generic_visit(node) #keep going

    def get_results(self):
        if self.loop_depth > 1:
            self.results.append({"message": "Nested loops detected.  Consider optimizing algorithm to reduce complexity."})
        return self.results

# Function to benchmark code
# unit_testing.py
def benchmark_code(code, function_name, args=None):
    """Benchmarks the execution time of a function."""
    try:
        # Prepare the setup code that defines the function
        setup_code = code

        # Determine the function call string, handling arguments if needed
        if args:
            # Create example arguments for timeit.  Replace with more appropriate values if necessary.
            arg_values = [10 for _ in args] # Example:  Pass 10 as argument for each argument listed
            func_call = f"{function_name}({', '.join(map(str, arg_values))})" #Join all the args
        else:
            func_call = f"{function_name}()"

        # Measure the execution time using timeit
        execution_time = timeit.timeit(func_call, setup=setup_code, number=1000) # Run 1000 times

        return execution_time
    except Exception as e:
        return f"Error during benchmarking: {e}"

# Function to suggest optimizations
def suggest_optimizations(complexity_results):
    """Provides basic optimization suggestions based on complexity analysis."""
    suggestions = []
    for result in complexity_results:
        if "Nested loops" in result["message"]:
            suggestions.append("Consider using a more efficient algorithm (e.g., divide and conquer) to reduce the number of nested loops.")
        if "`sum` function" in result["message"]:
            suggestions.append("If possible, avoid using the `sum` function on large lists.  Consider using an iterative approach for better performance.")
    
    return suggestions