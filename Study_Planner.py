import os
import google.generativeai as genai
from flask import Flask, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

# Load API Key from .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Flask App
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

@app.route("/", methods=["GET", "POST"])
def generate_plan():
    study_plan = None

    if request.method == "POST":
        subjects = request.form.get("subjects", "")
        study_hours = request.form.get("study_hours", "0")
        exam_date = request.form.get("exam_date", "")

        # Validate Input
        if not subjects or not study_hours.isdigit() or int(study_hours) <= 0 or not exam_date:
            study_plan = "<p style='color:red;'>Invalid input. Please enter valid details.</p>"
        else:
            study_hours = int(study_hours)

            # Calculate Remaining Days
            today = datetime.today().date()
            exam_date_obj = datetime.strptime(exam_date, "%Y-%m-%d").date()
            remaining_days = (exam_date_obj - today).days

            # AI Prompt for Structured Table Output
            prompt = f"""
            Generate a *structured study plan* for the following:
            - *Subjects:* {subjects}
            - *Study Hours per Day:* {study_hours} hours
            - *Exam Date:* {exam_date} (Remaining Days: {remaining_days})

            *Format the response in proper HTML table format with headings.*
            Include:
            1. *General Approach (in a bullet list)*
            2. *Weekly Study Schedule (as an HTML table)*
            3. *Subject-wise Breakdown (in an HTML table)*
            4. *Revision Strategy (in a structured list)*
            5. *Additional Tips (in a structured list)*

            Ensure proper *HTML table formatting* for readability.
            """

            try:
                model = genai.GenerativeModel("gemini-1.5-pro")
                response = model.generate_content(prompt)

                if response and response.candidates:
                    study_plan = response.candidates[0].content.parts[0].text
                else:
                    study_plan = "<p style='color:red;'>Failed to generate study plan.</p>"

            except Exception as e:
                study_plan = f"<p style='color:red;'>Error generating plan: {str(e)}</p>"

    return render_template("index.html", study_plan=study_plan)

if __name__ == "__main__":
    app.run(debug=True)