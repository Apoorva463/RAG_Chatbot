"""
Main Chatbot with RAG, Evaluation, and Recommendations
Handles user queries with hallucination prevention and citation system
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from rag_system import RAGSystem
from evaluation_system import EvaluationSystem, EvaluationResult
from observability import ObservabilitySystem
from recommendation_system import RecommendationSystem
from favorites_api import FavoritesAPI, Song

class SongChatbot:
    def __init__(self, dataset_path: str = "songs_dataset.csv"):
        """
        Initialize the complete song chatbot system
        """
        # Initialize core components
        self.rag_system = RAGSystem(dataset_path)
        self.evaluation_system = EvaluationSystem()
        self.observability = ObservabilitySystem()
        self.favorites_api = FavoritesAPI()
        self.recommendation_system = RecommendationSystem(self.rag_system, self.favorites_api)
        
        # Start a new session
        self.session_id = self.observability.start_session()
        
        print("Song Chatbot initialized successfully!")
    
    def process_query(self, query: str, user_id: str = None) -> Dict[str, any]:
        """
        Process a user query and return response with evaluation
        """
        # Log the query
        trace_id = self.observability.log_query(query, user_id)
        
        # Parse the query to understand intent
        intent = self._parse_intent(query)
        
        # Generate response based on intent
        response_data = self._generate_response(query, intent, user_id, trace_id)
        
        # Evaluate the response
        evaluation = self._evaluate_response(query, response_data, trace_id)
        
        # Log everything to observability system
        self._log_response_data(trace_id, response_data, evaluation)
        
        return {
            "query": query,
            "response": response_data["response"],
            "intent": intent,
            "evaluation": evaluation.__dict__,
            "trace_id": trace_id,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def _parse_intent(self, query: str) -> str:
        """
        Parse user query to understand intent
        """
        query_lower = query.lower()
        
        # Intent patterns
        intent_patterns = {
            "search_song": [
                r"who wrote", r"who sang", r"who performed", r"author of",
                r"what is the genre of", r"what genre is", r"genre of",
                r"what mood is", r"mood of", r"what year was", r"year of"
            ],
            "add_favorite": [
                r"add to favorites", r"save to favorites", r"favorite this",
                r"add.*favorite", r"save.*favorite"
            ],
            "get_favorites": [
                r"my favorites", r"show favorites", r"list favorites",
                r"what are my favorites", r"favorites list"
            ],
            "recommendation": [
                r"recommend", r"suggest", r"recommendation", r"what should i listen",
                r"mood.*music", r"songs for.*mood", r"happy music", r"sad music"
            ],
            "general_question": [
                r"what", r"who", r"when", r"where", r"how", r"tell me about"
            ]
        }
        
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        return "general_question"
    
    def _generate_response(self, query: str, intent: str, user_id: str, trace_id: str) -> Dict[str, any]:
        """
        Generate response based on parsed intent
        """
        if intent == "search_song":
            return self._handle_song_search(query, trace_id)
        elif intent == "add_favorite":
            return self._handle_add_favorite(query, user_id, trace_id)
        elif intent == "get_favorites":
            return self._handle_get_favorites(user_id, trace_id)
        elif intent == "recommendation":
            return self._handle_recommendation(query, user_id, trace_id)
        else:
            return self._handle_general_query(query, trace_id)
    
    def _handle_song_search(self, query: str, trace_id: str) -> Dict[str, any]:
        """
        Handle song search queries
        """
        # Extract song title from query
        song_title = self._extract_song_title(query)
        
        if not song_title:
            return {
                "response": "I need to know which song you're asking about. Please specify the song title.",
                "retrieved_docs": [],
                "citation": None
            }
        
        # Search for the song
        song = self.rag_system.get_song_by_exact_title(song_title)
        
        if not song:
            # Try partial match
            song = self.rag_system.search_song_by_title(song_title)
        
        if not song:
            return {
                "response": f"Sorry, I don't have information about '{song_title}' in my dataset.",
                "retrieved_docs": [],
                "citation": None
            }
        
        # Generate response based on query type
        response = self._generate_song_info_response(query, song)
        citation = f"Source: {song['Title']} by {song['Author']}"
        
        # Log retrieval
        self.observability.log_retrieval(trace_id, [song], query)
        
        return {
            "response": response,
            "retrieved_docs": [song],
            "citation": citation
        }
    
    def _handle_add_favorite(self, query: str, user_id: str, trace_id: str) -> Dict[str, any]:
        """
        Handle adding songs to favorites
        """
        if not user_id:
            return {
                "response": "I need your user ID to save favorites. Please provide a user ID.",
                "retrieved_docs": [],
                "citation": None
            }
        
        # Extract song title from query
        song_title = self._extract_song_title(query)
        
        if not song_title:
            return {
                "response": "I need to know which song to add to your favorites. Please specify the song title.",
                "retrieved_docs": [],
                "citation": None
            }
        
        # Find the song
        song = self.rag_system.get_song_by_exact_title(song_title)
        
        if not song:
            return {
                "response": f"Sorry, I don't have '{song_title}' in my dataset, so I can't add it to your favorites.",
                "retrieved_docs": [],
                "citation": None
            }
        
        # Add to favorites
        song_obj = Song(
            title=song['Title'],
            author=song['Author'],
            genre=song['Genre'],
            mood=song['Mood'],
            year=song['Year']
        )
        
        success = self.favorites_api.add_favorite(user_id, song_obj)
        
        if success:
            response = f"Added '{song['Title']}' by {song['Author']} to your favorites!"
            # Log favorites action
            self.observability.log_favorites_action(trace_id, user_id, "add", song, None)
        else:
            response = f"'{song['Title']}' is already in your favorites."
        
        return {
            "response": response,
            "retrieved_docs": [song],
            "citation": f"Source: {song['Title']} by {song['Author']}"
        }
    
    def _handle_get_favorites(self, user_id: str, trace_id: str) -> Dict[str, any]:
        """
        Handle getting user's favorites
        """
        if not user_id:
            return {
                "response": "I need your user ID to show your favorites. Please provide a user ID.",
                "retrieved_docs": [],
                "citation": None
            }
        
        favorites = self.favorites_api.get_favorites(user_id)
        
        if not favorites:
            return {
                "response": "You don't have any favorite songs yet. Try asking me to add some songs to your favorites!",
                "retrieved_docs": [],
                "citation": None
            }
        
        # Format favorites list
        favorites_list = []
        for fav in favorites:
            favorites_list.append(f"• {fav.title} by {fav.author} ({fav.genre}, {fav.mood})")
        
        response = f"Here are your {len(favorites)} favorite songs:\n" + "\n".join(favorites_list)
        
        # Log favorites action
        self.observability.log_favorites_action(trace_id, user_id, "get", None, [fav.__dict__ for fav in favorites])
        
        return {
            "response": response,
            "retrieved_docs": [fav.__dict__ for fav in favorites],
            "citation": f"Source: Your favorites list ({len(favorites)} songs)"
        }
    
    def _handle_recommendation(self, query: str, user_id: str, trace_id: str) -> Dict[str, any]:
        """
        Handle recommendation requests
        """
        # Extract mood from query
        mood = self._extract_mood_from_query(query)
        
        if mood:
            # Mood-based recommendations
            recommendations = self.recommendation_system.get_mood_based_recommendations(mood, limit=5)
            response = f"Here are some {mood} songs you might like:\n"
        else:
            # User preference-based recommendations
            recommendations = self.recommendation_system.get_user_preference_recommendations(user_id, limit=5)
            response = "Here are some songs you might like based on your preferences:\n"
        
        if not recommendations:
            response = "I don't have any recommendations for you right now. Try adding some songs to your favorites first!"
            return {
                "response": response,
                "retrieved_docs": [],
                "citation": None
            }
        
        # Format recommendations
        rec_list = []
        for i, rec in enumerate(recommendations, 1):
            rec_list.append(f"{i}. {rec['Title']} by {rec['Author']} ({rec['Genre']}, {rec['Mood']})")
        
        response += "\n".join(rec_list)
        
        # Log recommendation
        self.observability.log_recommendation(trace_id, user_id, "mood" if mood else "preference", recommendations)
        
        return {
            "response": response,
            "retrieved_docs": recommendations,
            "citation": f"Source: Recommendation system ({len(recommendations)} songs)"
        }
    
    def _handle_general_query(self, query: str, trace_id: str) -> Dict[str, any]:
        """
        Handle general queries using RAG
        """
        # First check if query is valid
        if not self.rag_system.is_valid_query(query):
            return {
                "response": f"Sorry, I don't have information about '{query}' in my dataset. Please try asking about a specific song, artist, genre, or mood.",
                "retrieved_docs": [],
                "citation": None
            }
        
        # Use RAG to find relevant songs with similarity threshold
        relevant_songs = self.rag_system.retrieve_relevant_songs(query, top_k=3, similarity_threshold=0.3)
        
        if not relevant_songs:
            return {
                "response": f"Sorry, I don't have information about '{query}' in my dataset. Please try asking about a specific song, artist, genre, or mood.",
                "retrieved_docs": [],
                "citation": None
            }
        
        # Generate response based on relevant songs
        response = self._generate_general_response(query, relevant_songs)
        
        # Log retrieval
        self.observability.log_retrieval(trace_id, relevant_songs, query)
        
        return {
            "response": response,
            "retrieved_docs": relevant_songs,
            "citation": f"Source: {len(relevant_songs)} relevant songs from dataset"
        }
    
    def _extract_song_title(self, query: str) -> Optional[str]:
        """
        Extract song title from query
        """
        query_lower = query.lower()
        
        # Common patterns for song titles
        patterns = [
            r'"([^"]+)"',  # Quoted titles
            r"'([^']+)'",  # Single quoted titles
            r"about (.+?)(?:\?|$)",  # "about [song]"
            r"who wrote (.+?)(?:\?|$)",  # "who wrote [song]"
            r"what genre is (.+?)(?:\?|$)",  # "what genre is [song]"
            r"what mood is (.+?)(?:\?|$)",  # "what mood is [song]"
            r"tell me about (.+?)(?:\?|$)",  # "tell me about [song]"
            r"add (.+?) to my favorites",  # "add [song] to my favorites"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                title = match.group(1).strip()
                # Clean up common words
                title = re.sub(r'\b(the|a|an)\b', '', title, flags=re.IGNORECASE).strip()
                return title
        
        return None
    
    def _extract_mood_from_query(self, query: str) -> Optional[str]:
        """
        Extract mood from recommendation query
        """
        mood_keywords = {
            'happy': ['happy', 'joyful', 'cheerful', 'upbeat'],
            'sad': ['sad', 'melancholic', 'depressed', 'gloomy'],
            'energetic': ['energetic', 'exciting', 'pumping', 'high-energy'],
            'chill': ['chill', 'relaxed', 'calm', 'peaceful'],
            'romantic': ['romantic', 'love', 'intimate', 'passionate'],
            'angry': ['angry', 'aggressive', 'intense', 'fierce']
        }
        
        query_lower = query.lower()
        for mood, keywords in mood_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return mood
        
        return None
    
    def _generate_song_info_response(self, query: str, song: Dict) -> str:
        """
        Generate response for song information queries
        """
        query_lower = query.lower()
        
        if "who wrote" in query_lower or "who sang" in query_lower or "author" in query_lower:
            return f"'{song['Title']}' was written/performed by {song['Author']}."
        elif "genre" in query_lower:
            return f"'{song['Title']}' is a {song['Genre']} song."
        elif "mood" in query_lower:
            return f"'{song['Title']}' has a {song['Mood']} mood."
        elif "year" in query_lower:
            return f"'{song['Title']}' was released in {song['Year']}."
        else:
            return f"'{song['Title']}' by {song['Author']} is a {song['Genre']} song with a {song['Mood']} mood, released in {song['Year']}."
    
    def _generate_general_response(self, query: str, relevant_songs: List[Dict]) -> str:
        """
        Generate response for general queries
        """
        if len(relevant_songs) == 1:
            song = relevant_songs[0]
            return f"Based on your query, I found '{song['Title']}' by {song['Author']} - a {song['Genre']} song with a {song['Mood']} mood from {song['Year']}."
        else:
            response = f"I found {len(relevant_songs)} songs that might be relevant:\n"
            for i, song in enumerate(relevant_songs, 1):
                response += f"{i}. '{song['Title']}' by {song['Author']} ({song['Genre']}, {song['Mood']})\n"
            return response.strip()
    
    def _evaluate_response(self, query: str, response_data: Dict, trace_id: str) -> EvaluationResult:
        """
        Evaluate the generated response
        """
        evaluation = self.evaluation_system.evaluate_response(
            query=query,
            response=response_data["response"],
            retrieved_docs=response_data["retrieved_docs"]
        )
        
        # Log evaluation
        self.observability.log_evaluation(trace_id, evaluation, evaluation.__dict__)
        
        return evaluation
    
    def _log_response_data(self, trace_id: str, response_data: Dict, evaluation: EvaluationResult):
        """
        Log response data to observability system
        """
        self.observability.log_response(trace_id, response_data["response"], response_data["retrieved_docs"])
    
    def get_session_analytics(self) -> Dict[str, any]:
        """
        Get analytics for the current session
        """
        return self.observability.get_session_summary(self.session_id)
    
    def export_session_traces(self, filepath: str = None) -> str:
        """
        Export session traces to file
        """
        return self.observability.export_traces(filepath)
    
    def flush_traces(self):
        """
        Flush all traces to Langfuse
        """
        self.observability.flush()
