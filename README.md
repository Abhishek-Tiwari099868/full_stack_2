# full_stack_2
InterviewAI

An AI-powered platform to help students practice for tech interviews — upload your resume, get instant AI feedback, and track your prep.

Live: https://interviewai-j6oj.onrender.com

What it does:
Sign up / log in with email+password, Google, or GitHub
Upload your resume (PDF) — get it parsed and reviewed by Gemini AI (extracted skills, target role, strengths, and improvement suggestions)
Edit and manage your extracted skills


Tech Stack:
Frontend: HTML, CSS, JavaScript
Backend: Flask (Python), PostgreSQL via Supabase, JWT auth, Authlib (OAuth)
AI: Google Gemini
Storage: Supabase Storage
Hosting: Render (backend as a web service, frontend as a static site)


Backend:
bashcd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
python run.py

You'll need a .env file with your own Supabase, Google/GitHub OAuth, and Gemini API keys — see backend/app/config.py for the full list of variables it expects.

Frontend:
Just open frontend/index.html in a browser, or serve the folder with any static server. Update frontend/js/config.js to point at your backend URL.
