import faiss
import numpy as np
import pandas as pd
import json
import os

class VectorDatabase:
    def __init__(self, dimension):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        self.metadata = []
        
    def add_embeddings(self, embeddings, metadata_list):
        """Add embeddings and metadata to vector database"""
        if len(embeddings) != len(metadata_list):
            raise ValueError("Number of embeddings must match number of metadata entries")
        
        # Convert to numpy array and normalize
        embeddings = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        self.metadata.extend(metadata_list)
        
    def search(self, query_embedding, k=5):
        """Search for similar vectors"""
        # Normalize query embedding
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        # Search
        similarities, indices = self.index.search(query_embedding, k)
        
        # Prepare results
        results = []
        for i, (score, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx < len(self.metadata) and idx >= 0:  # Valid index
                results.append({
                    'rank': i + 1,
                    'similarity_score': float(score),
                    'metadata': self.metadata[idx]
                })
        return results

    def get_database_stats(self):
        """Get statistics about the vector database"""
        return {
            'total_projects': len(self.metadata),
            'embedding_dimension': self.dimension,
            'index_size': self.index.ntotal
        }
    
    def save_system(self, csv_path, metadata_path, index_path):
        """Save the vector database system"""
        # Save embeddings and metadata to CSV
        save_data = []
        for i, meta in enumerate(self.metadata):
            row = meta.copy()
            save_data.append(row)
        
        df = pd.DataFrame(save_data)
        df.to_csv(csv_path, index=False)
        
        # Save metadata
        system_metadata = {
            'total_projects': len(self.metadata),
            'embedding_dimension': self.dimension,
            'index_size': self.index.ntotal
        }
        with open(metadata_path, 'w') as f:
            json.dump(system_metadata, f, indent=2)
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
    
    def load_with_index(self, embeddings, metadata_list, index_path):
        """Load with pre-built FAISS index"""
        # Add embeddings and metadata
        self.add_embeddings(embeddings, metadata_list)
        
        # Load the pre-built FAISS index
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            print(f"✅ Loaded pre-built FAISS index with {self.index.ntotal} vectors")
        else:
            print(f"⚠️  FAISS index not found at {index_path}, using current index")
        
        return self
    
    @classmethod
    def load_system(cls, csv_path, metadata_path, index_path, embedder):
        """Load a saved vector database system"""
        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Create vector database
        vector_db = cls(metadata['embedding_dimension'])
        
        # Load data
        df = pd.read_csv(csv_path)
        
        # Check if embeddings are already in the CSV
        if 'embedding' in df.columns:
            print("🔍 Found pre-computed embeddings in CSV, loading directly...")
            # Convert embeddings from string back to arrays
            embeddings = []
            metadata_list = []
            
            for _, row in df.iterrows():
                # Convert embedding string to numpy array
                if isinstance(row['embedding'], str):
                    embedding_array = np.fromstring(row['embedding'].strip('[]'), sep=' ')
                else:
                    embedding_array = row['embedding']
                
                embeddings.append(embedding_array)
                
                metadata_list.append({
                    'id': int(row['id']),
                    'title': row['title'],
                    'year': int(row['year']),
                    'decision': row['decision'],
                    'original_text': row.get('combined_text', row.get('original_text', ''))
                })
            
            # Use load_with_index to load pre-computed embeddings and FAISS index
            vector_db.load_with_index(embeddings, metadata_list, index_path)
            
        else:
            print("🔄 No pre-computed embeddings found, regenerating from text...")
            # Prepare metadata and regenerate embeddings
            metadata_list = []
            texts_to_embed = []
            
            for _, row in df.iterrows():
                meta = {
                    'id': int(row['id']),
                    'title': row['title'],
                    'year': int(row['year']),
                    'decision': row['decision'],
                    'original_text': row.get('combined_text', '')
                }
                metadata_list.append(meta)
                texts_to_embed.append(meta['original_text'])
            
            # Regenerate embeddings
            embeddings = embedder.encode_batch(texts_to_embed)
            
            # Add to vector database
            vector_db.add_embeddings(embeddings, metadata_list)
            
            # Save the index for future use
            faiss.write_index(vector_db.index, index_path)
        
        return vector_db
    
    @classmethod
    def load_system_fast(cls, csv_path, metadata_path, index_path):
        """Fast loading using pre-computed embeddings and FAISS index"""
        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Create vector database
        vector_db = cls(metadata['embedding_dimension'])
        
        # Load data with embeddings
        df = pd.read_csv(csv_path)
        
        # Convert embeddings from string back to arrays
        embeddings = []
        metadata_list = []
        
        for _, row in df.iterrows():
            # Convert embedding string to numpy array
            if isinstance(row['embedding'], str):
                embedding_array = np.fromstring(row['embedding'].strip('[]'), sep=' ')
            else:
                embedding_array = row['embedding']
            
            embeddings.append(embedding_array)
            
            metadata_list.append({
                'id': int(row['id']),
                'title': row['title'],
                'year': int(row['year']),
                'decision': row['decision'],
                'original_text': row.get('combined_text', row.get('original_text', ''))
            })
        
        # Use load_with_index to load everything
        vector_db.load_with_index(embeddings, metadata_list, index_path)
        
        print(f"✅ Fast-loaded system with {len(vector_db.metadata)} projects")
        return vector_db
    
    @classmethod
    def from_dataframe(cls, df, embedder):
        """Create vector database from pandas DataFrame"""
        # Preprocess dataframe
        if 'combined_text' not in df.columns:
            texts = [embedder.prepare_text(row['title'], row['description']) 
                    for _, row in df.iterrows()]
            df['combined_text'] = texts
        
        # Generate embeddings
        embeddings = embedder.encode_batch(df['combined_text'].tolist())
        
        # Prepare metadata
        metadata_list = []
        for _, row in df.iterrows():
            metadata_list.append({
                'id': int(row['id']),
                'title': row['title'],
                'year': int(row['year']),
                'decision': row['decision'],
                'original_text': row['combined_text']
            })
        
        # Create vector database
        vector_db = cls(embedder.embedding_dim)
        vector_db.add_embeddings(embeddings, metadata_list)
        
        return vector_db