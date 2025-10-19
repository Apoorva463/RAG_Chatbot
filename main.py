"""
Main Application - RAG Chatbot with Evaluation, Observability & Recommendations
Integrates all components into a complete chatbot system
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any

from chatbot import SongChatbot
from favorites_api import FavoritesAPI
from recommendation_system import RecommendationSystem
from evaluation_system import EvaluationSystem

# Page configuration
st.set_page_config(
    page_title="Song RAG Chatbot",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .evaluation-metric {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_chatbot():
    """Initialize the chatbot system"""
    if 'chatbot' not in st.session_state:
        with st.spinner("Initializing RAG Chatbot System..."):
            st.session_state.chatbot = SongChatbot()
            st.session_state.chat_history = []
            st.session_state.evaluation_history = []
    return st.session_state.chatbot

def display_chat_history():
    """Display chat history"""
    if st.session_state.chat_history:
        st.subheader("💬 Conversation History")
        
        for i, chat in enumerate(st.session_state.chat_history):
            with st.expander(f"Query {i+1}: {chat['query'][:50]}...", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Query:** {chat['query']}")
                    st.markdown(f"**Response:** {chat['response']}")
                    if chat.get('citation'):
                        st.markdown(f"**Citation:** {chat['citation']}")
                
                with col2:
                    if 'evaluation' in chat:
                        eval_data = chat['evaluation']
                        st.markdown("**Evaluation:**")
                        st.markdown(f"Tone: {eval_data.get('tone', 'N/A')}")
                        st.markdown(f"Factuality: {eval_data.get('factuality_score', 0):.2f}")
                        st.markdown(f"Hallucination: {'Yes' if eval_data.get('hallucination_detected') else 'No'}")
                        st.markdown(f"Quality: {eval_data.get('response_quality', 'N/A')}")

def display_analytics():
    """Display analytics and evaluation metrics"""
    st.subheader("📊 Analytics & Evaluation")
    
    if st.session_state.evaluation_history:
        # Create evaluation metrics
        evaluations = st.session_state.evaluation_history
        eval_system = EvaluationSystem()
        report = eval_system.generate_evaluation_report(evaluations)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Queries", report.get('total_evaluations', 0))
            st.metric("Avg Factuality", f"{report.get('average_factuality_score', 0):.2f}")
        
        with col2:
            st.metric("Hallucination Rate", f"{report.get('hallucination_rate', 0):.1%}")
            st.metric("Citation Rate", f"{report.get('citation_rate', 0):.1%}")
        
        with col3:
            st.metric("Avg RAG Precision", f"{report.get('average_rag_precision', 0):.2f}")
            st.metric("Avg RAG Recall", f"{report.get('average_rag_recall', 0):.2f}")
        
        # Tone distribution chart
        if report.get('tone_distribution'):
            st.subheader("Tone Distribution")
            tone_data = report['tone_distribution']
            fig = px.pie(values=list(tone_data.values()), names=list(tone_data.keys()), 
                        title="Response Tone Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Quality distribution chart
        if report.get('quality_distribution'):
            st.subheader("Response Quality Distribution")
            quality_data = report['quality_distribution']
            fig = px.bar(x=list(quality_data.keys()), y=list(quality_data.values()),
                        title="Response Quality Distribution")
            st.plotly_chart(fig, use_container_width=True)

def display_favorites_management():
    """Display favorites management interface"""
    st.subheader("❤️ Favorites Management")
    
    user_id = st.text_input("User ID", value="user_123", help="Enter your user ID to manage favorites")
    
    if user_id:
        favorites_api = FavoritesAPI()
        favorites = favorites_api.get_favorites(user_id)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Your Favorites:**")
            if favorites:
                for i, fav in enumerate(favorites, 1):
                    st.markdown(f"{i}. **{fav.title}** by {fav.author} ({fav.genre}, {fav.mood})")
            else:
                st.markdown("*No favorites yet. Add some songs to your favorites!*")
        
        with col2:
            st.markdown("**Add to Favorites:**")
            song_title = st.text_input("Song Title", placeholder="Enter song title")
            if st.button("Add to Favorites") and song_title:
                # Find the song in the dataset
                chatbot = st.session_state.chatbot
                song = chatbot.rag_system.get_song_by_exact_title(song_title)
                
                if song:
                    from favorites_api import Song
                    song_obj = Song(
                        title=song['Title'],
                        author=song['Author'],
                        genre=song['Genre'],
                        mood=song['Mood'],
                        year=song['Year']
                    )
                    
                    success = favorites_api.add_favorite(user_id, song_obj)
                    if success:
                        st.success(f"Added '{song['Title']}' to your favorites!")
                        st.rerun()
                    else:
                        st.warning(f"'{song['Title']}' is already in your favorites.")
                else:
                    st.error(f"Song '{song_title}' not found in dataset.")

def display_recommendations():
    """Display recommendation interface"""
    st.subheader("🎯 Recommendations")
    
    user_id = st.text_input("User ID for Recommendations", value="user_123")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Mood-based Recommendations:**")
        mood = st.selectbox("Select Mood", 
                           ["happy", "sad", "energetic", "chill", "romantic", "angry", "peaceful"])
        
        if st.button("Get Mood Recommendations"):
            chatbot = st.session_state.chatbot
            recommendations = chatbot.recommendation_system.get_mood_based_recommendations(mood, limit=5)
            
            if recommendations:
                st.markdown(f"**{mood.title()} songs you might like:**")
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"{i}. **{rec['Title']}** by {rec['Author']} ({rec['Genre']})")
            else:
                st.markdown(f"No {mood} songs found in the dataset.")
    
    with col2:
        st.markdown("**User Preference Recommendations:**")
        if st.button("Get Personal Recommendations"):
            chatbot = st.session_state.chatbot
            recommendations = chatbot.recommendation_system.get_user_preference_recommendations(user_id, limit=5)
            
            if recommendations:
                st.markdown("**Songs based on your preferences:**")
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"{i}. **{rec['Title']}** by {rec['Author']} ({rec['Genre']}, {rec['Mood']})")
            else:
                st.markdown("No recommendations available. Try adding some songs to your favorites first!")

def main():
    """Main application"""
    # Header
    st.markdown('<h1 class="main-header">🎵 Song RAG Chatbot</h1>', unsafe_allow_html=True)
    st.markdown("**Retrieval-Augmented Generation Chatbot with Evaluation, Observability & Recommendations**")
    
    # Initialize chatbot
    chatbot = initialize_chatbot()
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # User ID input
        user_id = st.text_input("User ID", value="user_123", help="Enter your user ID for personalized features")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.evaluation_history = []
            st.rerun()
        
        # Export traces button
        if st.button("📊 Export Session Traces"):
            filepath = chatbot.export_session_traces()
            st.success(f"Traces exported to {filepath}")
        
        # Session analytics
        st.header("📈 Session Analytics")
        analytics = chatbot.get_session_analytics()
        if analytics:
            st.metric("Total Traces", analytics.get('total_traces', 0))
            st.metric("Unique Users", len(analytics.get('unique_users', [])))
            if analytics.get('duration_minutes'):
                st.metric("Session Duration", f"{analytics['duration_minutes']:.1f} min")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat", "📊 Analytics", "❤️ Favorites", "🎯 Recommendations", "📋 Dataset"])
    
    with tab1:
        st.subheader("Chat with the Song Bot")
        st.markdown("Ask me about songs in my dataset! I can tell you about authors, genres, moods, and more.")
        
        # Chat input
        query = st.text_input("Ask me about a song:", placeholder="e.g., Who wrote Imagine? What genre is Bohemian Rhapsody?")
        
        if st.button("Send") and query:
            with st.spinner("Processing your query..."):
                # Process query
                result = chatbot.process_query(query, user_id)
                
                # Store in session state
                st.session_state.chat_history.append(result)
                st.session_state.evaluation_history.append(result['evaluation'])
                
                # Display response
                st.markdown(f'<div class="chat-message bot-message">', unsafe_allow_html=True)
                st.markdown(f"**Response:** {result['response']}")
                if result.get('citation'):
                    st.markdown(f"**Citation:** {result['citation']}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Display evaluation metrics
                with st.expander("📊 Response Evaluation", expanded=False):
                    eval_data = result['evaluation']
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Tone", eval_data.get('tone', 'N/A'))
                        st.metric("Factuality Score", f"{eval_data.get('factuality_score', 0):.2f}")
                    
                    with col2:
                        st.metric("Hallucination", "Yes" if eval_data.get('hallucination_detected') else "No")
                        st.metric("Citation Present", "Yes" if eval_data.get('citation_present') else "No")
                    
                    with col3:
                        st.metric("RAG Precision", f"{eval_data.get('rag_precision', 0):.2f}")
                        st.metric("Response Quality", eval_data.get('response_quality', 'N/A'))
        
        # Display chat history
        display_chat_history()
    
    with tab2:
        display_analytics()
    
    with tab3:
        display_favorites_management()
    
    with tab4:
        display_recommendations()
    
    with tab5:
        st.subheader("📋 Song Dataset")
        st.markdown("Explore the songs in our dataset:")
        
        # Load and display dataset
        df = pd.read_csv("songs_dataset.csv")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_genre = st.selectbox("Filter by Genre", ["All"] + list(df['Genre'].unique()))
        
        with col2:
            selected_mood = st.selectbox("Filter by Mood", ["All"] + list(df['Mood'].unique()))
        
        with col3:
            year_range = st.slider("Year Range", 
                                 int(df['Year'].min()), 
                                 int(df['Year'].max()), 
                                 (int(df['Year'].min()), int(df['Year'].max())))
        
        # Apply filters
        filtered_df = df.copy()
        if selected_genre != "All":
            filtered_df = filtered_df[filtered_df['Genre'] == selected_genre]
        if selected_mood != "All":
            filtered_df = filtered_df[filtered_df['Mood'] == selected_mood]
        filtered_df = filtered_df[
            (filtered_df['Year'] >= year_range[0]) & 
            (filtered_df['Year'] <= year_range[1])
        ]
        
        st.markdown(f"**Showing {len(filtered_df)} songs:**")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Dataset statistics
        st.subheader("📈 Dataset Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Songs", len(df))
            st.metric("Unique Genres", df['Genre'].nunique())
        
        with col2:
            st.metric("Unique Authors", df['Author'].nunique())
            st.metric("Unique Moods", df['Mood'].nunique())
        
        with col3:
            st.metric("Year Range", f"{df['Year'].min()}-{df['Year'].max()}")
            st.metric("Avg Year", f"{df['Year'].mean():.0f}")
        
        # Genre distribution
        st.subheader("Genre Distribution")
        genre_counts = df['Genre'].value_counts()
        fig = px.pie(values=genre_counts.values, names=genre_counts.index, title="Songs by Genre")
        st.plotly_chart(fig, use_container_width=True)
        
        # Mood distribution
        st.subheader("Mood Distribution")
        mood_counts = df['Mood'].value_counts()
        fig = px.bar(x=mood_counts.index, y=mood_counts.values, title="Songs by Mood")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
