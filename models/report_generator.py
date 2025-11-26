class ReportGenerator:
    def generate_report(self, new_project_text, similar_projects):
        if not similar_projects:
            return "No similar projects found. This appears to be an original work."
        
        top_match = similar_projects[0]
        
        if top_match['similarity_score'] > 0.8:
            risk_level = "HIGH"
            suggestion = "Strong evidence of potential plagiarism. Recommend careful review."
        elif top_match['similarity_score'] > 0.6:
            risk_level = "MEDIUM" 
            suggestion = "Moderate similarity detected. Recommend supervisor review."
        elif top_match['similarity_score'] > 0.4:
            risk_level = "LOW"
            suggestion = "Low similarity detected. Common concepts may be shared."
        else:
            risk_level = "VERY LOW"
            suggestion = "Minimal similarity. Likely original work."
        
        report = f"""
PLAGIARISM DETECTION REPORT
============================

RISK LEVEL: {risk_level}
HIGHEST SIMILARITY SCORE: {top_match['similarity_score']:.3f}

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
"""
        
        return report