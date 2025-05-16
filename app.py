# ai_resume_analyzer/app.py
import streamlit as st
from utils import (
    extract_text_from_pdf, extract_text_from_txt,
    get_gemini_response, load_api_key,
    format_extracted_details, format_analysis, format_suggestions,
    format_job_match, format_skill_gap, format_ats_check, format_grammar_check
)
from prompts import (
    EXTRACT_PROMPT_TEMPLATE, ANALYSIS_PROMPT_TEMPLATE,
    IMPROVEMENT_SUGGESTIONS_PROMPT_TEMPLATE, JOB_MATCH_PROMPT_TEMPLATE,
    SKILL_GAP_PROMPT_TEMPLATE, ATS_CHECK_PROMPT_TEMPLATE,
    GRAMMAR_CLARITY_PROMPT_TEMPLATE
)
import os # For clearing API key from env if needed

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Initialize session state ---
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "api_key_loaded" not in st.session_state:
    st.session_state.api_key_loaded = False
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}
if "show_api_key_input" not in st.session_state:
    st.session_state.show_api_key_input = True

# --- Sidebar ---
with st.sidebar:
    st.title("🚀 AI Resume Analyzer")
    st.markdown("---")
    
    # API Key Management
    if not st.session_state.api_key_loaded:
        loaded_key = load_api_key() 
        if loaded_key:
            st.session_state.api_key_loaded = True
            st.session_state.show_api_key_input = False
            st.success("Gemini API Key loaded successfully!")
        else:
            st.session_state.show_api_key_input = True

    if st.session_state.show_api_key_input:
        api_key_input_val = st.text_input(
            "Enter your Google Gemini API Key:", 
            type="password", 
            key="api_key_user_input", # This key is for the widget itself
            help="Get your key from Google AI Studio. This will be used for the current session."
        )
        if st.button("Load API Key from Input"):
            if api_key_input_val:
                loaded_key_from_input = load_api_key(api_key_input=api_key_input_val)
                if loaded_key_from_input:
                    st.session_state.api_key_loaded = True
                    st.session_state.show_api_key_input = False 
                    st.success("API Key loaded from input!")
                    st.rerun() 
                else:
                    st.error("Failed to load API key from input. Please check the key and try again.")
            else:
                st.warning("Please enter an API key.")
    
    if st.session_state.api_key_loaded and not st.session_state.show_api_key_input:
        st.success("Gemini API Key is active.")
        if st.button("Change/Clear API Key"):
            if "GOOGLE_API_KEY" in os.environ:
                del os.environ["GOOGLE_API_KEY"]
            st.session_state.api_key_loaded = False
            st.session_state.show_api_key_input = True
            # Clear the actual value from the input widget's state if it exists
            if "api_key_user_input" in st.session_state:
                st.session_state.api_key_user_input = "" 
            st.info("API Key cleared. Please enter a new key.")
            st.rerun()

    st.markdown("---")
    uploaded_file = st.file_uploader("Upload your Resume (PDF or TXT)", type=["pdf", "txt"], key="resume_upload")
    
    if uploaded_file:
        file_type = uploaded_file.type
        with st.spinner(f"Extracting text from {uploaded_file.name}..."):
            if file_type == "application/pdf":
                st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
            elif file_type == "text/plain":
                st.session_state.resume_text = extract_text_from_txt(uploaded_file)
            
            if st.session_state.resume_text and "Error extracting" in st.session_state.resume_text:
                st.error(st.session_state.resume_text)
                st.session_state.resume_text = None
            elif not st.session_state.resume_text or st.session_state.resume_text.strip() == "Could not extract any text from PDF.":
                 st.error("Could not extract any text from the uploaded file or the file is empty.")
                 st.session_state.resume_text = None
            else:
                st.success(f"Resume '{uploaded_file.name}' uploaded and text extracted!")

    st.markdown("---")
    # The `value` argument retrieves from session_state if it exists, otherwise uses default.
    # Streamlit automatically updates st.session_state.job_title_input when the user types.
    job_title = st.text_input(
        "Enter Target Job Title (e.g., Software Engineer)", 
        key="job_title_input", 
        value=st.session_state.get("job_title_input", "") 
    )
    
    job_description = st.text_area(
        "Paste Job Description (Optional, for better analysis)", 
        height=150, 
        key="jd_input", 
        value=st.session_state.get("jd_input", "")
    )
    st.markdown("---")
    
    # THESE LINES WERE THE PROBLEM AND ARE NOW REMOVED:
    # st.session_state.job_title_input = job_title # REMOVED
    # st.session_state.jd_input = job_description  # REMOVED

    analyze_button_disabled = not (st.session_state.resume_text and job_title and st.session_state.api_key_loaded)
    analyze_button = st.button("✨ Analyze Resume", type="primary", disabled=analyze_button_disabled, use_container_width=True)

    if not st.session_state.api_key_loaded:
        st.error("API Key is required for analysis. Please load your key.")
    if not st.session_state.resume_text:
        st.info("Please upload a resume.")
    if not job_title: # Check the variable 'job_title' which holds the current widget value
        st.info("Please enter a target job title.")


# --- Main Content Area ---
st.title("📄 AI-Powered Resume Analysis")

if analyze_button and not analyze_button_disabled:
    st.session_state.analysis_results = {} 
    with st.spinner("🤖 AI is analyzing your resume... This might take a few moments!"):
        # Use the current value of job_title and job_description from the widgets
        current_job_title_for_analysis = st.session_state.get("job_title_input", "") 
        current_jd_for_analysis = st.session_state.get("jd_input", "")

        analysis_tasks = [
            ("extracted_details", EXTRACT_PROMPT_TEMPLATE.format(resume_text=st.session_state.resume_text)),
            ("strengths_weaknesses_missing", ANALYSIS_PROMPT_TEMPLATE.format(resume_text=st.session_state.resume_text, job_title=current_job_title_for_analysis)),
            ("improvement_suggestions", IMPROVEMENT_SUGGESTIONS_PROMPT_TEMPLATE.format(resume_text=st.session_state.resume_text, job_title=current_job_title_for_analysis)),
            ("job_match", JOB_MATCH_PROMPT_TEMPLATE.format(resume_text=st.session_state.resume_text, job_title=current_job_title_for_analysis, job_description_section=f"Job Description:\n```\n{current_jd_for_analysis}\n```" if current_jd_for_analysis else "No job description provided.")),
            ("ats_check", ATS_CHECK_PROMPT_TEMPLATE.format(resume_text=st.session_state.resume_text, job_title=current_job_title_for_analysis)),
            ("grammar_clarity", GRAMMAR_CLARITY_PROMPT_TEMPLATE.format(resume_text=st.session_state.resume_text))
        ]
        if current_jd_for_analysis:
            analysis_tasks.insert(4, ("skill_gap", SKILL_GAP_PROMPT_TEMPLATE.format(resume_text=st.session_state.resume_text, jd_text=current_jd_for_analysis, job_title=current_job_title_for_analysis)))
        else:
             st.session_state.analysis_results["skill_gap"] = {"info": "Job description not provided for skill gap analysis."}


        for key, prompt in analysis_tasks:
            if key == "skill_gap" and not current_jd_for_analysis: 
                continue
            st.write(f"Processing: {key.replace('_', ' ').title()}...") 
            result = get_gemini_response(prompt)
            st.session_state.analysis_results[key] = result
            if isinstance(result, dict) and "error" in result:
                st.error(f"Error during {key.replace('_', ' ').title()}: {result['error']}")
                if result.get("raw_response"):
                    with st.expander("Show Raw Error Response"):
                        st.code(result["raw_response"], language='text')
        st.success("Analysis Complete!")


# --- Display Results ---
if st.session_state.analysis_results:
    tabs_config = [
        {"title": "📝 Extracted Details", "key": "extracted_details", "formatter": format_extracted_details},
        {"title": "📊 Strengths & Weaknesses", "key": "strengths_weaknesses_missing", "formatter": format_analysis, "job_title_context": True},
        {"title": "💡 Improvement Suggestions", "key": "improvement_suggestions", "formatter": format_suggestions, "job_title_context": True},
        {"title": "🎯 Job Match & Recommendations", "key": "job_match", "formatter": format_job_match, "job_title_context": True},
    ]
    # Check if skill_gap analysis was performed and didn't just store an info message
    skill_gap_result = st.session_state.analysis_results.get("skill_gap")
    if skill_gap_result and not (isinstance(skill_gap_result, dict) and "info" in skill_gap_result):
        tabs_config.append({"title": "↔️ Skill Gap (vs JD)", "key": "skill_gap", "formatter": format_skill_gap, "job_title_context": True})
    
    tabs_config.extend([
        {"title": "🤖 ATS Compatibility", "key": "ats_check", "formatter": format_ats_check, "job_title_context": True},
        {"title": "✍️ Grammar & Clarity", "key": "grammar_clarity", "formatter": format_grammar_check},
        {"title": "📜 Full Resume Text", "key": "resume_text_display", "is_special": True}
    ])

    tab_titles = [t["title"] for t in tabs_config]
    created_tabs = st.tabs(tab_titles)

    for i, tab_info in enumerate(tabs_config):
        with created_tabs[i]:
            # Use the value from session state for display consistency
            current_job_title_display = st.session_state.get("job_title_input", "the target role") 
            header_title = tab_info["title"]
            if tab_info.get("job_title_context"):
                header_title = f"{tab_info['title']} for '{current_job_title_display}'"
            st.header(header_title)

            if tab_info.get("is_special") and tab_info["key"] == "resume_text_display":
                if st.session_state.resume_text:
                    st.text_area("Resume Content", st.session_state.resume_text, height=400, disabled=True, key=f"resume_display_{i}")
                    export_text = f"# Resume Analysis for: {current_job_title_display}\n\n"
                    export_text += f"## Original Resume Text\n\n```\n{st.session_state.resume_text}\n```\n\n---\n\n"
                    
                    for res_key_export, res_data_export in st.session_state.analysis_results.items():
                        # Find corresponding tab info for title and formatter
                        export_tab_info = next((t for t in tabs_config if t["key"] == res_key_export), None)
                        if not export_tab_info and res_key_export != "skill_gap": # skill_gap might not have a tab if no JD
                            continue
                        
                        export_title = export_tab_info["title"] if export_tab_info else res_key_export.replace("_", " ").title()
                        
                        if isinstance(res_data_export, dict) and "info" in res_data_export : # Skip info messages
                             export_text += f"## {export_title}\n\n{res_data_export['info']}\n\n---\n\n"
                             continue
                        
                        if isinstance(res_data_export, dict) and "error" not in res_data_export:
                            formatter_func = export_tab_info.get("formatter") if export_tab_info else None
                            if formatter_func:
                                export_text += f"## {export_title}\n\n{formatter_func(res_data_export)}\n\n---\n\n"
                        elif isinstance(res_data_export, dict) and "error" in res_data_export:
                            export_text += f"## {export_title}\n\nError: {res_data_export['error']}\nRaw: {res_data_export.get('raw_response', 'N/A')}\n\n---\n\n"

                    st.download_button(
                        label="📥 Download Full Analysis (Markdown)",
                        data=export_text,
                        file_name=f"resume_analysis_{current_job_title_display.replace(' ','_')}.md",
                        mime="text/markdown",
                        key=f"download_button_{i}"
                    )
                else:
                    st.info("Upload a resume to see its content here.")
            else: # Regular tabs
                res_data = st.session_state.analysis_results.get(tab_info["key"])
                if res_data and isinstance(res_data, dict) and "info" in res_data:
                    st.info(res_data["info"])
                elif res_data and isinstance(res_data, dict) and "error" not in res_data:
                    st.markdown(tab_info["formatter"](res_data))
                    if st.toggle(f"Show Raw JSON ({tab_info['title']})", key=f"toggle_json_{tab_info['key']}"):
                        st.json(res_data)
                elif res_data and isinstance(res_data, dict) and "error" in res_data:
                    st.error(f"An error occurred: {res_data.get('error', 'Unknown error')}")
                    if res_data.get("raw_response"):
                        with st.expander("Show Raw Error Response From AI"):
                            st.code(res_data["raw_response"], language='text')
                # Check if it's a key that should have data but doesn't (and isn't just an info message)
                elif not res_data and not (tab_info["key"] == "skill_gap" and st.session_state.analysis_results.get("skill_gap", {}).get("info")):
                    st.warning(f"No data available for {tab_info['title']} or an error occurred during its generation.")


elif not analyze_button and st.session_state.resume_text:
    st.info("⬅️ Fill in the details in the sidebar and click 'Analyze Resume'.")
    if st.session_state.resume_text:
        st.subheader("Preview of Extracted Resume Text:")
        st.text_area("", st.session_state.resume_text, height=300, disabled=True, key="resume_preview_main")
else:
    st.info("👋 Welcome! Please load your API key, upload your resume, and enter a job title in the sidebar to get started.")

st.markdown("---")
st.markdown("<sub>AI Resume Analyzer - v1.1</sub>", unsafe_allow_html=True)