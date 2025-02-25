import streamlit as st
import google.generativeai as genai
import os
import ast
import astunparse

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.  Please set this environment variable before running the application.")  # Improved message
genai.configure(api_key=GOOGLE_API_KEY)  # Use the environment variable directly
model = genai.GenerativeModel('gemini-pro')

def generate_code_from_problem(problem_description):
    prompt = f"""You are an expert Python programmer. Generate a complete, runnable Python function that solves the following problem:

    {problem_description}

    Include a docstring explaining the function's purpose, arguments, and return value.

    **Crucially, follow these rules:**

    *   **Error Handling:** If the input is invalid (e.g., negative when it should be positive), raise a ValueError with a clear error message.
    *   **Correctness:** Ensure the function produces the correct output for all valid inputs, including edge cases (e.g., zero, empty list).
    *   **Output Type:** The function must return the correct data type (e.g., a list of integers).

    Return ONLY the code.  Do not include any surrounding text, explanations, or markdown code fences (```python). The code should be able to run without any modifications.
    """
    try:
        response = model.generate_content(prompt)
        generated_code = response.text

        # Strip code fences, if present
        generated_code = generated_code.replace("```python", "").replace("```", "").strip()

        # Basic Post-processing (Error Handling Check - Example)
        if "raise ValueError" not in generated_code and "fibonacci" in problem_description.lower():  #Very specific to the Fibonacci example - makes sure there is negative input handling.
            #If it's fibonacci, and no value error is raised, adds it.
            generated_code = generated_code.replace("def fibonacci(n):",
                                                      """def fibonacci(n):
    if n < 0:
        raise ValueError("Input must be a non-negative integer")""")

    except Exception as e:
        return f"Error generating code: {e}"

    return generated_code

def transform_code(code):
    """Applies code transformations to improve efficiency."""
    tree = ast.parse(code)
    transformer = CodeTransformer()
    new_tree = transformer.visit(tree)
    return astunparse.unparse(new_tree)  # Convert AST back to code

class CodeTransformer(ast.NodeTransformer):
    def visit_For(self, node):
        """Unrolls loops with a fixed number of iterations."""
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
            # Check if range arguments are constants
            range_args = node.iter.args
            if all(isinstance(arg, ast.Constant) for arg in range_args):
                start = range_args[0].value if len(range_args) > 0 else 0
                stop = range_args[0].value if len(range_args) == 1 else range_args[1].value
                step = range_args[2].value if len(range_args) > 2 else 1

                if isinstance(start, int) and isinstance(stop, int) and isinstance(step, int):
                    # Unroll the loop
                    unrolled_code = []
                    for i in range(start, stop, step):
                        for body_node in node.body:
                            # Replace the loop variable with the current value
                            replacer = VariableReplacer(node.target.id, i)
                            new_body_node = replacer.visit(body_node)
                            unrolled_code.append(new_body_node)
                    return unrolled_code
        return node  # Return original node if not unrollable

    def visit_BinOp(self, node):
        """Folds constant expressions."""
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            try:
                # Evaluate the expression
                result = eval(compile(ast.Expression(node), '<string>', 'eval'))
                return ast.Constant(value=result)  # Replace with constant node
            except Exception:
                pass  # Ignore if evaluation fails
        return node

class VariableReplacer(ast.NodeTransformer):
    def __init__(self, variable_name, value):
        self.variable_name = variable_name
        self.value = value

    def visit_Name(self, node):
        """Replaces variable names with a constant value"""
        if node.id == self.variable_name:
            return ast.Constant(value=self.value)
        return node