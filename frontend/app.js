// Configuration
const API_BASE_URL = 'http://localhost:5000/api'; // Change this to your backend URL

// Global variables
let currentSubmissionId = null;
let submissions = [];

// Tab switching
function switchTab(tabName) {
    // Update tabs
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Load data for specific tabs
    if (tabName === 'supervisor') {
        loadSubmissions();
    } else if (tabName === 'admin') {
        loadAdminStats();
    }
}

// Student Submission
document.getElementById('submission-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const studentId = document.getElementById('studentId').value;
    const title = document.getElementById('projectTitle').value;
    const description = document.getElementById('projectDescription').value;
    
    // Show loading
    document.getElementById('student-loading').classList.remove('hidden');
    document.getElementById('student-results').classList.add('hidden');
    
    try {
        const response = await fetch(`${API_BASE_URL}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                student_id: studentId,
                title: title,
                description: description
            })
        });
        
        const result = await response.json();
        
        // Hide loading
        document.getElementById('student-loading').classList.add('hidden');
        
        if (response.ok) {
            displaySubmissionResults(result);
            document.getElementById('submission-id').textContent = result.submission_id;
            loadSubmissions(); // Refresh supervisor view
        } else {
            alert('Error: ' + (result.error || 'Submission failed'));
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('student-loading').classList.add('hidden');
        alert('Error submitting project. Please try again.');
    }
});

function displaySubmissionResults(result) {
    const resultsDiv = document.getElementById('student-results');
    const scoreDiv = document.getElementById('similarity-score');
    const reportDiv = document.getElementById('ai-report');
    const similarDiv = document.getElementById('similar-projects');
    
    // Calculate highest similarity
    const highestSimilarity = result.similar_projects.length > 0 
        ? result.similar_projects[0].similarity_score 
        : 0;
    
    // Display similarity score
    scoreDiv.textContent = `Similarity Score: ${(highestSimilarity * 100).toFixed(1)}%`;
    scoreDiv.className = 'similarity-score ';
    
    if (highestSimilarity > 0.7) {
        scoreDiv.classList.add('score-high');
    } else if (highestSimilarity > 0.4) {
        scoreDiv.classList.add('score-medium');
    } else {
        scoreDiv.classList.add('score-low');
    }
    
    // Display AI report
    reportDiv.innerHTML = `<div class="result-section">${formatReport(result.ai_report)}</div>`;
    
    // Display similar projects
    if (result.similar_projects.length > 0) {
        let similarHTML = '<h4>Similar Projects Found:</h4>';
        result.similar_projects.forEach(project => {
            similarHTML += `
                <div class="similar-project">
                    <strong>${project.metadata.title}</strong> (${project.metadata.year})<br>
                    <small>Similarity: ${(project.similarity_score * 100).toFixed(1)}%</small><br>
                    <small>Previous Decision: ${project.metadata.decision}</small>
                </div>
            `;
        });
        similarDiv.innerHTML = similarHTML;
    } else {
        similarDiv.innerHTML = '<p>No similar projects found.</p>';
    }
    
    resultsDiv.classList.remove('hidden');
}

function formatReport(report) {
    // Convert plain text report to formatted HTML
    return report.replace(/\n/g, '<br>')
                 .replace(/RISK LEVEL: (.*)/, '<strong>RISK LEVEL: $1</strong>')
                 .replace(/HIGHEST SIMILARITY SCORE: (.*)/, '<strong>HIGHEST SIMILARITY SCORE: $1</strong>');
}

// Supervisor Functions
async function loadSubmissions() {
    try {
        const response = await fetch(`${API_BASE_URL}/submissions`);
        const data = await response.json();
        
        submissions = data;
        displaySubmissions();
        updateSupervisorStats();
    } catch (error) {
        console.error('Error loading submissions:', error);
    }
}

function displaySubmissions() {
    const submissionsList = document.getElementById('submissions-list');
    const noSubmissions = document.getElementById('no-submissions');
    
    if (submissions.length === 0) {
        submissionsList.innerHTML = '';
        noSubmissions.classList.remove('hidden');
        return;
    }
    
    noSubmissions.classList.add('hidden');
    
    let html = '<h3>Pending Submissions</h3>';
    
    submissions.forEach((submission, index) => {
        const highestSimilarity = submission.similar_projects.length > 0 
            ? submission.similar_projects[0].similarity_score 
            : 0;
        
        let riskLevel = 'low';
        let riskText = 'Low Risk';
        
        if (highestSimilarity > 0.7) {
            riskLevel = 'high';
            riskText = 'High Risk';
        } else if (highestSimilarity > 0.4) {
            riskLevel = 'medium';
            riskText = 'Medium Risk';
        }
        
        html += `
            <div class="submission-item">
                <h4>${submission.title}</h4>
                <p><strong>Student ID:</strong> ${submission.student_id}</p>
                <p><strong>Submitted:</strong> ${new Date(submission.timestamp).toLocaleString()}</p>
                <div class="risk-badge risk-${riskLevel}">${riskText} (${(highestSimilarity * 100).toFixed(1)}%)</div>
                <div class="similar-project">
                    <strong>AI Report:</strong><br>
                    ${formatReport(submission.ai_report)}
                </div>
                <button class="btn" onclick="openRatingModal(${submission.submission_id})">Rate Submission</button>
            </div>
        `;
    });
    
    submissionsList.innerHTML = html;
}

function updateSupervisorStats() {
    document.getElementById('pending-count').textContent = submissions.length;
    document.getElementById('total-count').textContent = submissions.length; // In real app, get from API
    
    // Calculate average rating (mock data for now)
    const avgRating = 3.5; // This would come from API
    document.getElementById('avg-rating').textContent = avgRating.toFixed(1);
}

// Rating Modal Functions
function openRatingModal(submissionId) {
    currentSubmissionId = submissionId;
    const submission = submissions.find(s => s.submission_id === submissionId);
    
    if (submission) {
        document.getElementById('modal-submission-details').innerHTML = `
            <p><strong>Title:</strong> ${submission.title}</p>
            <p><strong>Student ID:</strong> ${submission.student_id}</p>
            <div class="similar-project">${formatReport(submission.ai_report)}</div>
        `;
    }
    
    document.getElementById('rating-modal').classList.remove('hidden');
    resetStars();
}

function closeRatingModal() {
    document.getElementById('rating-modal').classList.add('hidden');
    currentSubmissionId = null;
}

function resetStars() {
    document.querySelectorAll('.star').forEach(star => {
        star.classList.remove('active');
    });
    document.getElementById('selected-rating').value = '0';
}

// Star rating interaction
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('star')) {
        const rating = parseInt(e.target.getAttribute('data-rating'));
        setRating(rating);
    }
});

function setRating(rating) {
    resetStars();
    document.getElementById('selected-rating').value = rating;
    
    document.querySelectorAll('.star').forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        }
    });
}

async function submitRating() {
    const rating = parseInt(document.getElementById('selected-rating').value);
    const comments = document.getElementById('supervisor-comments').value;
    
    if (rating === 0) {
        alert('Please select a rating');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/supervisor/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                submission_id: currentSubmissionId,
                rating: rating,
                comments: comments
            })
        });
        
        if (response.ok) {
            alert('Rating submitted successfully!');
            closeRatingModal();
            loadSubmissions(); // Refresh the list
        } else {
            const error = await response.json();
            alert('Error: ' + (error.error || 'Rating submission failed'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error submitting rating. Please try again.');
    }
}

// Admin Functions
async function loadAdminStats() {
    // Mock data - in real app, fetch from API
    document.getElementById('total-projects').textContent = '20';
    document.getElementById('avg-similarity').textContent = '23.5%';
    document.getElementById('rejection-rate').textContent = '15%';
    
    // Load system log
    loadSystemLog();
}

function loadSystemLog() {
    const logEntries = document.getElementById('log-entries');
    const logs = [
        'System started successfully',
        'New project submitted by student_001',
        'Similarity analysis completed for submission #15',
        'Supervisor rating submitted for project #12',
        'Database backup completed'
    ];
    
    let html = '';
    logs.forEach(log => {
        html += `<p>${new Date().toLocaleString()} - ${log}</p>`;
    });
    
    logEntries.innerHTML = html;
}

function exportData() {
    alert('Export functionality would be implemented here');
    // In real app: trigger database export
}

function clearDatabase() {
    if (confirm('Are you sure you want to clear the database? This action cannot be undone.')) {
        alert('Database clearance functionality would be implemented here');
        // In real app: call API to clear database
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadSubmissions();
    loadAdminStats();
    
    // Add some sample submissions for demo
    if (submissions.length === 0) {
        submissions = [
            {
                submission_id: 1,
                student_id: 'STU001',
                title: 'Machine Learning for Healthcare',
                timestamp: new Date().toISOString(),
                similar_projects: [{ similarity_score: 0.75, metadata: { title: 'AI in Medicine', year: 2022, decision: 'accept' } }],
                ai_report: 'RISK LEVEL: HIGH\nHIGHEST SIMILARITY SCORE: 0.75\n\nHigh similarity detected with previous healthcare AI projects.'
            }
        ];
        displaySubmissions();
    }
});