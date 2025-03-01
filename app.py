import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash
from pdfminer.high_level import extract_text
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'resumes/'
app.secret_key = 'a_very_long_and_random_secret_key_123456789'

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gokulprakash1109@gmail.com'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'tpcc aueq wnym gjep'  # Replace with your App Password

# Initialize Flask-Mail
mail = Mail(app)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Step 1: Define job description skills
job_description = """
We are looking for candidates with the following skills:
- Java
- Spring
- Hibernate
- MySQL
"""

# Step 2: Define function to extract skills from resume
def extract_skills(resume_text):
    required_skills = ["Java", "Spring", "Hibernate", "MySQL"]
    resume_skills = [skill for skill in required_skills if skill.lower() in resume_text.lower()]
    return resume_skills

# Step 3: Define function to extract email from resume
def extract_email(resume_text):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    email = re.search(email_pattern, resume_text)
    return email.group(0) if email else None

# Step 4: Define function to send email confirmation using Flask-Mail
def send_email_confirmation(to_email):
    msg = Message(subject="Job Application Status",
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[to_email])
    msg.body = "Congratulations! You have been selected for the job based on your resume."
    
    # Send the email
    mail.send(msg)

# Step 5: Route for the home page and resume upload
@app.route('/')
def index():
    return render_template('index.html')

# Step 6: Handle file upload and processing
@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        flash('No file part')
        return redirect(request.url)

    resume_file = request.files['resume']

    if resume_file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if resume_file:
        # Save resume file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
        resume_file.save(filepath)

        # Extract text from PDF
        if resume_file.filename.endswith('.pdf'):
            resume_text = extract_text(filepath)
        else:
            with open(filepath, 'r', encoding='utf-8') as file:
                resume_text = file.read()

        # Extract skills and email
        skills = extract_skills(resume_text)
        email = extract_email(resume_text)

        # Check if candidate is selected
        if len(skills) == 4 and email:  # Updated to check for all 4 skills
            send_email_confirmation(email)
            flash(f"Selected: {resume_file.filename} - Skills: {skills}")
        else:
            flash(f"Not selected: {resume_file.filename} - Skills: {skills}")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
