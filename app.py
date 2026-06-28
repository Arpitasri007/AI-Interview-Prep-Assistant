from flask import Flask, render_template, request,redirect,session

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import random
import os
import sqlite3
from flask import jsonify
from PyPDF2 import PdfReader
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)
#skills database
skills_db = [
    "python",
    "sql",
    "machine learning",
    "flask",
    "html",
    "css",
    "javascript",
    "data analysis",
    "deep learning"
]
app.secret_key = 'your_secret_key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "questions.json"), "r") as file:
    questions = json.load(file)

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("interview.db")
    cursor = conn.cursor()

    # Overall statistics
    cursor.execute(
        """
        SELECT COUNT(*),
               AVG(score),
               MAX(score)
        FROM results
        WHERE user_id=?
        """,
        (session['user_id'],)
    )

    stats = cursor.fetchone()

    # Recent history
    cursor.execute(
        """
        SELECT subject, score
        FROM results
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 10
        """,
        (session['user_id'],)
    )

    history = cursor.fetchall()

    # Subject-wise performance
    cursor.execute(
        """
        SELECT subject,
               ROUND(AVG(score), 2)
        FROM results
        WHERE user_id=?
        GROUP BY subject
        """,
        (session['user_id'],)
    )

    subject_stats = cursor.fetchall()

    # Weakest subject
    weakest_subject = None

    if subject_stats:
        weakest_subject = min(
            subject_stats,
            key=lambda x: x[1]
        )[0]

    conn.close()

    scores = [row[1] for row in history]

    return render_template(
        "dashboard.html",
        total=stats[0] or 0,
        avg=round(stats[1] or 0, 2),
        highest=stats[2] or 0,
        history=history,
        scores=scores,
        subject_stats=subject_stats,
        weakest_subject=weakest_subject
    )

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = generate_password_hash(
            request.form['password']
        )

        conn = sqlite3.connect("interview.db")
        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, password)
            )

            conn.commit()

        except:
            return "Username already exists"

        finally:
            conn.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("interview.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(
            user[2],
            password
        ):

            session['user_id'] = user[0]
            session['username'] = user[1]

            return redirect('/')

        return "Invalid credentials"

    return render_template('login.html')

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/interview')
def home():

    subject = "Python"
    difficulty = "Easy"

    random_question = random.choice(
        questions[subject][difficulty]
    )

    return render_template(
        "index.html",
        subjects=questions.keys(),
        questions=questions,#IMPORTANT: Pass the entire questions dictionary to the template
        question=random_question["question"],
        difficulty=difficulty
    )


@app.route('/get_question', methods=['POST'])
def get_question():

    subject = request.form.get('subject')
    difficulty = request.form.get('difficulty')
    if not subject or not difficulty:
        return jsonify({"question": "No question found"})
    random_question = random.choice(
        questions[subject][difficulty]
    )

    return jsonify({
        "question": random_question["question"]
    })

@app.route('/evaluate', methods=['POST'])
def evaluate():

    subject = request.form.get('subject')
    difficulty = request.form.get('difficulty')
    question = request.form.get('question')
    user_answer = request.form.get('answer')

    model_answer = ""
    difficulty = request.form['difficulty']
    for q in questions[subject][difficulty]:
        if q["question"] == question:
            model_answer = q["answer"]
            break

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(
        [model_answer, user_answer]
    )

    score = cosine_similarity(
        vectors[0],
        vectors[1]
    )[0][0]
    keywords = model_answer.lower().split()
    bonus = 0
    for word in keywords:
        if word in user_answer.lower():
            bonus += 0.02
    percentage = round(score * 100, 2) + bonus
    feedback = []

    answer = user_answer.lower()

    if "mutable" in answer:
        feedback.append(
            "✓ Mentioned mutability"
        )

    if "ordered" in answer:
        feedback.append(
            "✓ Mentioned ordering"
        )

    if "collection" in answer:
        feedback.append(
            "✓ Explained collection concept"
        )

    if len(feedback) == 0:
        feedback.append(
            "Try adding more technical details."
        )

    # Save result if user is logged in
    if 'user_id' in session:

        conn = sqlite3.connect("interview.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO results
            (user_id, subject, difficulty, score)
            VALUES (?, ?, ?, ?)
            """,
            (
                session['user_id'],
                subject,
                difficulty,
                percentage
            )
        )

        conn.commit()
        conn.close()
    recommendation = ""
    if percentage >= 80:
        recommendation = "Excellent. Move to advanced interview questions."

    elif percentage >= 60:
        recommendation = "Good. Focus on improving explanation clarity."

    elif percentage >= 40:
        recommendation = "Revise core concepts and practice more."

    else:
        recommendation = "Study fundamentals before attempting advanced questions."
    return render_template(
        'result.html',
        score=percentage,
        user_answer=user_answer,
        model_answer=model_answer,
        feedback=feedback,
        recommendation=recommendation
    )

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("interview.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT users.username,
               ROUND(AVG(results.score),2)
        FROM results
        JOIN users
        ON results.user_id = users.id
        GROUP BY users.id
        ORDER BY AVG(results.score) DESC
        LIMIT 10
    """)

    leaders = cursor.fetchall()

    conn.close()

    return render_template(
        "leaderboard.html",
        leaders=leaders
    )

@app.route('/resume', methods=['GET', 'POST'])
def resume():

    if request.method == 'POST':

        file = request.files['resume']

        os.makedirs("uploads", exist_ok=True)

        filepath = os.path.join(
            "uploads",
            file.filename
        )

        file.save(filepath)

        resume_text = extract_resume_text(filepath)

        skills = extract_skills(resume_text)

        # SCORE CALCULATION FIRST
        score = 50

        score += len(skills) * 4

        if len(resume_text) > 500:
            score += 10

        if len(resume_text) > 1000:
            score += 10

        score = min(score, 100)

        # SUGGESTIONS AFTER SCORE EXISTS
        suggestions = []

        if "python" not in skills:
            suggestions.append(
                "Learn Python for software development and AI."
            )

        if "sql" not in skills:
            suggestions.append(
                "Add SQL skills for database management."
            )

        if "flask" not in skills:
            suggestions.append(
                "Build Flask projects to strengthen backend development."
            )

        if "machine learning" not in skills:
            suggestions.append(
                "Explore Machine Learning projects and courses."
            )

        if "github" not in skills:
            suggestions.append(
                "Use GitHub to showcase your projects."
            )

        if score >= 80:
            suggestions.append(
                "Excellent profile. Keep building advanced projects."
            )
        print("SKILLS:", skills)
        print("SCORE:", score)
        print("SUGGESTIONS:", suggestions)
        return render_template(
            "resume_result.html",
            skills=skills,
            score=score,
            text=resume_text[:1000],
            suggestions=suggestions
        )

    return render_template("resume.html")

def extract_skills(text):

    skills_db = [
        "python",
        "java",
        "c++",
        "c",
        "sql",
        "mysql",
        "html",
        "css",
        "javascript",
        "bootstrap",
        "react",
        "nodejs",
        "flask",
        "django",
        "git",
        "github",
        "machine learning",
        "deep learning",
        "data science",
        "artificial intelligence",
        "tensorflow",
        "pandas",
        "numpy",
        "opencv",

        # general skills
        "computer",
        "ms office",
        "excel",
        "word",
        "powerpoint",
        "communication",
        "leadership",
        "teamwork",
        "problem solving"
    ]

    text = text.lower()

    found_skills = []

    for skill in skills_db:
        if skill.lower() in text:
            found_skills.append(skill)

    return list(set(found_skills))

def extract_resume_text(pdf_path):
    text = ""

    try:
        reader = PdfReader(pdf_path)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:
        print("PDF Extraction Error:", e)

    return text



@app.route('/hr')
def hr():
    if 'user_id' not in session:
        return redirect('/login')

    with open(
        "hr_questions.json"
    ) as f:

        hr_questions = json.load(f)

    question = random.choice(
        hr_questions
    )

    return render_template(
        "hr.html",
        question=question
    )

@app.route('/evaluate_hr', methods=['POST'])
def evaluate_hr():

    answer = request.form['answer']

    score = 0
    words = len(answer.split())
    if words >= 20:
        score += 20
    if words >= 50:
        score += 30
    if words >= 100:
        score += 30

    keywords = [
        "team",
        "leadership",
        "project",
        "challenge",
        "communication"
    ]

    for keyword in keywords:
        if keyword in answer.lower():
            score += 4

    score = min(score, 100)

    feedback = []

    if len(answer.split()) < 30:
        feedback.append(
            "Try giving more details."
        )

    if "team" in answer.lower():
        feedback.append(
            "Good teamwork example."
        )

    return render_template(
        "hr_result.html",
        score=score,
        feedback=feedback
    )

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)