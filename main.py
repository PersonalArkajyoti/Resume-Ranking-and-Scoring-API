from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import os
import json
import pandas as pd
import PyPDF2  # PyMuPDF for PDFs
import docx
from io import BytesIO
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
groq_api = os.getenv("GROQ_API")

if not groq_api:
    raise ValueError("❌ Error: GROQ_API key is missing. Please check your .env file.")

# Initialize Groq API client
client = Groq(api_key=groq_api)

app = FastAPI(title="Resume Ranking API")

# Store extracted criteria globally (Temporary Storage)
extracted_criteria = {"criteria": []}

# ---------------------- Text Extraction Functions ---------------------- #

def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    """Extracts text from a PDF file."""
    # Read the PDF file
    pdf_reader = PyPDF2.PdfReader(pdf_file.file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"  # Extract text from each page
    return text.strip()  # Return the text without leading/trailing whitespace

def extract_text_from_docx(docx_file: UploadFile) -> str:
    """Extracts text from a DOCX file."""
    doc = docx.Document(docx_file.file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# ---------------------- Extract Criteria API ---------------------- #
@app.post("/extract_criteria/")
async def extract_criteria(file: UploadFile = File(...)):
    """
    Extracts job criteria from a job description document (PDF/DOCX).
    Stores the result globally to be used in the next API call.
    """
    global extracted_criteria  # Use the global variable

    if file.filename.endswith(".pdf"):
        job_description_text = extract_text_from_pdf(file)
    elif file.filename.endswith(".docx"):
        job_description_text = extract_text_from_docx(file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a PDF or DOCX.")

    # Groq API Prompt for Criteria Extraction
    prompt = f"""
    Extract the key hiring criteria from the following job description. Provide them in a JSON format.
    
    Job Description:
    {job_description_text}

    Output format:
    {{
      "criteria": [
        "Required skill 1",
        "Required skill 2",
        "Required qualification",
        "Experience in XYZ",
        ...
      ]
    }}
    """

    messages = [
        {"role": "system", "content": "You are an expert in HR and job description analysis."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.3,
            max_tokens=512,
            top_p=1,
            stream=False
        )

        # Print the raw response for debugging
        print("Raw response from Groq API:", response)

        # Extract the content from the response
        content = response.choices[0].message.content.strip("```").strip()

        # Find the first valid JSON object in the response
        json_start = content.find('{')
        json_end = content.find('}', json_start) + 1

        if json_start == -1 or json_end == -1:
            raise ValueError("No valid JSON found in the response.")

        json_content = content[json_start:json_end]

        # Parse the JSON content
        extracted_criteria = json.loads(json_content)  # Store globally
        return extracted_criteria

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting criteria: {e}")
# ---------------------- Score Resumes API ---------------------- #
# ---------------------- Score Resumes API ---------------------- #
# ---------------------- Score Resumes API ---------------------- #
@app.post("/score_resumes/") 
async def score_resumes(resumes: List[UploadFile] = File(...)):
    """
    Scores resumes dynamically based on previously extracted criteria.
    Returns a CSV file of scores with dynamic columns.
    """
    global extracted_criteria  # Use stored criteria from the previous API call

    if not extracted_criteria["criteria"]:
        raise HTTPException(status_code=400, detail="No criteria found. Please extract criteria first.")

    candidate_scores = []

    for resume in resumes:
        if resume.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume)
        elif resume.filename.endswith(".docx"):
            resume_text = extract_text_from_docx(resume)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {resume.filename}")

        candidate_name = "Extracted Name"  # Replace with actual name extraction logic if needed

        criteria_text = "\n".join(f"- {c}" for c in extracted_criteria["criteria"])

        prompt = f"""
        Instruction : 

        1. Evaluate the following resumes based on the extracted 'criteria' provided. Score each candidate on a scale of 0 to 5 for each of the relevant skills and provide a total score.
        2. Summarize the full extracted criteria into 3-4 key skill sets or categories that represent the most important attributes needed for the role. Make sure the summarized skill sets are concise and focused.
        3. Assign a score from 0 to 5 to each skill set or category for every candidate. The score should reflect how well the candidate demonstrates that skill based on the content in their resume.
        4. Provide a total score for each candidate by adding the scores from each skill set. The total score should be the sum of all individual skill set scores, and it must be between 0 and 20 (since each skill set score can be a maximum of 5).
        5. Ensure that the score for each individual skill set does not exceed 5. If a candidate demonstrates no expertise in a particular skill, assign a score of 0.
        6. Only return the response in a proper, clean, and well-structured JSON format. Do not include any additional text or commentary in the response.
        7. Ensure the key "candidate_name" is included with the candidate's name, and each skill set and total score must be correctly labeled and assigned.

        criteria:{criteria_text}

        Resume Text:{resume_text}

        Provide the output in the following JSON format:
        {{
            "candidates": 
            [
                {{
                    "candidate_name":"{candidate_name}",
                    "Python_development":"score_value",
                    "Machine_learning_algorithms": "score_value",
                    "Cloud_and_Database": "score_value",
                    "Certification": "score_value",
                    "total_score": "total_value"
                }}
            ]
        }}
        """

        messages = [
            {"role": "system", "content": "You are an AI expert in resume evaluation and ranking."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False
            )

            content = response.choices[0].message.content.strip("```").strip()
            json_start = content.find('{')
            json_end = content.rfind('}') + 1

            if json_start == -1 or json_end == -1:
                raise ValueError("No valid JSON found in the response.")

            json_content = content[json_start:json_end]
            resume_score = json.loads(json_content)

            if "candidates" not in resume_score:
                raise ValueError("Invalid response from Groq API")

            # Process each candidate and dynamically create the CSV columns based on the keys
            for candidate in resume_score["candidates"]:
                candidate_data = {
                    "candidate_name": candidate["candidate_name"]
                }

                # Add all keys dynamically from the candidate's data
                for key, value in candidate.items():
                    if key != "candidate_name":  # Exclude candidate_name from the loop
                        candidate_data[key] = value

                candidate_scores.append(candidate_data)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error scoring resume {resume.filename}: {e}")
    
    
    

    # Create DataFrame from the candidate_scores and write to CSV
    df = pd.DataFrame(candidate_scores)
    df2 = df.sort_values(by='total_score', ascending=False)
    output = BytesIO()
    df2.to_csv(output, index=False)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=resumes_scores.csv"})
