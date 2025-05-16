# ai_resume_analyzer/prompts.py

# --- PROMPT FOR EXTRACTING KEY DETAILS ---
EXTRACT_PROMPT_TEMPLATE = """
Analyze the following resume text and extract the information in a structured JSON format.
If a field is not found, use "N/A" as the value for strings, or an empty list [] for lists.

Resume Text:
'''{resume_text}'''

Desired JSON Structure:
{{
  "name": "Full Name",
  "contact_information": {{
    "email": "email_address",
    "phone": "phone_number",
    "linkedin": "linkedin_url (if available, full URL)",
    "github": "github_url (if available, full URL)",
    "portfolio": "portfolio_url (if available, full URL)"
  }},
  "summary": "A brief professional summary or objective. If not present, provide 'N/A'.",
  "skills": [
    "Skill 1",
    "Skill 2"
  ],
  "work_experience": [
    {{
      "job_title": "Job Title",
      "company": "Company Name",
      "location": "Location (City, State)",
      "dates": "Employment Dates (e.g., MM/YYYY - MM/YYYY or MM/YYYY - Present)",
      "responsibilities": [
        "Responsibility/Accomplishment 1 (use action verbs)",
        "Responsibility/Accomplishment 2 (quantify if possible)"
      ]
    }}
  ],
  "education": [
    {{
      "degree": "Degree Name (e.g., Bachelor of Science in Computer Science)",
      "institution": "Institution Name",
      "location": "Location (City, State)",
      "graduation_date": "Graduation Date (e.g., MM/YYYY or Expected MM/YYYY)",
      "details": "Optional: GPA, relevant coursework, honors. If none, 'N/A'."
    }}
  ],
  "projects": [
    {{
      "project_name": "Project Name",
      "description": "Brief description of the project, highlighting your role and impact.",
      "technologies_used": ["Tech 1", "Tech 2"],
      "link": "Project URL (if available, full URL)"
    }}
  ],
  "certifications_and_awards": [
      "Certification/Award 1",
      "Certification/Award 2"
  ]
}}

Provide ONLY the JSON object as a single block of text, without any surrounding text or markdown formatting like ```json ... ```.
Ensure the JSON is valid.
"""


# --- PROMPT FOR STRENGTHS, WEAKNESSES, MISSING SKILLS ---
ANALYSIS_PROMPT_TEMPLATE = """
Analyze the following resume text specifically for the job role of '{job_title}'.

Resume Text:
'''{resume_text}'''

Job Role: {job_title}

Provide the analysis in the following structured JSON format:
{{
  "strengths": [
    "Strength 1 relevant to the job role, explained briefly.",
    "Strength 2 relevant to the job role, explained briefly."
  ],
  "weaknesses": [
    "Weakness 1 or area for improvement for this job role, with reasoning.",
    "Weakness 2 or area for improvement for this job role, with reasoning."
  ],
  "missing_skills_for_role": [
    "Skill or experience commonly expected for '{job_title}' that seems missing or underrepresented.",
    "Another missing skill or experience."
  ]
}}

Focus on aspects directly relevant to the specified job role. Be concise, constructive, and actionable.
Provide ONLY the JSON object as a single block of text, without any surrounding text or markdown formatting like ```json ... ```.
Ensure the JSON is valid.
"""

# --- PROMPT FOR IMPROVEMENT SUGGESTIONS ---
IMPROVEMENT_SUGGESTIONS_PROMPT_TEMPLATE = """
Based on the following resume text and targeting the job role of '{job_title}', provide specific, actionable suggestions to improve the resume content.
Focus on tailoring it better for the role. Suggest rephrasing bullet points for impact using the STAR method (Situation, Task, Action, Result) where appropriate, adding quantifiable achievements if possible, and highlighting relevant skills more effectively.

Resume Text:
'''{resume_text}'''

Job Role: {job_title}

Provide suggestions in the following structured JSON format:
{{
  "general_suggestions": [
    "General tip 1 (e.g., 'Consider adding a concise professional summary tailored to {job_title} if missing or generic.').",
    "General tip 2 (e.g., 'Ensure consistent formatting throughout the resume for readability.')."
  ],
  "section_specific_suggestions": {{
    "summary": [
      "Suggestion for summary section if applicable (e.g., 'Make the summary more impactful by highlighting 2-3 key achievements relevant to {job_title}.')."
    ],
    "experience": [
      "Suggestion for experience section (e.g., 'For the role at [Company X], try to quantify achievements. Instead of 'Managed project', try 'Managed project Y, resulting in Z% improvement'.').",
      "Another suggestion for experience (e.g., 'Use strong action verbs to start your bullet points in the experience section.')."
    ],
    "skills": [
      "Suggestion for skills section (e.g., 'Ensure skills highly relevant to {job_title} such as A, B, C are prominent and perhaps categorized (e.g., Programming Languages, Tools, Frameworks).')."
    ],
    "education": [
      "Suggestion for education section (e.g., 'If you have relevant coursework or academic projects for {job_title} and are early in your career, consider listing them.')."
    ],
    "projects": [
        "Suggestion for projects section if applicable (e.g., 'Clearly state your role and contributions for each project, and quantify impact if possible.')."
    ]
  }},
  "tailoring_for_role": [
    "Specific advice on how to tailor the resume more effectively for '{job_title}' (e.g., 'Review the job description for {job_title} and incorporate keywords naturally.').",
    "Another tailoring advice (e.g., 'Emphasize experiences and skills that directly align with the primary responsibilities of a {job_title}.')."
  ]
}}
Provide ONLY the JSON object as a single block of text, without any surrounding text or markdown formatting like ```json ... ```.
Ensure the JSON is valid.
"""

# --- PROMPT FOR JOB MATCH PERCENTAGE AND RECOMMENDATIONS ---
JOB_MATCH_PROMPT_TEMPLATE = """
Given the following resume text and the target job role '{job_title}'.
If a job description is provided, use it heavily for a more accurate match.

Resume Text:
'''{resume_text}'''

Target Job Role: {job_title}

{job_description_section}

Based on the above, provide:
1. An estimated job match percentage (0-100%). This should be a single integer.
2. A brief justification for this percentage, highlighting key matching areas and gaps.
3. 3-5 key actionable recommendations for the candidate to improve their chances for this specific role or similar roles.

Format the output as a JSON object:
{{
  "job_match_percentage": "<integer (e.g., 75)>",
  "justification": "Brief reasoning for the score, mentioning specific resume points vs. role requirements.",
  "recommendations": [
    "Recommendation 1 to improve alignment with the role.",
    "Recommendation 2 focusing on skills or experience.",
    "Recommendation 3 regarding tailoring or presentation."
  ]
}}
Provide ONLY the JSON object as a single block of text, without any surrounding text or markdown formatting like ```json ... ```.
Ensure the JSON is valid.
"""

# --- PROMPT FOR SKILL GAP ANALYSIS (WITH JD) ---
SKILL_GAP_PROMPT_TEMPLATE = """
Compare the following resume text with the provided job description for the role of '{job_title}'.
Identify:
1. Skills/experiences mentioned in the resume that directly match requirements in the Job Description (JD).
2. Key skills/experiences required by the JD that are missing or not clearly demonstrated in the resume.
3. Optional: Skills in the resume that are not directly relevant to this JD but could be valuable in other contexts.

Resume Text:
'''{resume_text}'''

Job Description:
'''{jd_text}'''

Job Role: {job_title}

Provide the analysis in the following structured JSON format:
{{
  "matching_skills": [
    "Skill from resume matching the JD (e.g., 'Python - Resume mentions Python proficiency; JD requires Python experience.')."
  ],
  "missing_skills_from_jd": [
    "Skill from JD not found or not emphasized in resume (e.g., 'Cloud Platforms (AWS/Azure) - JD explicitly asks for AWS experience, which is not apparent in the resume.')."
  ],
  "additional_skills_in_resume": [
    "Skill in resume not directly mentioned in JD but potentially valuable (e.g., 'Leadership - Resume mentions leading a team project; JD does not list leadership but it is a good transferable skill.')."
  ]
}}
Provide ONLY the JSON object as a single block of text, without any surrounding text or markdown formatting like ```json ... ```.
Ensure the JSON is valid.
"""

# --- PROMPT FOR ATS COMPATIBILITY HINTS ---
ATS_CHECK_PROMPT_TEMPLATE = """
Analyze the following resume text for common ATS (Applicant Tracking System) compatibility hints, focusing on the text content itself.
Consider aspects like:
- Clarity and standard naming of section headings (e.g., "Experience", "Education", "Skills").
- Use of common, easily parsable date formats.
- Keyword relevance for the job title '{job_title}'.
- Presence of crucial information like contact details.
- Use of action verbs in experience descriptions.
- Avoidance of text within images, tables, or columns (advise based on text structure if it seems overly complex, as you only see text).

Resume Text:
'''{resume_text}'''

Job Role: {job_title}

Provide feedback in the following structured JSON format. The score should be an integer.
{{
  "overall_ats_friendliness_score_out_of_10": "<integer (0-10)>",
  "positive_points": [
    "Aspect that is likely ATS-friendly (e.g., 'Clear section headings like 'Experience' and 'Education' seem to be used.').",
    "Keywords relevant to '{job_title}' appear to be present."
  ],
  "potential_issues_and_recommendations": [
    "Potential issue and how to fix it (e.g., 'If using special characters or symbols in section titles or bullet points, consider replacing them with standard text for better parsing.').",
    "Ensure contact information (email, phone) is in plain text and clearly labeled.",
    "ATS systems prefer standard chronological or combination resume formats. Avoid functional resumes if possible.",
    "Verify that dates for education and experience are clear and consistently formatted (e.g., MM/YYYY - MM/YYYY)."
  ]
}}
Provide ONLY the JSON object as a single block of text, without any surrounding text or markdown formatting like ```json ... ```.
Ensure the JSON is valid.
"""

# --- PROMPT FOR GRAMMAR/CLARITY FEEDBACK ---
GRAMMAR_CLARITY_PROMPT_TEMPLATE = """
Review the following resume text for grammar, spelling, punctuation, clarity, and conciseness.
Provide constructive feedback and suggest improvements. Focus on professionalism and readability.
Identify specific examples if possible.

Resume Text:
'''{resume_text}'''

Provide feedback in the following structured JSON format:
{{
  "overall_assessment": "A brief overall assessment of the writing quality (e.g., 'The resume is generally well-written with good clarity, but a few minor grammatical tweaks could enhance professionalism.' or 'The resume needs significant revision for clarity, conciseness, and grammatical accuracy.').",
  "feedback_points": [
    {{
      "original_text_snippet": "Provide the problematic text snippet here if applicable (e.g., 'responsable for manage projects').",
      "issue_type": "Type of issue (e.g., 'Grammar - Verb Tense', 'Spelling', 'Clarity - Awkward Phrasing', 'Conciseness - Wordy', 'Punctuation - Missing Comma').",
      "suggestion": "Specific suggestion for improvement (e.g., 'Change to 'Responsible for managing projects' or 'Managed projects'.')."
    }}
  ],
  "positive_aspects": [
      "Point out 1-2 things that are well-written or clear (e.g., 'The use of action verbs in the experience section is strong.')."
  ]
}}
Provide ONLY the JSON object as a single block of text, without any surrounding text or markdown formatting like ```json ... ```.
Ensure the JSON is valid.
"""