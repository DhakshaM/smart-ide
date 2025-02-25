import streamlit as st
import google.generativeai as genai
import os
import utils #Import
import timeit
import ast

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.  Please set this environment variable before running the application.")  # Improved message
genai.configure(api_key=GOOGLE_API_KEY)  # Use the environment variable directly
model = genai.GenerativeModel('gemini-pro')

def generate_tests_with_api(code, function_name, args, docstring, edge_cases):
    arg_descriptions = ", ".join(f"{name} ({type})" for name, type in args)
    prompt = f"""You are a highly skilled AI test generator. You will analyze the given information and automatically generate high quality code.
    Generate Python unit tests for the following code using the `unittest` module:

    ```python
    {code}
    ```
    Function Name: {function_name}
    Arguments: {arg_descriptions}
    Docstring: {docstring}
    Edge Cases to Consider: {edge_cases}

    **Crucially, follow these rules when generating tests:**

    *   **Accuracy:** Ensure that the expected output values in your test assertions are absolutely correct. Double-check your work!
    *   **Error Handling Tests:** Always include tests to ensure that the function raises appropriate exceptions (ValueError, TypeError, etc.) when given invalid input.
    *   **Edge Case Tests:**  Include tests for all edge cases provided.
    *   **Comprehensive Coverage:**  Strive for comprehensive test coverage.
    *   **Test Class Name:** The test class should be named Test{function_name.capitalize()}.

    Return ONLY the code.  Do not include any surrounding text, explanations, or markdown code fences (```python).
    """
    try:
        response = model.generate_content(prompt)
        test_code = response.text

        # Strip code fences, if present
        test_code = test_code.replace("```python", "").replace("```", "").strip()

        return test_code
    except Exception as e:
        return f"Error generating tests: {e}"

def generate_code_explanation(code):
    """Generates a human-readable explanation of the code using Gemini."""
    prompt = f"""You are an expert Python programmer and technical writer. Explain the following Python code line by line in a way that is easy to understand for both beginners and experienced developers.

    ```python
    {code}
    ```

    Provide clear and concise explanations for each line, including the purpose of the code, the variables used, and the logic involved. Focus on making it educational. Return the explanations as a string. Do not include any extra explanations that are not direct explanations of the code.
    """
    try:
        response = model.generate_content(prompt)
        explanation = response.text
        return explanation
    except Exception as e:
        return f"Error generating code explanation: {e}"

# Function to generate markdown documentation
def generate_markdown_documentation(code):
    """Generates Markdown-formatted documentation from function signatures and docstrings."""
    try:
        tree = ast.parse(code)
        documentation = ""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_name = node.name
                args = ", ".join([arg.arg for arg in node.args.args])
                docstring = ast.get_docstring(node)
                documentation += f"""
### Function: `{function_name}({args})`

{docstring}
                """
        return documentation
    except Exception as e:
        return f"Error generating documentation: {e}"

def analyze_complexity(code):
    """Analyzes code complexity and uses Gemini to estimate Big O."""
    try:
        prompt = f"""You are an expert software engineer. Analyze the following Python code and provide the Big O notation for its time complexity. Explain your reasoning briefly.

        ```python
        {code}
        ```

        Return ONLY the Big O notation (e.g., O(n), O(log n), O(n^2)) and a short explanation in one line.  Do not include any extra explanations that are not direct explanations of the code.
        """

        response = model.generate_content(prompt)
        complexity_explanation = response.text.strip()
        return complexity_explanation

    except Exception as e:
        return f"Error analyzing complexity: {e}"

# Function to benchmark code
def benchmark_code(code, function_name):
    """Benchmarks the execution time of a function."""
    try:
        # Prepare the setup code that defines the function
        setup_code = code

        # Extract function information to determine if arguments are needed
        func_name, args, docstring = utils.extract_function_info(code)

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