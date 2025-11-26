class DecisionEngine:
    def __init__(self, similarity_threshold=0.7, rating_weight=0.3):
        self.similarity_threshold = similarity_threshold
        self.rating_weight = rating_weight
        
    def calculate_ai_score(self, similar_projects):
        if not similar_projects:
            return 0.0
        
        top_similarity = similar_projects[0]['similarity_score']
        return min(top_similarity / self.similarity_threshold, 1.0)
    
    def calculate_final_score(self, ai_score, supervisor_rating):
        rating_score = (5 - supervisor_rating) / 5
        final_score = (ai_score * (1 - self.rating_weight)) + (rating_score * self.rating_weight)
        return min(final_score, 1.0)
    
    def make_decision(self, final_score, decision_threshold=0.5):
        return "reject" if final_score > decision_threshold else "accept"