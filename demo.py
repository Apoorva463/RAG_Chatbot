#!/usr/bin/env python3
"""
Demo Script for RAG Chatbot
Demonstrates the core functionality of the chatbot system
"""

import sys
import os
from chatbot import SongChatbot

def demo_chatbot():
    """Demonstrate chatbot functionality"""
    print("🎵 RAG Chatbot Demo")
    print("=" * 50)
    
    # Initialize chatbot
    print("🔄 Initializing chatbot...")
    chatbot = SongChatbot()
    print("✅ Chatbot initialized successfully!")
    
    # Demo queries
    demo_queries = [
        "Who wrote Imagine?",
        "What genre is Bohemian Rhapsody?",
        "What mood is Hotel California?",
        "Tell me about Stairway to Heaven",
        "Add Imagine to my favorites",
        "What are my favorites?",
        "Recommend me happy songs"
    ]
    
    user_id = "demo_user"
    
    print(f"\n🤖 Processing {len(demo_queries)} demo queries...")
    print("=" * 50)
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 30)
        
        try:
            # Process query
            result = chatbot.process_query(query, user_id)
            
            # Display response
            print(f"🤖 Response: {result['response']}")
            
            # Display evaluation metrics
            eval_data = result['evaluation']
            print(f"📊 Evaluation:")
            print(f"   • Tone: {eval_data.get('tone', 'N/A')}")
            print(f"   • Factuality: {eval_data.get('factuality_score', 0):.2f}")
            print(f"   • Hallucination: {'Yes' if eval_data.get('hallucination_detected') else 'No'}")
            print(f"   • Quality: {eval_data.get('response_quality', 'N/A')}")
            
            if result.get('citation'):
                print(f"📚 Citation: {result['citation']}")
                
        except Exception as e:
            print(f"❌ Error processing query: {e}")
    
    # Display session analytics
    print(f"\n📈 Session Analytics")
    print("=" * 30)
    analytics = chatbot.get_session_analytics()
    if analytics:
        print(f"Total Traces: {analytics.get('total_traces', 0)}")
        print(f"Unique Users: {len(analytics.get('unique_users', []))}")
        if analytics.get('duration_minutes'):
            print(f"Session Duration: {analytics['duration_minutes']:.1f} minutes")
    
    # Export traces
    print(f"\n💾 Exporting session traces...")
    trace_file = chatbot.export_session_traces("demo_traces.json")
    print(f"✅ Traces exported to: {trace_file}")
    
    # Flush traces to Langfuse (if configured)
    print(f"\n🔄 Flushing traces to Langfuse...")
    chatbot.flush_traces()
    print("✅ Traces flushed successfully!")
    
    print(f"\n🎉 Demo completed successfully!")
    print("=" * 50)

def demo_api():
    """Demonstrate API functionality"""
    print("\n🔗 FastAPI Demo")
    print("=" * 30)
    print("To test the API endpoints, start the FastAPI server:")
    print("python favorites_api.py")
    print("\nThen test these endpoints:")
    print("• GET  http://localhost:8000/health")
    print("• GET  http://localhost:8000/favorites/demo_user")
    print("• POST http://localhost:8000/favorites/demo_user")
    print("• GET  http://localhost:8000/docs (API documentation)")

def main():
    """Main demo function"""
    print("🚀 Starting RAG Chatbot Demo")
    print("This demo will showcase the chatbot's capabilities")
    print("=" * 60)
    
    try:
        # Run chatbot demo
        demo_chatbot()
        
        # Show API demo info
        demo_api()
        
        print(f"\n🎯 Next Steps:")
        print("1. Run 'streamlit run main.py' for the web interface")
        print("2. Run 'python favorites_api.py' for the API server")
        print("3. Check the README.md for detailed usage instructions")
        
    except KeyboardInterrupt:
        print(f"\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
