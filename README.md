🧠 AI Interview Preparation Assistant

An intelligent web-based Interview Preparation System built using Flask that helps users practice interview questions, evaluate answers, and improve performance using an AI-based scoring approach.

**🚀 Features
📌 Subject-wise interview questions (Python, OOP, DBMS, etc.)
🎯 Difficulty levels (Easy, Medium, Hard)
🤖 AI-based answer evaluation / scoring system
🏆 Leaderboard to track performance
📊 Dashboard for user progress tracking
🔄 Random question generation for practice
🧑‍💻 Simple and interactive UI using Flask templates

**🛠️ Tech Stack
Backend: Python, Flask
Frontend: HTML, CSS, Bootstrap
AI/ML: Scikit-learn (for scoring logic / evaluation if used)
Database: CSV / JSON (or SQLite if implemented)
Other Tools: Git, GitHub

**📁 Project Structure
InterviewPrepAI/
│
├── app.py
├── requirements.txt
├── data/
│   └── questions.json / questions.csv
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── leaderboard.html
│
├── static/
│   ├── css/
│   ├── js/
│
├── models/ (if any ML model used)
└── README.md

**⚙️ Installation & Setup
1. Clone the repository
git clone https://github.com/your-username/AI-Interview-Prep-Assistant.git
cd AI-Interview-Prep-Assistant
2. Create virtual environment (optional but recommended)
python -m venv venv
3. Activate environment
Windows:
venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt
5. Run the application
python app.py
6. Open in browser
http://127.0.0.1:5000

**📊 How It Works
Select a subject (e.g., Python)
Choose difficulty level
Get a random interview question
Write your answer
System evaluates and provides feedback/score
Track progress on dashboard & leaderboard

**🧠 Future Improvements
🧠 Integrate OpenAI / LLM-based answer evaluation
🎤 Add voice-based interview simulation
📱 Mobile responsive UI improvements
🗄️ Use database (MySQL/PostgreSQL) instead of CSV
📈 Advanced analytics dashboard
🤝 Contributing

👨‍💻 Author:
Arpita Srivastava
GitHub: https://github.com/Arpitasri007/AI-Interview-Prep-Assistant

⭐ Show Your Support

If you like this project:

⭐ Star the repository
🍴 Fork it
📢 Share it
