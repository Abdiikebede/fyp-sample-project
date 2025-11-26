#!/usr/bin/env python3
import requests
import json

def test_system():
    """Test the plagiarism detection system"""
    base_url = "http://localhost:5000/api"
    
    try:
        # Health check
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test submission
        test_data = {
            "student_id": "test_student_001",
            "title": "Machine Learning for Healthcare Analysis",
            "description": "A system that uses machine learning algorithms to analyze healthcare data and improve patient outcomes through predictive analytics."
        }
        
        response = requests.post(f"{base_url}/submit", json=test_data)
        print(f"Submission test: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Submission ID: {result['submission_id']}")
            print(f"Similar projects found: {len(result['similar_projects'])}")
        
        # Test getting submissions
        response = requests.get(f"{base_url}/submissions")
        print(f"Submissions check: {response.status_code} - Found {len(response.json())} submissions")
        
    except Exception as e:
        print(f"Error testing system: {e}")

if __name__ == '__main__':
    test_system()