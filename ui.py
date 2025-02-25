# ui.py:
import streamlit as st
import code_generation
import unit_testing
import utils
import unittest
import io
import contextlib
import traceback
import os

def main_page():
    st.title("Intelligent IDE")
    st.write("Welcome! Choose an option below:")

    col1, col2 = st.columns(2) #Improved layout

    with col1:
      if st.button("Code Generation", use_container_width = True):
          st.session_state.page = "code_generation"


    with col2:
      if st.button("Unit Test Generation", use_container_width = True):
          st.session_state.page = "unit_test_generation"

    if st.button("Explanation, Documentation & Performance Profiling", use_container_width=True):
        st.session_state.page = "explanation_doc_perf"


def code_generation_page():
    st.title("Code Generation")
    if st.button("Back to Main Menu", on_click=go_to_main_page):
        pass
    problem_description = st.text_area("Enter Problem Description:", height=100)
    if st.button("Generate Code"):
        if problem_description:
            generated_code = code_generation.generate_code_from_problem(problem_description)
            st.session_state.generated_code = generated_code
            transformed_code = code_generation.transform_code(generated_code)
            st.code(transformed_code, language="python")
        else:
            st.warning("Please enter a problem description.")

def unit_test_generation_page():
    st.title("Unit Test Generation")
    if st.button("Back to Main Menu", on_click=go_to_main_page):
        pass

    if 'generated_code' in st.session_state and st.session_state.generated_code:
        code_input = st.text_area("Enter Python Code:", height=200, value=st.session_state.generated_code)
    else:
        code_input = st.text_area("Enter Python Code:", height=200, value="""""")

    if "test_code" not in st.session_state:
        st.session_state.test_code = ""

    if st.button("Generate Unit Tests"):
        function_name, args, docstring = utils.extract_function_info(code_input)

        if function_name:
            edge_cases = utils.suggest_edge_cases(args)
            st.session_state.test_code = unit_testing.generate_tests_with_api(code_input, function_name, args, docstring, edge_cases)
        else:
            st.error("No function definition found. Please provide valid Python code.")

    test_code_edited = st.text_area("Generated Unit Tests (Editable):", value=st.session_state.test_code, height=300)

    # Test Execution
    st.header("Test Execution")

    if st.button("Run Tests"):
        if test_code_edited:
            try:
                # Dynamically create a test suite
                suite = unittest.TestSuite()

                # Create a temporary module to hold the test code
                module_name = "temp_test_module"
                module = type(os)(module_name)  # Create a dummy module object
                exec(code_input, module.__dict__)
                exec(test_code_edited, module.__dict__)  # Execute the test code within the module

                # Discover and load tests from the dynamically created module
                test_loader = unittest.TestLoader()
                test_class_name = utils.extract_test_class_name(test_code_edited) # Extract name
                if not test_class_name:
                    st.error("Could not find a unittest.TestCase class in the generated tests.")
                     # Skip the rest of the test execution

                test_names = test_loader.getTestCaseNames(getattr(module, test_class_name))  # Use the dynamic name
                for name in test_names:
                    suite.addTest(getattr(module, test_class_name)(name)) #Use the dynamic name

                # Run the tests and capture the output
                with io.StringIO() as buf, contextlib.redirect_stdout(buf):
                    runner = unittest.TextTestRunner(stream=buf, verbosity=2)
                    result = runner.run(suite)
                    test_output = buf.getvalue()

                st.text("Test Results:")
                st.code(test_output)

                if result.errors:
                    st.error("Some tests failed with errors!")
                elif result.failures:
                    st.warning("Some tests failed!")
                else:
                    st.success("All tests passed!")


            except Exception as e:
                st.error(f"Error executing tests: {e}")
                st.error(traceback.format_exc())  # Display the traceback

# ui.py
def explanation_doc_perf_page():
    st.title("Explanation, Documentation & Performance Profiling")
    if st.button("Back to Main Menu", on_click=go_to_main_page):
        pass

    if 'generated_code' in st.session_state and st.session_state.generated_code:
        code_input = st.text_area("Enter Python Code:", height=200, value=st.session_state.generated_code)
    else:
        code_input = st.text_area("Enter Python Code:", height=200, value="""""")


    if st.button("Generate Explanation", use_container_width=True):
        if code_input:
            code_explanation = unit_testing.generate_code_explanation(code_input)
            st.subheader("Code Explanation:")
            st.write(code_explanation)
        else:
            st.warning("Please enter code to explain.")


    if st.button("Generate Documentation", use_container_width=True):
        if code_input:
            markdown_documentation = unit_testing.generate_markdown_documentation(code_input)
            st.subheader("Markdown Documentation:")
            st.markdown(markdown_documentation) #Use markdown to render
        else:
            st.warning("Please enter code to document.")


    if st.button("Analyze Performance", use_container_width=True):
        if code_input:
            function_name, args, docstring = utils.extract_function_info(code_input)
            if function_name: #make sure there is a function

                # Big O Complexity Analysis:
                complexity_result = unit_testing.analyze_complexity(code_input)
                st.subheader("Big O Complexity Analysis:")
                st.write(complexity_result)

                # BENCHMARKING: Pass the code to benchmark_code
                benchmarking_result = unit_testing.benchmark_code(code_input, function_name)
                st.subheader("Benchmarking Result:")
                if isinstance(benchmarking_result, (int, float)): # Make sure it is a number.
                    st.write(f"Execution Time: {benchmarking_result:.6f} seconds")  # show result
                else:
                    st.write(benchmarking_result)
            else:
                st.error("No function definition found. Please provide valid Python code.")
        else:
            st.warning("Please enter code to analyze.")
            
def go_to_main_page():
    st.session_state.page = "main"


def main():
    if "page" not in st.session_state:
        st.session_state.page = "main"

    if st.session_state.page == "main":
        main_page()
    elif st.session_state.page == "code_generation":
        code_generation_page()
    elif st.session_state.page == "unit_test_generation":
        unit_test_generation_page()
    elif st.session_state.page == "explanation_doc_perf":
        explanation_doc_perf_page()

if __name__ == "__main__":
    main()