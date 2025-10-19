#!/usr/bin/env python3
"""
Run Script for RAG Chatbot Application
Starts both the Streamlit web interface and FastAPI server
"""

import subprocess
import sys
import time
import os
from threading import Thread

def run_streamlit():
    """Run Streamlit application"""
    print("🚀 Starting Streamlit application...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "main.py", "--server.port", "8501"])

def run_fastapi():
    """Run FastAPI server"""
    print("🚀 Starting FastAPI server...")
    subprocess.run([sys.executable, "favorites_api.py"])

def main():
    """Main function to start both services"""
    print("🎵 Starting RAG Chatbot Application...")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        "main.py",
        "favorites_api.py", 
        "chatbot.py",
        "rag_system.py",
        "evaluation_system.py",
        "observability.py",
        "recommendation_system.py",
        "songs_dataset.csv"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please ensure all files are present in the current directory.")
        return
    
    print("✅ All required files found!")
    print("\n📋 Starting services...")
    print("🌐 Streamlit UI will be available at: http://localhost:8501")
    print("🔗 FastAPI will be available at: http://localhost:8000")
    print("📊 API documentation at: http://localhost:8000/docs")
    print("\n" + "=" * 50)
    
    try:
        # Start FastAPI in a separate thread
        fastapi_thread = Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()
        
        # Wait a moment for FastAPI to start
        time.sleep(2)
        
        # Start Streamlit (this will block)
        run_streamlit()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down application...")
        print("Thank you for using the RAG Chatbot!")

if __name__ == "__main__":
    main()
