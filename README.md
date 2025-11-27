# Academic Plagiarism Detection System
**A powerful AI-powered plagiarism detection system designed for Final Year Projects, theses, and academic submissions. Powered by Sentence-BERT embeddings and ultra-fast FAISS vector search.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3%2B-black?logo=flask)](https://flask.palletsprojects.com/)
[![Sentence-BERT](https://img.shields.io/badge/AI-SentenceBERT-green)](https://www.sbert.net/)
[![FAISS](https://img.shields.io/badge/Vector%20DB-FAISS-ff69b4)](https://github.com/facebookresearch/faiss)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features
- **AI-Powered Detection** – Uses **Sentence-BERT** (all-MiniLM-L6-v2) for deep semantic similarity (detects paraphrased plagiarism!)
- **Real-time Analysis** – Instant plagiarism checking on student submissions
- **Supervisor Dashboard** – Intuitive interface for reviewing reports, viewing highlighted matches, and assigning ratings
- **FAISS Vector Database** – Lightning-fast similarity search across thousands of past projects
- **Beautiful Modern UI** – Fully responsive web app with gradient backgrounds, glassmorphism, and smooth animations
- **Separate Student & Supervisor Portals** – Tailored experience for each user role

## Screenshots
<div align="center">
  <img src="https://via.placeholder.com/800x450/6366f1/ffffff?text=Student+Submission+Dashboard" alt="Student Dashboard" width="48%"/>
  <img src="https://via.placeholder.com/800x450/10b981/ffffff?text=Supervisor+Review+Panel" alt="Supervisor Dashboard" width="48%"/>
  <br/><br/>
  <img src="https://via.placeholder.com/800x450/ff6b6b/ffffff?text=Plagiarism+Report+%E2%80%93+Highlighted+Matches" alt="Plagiarism Report" width="80%"/>
</div>

*(Replace placeholder images with actual screenshots for best results!)*

## Technology Stack
| Layer       | Technology                                      |
|-------------|-------------------------------------------------|
| Backend     | Python 3.11+, Flask                             |
| AI / NLP    | Sentence-Transformers (SBERT), FAISS            |
| Data        | Pandas, NumPy, SQLite                           |
| Frontend    | HTML5, CSS3 (custom modern styles), Vanilla JS  |
| UI          | Gradient backgrounds, glassmorphism, animations |

## Prerequisites
- Python 3.11 or later (**3.11 recommended**)
- `pip` package manager
- Minimum 4GB RAM
- 2GB free disk space

## Quick Start (Recommended – Works on Python 3.11–3.13+)
```bash
git clone https://github.com/yourusername/academic-plagiarism-detector.git
cd academic-plagiarism-detector/sample-of-fyp/backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run compatibility version
python app_working.py
Open your browser → http://localhost:5000
##Development Mode (Python 3.11 only – full features)
python app.py
##Usage
1.Students → Upload project report (PDF, DOCX, TXT supported)
2.System instantly compares against all previous submissions
3.Supervisors → View detailed similarity reports with highlighted matches & scores
4.Provide ratings and feedback directly in the platform
##Contributing
Contributions, issues, and feature requests are welcome! Feel free to fork and submit pull requests.
##License
This project is licensed under the MIT License – see the LICENSE file for details.
##Made with ❤️ for academic integrity
##⭐ Star this repo if you find it helpful! ⭐
