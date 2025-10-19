"""
Recommendation System for Song Chatbot
Provides mood-based and user preference-based recommendations
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import Counter
import random

class RecommendationSystem:
    def __init__(self, rag_system, favorites_api):
        """
        Initialize recommendation system with RAG system and favorites API
        """
        self.rag_system = rag_system
        self.favorites_api = favorites_api
        self.songs_df = rag_system.songs_df
    
    def get_mood_based_recommendations(self, mood: str, limit: int = 5, 
                                     exclude_favorites: List[Dict] = None) -> List[Dict]:
        """
        Get song recommendations based on mood
        """
        mood_lower = mood.lower()
        
        # Find songs with matching mood
        mood_matches = self.songs_df[
            self.songs_df['Mood'].str.lower().str.contains(mood_lower, na=False)
        ]
        
        if len(mood_matches) == 0:
            # If no exact mood match, find similar moods
            similar_moods = self._find_similar_moods(mood_lower)
            if similar_moods:
                mood_matches = self.songs_df[
                    self.songs_df['Mood'].str.lower().isin(similar_moods)
                ]
        
        if len(mood_matches) == 0:
            return []
        
        # Convert to list of dictionaries
        recommendations = mood_matches.to_dict('records')
        
        # Exclude user's favorites if provided
        if exclude_favorites:
            recommendations = self._exclude_favorites(recommendations, exclude_favorites)
        
        # Shuffle and limit results
        random.shuffle(recommendations)
        return recommendations[:limit]
    
    def get_user_preference_recommendations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """
        Get recommendations based on user's favorite songs
        """
        user_favorites = self.favorites_api.get_favorites(user_id)
        
        if not user_favorites:
            # If no favorites, return random popular songs
            return self._get_popular_songs(limit)
        
        # Analyze user preferences
        user_genres = [fav.genre for fav in user_favorites]
        user_moods = [fav.mood for fav in user_favorites]
        user_authors = [fav.author for fav in user_favorites]
        
        # Find most common preferences
        genre_preferences = Counter(user_genres)
        mood_preferences = Counter(user_moods)
        author_preferences = Counter(user_authors)
        
        # Get recommendations based on preferences
        recommendations = []
        
        # 1. Same genre, different mood
        top_genre = genre_preferences.most_common(1)[0][0]
        genre_recs = self.songs_df[
            (self.songs_df['Genre'] == top_genre) & 
            (~self.songs_df['Title'].isin([fav.title for fav in user_favorites]))
        ]
        recommendations.extend(genre_recs.to_dict('records'))
        
        # 2. Same mood, different genre
        top_mood = mood_preferences.most_common(1)[0][0]
        mood_recs = self.songs_df[
            (self.songs_df['Mood'] == top_mood) & 
            (~self.songs_df['Title'].isin([fav.title for fav in user_favorites]))
        ]
        recommendations.extend(mood_recs.to_dict('records'))
        
        # 3. Same author, different songs
        top_author = author_preferences.most_common(1)[0][0]
        author_recs = self.songs_df[
            (self.songs_df['Author'] == top_author) & 
            (~self.songs_df['Title'].isin([fav.title for fav in user_favorites]))
        ]
        recommendations.extend(author_recs.to_dict('records'))
        
        # Remove duplicates and shuffle
        unique_recommendations = self._remove_duplicates(recommendations)
        random.shuffle(unique_recommendations)
        
        return unique_recommendations[:limit]
    
    def get_hybrid_recommendations(self, user_id: str, mood: str = None, 
                                 limit: int = 5) -> List[Dict]:
        """
        Get hybrid recommendations combining user preferences and mood
        """
        user_favorites = self.favorites_api.get_favorites(user_id)
        
        if not user_favorites and not mood:
            return self._get_popular_songs(limit)
        
        recommendations = []
        
        # Get mood-based recommendations
        if mood:
            mood_recs = self.get_mood_based_recommendations(
                mood, limit=limit//2, exclude_favorites=user_favorites
            )
            recommendations.extend(mood_recs)
        
        # Get user preference recommendations
        if user_favorites:
            pref_recs = self.get_user_preference_recommendations(user_id, limit=limit//2)
            recommendations.extend(pref_recs)
        
        # If we still need more recommendations, add popular songs
        if len(recommendations) < limit:
            popular_recs = self._get_popular_songs(limit - len(recommendations))
            recommendations.extend(popular_recs)
        
        # Remove duplicates and limit
        unique_recommendations = self._remove_duplicates(recommendations)
        return unique_recommendations[:limit]
    
    def get_similar_songs(self, song_title: str, limit: int = 5) -> List[Dict]:
        """
        Get songs similar to a specific song
        """
        # Find the reference song
        reference_song = self.rag_system.get_song_by_exact_title(song_title)
        if not reference_song:
            return []
        
        # Find songs with same genre or mood
        similar_songs = self.songs_df[
            ((self.songs_df['Genre'] == reference_song['Genre']) | 
             (self.songs_df['Mood'] == reference_song['Mood'])) &
            (self.songs_df['Title'] != song_title)
        ]
        
        recommendations = similar_songs.to_dict('records')
        random.shuffle(recommendations)
        
        return recommendations[:limit]
    
    def get_trending_recommendations(self, limit: int = 5) -> List[Dict]:
        """
        Get trending/popular song recommendations
        """
        return self._get_popular_songs(limit)
    
    def get_diverse_recommendations(self, limit: int = 5) -> List[Dict]:
        """
        Get diverse recommendations across different genres and moods
        """
        # Get one song from each genre
        genre_groups = self.songs_df.groupby('Genre')
        diverse_songs = []
        
        for genre, group in genre_groups:
            if len(diverse_songs) >= limit:
                break
            song = group.sample(1).iloc[0].to_dict()
            diverse_songs.append(song)
        
        # If we need more, add songs from different moods
        if len(diverse_songs) < limit:
            mood_groups = self.songs_df.groupby('Mood')
            for mood, group in mood_groups:
                if len(diverse_songs) >= limit:
                    break
                # Check if we already have a song from this mood
                if not any(song['Mood'] == mood for song in diverse_songs):
                    song = group.sample(1).iloc[0].to_dict()
                    diverse_songs.append(song)
        
        return diverse_songs[:limit]
    
    def _find_similar_moods(self, target_mood: str) -> List[str]:
        """
        Find moods similar to the target mood
        """
        mood_similarity = {
            'happy': ['energetic', 'upbeat', 'joyful'],
            'sad': ['melancholic', 'emotional', 'depressed'],
            'energetic': ['happy', 'upbeat', 'exciting'],
            'chill': ['peaceful', 'calm', 'relaxed'],
            'romantic': ['emotional', 'love', 'intimate'],
            'angry': ['aggressive', 'intense', 'fierce'],
            'peaceful': ['chill', 'calm', 'serene']
        }
        
        return mood_similarity.get(target_mood, [])
    
    def _exclude_favorites(self, recommendations: List[Dict], 
                          favorites: List[Dict]) -> List[Dict]:
        """
        Exclude user's favorite songs from recommendations
        """
        favorite_titles = [fav.title for fav in favorites]
        return [rec for rec in recommendations if rec['Title'] not in favorite_titles]
    
    def _remove_duplicates(self, recommendations: List[Dict]) -> List[Dict]:
        """
        Remove duplicate recommendations based on title and author
        """
        seen = set()
        unique_recommendations = []
        
        for rec in recommendations:
            key = (rec['Title'], rec['Author'])
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def _get_popular_songs(self, limit: int) -> List[Dict]:
        """
        Get popular songs (random selection for demo purposes)
        """
        # In a real system, this would be based on play counts, ratings, etc.
        popular_songs = self.songs_df.sample(min(limit, len(self.songs_df)))
        return popular_songs.to_dict('records')
    
    def analyze_user_preferences(self, user_id: str) -> Dict[str, any]:
        """
        Analyze user's music preferences
        """
        user_favorites = self.favorites_api.get_favorites(user_id)
        
        if not user_favorites:
            return {"message": "No favorites found for analysis"}
        
        # Analyze preferences
        genres = [fav.genre for fav in user_favorites]
        moods = [fav.mood for fav in user_favorites]
        authors = [fav.author for fav in user_favorites]
        years = [fav.year for fav in user_favorites]
        
        analysis = {
            "total_favorites": len(user_favorites),
            "favorite_genres": Counter(genres).most_common(3),
            "favorite_moods": Counter(moods).most_common(3),
            "favorite_authors": Counter(authors).most_common(3),
            "year_range": {
                "earliest": min(years),
                "latest": max(years),
                "average": round(sum(years) / len(years), 1)
            },
            "diversity_score": self._calculate_diversity_score(user_favorites)
        }
        
        return analysis
    
    def _calculate_diversity_score(self, favorites: List[Dict]) -> float:
        """
        Calculate diversity score based on genres and moods
        """
        if not favorites:
            return 0.0
        
        genres = set(fav.genre for fav in favorites)
        moods = set(fav.mood for fav in favorites)
        
        # Simple diversity score: unique genres + unique moods / total possible
        total_unique = len(genres) + len(moods)
        max_possible = len(self.songs_df['Genre'].unique()) + len(self.songs_df['Mood'].unique())
        
        return round(total_unique / max_possible, 3)
