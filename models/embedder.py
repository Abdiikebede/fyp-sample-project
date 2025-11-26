from sentence_transformers import SentenceTransformer
import numpy as np
import os

class PlagiarismEmbedder:
    def __init__(self, model_name='all-MiniLM-L6-v2', use_local=True):
        """
        Initialize the embedder
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = 384
            self.model_name = model_name
            print(f"✅ Embedder initialized with {model_name}")
        except Exception as e:
            print(f"❌ Error initializing embedder: {e}")
            raise
        
    def prepare_text(self, title, description):
        return f"TITLE: {title}. DESCRIPTION: {description}"
    
    def encode_text(self, text):
        if isinstance(text, str):
            return self.model.encode([text])[0]
        else:
            return self.model.encode(text)
    
    def encode_batch(self, texts):
        return self.model.encode(texts)