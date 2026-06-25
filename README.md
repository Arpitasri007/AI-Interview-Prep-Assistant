🧠 AI Interview Preparation Assistant

An AI-powered web application that helps students and job seekers prepare for technical interviews through interactive practice sessions, answer evaluation, performance tracking, and leaderboards.

📌 Project Overview

The AI Interview Preparation Assistant simulates a real interview environment by presenting users with subject-specific questions and evaluating their responses. It enables continuous learning through practice, feedback, and progress tracking.

This project is designed to help candidates improve their technical knowledge, confidence, and interview performance.

✨ Features
🎯 Subject-wise interview preparation
📚 Multiple domains such as Python, OOP, DBMS, and more
📊 Easy, Medium, and Hard difficulty levels
🔀 Random interview question generation
🤖 Automated answer evaluation and scoring
🏆 Leaderboard to compare performance
📈 Dashboard for tracking progress
💻 User-friendly web interface
🔄 Extensible question dataset


🛠️ Tech Stack

Technology	Purpose
Python	Core programming language
Flask	Backend web framework
HTML/CSS	Frontend structure and styling
Bootstrap	Responsive UI
Scikit-learn	Answer evaluation and scoring
Pandas	Data processing
NumPy	Numerical computations
Git & GitHub	Version control



📂 Project Structure

AI-Interview-Prep-Assistant/
│
├── app.py
├── requirements.txt
├── Procfile
├── README.md
├── .gitignore
│
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── leaderboard.html
│   └── ...
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── data/
│   └── questions.json
│
└── models/
    └── scoring_model.pkl


🚀 Installation
Clone the Repository
git clone https://github.com/Arpitasri007/AI-Interview-Prep-Assistant.git
cd AI-Interview-Prep-Assistant
Create Virtual Environment
python -m venv venv
Activate Virtual Environment

Windows

venv\Scripts\activate

Linux / macOS

source venv/bin/activate
Install Dependencies
pip install -r requirements.txt
Run the Application
python app.py

Open:

http://127.0.0.1:5000


🎮 Usage
Launch the application.
Select a subject and difficulty level.
Attempt the generated interview question.
Submit your answer.
Receive an evaluation score and feedback.
Track your progress on the dashboard.
Compete with others through the leaderboard.
📸 Screenshots

Add screenshots of your application here:

Home Page
screenshots/home.png
Dashboard
screenshots/dashboard.png
Leaderboard
screenshots/leaderboard.png
🔮 Future Enhancements
Integration with Large Language Models (LLMs)
Real-time AI feedback
Voice-based mock interviews
Resume-based question generation
User authentication system
Cloud database integration
Interview performance analytics
🤝 Contributing

Contributions are welcome.

Fork the repository

Create a feature branch

git checkout -b feature-name

Commit changes

git commit -m "Add new feature"

Push to your branch

git push origin feature-name

Create a Pull Request


👩‍💻 Author

Arpita Srivastava

GitHub: https://github.com/Arpitasri007

⭐ Acknowledgements

This project was developed to help students and professionals prepare effectively for technical interviews through interactive and AI-assisted learning.
