from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime
import numpy as np
import pandas as pd
import faiss

# Add the current directory and parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

# Now import our custom modules
try:
    from models.embedder import PlagiarismEmbedder
    from models.vector_db import VectorDatabase
    from models.decision_engine import DecisionEngine
    from models.report_generator import ReportGenerator
    print("✅ Successfully imported all custom modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔄 Trying alternative import...")
    # Alternative import method
    import importlib.util
    spec = importlib.util.spec_from_file_location("embedder", "../models/embedder.py")
    embedder_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(embedder_module)
    PlagiarismEmbedder = embedder_module.PlagiarismEmbedder
    
    spec = importlib.util.spec_from_file_location("vector_db", "../models/vector_db.py")
    vector_db_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vector_db_module)
    VectorDatabase = vector_db_module.VectorDatabase
    
    spec = importlib.util.spec_from_file_location("decision_engine", "../models/decision_engine.py")
    decision_engine_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decision_engine_module)
    DecisionEngine = decision_engine_module.DecisionEngine
    
    spec = importlib.util.spec_from_file_location("report_generator", "../models/report_generator.py")
    report_generator_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(report_generator_module)
    ReportGenerator = report_generator_module.ReportGenerator

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variables
embedder = None
vector_db = None
decision_engine = None
report_generator = None

# Storage for submissions and decisions
submissions_db = []
decisions_db = []
next_submission_id = 1

def load_saved_system():
    """Load your previously trained system from Colab with pre-computed embeddings"""
    global embedder, vector_db, decision_engine, report_generator
    
    print("=" * 60)
    print("🚀 LOADING YOUR PRE-TRAINED PLAGIARISM DETECTION SYSTEM")
    print("=" * 60)
    
    # Initialize components
    embedder = PlagiarismEmbedder()
    decision_engine = DecisionEngine()
    report_generator = ReportGenerator()
    
    # Paths to your saved system files
    csv_path = 'plagiarism_dataset_with_embeddings.csv'
    metadata_path = 'plagiarism_system_metadata.json'
    index_path = 'plagiarism_index.faiss'
    
    # Check if all system files exist
    if all(os.path.exists(path) for path in [csv_path, metadata_path, index_path]):
        print("✅ Found your saved system files:")
        print(f"   - {csv_path}")
        print(f"   - {metadata_path}") 
        print(f"   - {index_path}")
        print("\n🔍 Loading your pre-computed embeddings and FAISS index...")
        
        try:
            # Use the fast loading method
            vector_db = VectorDatabase.load_system_fast(
                csv_path=csv_path,
                metadata_path=metadata_path,
                index_path=index_path
            )
            
            print(f"✅ System loaded successfully!")
            print(f"📊 Loaded {len(vector_db.metadata)} projects from your training")
            print(f"🔍 FAISS index size: {vector_db.index.ntotal} vectors")
            
        except Exception as e:
            print(f"❌ Error loading system: {e}")
            print("🔄 Falling back to standard loading...")
            vector_db = VectorDatabase.load_system(
                csv_path=csv_path,
                metadata_path=metadata_path,
                index_path=index_path,
                embedder=embedder
            )
    
    else:
        print("❌ Saved system files not found. Creating empty system...")
        missing_files = []
        if not os.path.exists(csv_path): missing_files.append(csv_path)
        if not os.path.exists(metadata_path): missing_files.append(metadata_path) 
        if not os.path.exists(index_path): missing_files.append(index_path)
        print(f"   Missing: {missing_files}")
        
        # Create empty vector database
        vector_db = VectorDatabase(embedder.embedding_dim)
        print("⚠️  Created empty system. You need to train with your dataset.")

    # Test the system
    print("\n🧪 Testing system functionality...")
    try:
        test_embedding = embedder.encode_text("System test")
        print(f"✅ Embedder working - Dimension: {test_embedding.shape}")
        
        if len(vector_db.metadata) > 0:
            test_results = vector_db.search(test_embedding, k=1)
            print(f"✅ Vector database working - Found {len(test_results)} similar projects")
        else:
            print("✅ Vector database initialized (empty)")
            
    except Exception as e:
        print(f"❌ System test failed: {e}")

# Initialize the system when the app starts
load_saved_system()

# ==================== ROUTES ====================

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
    """Health check endpoint showing system status"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'system': 'Your Pre-trained Plagiarism Detection System',
        'projects_loaded': len(vector_db.metadata) if vector_db else 0,
        'faiss_index_size': vector_db.index.ntotal if vector_db and vector_db.index else 0,
        'submissions_pending': len([s for s in submissions_db if s['status'] == 'pending_review'])
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
        
        # Generate embedding using your trained system
        new_text = embedder.prepare_text(title, description)
        new_embedding = embedder.encode_text(new_text)
        
        # Search against YOUR trained vector database
        similar_projects = vector_db.search(new_embedding, k=5)
        
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
        
        print(f"✅ Submission #{submission['submission_id']} processed. Found {len(similar_projects)} similar projects")
        
        return jsonify({
            'submission_id': submission['submission_id'],
            'ai_report': ai_report,
            'similar_projects': similar_projects,
            'status': 'submitted',
            'message': 'Project submitted successfully for review'
        })
        
    except Exception as e:
        print(f"❌ Error processing submission: {e}")
        return jsonify({'error': 'Internal server error processing submission'}), 500

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
        print(f"❌ Error fetching submissions: {e}")
        return jsonify({'error': 'Internal server error fetching submissions'}), 500

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
        
        # Calculate final decision using your trained system
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
        
        # Add to your vector database if accepted (expands your knowledge base!)
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
            print(f"📈 Database now contains {len(vector_db.metadata)} projects")
        
        response_data = {
            'submission_id': submission_id,
            'rating': rating,
            'final_decision': decision,
            'final_score': round(final_score, 3),
            'ai_score': round(ai_score, 3),
            'message': 'Rating submitted successfully',
            'projects_in_database': len(vector_db.metadata)
        }
        
        if decision == 'accept':
            response_data['message'] += '. Project added to database.'
        else:
            response_data['message'] += '. Project rejected.'
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error processing rating: {e}")
        return jsonify({'error': 'Internal server error processing rating'}), 500

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get comprehensive system statistics"""
    try:
        total_projects = len(vector_db.metadata) if vector_db else 0
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
                'version': '1.0.0',
                'model': 'Sentence-BERT all-MiniLM-L6-v2'
            },
            'projects': {
                'total_projects': total_projects,
                'your_trained_projects': total_projects,
                'embedding_dimension': embedder.embedding_dim if embedder else 384,
                'faiss_index_size': vector_db.index.ntotal if vector_db and vector_db.index else 0
            },
            'submissions': {
                'total_submissions': total_submissions,
                'pending_reviews': pending_reviews,
                'total_decisions': total_decisions,
                'rejection_rate': round(rejection_rate, 1)
            },
            'performance': {
                'system_loaded': total_projects > 0,
                'using_pretrained_embeddings': True
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")
        return jsonify({'error': 'Internal server error fetching statistics'}), 500

@app.route('/api/admin/export', methods=['GET'])
def export_data():
    """Export system data for backup or analysis"""
    try:
        export_data = {
            'export_time': datetime.now().isoformat(),
            'system_info': {
                'projects_loaded': len(vector_db.metadata) if vector_db else 0,
                'total_submissions': len(submissions_db),
                'total_decisions': len(decisions_db)
            },
            'submissions': submissions_db,
            'decisions': decisions_db,
            'metadata': vector_db.metadata[:10] if vector_db and vector_db.metadata else []
        }
        
        return jsonify(export_data)
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return jsonify({'error': 'Internal server error exporting data'}), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🎉 YOUR PLAGIARISM DETECTION SYSTEM IS READY!")
    print("=" * 60)
    print(f"📊 System loaded with {len(vector_db.metadata) if vector_db else 0} trained projects")
    print(f"🔍 FAISS index contains {vector_db.index.ntotal if vector_db and vector_db.index else 0} vectors")
    print(f"🌐 Starting server at: http://localhost:5000")
    print("\n📋 AVAILABLE ENDPOINTS:")
    print("  Frontend:        http://localhost:5000")
    print("  Health Check:    GET  http://localhost:5000/api/health")
    print("  Submit Project:  POST http://localhost:5000/api/submit")
    print("  Get Submissions: GET  http://localhost:5000/api/submissions")
    print("  Rate Submission: POST http://localhost:5000/api/supervisor/rate")
    print("  System Stats:    GET  http://localhost:5000/api/admin/stats")
    print("\n💡 Use Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)