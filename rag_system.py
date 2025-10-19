"""
RAG (Retrieval-Augmented Generation) System for Song Chatbot
Handles vector embeddings, document retrieval, and response generation
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Optional
import json
import os
import re

class RAGSystem:
    def __init__(self, dataset_path: str = "songs_dataset.csv"):
        """
        Initialize the RAG system with song dataset
        """
        self.dataset_path = dataset_path
        self.songs_df = None
        self.embeddings = None
        self.model = None
        self.load_dataset()
        self.setup_embeddings()
    
    def load_dataset(self):
        """Load and preprocess the songs dataset"""
        self.songs_df = pd.read_csv(self.dataset_path)
        # Create text representations for each song
        self.songs_df['text_representation'] = self.songs_df.apply(
            lambda row: f"Song: {row['Title']} by {row['Author']} - Genre: {row['Genre']} - Mood: {row['Mood']} - Year: {row['Year']}", 
            axis=1
        )
        print(f"Loaded {len(self.songs_df)} songs from dataset")
    
    def setup_embeddings(self):
        """Initialize sentence transformer model and create embeddings"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Create embeddings for all songs
        song_texts = self.songs_df['text_representation'].tolist()
        self.embeddings = self.model.encode(song_texts)
        print("Created embeddings for all songs")
    
    def retrieve_relevant_songs(self, query: str, top_k: int = 3, similarity_threshold: float = 0.1) -> List[Dict]:
        """
        Retrieve most relevant songs based on query similarity
        Only return songs above the similarity threshold
        """
        # Encode the query
        query_embedding = self.model.encode([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top-k most similar songs
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        relevant_songs = []
        for idx in top_indices:
            similarity_score = float(similarities[idx])
            # Only include songs above the similarity threshold
            if similarity_score >= similarity_threshold:
                song_data = self.songs_df.iloc[idx].to_dict()
                song_data['similarity_score'] = similarity_score
                relevant_songs.append(song_data)
        
        # If no songs found with semantic search, try exact word matching
        if not relevant_songs:
            relevant_songs = self._fallback_exact_search(query, top_k)
        
        return relevant_songs
    
    def _fallback_exact_search(self, query: str, top_k: int) -> List[Dict]:
        """
        Fallback to exact word matching if semantic search fails
        """
        query_lower = query.lower().strip()
        matches = []
        
        # Search in all text fields
        for idx, row in self.songs_df.iterrows():
            # Create combined text for matching
            combined_text = f"{row['Title']} {row['Author']} {row['Genre']} {row['Mood']} {row['Year']}".lower()
            
            # Check if query appears in any field
            if query_lower in combined_text:
                song_data = row.to_dict()
                song_data['similarity_score'] = 0.5  # Give it a reasonable score
                matches.append(song_data)
                
                if len(matches) >= top_k:
                    break
        
        return matches
    
    def search_song_by_title(self, title: str) -> Optional[Dict]:
        """Search for a specific song by title (exact or partial match)"""
        title_lower = title.lower()
        matches = self.songs_df[
            self.songs_df['Title'].str.lower().str.contains(title_lower, na=False)
        ]
        
        if len(matches) > 0:
            return matches.iloc[0].to_dict()
        return None
    
    def search_songs_by_author(self, author: str) -> List[Dict]:
        """Search for songs by author"""
        author_lower = author.lower()
        matches = self.songs_df[
            self.songs_df['Author'].str.lower().str.contains(author_lower, na=False)
        ]
        return matches.to_dict('records')
    
    def search_songs_by_genre(self, genre: str) -> List[Dict]:
        """Search for songs by genre"""
        genre_lower = genre.lower()
        matches = self.songs_df[
            self.songs_df['Genre'].str.lower().str.contains(genre_lower, na=False)
        ]
        return matches.to_dict('records')
    
    def search_songs_by_mood(self, mood: str) -> List[Dict]:
        """Search for songs by mood"""
        mood_lower = mood.lower()
        matches = self.songs_df[
            self.songs_df['Mood'].str.lower().str.contains(mood_lower, na=False)
        ]
        return matches.to_dict('records')
    
    def get_all_songs(self) -> List[Dict]:
        """Get all songs in the dataset"""
        return self.songs_df.to_dict('records')
    
    def get_song_by_exact_title(self, title: str) -> Optional[Dict]:
        """Get song by exact title match"""
        matches = self.songs_df[self.songs_df['Title'].str.lower() == title.lower()]
        if len(matches) > 0:
            return matches.iloc[0].to_dict()
        return None
    
    def is_valid_query(self, query: str) -> bool:
        """
        Check if query is valid for search
        Returns False for special characters only, very short queries, or meaningless text
        """
        if not query or len(query.strip()) < 1:
            return False
        
        # Remove whitespace and check if only special characters
        cleaned_query = re.sub(r'[^\w\s]', '', query.strip())
        if len(cleaned_query) < 1:
            return False
        
        # Allow single meaningful words (like "Epic", "Rock", "Happy")
        words = [word for word in cleaned_query.split() if len(word) >= 1]
        if len(words) == 0:
            return False
        
        return True
