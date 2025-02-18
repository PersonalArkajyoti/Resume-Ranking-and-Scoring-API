import streamlit as st
import pandas as pd
import requests
import io

# Streamlit Page Config
st.set_page_config(page_title="Resume Ranking System", page_icon="📄", layout="wide")

# Title & Description
st.title("📄 AI-Powered Resume Ranking")
st.markdown(
    "Use AI to evaluate resumes based on job descriptions. Upload resumes, get scores, and download ranked results."
)

# Backend API Endpoints
EXTRACT_CRITERIA_API = "http://localhost:8099/extract_criteria/"
SCORE_RESUMES_API = "http://localhost:8099/score_resumes/"

# Upload Job Description
st.sidebar.header("Upload Job Description")
job_desc_file = st.sidebar.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"])
criteria = None

if job_desc_file:
    with st.spinner("Extracting job criteria..."):
        files = {"file": (job_desc_file.name, job_desc_file, job_desc_file.type)}
        response = requests.post(EXTRACT_CRITERIA_API, files=files)
        if response.status_code == 200:
            criteria = response.json().get("criteria", [])
            st.sidebar.success("Job criteria extracted successfully!")
        else:
            st.sidebar.error("Failed to extract criteria.")

# Display Extracted Criteria
if criteria:
    with st.expander("📌 Extracted Job Criteria"):
        st.write(criteria)

# Upload Resumes
st.header("📂 Upload Resumes")
resume_files = st.file_uploader("Upload Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

# Process & Score Resumes
if resume_files and criteria:
    if st.button("Analyze & Rank Resumes", use_container_width=True):
        with st.spinner("Processing resumes and ranking candidates..."):
            files = [("resumes", (file.name, file, file.type)) for file in resume_files]
            response = requests.post(SCORE_RESUMES_API, files=files)
            
            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.text))
                df = df.sort_values(by='total_score', ascending=False)  # Sort by highest score
                
                # Display Results
                st.subheader("🏆 Ranked Candidates")
                st.dataframe(df.style.format({"total_score": "{:.2f}"}))
                
                # Download Button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Ranked List", csv, "ranked_resumes.csv", "text/csv", use_container_width=True)
            else:
                st.error("Failed to process resumes.")

# Footer
st.markdown("---")
st.caption("🚀 AI-powered Resume Ranking System | Built with FastAPI & Streamlit")
