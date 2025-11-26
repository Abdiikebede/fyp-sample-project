#!/usr/bin/env python3
import os
import subprocess
import sys

def setup_project():
    """Setup the plagiarism detection system"""
    print("Setting up Plagiarism Detection System...")
    
    # Create directory structure
    directories = [
        'backend/data',
        'frontend/assets',
        'models',
        'scripts'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Install requirements
    print("Installing Python requirements...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'])
    
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Place your dataset CSV in backend/data/")
    print("2. Run: python backend/app.py")
    print("3. Open http://localhost:5000 in your browser")

if __name__ == '__main__':
    setup_project()