# Resume Ranking and Scoring API

This API allows you to score resumes dynamically based on extracted job criteria. The resumes are evaluated on multiple key skill sets, and a score from 0 to 5 is assigned to each skill, resulting in an overall total score for each candidate.

The API integrates with the Groq API to extract job criteria from job descriptions and uses these criteria to score resumes. The scores are then returned in a CSV format, which can be downloaded for further analysis.

## Features

- **Extract Criteria**: Extract job criteria from a job description document (PDF or DOCX) using Groq API.
- **Score Resumes**: Score uploaded resumes based on extracted criteria and return the results in a downloadable CSV format.
- **Dynamic Scoring**: The scoring of resumes is dynamic, with the API adjusting the criteria and scores based on the input job description and resumes.
- **Sorting by Total Score**: Candidates are ranked based on their total score, with the highest score at the top.

## Prerequisites

- Python 3.x
- Groq API key (for criteria extraction)
- FastAPI
- Uvicorn (for running the FastAPI app)
- pandas
- PyPDF2 (for PDF text extraction)
- python-docx (for DOCX text extraction)

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/resume-ranking-api.git
   cd resume-ranking-api

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

3. Set up your environment variables:
    ```bash
   GROQ_API=your_groq_api_key

## Usage
1. Extract Job Criteria from a Job Description
To extract job criteria, send a POST request to /extract_criteria/ with a PDF or DOCX file containing the job description. The response will return the extracted criteria in JSON format.

   Example request:
   ```bash
   curl -X 'POST' \
     'http://127.0.0.1:8000/extract_criteria/' \
     -F 'file=@job_description.pdf'


2. Score Resumes
After extracting the job criteria, you can score resumes by sending a POST request to /score_resumes/ with one or more resume files (PDF or DOCX). The API will return a CSV file with the candidates' scores based on the extracted criteria.
   Example request:
   ```bash
   curl -X 'POST' \
     'http://127.0.0.1:8000/score_resumes/' \
     -F 'resumes=@resume1.pdf' \
     -F 'resumes=@resume2.docx'


3. CSV Output
   The response will include a CSV file with the following columns:
   
   - candidate_name: The name of the candidate (if extracted).
   - Skill_set1: The score for Skill_Set1
   - Skill_set2: The score for Skill_Set2
   - Skill_set3: The score for Skill_Set3
   - total_score: The total score for the candidate, based on the sum of all skill set scores.
   
## Running the Application
   To run the FastAPI app locally, use Uvicorn:
      ```bash
      uvicorn main:app --reload
   This will start the API on http://127.0.0.1:8000.

## Endpoints
   - POST /extract_criteria/: Extract job criteria from a job description (PDF or DOCX).
   - POST /score_resumes/: Score resumes based on the extracted criteria and return the results in CSV format.

## Contribution Guidelines : 

We welcome contributions to this project! If you'd like to help improve it, please follow these guidelines:

### 1. **Fork the Repository**

   Start by forking the repository. This will create a copy of the project under your GitHub account, where you can freely make changes.

### 2. **Make Changes**

   Create a new branch for each significant change you make. This keeps your work isolated from the main codebase until it is ready. Use a descriptive branch name, such as:
   
      ```bash
      git checkout -b feature/add-resume-upload

### 3. ** Make Changes and Commit**
   Make the necessary changes to the project. Be sure to follow the existing coding style and conventions. Add tests where applicable, and ensure all tests pass before committing.
   When making commits, use clear and concise commit messages to describe the purpose of the changes. Follow the format:

      ```bash
      git commit -m "Brief description of changes"
   If your commit fixes a bug or addresses an issue, include the issue number in the commit message:
      ```bash
      git commit -m "Fix bug with PDF extraction #15"
      
### 5. **Test Your Changes**
   Make sure to test your changes thoroughly. Ensure that the application works as expected and that all new features or bug fixes have appropriate tests.

### 6. **Push Your Changes**
   Once you're happy with your changes, push the branch to your forked repository:

      ```bash
      git push origin feature/add-resume-upload
      

## License
   This project is licensed under the MIT License - see the LICENSE file for details.


