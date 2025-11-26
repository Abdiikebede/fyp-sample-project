from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime
import numpy as np
import pandas as pd

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

app = Flask(__name__)
CORS(app)

print("=" * 60)
print("🔧 PLAGIARISM DETECTION SYSTEM - COMPATIBILITY MODE")
print("=" * 60)

# ==================== MOCK AI CLASSES ====================

class MockEmbedder:
    def __init__(self):
        self.embedding_dim = 384
        print("✅ Mock Embedder initialized")
    
    def prepare_text(self, title, description):
        return f"TITLE: {title}. DESCRIPTION: {description}"
    
    def encode_text(self, text):
        # Return consistent mock embeddings based on text length
        np.random.seed(hash(text) % 10000)
        return np.random.randn(self.embedding_dim).astype('float32')

class MockVectorDatabase:
    def __init__(self, dimension):
        self.dimension = dimension
        self.metadata = []
        print("✅ Mock Vector Database initialized")
    
    def search(self, query_embedding, k=5):
        # Return mock similar projects
        mock_projects = [
            {
                'rank': 1,
                'similarity_score': 0.75,
                'metadata': {
                    'id': 1,
                    'title': 'AI-Based Learning System',
                    'year': 2023,
                    'decision': 'accept',
                    'original_text': 'An AI system for educational purposes'
                }
            },
            {
                'rank': 2, 
                'similarity_score': 0.62,
                'metadata': {
                    'id': 2,
                    'title': 'Machine Learning Project',
                    'year': 2022,
                    'decision': 'accept',
                    'original_text': 'ML algorithms for data analysis'
                }
            }
        ]
        return mock_projects[:k]
    
    def add_embeddings(self, embeddings, metadata_list):
        self.metadata.extend(metadata_list)

class MockDecisionEngine:
    def calculate_ai_score(self, similar_projects):
        if not similar_projects:
            return 0.0
        return min(similar_projects[0]['similarity_score'] / 0.7, 1.0)
    
    def calculate_final_score(self, ai_score, supervisor_rating):
        rating_score = (5 - supervisor_rating) / 5
        return (ai_score * 0.7) + (rating_score * 0.3)
    
    def make_decision(self, final_score):
        return "reject" if final_score > 0.5 else "accept"

class MockReportGenerator:
    def generate_report(self, new_project_text, similar_projects):
        if not similar_projects:
            return "No similar projects found. This appears to be an original work."
        
        top_match = similar_projects[0]
        similarity = top_match['similarity_score']
        
        if similarity > 0.8:
            risk_level = "HIGH"
            suggestion = "Strong evidence of potential plagiarism. Recommend careful review and comparison with similar projects."
        elif similarity > 0.6:
            risk_level = "MEDIUM"
            suggestion = "Moderate similarity detected. Recommend supervisor review and student explanation."
        elif similarity > 0.4:
            risk_level = "LOW" 
            suggestion = "Low similarity detected. Common concepts may be shared. Routine review recommended."
        else:
            risk_level = "VERY LOW"
            suggestion = "Minimal similarity. Likely original work."
        
        report = f"""
PLAGIARISM DETECTION REPORT
============================

RISK LEVEL: {risk_level}
HIGHEST SIMILARITY SCORE: {similarity:.3f}

MOST SIMILAR EXISTING PROJECTS:
"""
        
        for i, project in enumerate(similar_projects[:3]):
            report += f"""
{i+1}. {project['metadata']['title']}
    • Year: {project['metadata']['year']}
    • Previous Decision: {project['metadata']['decision']}
    • Similarity Score: {project['similarity_score']:.3f}
"""
        
        report += f"""
ANALYSIS:
{suggestion}

Total similar projects found: {len(similar_projects)}

NOTE: System running in compatibility mode. Install Python 3.11 for full AI features.
"""
        
        return report

# ==================== INITIALIZE SYSTEM ====================

embedder = MockEmbedder()
vector_db = MockVectorDatabase(384)
decision_engine = MockDecisionEngine()
report_generator = MockReportGenerator()

# Load your actual dataset if available
try:
    if os.path.exists('plagiarism_dataset_with_embeddings.csv'):
        df = pd.read_csv('plagiarism_dataset_with_embeddings.csv')
        print(f"📊 Loaded {len(df)} projects from your dataset")
    else:
        print("💡 No dataset found. Using demo data.")
except Exception as e:
    print(f"⚠️  Could not load dataset: {e}")

# Storage for submissions and decisions
submissions_db = []
decisions_db = []
next_submission_id = 1

print("✅ System initialized successfully!")
print("🌐 Starting server at: http://localhost:5000")
print("=" * 60)

# ==================== FLASK ROUTES ====================

@app.route('/')
def serve_frontend():
    """Serve the main frontend page"""
    frontend_dir = os.path.join(parent_dir, 'frontend')
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, etc.)"""
    frontend_dir = os.path.join(parent_dir, 'frontend')
    return send_from_directory(frontend_dir, path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'mode': 'compatibility',
        'timestamp': datetime.now().isoformat(),
        'message': 'System running in compatibility mode',
        'projects_loaded': len(vector_db.metadata),
        'python_version': sys.version
    })

@app.route('/api/submit', methods=['POST'])
def submit_project():
    """Student project submission endpoint"""
    global next_submission_id
    
    try:
        data = request.json
        student_id = data.get('student_id', 'unknown').strip()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        # Validate input
        if not title or not description:
            return jsonify({'error': 'Title and description are required'}), 400
        
        if len(title) < 5:
            return jsonify({'error': 'Title must be at least 5 characters long'}), 400
        
        if len(description) < 20:
            return jsonify({'error': 'Description must be at least 20 characters long'}), 400
        
        print(f"📥 New submission from student {student_id}: {title}")
        
        # Generate embedding
        new_text = embedder.prepare_text(title, description)
        new_embedding = embedder.encode_text(new_text)
        
        # Search for similar projects
        similar_projects = vector_db.search(new_embedding, k=3)
        
        # Generate AI report
        ai_report = report_generator.generate_report(new_text, similar_projects)
        
        # Store submission
        submission = {
            'submission_id': next_submission_id,
            'student_id': student_id,
            'title': title,
            'description': description,
            'similar_projects': similar_projects,
            'ai_report': ai_report,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending_review'
        }
        submissions_db.append(submission)
        
        next_submission_id += 1
        
        print(f"✅ Submission #{submission['submission_id']} processed")
        
        return jsonify({
            'submission_id': submission['submission_id'],
            'ai_report': ai_report,
            'similar_projects': similar_projects,
            'status': 'submitted',
            'message': 'Project submitted successfully for review'
        })
        
    except Exception as e:
        print(f"❌ Error processing submission: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """Get all submissions pending supervisor review"""
    try:
        pending_submissions = [s for s in submissions_db if s['status'] == 'pending_review']
        
        # Format response for frontend
        formatted_submissions = []
        for submission in pending_submissions:
            highest_similarity = submission['similar_projects'][0]['similarity_score'] if submission['similar_projects'] else 0
            
            # Determine risk level
            if highest_similarity > 0.7:
                risk_level = 'high'
            elif highest_similarity > 0.4:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            formatted_submissions.append({
                **submission,
                'risk_level': risk_level,
                'highest_similarity': highest_similarity
            })
        
        return jsonify(formatted_submissions)
        
    except Exception as e:
        return jsonify({'error': 'Error fetching submissions'}), 500

@app.route('/api/supervisor/rate', methods=['POST'])
def rate_submission():
    """Supervisor rating and decision endpoint"""
    try:
        data = request.json
        submission_id = data.get('submission_id')
        rating = data.get('rating', 3)
        comments = data.get('comments', '').strip()
        
        # Validate input
        if submission_id is None:
            return jsonify({'error': 'Submission ID is required'}), 400
        
        if not isinstance(rating, int) or rating < 0 or rating > 5:
            return jsonify({'error': 'Rating must be an integer between 0 and 5'}), 400
        
        # Find the submission
        submission = None
        for sub in submissions_db:
            if sub.get('submission_id') == submission_id:
                submission = sub
                break
        
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
        
        print(f"⭐ Rating submission #{submission_id} with rating {rating}/5")
        
        # Calculate final decision
        ai_score = decision_engine.calculate_ai_score(submission['similar_projects'])
        final_score = decision_engine.calculate_final_score(ai_score, rating)
        decision = decision_engine.make_decision(final_score)
        
        # Update submission status
        submission['status'] = 'reviewed'
        submission['supervisor_rating'] = rating
        submission['supervisor_comments'] = comments
        submission['final_decision'] = decision
        submission['final_score'] = final_score
        submission['reviewed_at'] = datetime.now().isoformat()
        
        # Store decision
        decision_record = {
            'submission_id': submission_id,
            'rating': rating,
            'comments': comments,
            'final_decision': decision,
            'final_score': final_score,
            'ai_score': ai_score,
            'timestamp': datetime.now().isoformat()
        }
        decisions_db.append(decision_record)
        
        # Add to database if accepted
        if decision == 'accept':
            new_metadata = {
                'id': len(vector_db.metadata) + 1,
                'title': submission['title'],
                'year': datetime.now().year,
                'decision': 'accept',
                'original_text': embedder.prepare_text(submission['title'], submission['description'])
            }
            new_embedding = embedder.encode_text(new_metadata['original_text'])
            vector_db.add_embeddings([new_embedding], [new_metadata])
            
            print(f"✅ Added new project to database: {submission['title']}")
        
        return jsonify({
            'submission_id': submission_id,
            'rating': rating,
            'final_decision': decision,
            'final_score': round(final_score, 3),
            'ai_score': round(ai_score, 3),
            'message': 'Rating submitted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': 'Error processing rating'}), 500

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get system statistics"""
    total_projects = len(vector_db.metadata)
    total_submissions = len(submissions_db)
    total_decisions = len(decisions_db)
    pending_reviews = len([s for s in submissions_db if s['status'] == 'pending_review'])
    
    # Calculate rejection rate
    if total_decisions > 0:
        rejections = len([d for d in decisions_db if d['final_decision'] == 'reject'])
        rejection_rate = (rejections / total_decisions) * 100
    else:
        rejection_rate = 0
    
    stats = {
        'system': {
            'status': 'active',
            'mode': 'compatibility',
            'version': '1.0.0',
            'message': 'Install Python 3.11 for full AI features'
        },
        'projects': {
            'total_projects': total_projects,
            'embedding_dimension': embedder.embedding_dim
        },
        'submissions': {
            'total_submissions': total_submissions,
            'pending_reviews': pending_reviews,
            'total_decisions': total_decisions,
            'rejection_rate': round(rejection_rate, 1)
        }
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)