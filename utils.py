# ai_resume_analyzer/utils.py

import PyPDF2
import google.generativeai as genai
import os
import json
import streamlit as st # For st.secrets access
# Ensure dotenv is imported here if you use it directly in this function
from dotenv import load_dotenv


# --- API Key and Gemini Configuration ---
def load_api_key(api_key_input=None):
    """
    Loads the Gemini API key from Streamlit secrets, user input, or .env file.
    Sets the GOOGLE_API_KEY environment variable.
    """
    # 1. Try from Streamlit secrets (for deployed app)
    # Check if st.secrets has items before trying to access a specific key
    # This avoids the StreamlitSecretNotFoundError if no secrets file exists locally.
    try:
        if hasattr(st, 'secrets') and st.secrets and "GOOGLE_API_KEY_FROM_SECRETS" in st.secrets:
            key_from_secrets = st.secrets.get("GOOGLE_API_KEY_FROM_SECRETS")
            if key_from_secrets:
                os.environ["GOOGLE_API_KEY"] = key_from_secrets
                # st.info("API Key loaded from Streamlit secrets.") # Optional: for debugging
                return key_from_secrets
    except Exception as e:
        # This might happen if .streamlit/secrets.toml doesn't exist or is malformed
        # We can silently ignore it for local dev if .env or input is the primary method
        # st.warning(f"Could not access Streamlit secrets (expected for local dev if not configured): {e}")
        pass


    # 2. Try from user input in the app
    if api_key_input:
        os.environ["GOOGLE_API_KEY"] = api_key_input
        # st.info("API Key loaded from user input.") # Optional: for debugging
        return api_key_input

    # 3. Try from .env file (for local development)
    load_dotenv() # Make sure this is called to load .env variables
    env_key = os.getenv("GOOGLE_API_KEY_ENV") # Use a distinct name for .env variable
    if env_key:
        os.environ["GOOGLE_API_KEY"] = env_key
        # st.info("API Key loaded from .env file.") # Optional: for debugging
        return env_key
    
    # st.info("No API key loaded from secrets, input, or .env.") # Optional: for debugging
    return None


def configure_gemini_api():
    """
    Configures the Gemini API using the GOOGLE_API_KEY environment variable.
    This should be called after load_api_key has set the environment variable.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        # This case should ideally be handled by UI preventing analysis without a key
        st.error("Google API Key is not configured. Please provide it.")
        return False
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Failed to configure Gemini API: {e}")
        return False

def get_gemini_response(prompt_text, model_name="gemini-1.5-flash-latest", retries=3):
    """
    Sends a prompt to the configured Gemini API and returns the parsed JSON response.
    Handles potential errors and retries.
    """
    if not configure_gemini_api(): # Ensure API is configured before making a call
        return {"error": "Gemini API not configured.", "raw_response": None}

    model = genai.GenerativeModel(model_name)
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt_text)
            cleaned_response_text = response.text.strip()

            # Remove markdown ```json ... ``` if present
            if cleaned_response_text.startswith("```json"):
                cleaned_response_text = cleaned_response_text[7:]
            if cleaned_response_text.endswith("```"):
                cleaned_response_text = cleaned_response_text[:-3]
            
            # Attempt to parse as JSON
            parsed_json = json.loads(cleaned_response_text)
            return parsed_json
        except json.JSONDecodeError as e:
            error_message = f"JSONDecodeError on attempt {attempt + 1}/{retries}: {e}. Response: '{cleaned_response_text[:500]}...'"
            st.warning(error_message) # Show warning in UI for easier debugging
            print(error_message)
            if attempt == retries - 1:
                return {"error": "Failed to parse LLM response as JSON after multiple retries.", "raw_response": response.text}
        except Exception as e:
            error_message = f"Error calling Gemini API (attempt {attempt + 1}/{retries}): {e}"
            st.warning(error_message)
            print(error_message)
            if attempt == retries - 1:
                return {"error": f"Failed to get response from Gemini after {retries} attempts: {e}", "raw_response": None}
        
        if attempt < retries - 1:
            st.info(f"Retrying Gemini call (attempt {attempt + 2}/{retries})...")
            print(f"Retrying Gemini call ({attempt+2})...")

    return {"error": f"Failed to get valid response from Gemini after {retries} attempts.", "raw_response": None}


# --- Text Extraction ---
def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() or "" # Ensure None is handled
        return text if text else "Could not extract any text from PDF."
    except Exception as e:
        return f"Error extracting PDF: {e}"

def extract_text_from_txt(uploaded_file):
    """Extracts text from an uploaded TXT file."""
    try:
        return uploaded_file.read().decode("utf-8")
    except Exception as e:
        return f"Error extracting TXT: {e}"


# --- Formatting Functions for Display ---
def format_extracted_details(details_json):
    """Formats the extracted JSON details into a readable markdown string."""
    if not isinstance(details_json, dict) or "error" in details_json:
        return f"Could not extract details or an error occurred: {details_json.get('error', 'Unknown error') if isinstance(details_json, dict) else 'Invalid data format'}"

    md_parts = []

    if details_json.get("name") and details_json["name"] != "N/A":
        md_parts.append(f"### 👤 Name: {details_json['name']}")

    contact = details_json.get("contact_information", {})
    if isinstance(contact, dict) and any(v and v != "N/A" for v in contact.values()):
        contact_md = ["#### 📞 Contact Information"]
        if contact.get("email") and contact["email"] != "N/A": contact_md.append(f"- **Email:** {contact['email']}")
        if contact.get("phone") and contact["phone"] != "N/A": contact_md.append(f"- **Phone:** {contact['phone']}")
        if contact.get("linkedin") and contact["linkedin"] != "N/A": contact_md.append(f"- **LinkedIn:** [{contact['linkedin']}]({contact['linkedin']})")
        if contact.get("github") and contact["github"] != "N/A": contact_md.append(f"- **GitHub:** [{contact['github']}]({contact['github']})")
        if contact.get("portfolio") and contact["portfolio"] != "N/A": contact_md.append(f"- **Portfolio:** [{contact['portfolio']}]({contact['portfolio']})")
        if len(contact_md) > 1: md_parts.append("\n".join(contact_md))


    if details_json.get("summary") and details_json["summary"] != "N/A":
        md_parts.append(f"#### 📝 Summary\n{details_json['summary']}")

    skills = details_json.get("skills", [])
    if isinstance(skills, list) and skills:
        md_parts.append("#### 🛠️ Skills\n- " + "\n- ".join(skills))

    experience = details_json.get("work_experience", [])
    if isinstance(experience, list) and experience:
        exp_md = ["#### 💼 Work Experience"]
        for exp in experience:
            if not isinstance(exp, dict): continue
            title = exp.get('job_title', 'N/A')
            company = exp.get('company', 'N/A')
            location = exp.get('location', 'N/A')
            dates = exp.get('dates', 'N/A')
            exp_md.append(f"- **{title}** at {company} ({location})")
            exp_md.append(f"  *Dates: {dates}*")
            responsibilities = exp.get("responsibilities", [])
            if isinstance(responsibilities, list) and responsibilities:
                for resp in responsibilities:
                    exp_md.append(f"  - {resp}")
            exp_md.append("") # Add a blank line for spacing
        md_parts.append("\n".join(exp_md))

    education_list = details_json.get("education", [])
    if isinstance(education_list, list) and education_list:
        edu_md = ["#### 🎓 Education"]
        for edu in education_list:
            if not isinstance(edu, dict): continue
            degree = edu.get('degree', 'N/A')
            institution = edu.get('institution', 'N/A')
            location = edu.get('location', 'N/A')
            grad_date = edu.get('graduation_date', 'N/A')
            details = edu.get('details', 'N/A')
            edu_md.append(f"- **{degree}**, {institution} ({location})")
            edu_md.append(f"  *Graduation: {grad_date}*")
            if details and details != "N/A":
                 edu_md.append(f"  *Details: {details}*")
            edu_md.append("")
        md_parts.append("\n".join(edu_md))
    
    projects = details_json.get("projects", [])
    if isinstance(projects, list) and projects:
        proj_md = ["#### 🚀 Projects"]
        for proj in projects:
            if not isinstance(proj, dict): continue
            proj_md.append(f"- **{proj.get('project_name', 'N/A')}**")
            if proj.get('description'): proj_md.append(f"  *{proj['description']}*")
            tech = proj.get('technologies_used', [])
            if isinstance(tech, list) and tech: proj_md.append(f"  Technologies: {', '.join(tech)}")
            if proj.get('link') and proj['link'] != "N/A": proj_md.append(f"  Link: [{proj['link']}]({proj['link']})")
            proj_md.append("")
        md_parts.append("\n".join(proj_md))

    certs = details_json.get("certifications_and_awards", [])
    if isinstance(certs, list) and certs:
        md_parts.append("#### 🏆 Certifications & Awards\n- " + "\n- ".join(certs))

    return "\n\n".join(md_parts) if md_parts else "No details extracted or recognized."


def format_analysis(analysis_json):
    if not isinstance(analysis_json, dict) or "error" in analysis_json:
        return f"Could not perform analysis or an error occurred: {analysis_json.get('error', 'Unknown error') if isinstance(analysis_json, dict) else 'Invalid data format'}"
    
    md_parts = []
    strengths = analysis_json.get("strengths", [])
    if isinstance(strengths, list) and strengths:
        md_parts.append("#### ✅ Strengths\n" + "\n".join(f"- {s}" for s in strengths))
    
    weaknesses = analysis_json.get("weaknesses", [])
    if isinstance(weaknesses, list) and weaknesses:
        md_parts.append("#### ⚠️ Weaknesses / Areas for Improvement\n" + "\n".join(f"- {w}" for w in weaknesses))
        
    missing_skills = analysis_json.get("missing_skills_for_role", [])
    if isinstance(missing_skills, list) and missing_skills:
        md_parts.append("#### ❓ Missing Skills/Experience for Role\n" + "\n".join(f"- {m}" for m in missing_skills))
        
    return "\n\n".join(md_parts) if md_parts else "No analysis data available."

def format_suggestions(suggestions_json):
    if not isinstance(suggestions_json, dict) or "error" in suggestions_json:
        return f"Could not get suggestions or an error occurred: {suggestions_json.get('error', 'Unknown error') if isinstance(suggestions_json, dict) else 'Invalid data format'}"

    md_parts = []
    general = suggestions_json.get("general_suggestions", [])
    if isinstance(general, list) and general:
        md_parts.append("#### 💡 General Suggestions\n" + "\n".join(f"- {s}" for s in general))

    section_specific = suggestions_json.get("section_specific_suggestions", {})
    if isinstance(section_specific, dict) and section_specific:
        sec_md = ["#### 📄 Section-Specific Suggestions"]
        for section, sugg_list in section_specific.items():
            if isinstance(sugg_list, list) and sugg_list:
                sec_md.append(f"- **{section.capitalize()}:**")
                for sugg in sugg_list:
                    if sugg: sec_md.append(f"  - {sugg}")
        if len(sec_md) > 1: md_parts.append("\n".join(sec_md))
    
    tailoring = suggestions_json.get("tailoring_for_role", [])
    if isinstance(tailoring, list) and tailoring:
        md_parts.append("#### 🎯 Tailoring for Role\n" + "\n".join(f"- {t}" for t in tailoring))
        
    return "\n\n".join(md_parts) if md_parts else "No improvement suggestions available."

def format_job_match(match_json):
    if not isinstance(match_json, dict) or "error" in match_json:
        return f"Could not perform job match or an error occurred: {match_json.get('error', 'Unknown error') if isinstance(match_json, dict) else 'Invalid data format'}"

    md_parts = []
    percentage = match_json.get("job_match_percentage", "N/A")
    md_parts.append(f"### 🎯 Job Match Score: {percentage}%") # Changed from <integer> to value
    
    justification = match_json.get("justification")
    if justification:
        md_parts.append(f"**Justification:** {justification}")
        
    recommendations = match_json.get("recommendations", [])
    if isinstance(recommendations, list) and recommendations:
        md_parts.append("#### 🚀 Recommendations to Improve Match\n" + "\n".join(f"- {r}" for r in recommendations))
        
    return "\n\n".join(md_parts) if md_parts else "No job match data available."

def format_skill_gap(gap_json):
    if not isinstance(gap_json, dict) or "error" in gap_json:
        return f"Could not perform skill gap analysis or an error occurred: {gap_json.get('error', 'Unknown error') if isinstance(gap_json, dict) else 'Invalid data format'}"

    md_parts = []
    matching = gap_json.get("matching_skills", [])
    if isinstance(matching, list) and matching:
        md_parts.append("#### ✅ Matching Skills (Resume vs. JD)\n" + "\n".join(f"- {s}" for s in matching))
        
    missing = gap_json.get("missing_skills_from_jd", [])
    if isinstance(missing, list) and missing:
        md_parts.append("#### ❓ Skills in JD Missing/Not Clear in Resume\n" + "\n".join(f"- {s}" for s in missing))
        
    additional = gap_json.get("additional_skills_in_resume", [])
    if isinstance(additional, list) and additional:
        md_parts.append("#### ✨ Additional Skills in Resume (Not in JD but potentially valuable)\n" + "\n".join(f"- {s}" for s in additional))
        
    return "\n\n".join(md_parts) if md_parts else "No skill gap data available."

def format_ats_check(ats_json):
    if not isinstance(ats_json, dict) or "error" in ats_json:
        return f"Could not perform ATS check or an error occurred: {ats_json.get('error', 'Unknown error') if isinstance(ats_json, dict) else 'Invalid data format'}"

    md_parts = []
    score = ats_json.get("overall_ats_friendliness_score_out_of_10", "N/A")
    md_parts.append(f"### 🤖 ATS Friendliness Score: {score}/10")
    
    positive = ats_json.get("positive_points", [])
    if isinstance(positive, list) and positive:
        md_parts.append("#### 👍 Positive Points (Likely ATS-Friendly)\n" + "\n".join(f"- {p}" for p in positive))
    
    issues = ats_json.get("potential_issues_and_recommendations", [])
    if isinstance(issues, list) and issues:
        md_parts.append("#### ⚠️ Potential Issues & Recommendations\n" + "\n".join(f"- {i}" for i in issues))
        
    return "\n\n".join(md_parts) if md_parts else "No ATS check data available."

def format_grammar_check(grammar_json):
    if not isinstance(grammar_json, dict) or "error" in grammar_json:
        return f"Could not perform grammar check or an error occurred: {grammar_json.get('error', 'Unknown error') if isinstance(grammar_json, dict) else 'Invalid data format'}"

    md_parts = []
    assessment = grammar_json.get("overall_assessment")
    if assessment:
        md_parts.append(f"**Overall Assessment:** {assessment}")

    positive = grammar_json.get("positive_aspects", [])
    if isinstance(positive, list) and positive:
        md_parts.append("#### 👍 Well-Written Aspects\n" + "\n".join(f"- {pa}" for pa in positive))
        
    feedback_points = grammar_json.get("feedback_points", [])
    if isinstance(feedback_points, list) and feedback_points:
        fb_md = ["#### ✍️ Feedback & Suggestions"]
        for fb in feedback_points:
            if not isinstance(fb, dict): continue
            issue_type = fb.get('issue_type', 'N/A')
            suggestion = fb.get('suggestion', 'N/A')
            snippet = fb.get("original_text_snippet")
            
            fb_md.append(f"- **Issue Type:** {issue_type}")
            if snippet: fb_md.append(f"  *Original Snippet:* \"{snippet}\"")
            fb_md.append(f"  *Suggestion:* {suggestion}")
            fb_md.append("") # spacing
        if len(fb_md) > 1 : md_parts.append("\n".join(fb_md))
        
    return "\n\n".join(md_parts) if md_parts else "No grammar check data available."