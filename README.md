# AI-Powered Resume Analyzer (v1.0)

This is a web application built with Python and Streamlit that uses Google's Gemini API to analyze resumes. It extracts key information, assesses strengths and weaknesses for a specific job role, provides improvement suggestions, and offers other valuable insights to help job seekers enhance their resumes.

## Features

*   **Resume Upload:** Supports PDF and TXT file formats.
*   **API Key Management:** Securely load your Google Gemini API key via Streamlit secrets (for deployment), a local `.env` file, or direct input in the app.
*   **Key Detail Extraction:** Uses AI (Gemini) to identify:
    *   Name, Contact Information (Email, Phone, LinkedIn, GitHub, Portfolio)
    *   Professional Summary
    *   Skills
    *   Work Experience (Job Title, Company, Dates, Responsibilities)
    *   Education (Degree, Institution, Graduation Date, Details)
    *   Projects (Name, Description, Technologies, Link)
    *   Certifications & Awards
*   **Targeted Analysis for Job Role:**
    *   Identifies strengths and weaknesses of the resume concerning a user-provided job title.
    *   Suggests missing skills or experiences relevant to the target role.
*   **Improvement Suggestions:** Offers actionable advice to enhance resume content and tailor it for the specified job title.
*   **Job Role Match:**
    *   Estimates a match percentage for the target job role.
    *   Provides recommendations to improve the candidate's fit.
    *   Uses an optionally pasted Job Description for more accurate matching.
*   **Bonus Features:**
    *   **Skill Gap Analysis:** Compares resume skills against a provided Job Description.
    *   **ATS Compatibility Hints:** Provides general feedback on how ATS-friendly the resume text might be.
    *   **Grammar & Clarity Feedback:** Offers suggestions to improve writing quality.
    *   **Export Analysis:** Allows downloading the complete analysis (including extracted text and all feedback sections) in a single Markdown file.

## Tech Stack

*   **Python 3.8+**
*   **Streamlit:** For the web interface.
*   **Google Gemini API:** For all NLP tasks (extraction, analysis, generation). `gemini-1.5-flash-latest` is used by default.
*   **PyPDF2:** For extracting text from PDF files.
*   **python-dotenv:** For managing API keys locally during development.

## Setup and Installation

1.  **Clone the Repository (or download files):**
    ```bash
    git clone <your-repository-link> # If you put this on GitHub
    cd ai_resume_analyzer
    ```
    Alternatively, create the `ai_resume_analyzer` folder and all the files manually with the provided content.

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Google Gemini API Key:**
    You **MUST** have a Google Gemini API Key. Get one from [Google AI Studio](https://aistudio.google.com/).

    There are three ways the app can load the API key (in order of precedence):
    *   **For Streamlit Cloud Deployment (Recommended for sharing):**
        *   When deploying to Streamlit Community Cloud, add your API key as a "Secret".
        *   The secret **key name** must be `GOOGLE_API_KEY_FROM_SECRETS`.
        *   The **secret value** should be your actual Gemini API key string (e.g., `AIzaxxxxxxxxxxxxxxxx`).
    *   **Direct Input in App (for quick local tests or if other methods fail):**
        *   The app will prompt you to enter the API key in the sidebar if it's not found elsewhere.
    *   **Local `.env` File (for local development):**
        *   Create a file named `.env` in the project root (`ai_resume_analyzer/`).
        *   Add your API key like this (using a distinct variable name):
            ```env
            GOOGLE_API_KEY_ENV="YOUR_GEMINI_API_KEY_HERE"
            ```
        *   Ensure `.env` is listed in your `.gitignore` file to prevent committing it.

## How to Run the Project Locally

1.  Ensure you have completed the Setup steps (Python, virtual environment, dependencies installed).
2.  Ensure your API key is available (e.g., in `.env` or you're ready to paste it).
3.  Open your terminal, navigate to the project's root directory (`ai_resume_analyzer/`), and make sure your virtual environment is activated.
4.  Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```
5.  The application will open in your default web browser (usually `http://localhost:8501`).
6.  If the API key wasn't loaded automatically (e.g., from `.env` or Streamlit secrets), enter it in the sidebar.
7.  Upload a resume (PDF or TXT), enter a target job title, optionally paste a job description, and click "✨ Analyze Resume".

## Code Structure

*   `app.py`: Main Streamlit application file (UI logic, workflow).
*   `utils.py`: Helper functions (API key loading, Gemini calls, text extraction, result formatting).
*   `prompts.py`: Stores all engineered prompts for the Gemini model, requesting JSON output.
*   `requirements.txt`: Python package dependencies.
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.
*   `.env` (optional, gitignored): Used to store `GOOGLE_API_KEY_ENV` locally.
*   `sample_resumes/`: Directory for sample resumes (you add your own for testing).
*   `README.md`: This file.

## How it Works

1.  **User Input:** The user provides their API Key (if needed), uploads a resume, enters a target job title, and optionally a job description.
2.  **Text Extraction:** `utils.py` extracts plain text from the resume.
3.  **Gemini API Calls:** For each analysis feature, a specific prompt from `prompts.py` is formatted with the resume text and other inputs. This is sent to the Gemini API via `get_gemini_response` in `utils.py`. Prompts are designed to ask for structured JSON output.
4.  **Display Results:** `app.py` receives the JSON responses, uses formatting functions from `utils.py` to convert them into readable Markdown, and displays them in different tabs. Error handling is included for API issues or malformed JSON.

## Deployment to Streamlit Community Cloud

1.  Push your project to a public GitHub repository. Make sure your `.gitignore` file is correctly set up (especially to exclude `.env`).
2.  Sign up/log in to [Streamlit Community Cloud](https://share.streamlit.io/) using your GitHub account.
3.  Click "New app," select your repository, branch (`main`), and set the main file path to `app.py`.
4.  **Crucially:** Go to "Advanced settings..." and add your Gemini API Key as a **Secret**.
    *   Secret key: `GOOGLE_API_KEY_FROM_SECRETS`
    *   Secret value: `YOUR_ACTUAL_GEMINI_API_KEY`
5.  Click "Deploy!".

## Important Notes & Limitations

*   **API Key is Essential:** The app will not function without a valid Google Gemini API Key.
*   **API Costs/Limits:** Be mindful of Google API usage policies, costs, and rate limits. The `gemini-1.5-flash-latest` model is generally efficient.
*   **Prompt Quality:** The analysis quality depends heavily on the prompts in `prompts.py`.
*   **JSON Robustness:** The app expects JSON from Gemini. While prompts request this, and there's basic cleaning, highly malformed responses could still cause issues, though error messages are now more informative.
*   **ATS Check:** The ATS compatibility hints are based on text content analysis and general best practices, not an emulation of a real ATS.
*   **Data Privacy:** This application processes resumes for the duration of the analysis. If deployed, ensure you understand the data handling implications of your hosting provider. For local use, data stays on your machine during processing. No resume data is stored by the application itself beyond the session.

This project serves as a strong example of leveraging LLMs for practical, real-world NLP applications and makes for a good portfolio piece.