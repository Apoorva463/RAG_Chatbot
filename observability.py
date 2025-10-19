"""
Observability and Tracing System using Langfuse
Tracks conversations, evaluations, and system performance
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

try:
    from langfuse import Langfuse
    from langfuse.callback import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("Langfuse not available. Install with: pip install langfuse")

class ObservabilitySystem:
    def __init__(self, langfuse_secret_key: str = None, langfuse_public_key: str = None, 
                 langfuse_host: str = "https://cloud.langfuse.com"):
        """
        Initialize observability system with Langfuse
        """
        self.langfuse = None
        self.callback_handler = None
        self.session_id = None
        self.traces = []
        
        if LANGFUSE_AVAILABLE:
            try:
                # Initialize Langfuse with environment variables or provided keys
                self.langfuse = Langfuse(
                    secret_key=langfuse_secret_key or os.getenv("LANGFUSE_SECRET_KEY"),
                    public_key=langfuse_public_key or os.getenv("LANGFUSE_PUBLIC_KEY"),
                    host=langfuse_host or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
                )
                self.callback_handler = CallbackHandler(
                    secret_key=langfuse_secret_key or os.getenv("LANGFUSE_SECRET_KEY"),
                    public_key=langfuse_public_key or os.getenv("LANGFUSE_PUBLIC_KEY"),
                    host=langfuse_host or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
                )
                print("Langfuse initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Langfuse: {e}")
                self.langfuse = None
                self.callback_handler = None
        else:
            print("Langfuse not available. Using local logging instead.")
    
    def start_session(self, session_id: str = None) -> str:
        """Start a new conversation session"""
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.session_id = session_id
        return session_id
    
    def log_query(self, query: str, user_id: str = None) -> str:
        """Log a user query and return trace ID"""
        trace_id = f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        trace_data = {
            "trace_id": trace_id,
            "session_id": self.session_id,
            "user_id": user_id,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "type": "query"
        }
        
        self.traces.append(trace_data)
        
        if self.langfuse:
            try:
                self.langfuse.trace(
                    id=trace_id,
                    name="user_query",
                    input=query,
                    metadata={"user_id": user_id, "session_id": self.session_id}
                )
            except Exception as e:
                print(f"Failed to log query to Langfuse: {e}")
        
        return trace_id
    
    def log_retrieval(self, trace_id: str, retrieved_docs: List[Dict], 
                     query: str, top_k: int = 3) -> None:
        """Log document retrieval results"""
        retrieval_data = {
            "trace_id": trace_id,
            "retrieved_docs": retrieved_docs,
            "query": query,
            "top_k": top_k,
            "timestamp": datetime.now().isoformat(),
            "type": "retrieval"
        }
        
        self.traces.append(retrieval_data)
        
        if self.langfuse:
            try:
                self.langfuse.span(
                    trace_id=trace_id,
                    name="document_retrieval",
                    input=query,
                    output=retrieved_docs,
                    metadata={"top_k": top_k, "num_docs": len(retrieved_docs)}
                )
            except Exception as e:
                print(f"Failed to log retrieval to Langfuse: {e}")
    
    def log_response(self, trace_id: str, response: str, 
                    retrieved_docs: List[Dict] = None) -> None:
        """Log chatbot response"""
        response_data = {
            "trace_id": trace_id,
            "response": response,
            "retrieved_docs": retrieved_docs,
            "timestamp": datetime.now().isoformat(),
            "type": "response"
        }
        
        self.traces.append(response_data)
        
        if self.langfuse:
            try:
                self.langfuse.span(
                    trace_id=trace_id,
                    name="chatbot_response",
                    input=retrieved_docs,
                    output=response,
                    metadata={"response_length": len(response)}
                )
            except Exception as e:
                print(f"Failed to log response to Langfuse: {e}")
    
    def log_evaluation(self, trace_id: str, evaluation_result: Any, 
                      evaluation_metrics: Dict[str, Any]) -> None:
        """Log evaluation results"""
        evaluation_data = {
            "trace_id": trace_id,
            "evaluation_result": evaluation_result.__dict__ if hasattr(evaluation_result, '__dict__') else evaluation_result,
            "evaluation_metrics": evaluation_metrics,
            "timestamp": datetime.now().isoformat(),
            "type": "evaluation"
        }
        
        self.traces.append(evaluation_data)
        
        if self.langfuse:
            try:
                self.langfuse.span(
                    trace_id=trace_id,
                    name="evaluation",
                    input=evaluation_metrics,
                    output=evaluation_result.__dict__ if hasattr(evaluation_result, '__dict__') else evaluation_result,
                    metadata={"evaluation_type": "comprehensive"}
                )
            except Exception as e:
                print(f"Failed to log evaluation to Langfuse: {e}")
    
    def log_recommendation(self, trace_id: str, user_id: str, recommendation_type: str,
                          recommendations: List[Dict], user_favorites: List[Dict] = None) -> None:
        """Log recommendation generation"""
        recommendation_data = {
            "trace_id": trace_id,
            "user_id": user_id,
            "recommendation_type": recommendation_type,
            "recommendations": recommendations,
            "user_favorites": user_favorites,
            "timestamp": datetime.now().isoformat(),
            "type": "recommendation"
        }
        
        self.traces.append(recommendation_data)
        
        if self.langfuse:
            try:
                self.langfuse.span(
                    trace_id=trace_id,
                    name="recommendation_generation",
                    input={"user_favorites": user_favorites, "type": recommendation_type},
                    output=recommendations,
                    metadata={"num_recommendations": len(recommendations)}
                )
            except Exception as e:
                print(f"Failed to log recommendation to Langfuse: {e}")
    
    def log_favorites_action(self, trace_id: str, user_id: str, action: str,
                            song: Dict = None, favorites: List[Dict] = None) -> None:
        """Log favorites management actions"""
        favorites_data = {
            "trace_id": trace_id,
            "user_id": user_id,
            "action": action,
            "song": song,
            "favorites": favorites,
            "timestamp": datetime.now().isoformat(),
            "type": "favorites"
        }
        
        self.traces.append(favorites_data)
        
        if self.langfuse:
            try:
                self.langfuse.span(
                    trace_id=trace_id,
                    name="favorites_management",
                    input={"action": action, "song": song},
                    output=favorites,
                    metadata={"user_id": user_id, "action": action}
                )
            except Exception as e:
                print(f"Failed to log favorites action to Langfuse: {e}")
    
    def get_session_traces(self, session_id: str = None) -> List[Dict]:
        """Get all traces for a session"""
        if session_id:
            return [trace for trace in self.traces if trace.get('session_id') == session_id]
        return self.traces
    
    def get_trace_by_id(self, trace_id: str) -> Optional[Dict]:
        """Get a specific trace by ID"""
        for trace in self.traces:
            if trace.get('trace_id') == trace_id:
                return trace
        return None
    
    def export_traces(self, filepath: str = None) -> str:
        """Export all traces to a JSON file"""
        if not filepath:
            filepath = f"traces_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filepath, 'w') as f:
            json.dump(self.traces, f, indent=2, default=str)
        
        return filepath
    
    def get_session_summary(self, session_id: str = None) -> Dict[str, Any]:
        """Get a summary of session activity"""
        session_traces = self.get_session_traces(session_id)
        
        if not session_traces:
            return {"error": "No traces found for session"}
        
        # Count different types of activities
        activity_counts = {}
        for trace in session_traces:
            activity_type = trace.get('type', 'unknown')
            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
        
        # Get unique users
        user_ids = set(trace.get('user_id') for trace in session_traces if trace.get('user_id'))
        
        # Get time range
        timestamps = [trace.get('timestamp') for trace in session_traces if trace.get('timestamp')]
        start_time = min(timestamps) if timestamps else None
        end_time = max(timestamps) if timestamps else None
        
        return {
            "session_id": session_id or self.session_id,
            "total_traces": len(session_traces),
            "activity_counts": activity_counts,
            "unique_users": list(user_ids),
            "start_time": start_time,
            "end_time": end_time,
            "duration_minutes": self._calculate_duration(start_time, end_time)
        }
    
    def _calculate_duration(self, start_time: str, end_time: str) -> Optional[float]:
        """Calculate duration in minutes between two timestamps"""
        if not start_time or not end_time:
            return None
        
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            duration = (end_dt - start_dt).total_seconds() / 60
            return round(duration, 2)
        except:
            return None
    
    def flush(self):
        """Flush all pending traces to Langfuse"""
        if self.langfuse:
            try:
                self.langfuse.flush()
                print("Successfully flushed traces to Langfuse")
            except Exception as e:
                print(f"Failed to flush traces to Langfuse: {e}")
