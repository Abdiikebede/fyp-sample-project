🎓 Academic Plagiarism Detection System
A powerful, AI-powered plagiarism detection system specifically designed for Final Year Projects, theses, and academic submissions using state-of-the-art Sentence-BERT embeddings and ultra-fast vector similarity search.
Python
Flask
Sentence-BERT
FAISS
License: MIT
🚀 Features

🔥 AI-Powered Detection – Uses Sentence-BERT (all-MiniLM-L6-v2) for deep semantic similarity detection (catches paraphrased plagiarism!)
⚡ Real-time Analysis – Instant plagiarism checking as soon as students submit
👨‍🏫 Supervisor Dashboard – Clean interface for supervisors to review reports, view similarity highlights, and assign grades/ratings
🧠 FAISS Vector Database – Lightning-fast similarity search even with thousands of past projects
🎨 Beautiful Modern UI – Fully responsive web interface with gradient backgrounds, smooth animations, and glassmorphism design
📱 Student & Supervisor Portals – Separate views tailored for both roles

🖼️ Screenshots

  Student Dashboard
  Supervisor Dashboard
  


  Plagiarism Report

(Replace the placeholder links above with real screenshots for maximum appeal!)
🛠️ Technology Stack





























LayerTechnologyBackendPython 3.11+, FlaskAI/NLPSentence-Transformers (SBERT), FAISSDataPandas, NumPy, SQLite (default)FrontendHTML5, CSS3 (Tailwind-like custom styles), Vanilla JSUI EffectsGradient backgrounds, glassmorphism, animations
📋 Prerequisites

Python 3.11 or later (3.11 highly recommended for best performance)
pip package manager
Minimum 4GB RAM
2GB free disk space

🚀 Quick Start
Method 1: Compatibility Mode (Recommended for Python 3.11 – 3.13+)
Bash# Clone or download the project
git clone https://github.com/yourusername/academic-plagiarism-detector.git
cd academic-plagiarism-detector/sample-of-fyp/backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application (compatibility version)
python app_working.py
🌍 Open your browser and go to: http://localhost:5000
Method 2: Development Mode (Python 3.11 only – full features)
Bashpython app.py
🎯 Usage

Students → Upload your project report (PDF/TXT/DOCX supported)
System instantly analyzes against all previous submissions
Supervisors → Get detailed similarity reports with highlighted matches and percentage scores
Rate and provide feedback directly in the platform

🤝 Contributing
Contributions are welcome! Feel free to submit issues or pull requests. Let's make academic integrity easier together.
📄 License
This project is licensed under the MIT License – see the LICENSE file for details.

Made with ❤️ for fair academia
⭐ Star this repo if you find it useful! ⭐
