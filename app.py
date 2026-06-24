from flask import Flask, render_template, request,redirect,session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import random
import os
import sqlite3
from flask import jsonify
import fitz

from streamlit import feedback
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
        question=random_question["question"],
        difficulty=difficulty
    )


@app.route('/get_question', methods=['POST'])
def get_question():

    subject = request.form['subject']
    difficulty = request.form['difficulty']
    random_question = random.choice(
        questions[subject][difficulty]
    )

    return jsonify({
        "question": random_question["question"]
    })

@app.route('/evaluate', methods=['POST'])
def evaluate():

    subject = request.form['subject']
    question = request.form['question']
    user_answer = request.form['answer']

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

    percentage = round(score * 100, 2)
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
            (user_id, subject, score)
            VALUES (?, ?, ?)
            """,
            (
                session['user_id'],
                subject,
                percentage
            )
        )

        conn.commit()
        conn.close()

    return render_template(
        'result.html',
        score=percentage,
        user_answer=user_answer,
        model_answer=model_answer,
        feedback=feedback
    )

@app.route('/leaderboard')
def leaderboard():

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

@app.route('/resume')
def resume():
    return render_template("resume.html")


@app.route('/upload_resume', methods=['POST'])
def upload_resume():

    file = request.files['resume']

    path = os.path.join(
        "uploads",
        file.filename
    )

    file.save(path)

    doc = fitz.open(path)

    text = ""

    for page in doc:
        text += page.get_text()
    found_skills = []
    for skill in skills_db:
        if skill.lower() in text.lower():
            found_skills.append(skill)
            

    return render_template(
        "skills.html",
        text=text,
        skills=found_skills
    )

@app.route('/hr')
def hr():

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

    score = 50

    if len(answer.split()) > 50:
        score += 20

    if len(answer.split()) > 100:
        score += 20

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