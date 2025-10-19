# 🎵 RAG Chatbot with Evaluation, Observability & Recommendations

A comprehensive Retrieval-Augmented Generation (RAG) chatbot system for answering questions about songs, with built-in evaluation, observability, and recommendation features.

## 🎯 Features

### Core Functionality
- **RAG Pipeline**: Vector embeddings and semantic search for song information
- **Hallucination Prevention**: Restricts answers to dataset facts only
- **Citation System**: All responses include proper citations
- **Intent Recognition**: Understands different types of queries (search, favorites, recommendations)

### Evaluation System
- **Tone Analysis**: Evaluates response tone (neutral, apologetic, friendly)
- **Factuality Scoring**: Measures accuracy against dataset
- **Hallucination Detection**: Identifies when bot invents information
- **RAG Metrics**: Precision and recall of retrieved documents
- **Response Quality**: Overall assessment of response quality

### Observability & Tracing
- **Langfuse Integration**: End-to-end tracing of conversations
- **Session Management**: Track user interactions across sessions
- **Performance Metrics**: Monitor system performance and usage
- **Export Capabilities**: Export traces for analysis

### Favorites Management
- **REST API**: FastAPI-based favorites management
- **User-specific Storage**: SQLite database for user favorites
- **CRUD Operations**: Add, remove, list, and clear favorites

### Recommendation System
- **Mood-based Recommendations**: Suggest songs based on mood
- **User Preference Learning**: Recommendations based on user's favorite songs
- **Hybrid Approach**: Combines mood and user preferences
- **Diversity Options**: Trending and diverse recommendations

## 📊 Dataset

The system includes a dataset of 30 songs with the following attributes:
- **Title**: Song name
- **Author**: Artist/band name
- **Genre**: Musical genre
- **Mood**: Emotional tone (happy, sad, energetic, etc.)
- **Year**: Release year

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd apoorva
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (optional, for Langfuse):
```bash
export LANGFUSE_SECRET_KEY="your-secret-key"
export LANGFUSE_PUBLIC_KEY="your-public-key"
export LANGFUSE_HOST="https://cloud.langfuse.com"
```

### Running the Application

1. **Start the Streamlit web interface**:
```bash
streamlit run main.py
```

2. **Start the Favorites API** (in a separate terminal):
```bash
python favorites_api.py
```

3. **Access the application**:
   - Streamlit UI: http://localhost:8501
   - Favorites API: http://localhost:8000

## 🏗️ Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAG System    │    │  Evaluation     │    │ Observability   │
│                 │    │   System        │    │    System       │
│ • Vector Search │    │ • Tone Analysis │    │ • Langfuse     │
│ • Embeddings    │    │ • Factuality    │    │ • Tracing      │
│ • Retrieval     │    │ • Hallucination │    │ • Analytics    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Main Chatbot  │
                    │                 │
                    │ • Intent Parse  │
                    │ • Response Gen  │
                    │ • Integration   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Recommendations │
                    │                 │
                    │ • Mood-based    │
                    │ • User Prefs    │
                    │ • Hybrid        │
                    └─────────────────┘
```

### File Structure

```
apoorva/
├── main.py                 # Main Streamlit application
├── chatbot.py             # Core chatbot logic
├── rag_system.py          # RAG pipeline and vector search
├── evaluation_system.py   # Response evaluation framework
├── observability.py       # Langfuse integration and tracing
├── recommendation_system.py # Recommendation engine
├── favorites_api.py       # FastAPI for favorites management
├── songs_dataset.csv      # Song dataset
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 💬 Usage Examples

### Basic Queries
- "Who wrote Imagine?"
- "What genre is Bohemian Rhapsody?"
- "What mood is Hotel California?"
- "Tell me about Stairway to Heaven"

### Favorites Management
- "Add Imagine to my favorites"
- "What are my favorites?"
- "Show me my favorite songs"

### Recommendations
- "Recommend me happy songs"
- "What songs should I listen to for a sad mood?"
- "Suggest songs based on my preferences"

## 🔧 API Endpoints

### Favorites API (FastAPI)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/favorites/{user_id}` | Add song to favorites |
| GET | `/favorites/{user_id}` | Get user's favorites |
| DELETE | `/favorites/{user_id}` | Remove specific favorite |
| DELETE | `/favorites/{user_id}/clear` | Clear all favorites |
| GET | `/favorites/{user_id}/count` | Get favorites count |
| GET | `/favorites/analytics/all` | Get analytics for all users |
| GET | `/health` | Health check |

### Example API Usage

```python
import requests

# Add a favorite
response = requests.post(
    "http://localhost:8000/favorites/user_123",
    json={
        "song": {
            "title": "Imagine",
            "author": "John Lennon",
            "genre": "Rock",
            "mood": "Peaceful",
            "year": 1971
        }
    }
)

# Get favorites
response = requests.get("http://localhost:8000/favorites/user_123")
favorites = response.json()
```

## 📈 Evaluation Metrics

### Response Quality Metrics
- **Tone**: Neutral, Apologetic, Friendly
- **Factuality Score**: 0.0 - 1.0 (accuracy against dataset)
- **Hallucination Detection**: Boolean (invents information)
- **Citation Present**: Boolean (includes source)
- **RAG Precision**: 0.0 - 1.0 (relevant docs retrieved)
- **RAG Recall**: 0.0 - 1.0 (completeness of retrieval)
- **Response Quality**: Poor, Fair, Good, Excellent

### Analytics Dashboard
- Session analytics and user behavior
- Evaluation metrics over time
- Tone and quality distribution
- Hallucination rate tracking
- Citation rate monitoring

## 🔍 Observability Features

### Langfuse Integration
- **Trace Tracking**: Complete conversation flows
- **Span Logging**: Individual component activities
- **Metadata**: Rich context and performance data
- **Export**: Trace data for analysis

### Local Logging
- **Session Management**: Track user sessions
- **Export Capabilities**: JSON trace export
- **Analytics**: Session summaries and metrics

## 🎯 Recommendation Engine

### Types of Recommendations

1. **Mood-based**: Songs matching specific moods
2. **User Preference**: Based on user's favorite songs
3. **Hybrid**: Combines mood and user preferences
4. **Similar Songs**: Songs similar to a specific track
5. **Trending**: Popular songs (random selection)
6. **Diverse**: Cross-genre and cross-mood variety

### Recommendation Logic
- Analyzes user's favorite genres, moods, and artists
- Finds similar songs based on preferences
- Excludes already favorited songs
- Provides diverse recommendations

## 🛠️ Development

### Adding New Songs
1. Edit `songs_dataset.csv`
2. Restart the application
3. New songs will be automatically indexed

### Customizing Evaluation
- Modify `evaluation_system.py`
- Add new evaluation metrics
- Adjust scoring algorithms

### Extending Recommendations
- Update `recommendation_system.py`
- Add new recommendation strategies
- Implement custom similarity metrics

## 🧪 Testing

### Manual Testing
1. Start the application
2. Try various query types
3. Check evaluation metrics
4. Test favorites functionality
5. Verify recommendations

### API Testing
```bash
# Test favorites API
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/favorites/user_123"
```

## 📝 Configuration

### Environment Variables
```bash
# Langfuse (optional)
LANGFUSE_SECRET_KEY=your-secret-key
LANGFUSE_PUBLIC_KEY=your-public-key
LANGFUSE_HOST=https://cloud.langfuse.com

# Database
DATABASE_PATH=favorites.db
```

### Customization Options
- Dataset path in `RAGSystem`
- Database path in `FavoritesAPI`
- Evaluation thresholds in `EvaluationSystem`
- Recommendation limits in `RecommendationSystem`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review the code comments
3. Test with the provided examples
4. Create an issue with detailed information

## 🎉 Features Completed

✅ **Dataset**: 30 songs with comprehensive metadata  
✅ **RAG Pipeline**: Vector embeddings and semantic search  
✅ **Chatbot**: Intent recognition and response generation  
✅ **Evaluation**: Comprehensive response evaluation  
✅ **Observability**: Langfuse integration and tracing  
✅ **Favorites API**: Complete CRUD operations  
✅ **Recommendations**: Mood-based and user preference systems  
✅ **Web Interface**: Streamlit dashboard with analytics  
✅ **Documentation**: Comprehensive setup and usage guide  

---

**Built with ❤️ for demonstrating RAG chatbot capabilities with evaluation, observability, and recommendations.**
