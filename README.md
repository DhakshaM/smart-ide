# CarftCode - Intelligent Code Development Environment

## Overview

CraftCode is a Streamlit-based intelligent code development environment that integrates code generation, unit test generation, code explanation, documentation generation and performance profiling. It leverages the power of the Gemini AI model to assist developers in various stages of the software development lifecycle.

## Features

*   **Code Generation:** Generate Python code snippets from natural language problem descriptions.
*   **Unit Test Generation:** Automatically create unit tests for your code using the `unittest` module.
*   **Code Explanation:** Obtain human-readable explanations of Python code.
*   **Documentation Generation:** Generate Markdown-formatted documentation from function signatures and docstrings.
*   **Performance Profiling:** Analyze the Big O complexity of the Python Code and get a benchmarking report of the performance of the code

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python:** Version 3.7 or higher.
*   **pip:** Python package installer.
*   **Streamlit:** For creating the web application.
*   **google-generativeai:** For interacting with the Gemini AI model.
*   **astunparse:** For unparsing the modified ast.
*   **Google Cloud Account and API Key:** Required to use the Gemini AI model.

## Setup Instructions

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/DhakshaM/smart-ide.git
    cd smart-ide
    ```

2.  **Create a Virtual Environment (Recommended):**

    It is highly recommended to create a virtual environment to isolate the project's dependencies.

    ```bash
    python -m venv venv  # Create the virtual environment
    ```

    *   **Activate the virtual environment:**
        *   **Linux/macOS:**
            ```bash
            source venv/bin/activate
            ```
        *   **Windows:**
            ```powershell
            .\venv\Scripts\activate
            ```

3.  **Install Dependencies:**

    Install the required Python packages using pip:

    ```bash
    pip install streamlit google-generativeai astunparse
    ```

4.  **Obtain a Google Cloud API Key:**

    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing project.
    *   Enable the Gemini API for your project.
    *   Create an API key.  See [Google AI for Developers](https://ai.google.dev/) for more details.

5.  **Configure the `GOOGLE_API_KEY` Environment Variable:**

    The Smart IDE requires the `GOOGLE_API_KEY` environment variable to be set. 

    *   **Linux/macOS:**

        ```bash
        export GOOGLE_API_KEY="YOUR_ACTUAL_API_KEY"
        ```

        Add this line to your shell configuration file (e.g., `~/.bashrc`, `~/.zshrc`) for persistent storage.

    *   **Windows:**

        ```powershell
        $env:GOOGLE_API_KEY="YOUR_ACTUAL_API_KEY"
        ```

        To set it permanently, use the System Properties dialog (search for "environment variables" in the Start menu).

    Replace `"YOUR_ACTUAL_API_KEY"` with your Google Cloud API key.

## Running the Application

1.  **Activate the virtual environment (if you haven't already).**
2.  **Run the Streamlit application:**

    ```bash
    streamlit run app.py
    ```

    This will start the Streamlit server and open the Smart IDE in your web browser.

## Usage

1.  **Code Generation:**
    *   Navigate to the "Code Generation" page.
    *   Enter a description of the problem you want to solve in the "Enter Problem Description" text area.
    *   Click the "Generate Code" button.  The generated code will be displayed below.
2.  **Unit Test Generation:**
    *   Navigate to the "Unit Test Generation" page.
    *   Enter the Python code you want to test in the "Enter Python Code" text area.
    *   Click the "Generate Unit Tests" button.  The generated unit tests will be displayed below.
    *   You can edit the generated tests and then click the "Run Tests" button to execute them.
3.  **Explanation, Documentation, and Performance Profiling:**
    *   Navigate to the "Explanation, Documentation & Performance Profiling" page.
    *   Enter the Python code you want to analyze in the "Enter Python Code" text area.
    *   Click the "Generate Explanation" button to get a line-by-line explanation of the code.
    *   Click the "Generate Documentation" button to generate Markdown-formatted documentation.
    *   Click the "Analyze Performance" button to get the Big O complexity and benchmarking results.
