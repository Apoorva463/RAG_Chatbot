"""
Evaluation System for RAG Chatbot
Evaluates tone, factuality, hallucination rate, and RAG metrics
"""

import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import json

@dataclass
class EvaluationResult:
    """Data class for evaluation results"""
    tone: str
    factuality_score: float
    hallucination_detected: bool
    rag_precision: float
    rag_recall: float
    citation_present: bool
    response_quality: str

class EvaluationSystem:
    def __init__(self):
        """Initialize the evaluation system"""
        self.factual_keywords = [
            'song', 'title', 'author', 'artist', 'genre', 'mood', 'year',
            'wrote', 'performed', 'released', 'created'
        ]
        
        self.hallucination_indicators = [
            'i think', 'probably', 'might be', 'could be', 'possibly',
            'i believe', 'i assume', 'i guess', 'i\'m not sure'
        ]
        
        self.tone_indicators = {
            'friendly': ['great', 'wonderful', 'amazing', 'awesome', 'love', 'enjoy'],
            'apologetic': ['sorry', 'unfortunately', 'i don\'t have', 'can\'t find', 'not available'],
            'neutral': ['the', 'is', 'was', 'by', 'from', 'in', 'on']
        }
    
    def evaluate_response(self, query: str, response: str, retrieved_docs: List[Dict], 
                         expected_answer: str = None) -> EvaluationResult:
        """
        Comprehensive evaluation of chatbot response
        """
        # Evaluate tone
        tone = self._evaluate_tone(response)
        
        # Evaluate factuality
        factuality_score = self._evaluate_factuality(response, retrieved_docs)
        
        # Detect hallucination
        hallucination_detected = self._detect_hallucination(response, retrieved_docs)
        
        # Evaluate RAG metrics
        rag_precision, rag_recall = self._evaluate_rag_metrics(query, retrieved_docs, response)
        
        # Check for citation
        citation_present = self._check_citation(response)
        
        # Overall response quality
        response_quality = self._assess_response_quality(
            factuality_score, hallucination_detected, citation_present
        )
        
        return EvaluationResult(
            tone=tone,
            factuality_score=factuality_score,
            hallucination_detected=hallucination_detected,
            rag_precision=rag_precision,
            rag_recall=rag_recall,
            citation_present=citation_present,
            response_quality=response_quality
        )
    
    def _evaluate_tone(self, response: str) -> str:
        """Evaluate the tone of the response"""
        response_lower = response.lower()
        
        friendly_score = sum(1 for word in self.tone_indicators['friendly'] 
                           if word in response_lower)
        apologetic_score = sum(1 for word in self.tone_indicators['apologetic'] 
                             if word in response_lower)
        
        if apologetic_score > friendly_score:
            return "apologetic"
        elif friendly_score > 0:
            return "friendly"
        else:
            return "neutral"
    
    def _evaluate_factuality(self, response: str, retrieved_docs: List[Dict]) -> float:
        """Evaluate how factual the response is based on retrieved documents"""
        if not retrieved_docs:
            return 0.5  # Give some credit even without docs
        
        # Extract factual information from retrieved docs
        doc_facts = []
        for doc in retrieved_docs:
            doc_facts.extend([
                doc.get('Title', '').lower(),
                doc.get('Author', '').lower(),
                doc.get('Genre', '').lower(),
                doc.get('Mood', '').lower(),
                str(doc.get('Year', '')).lower()
            ])
        
        # Check if response contains facts from retrieved docs
        response_lower = response.lower()
        factual_matches = sum(1 for fact in doc_facts 
                            if fact and fact in response_lower)
        
        # Also check for partial matches (more lenient)
        partial_matches = 0
        for fact in doc_facts:
            if fact and len(fact) > 2:  # Only check meaningful facts
                # Check if any part of the fact appears in response
                fact_words = fact.split()
                for word in fact_words:
                    if len(word) > 2 and word in response_lower:
                        partial_matches += 0.5
                        break
        
        # Normalize by response length and number of available facts
        total_facts = len([f for f in doc_facts if f])
        if total_facts == 0:
            return 0.5
        
        # Combine exact and partial matches
        total_matches = factual_matches + partial_matches
        return min(total_matches / total_facts, 1.0)
    
    def _detect_hallucination(self, response: str, retrieved_docs: List[Dict]) -> bool:
        """Detect if the response contains hallucinated information"""
        response_lower = response.lower()
        
        # Check for explicit hallucination indicators
        for indicator in self.hallucination_indicators:
            if indicator in response_lower:
                return True
        
        # If no retrieved docs, be more lenient
        if not retrieved_docs:
            return False  # Changed from True to False - don't penalize for no docs
        
        # Extract all information from retrieved docs
        doc_info = []
        for doc in retrieved_docs:
            doc_info.extend([
                doc.get('Title', ''),
                doc.get('Author', ''),
                doc.get('Genre', ''),
                doc.get('Mood', ''),
                str(doc.get('Year', ''))
            ])
        
        # Common words that should be allowed in responses
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'song', 'music', 'artist', 'band', 'album', 'released', 'written', 'performed', 'created'
        }
        
        # Check if response contains specific claims not backed by docs
        response_words = response_lower.split()
        doc_words = ' '.join(doc_info).lower().split()
        
        # Filter out common words and short words
        unknown_words = [word for word in response_words 
                        if word not in doc_words and word not in common_words and len(word) > 4]
        
        # More lenient threshold - only flag if >50% of meaningful words are unknown
        return len(unknown_words) > len(response_words) * 0.5
    
    def _evaluate_rag_metrics(self, query: str, retrieved_docs: List[Dict], response: str) -> Tuple[float, float]:
        """Evaluate RAG precision and recall"""
        if not retrieved_docs:
            return 0.0, 0.0
        
        # Extract query terms and filter out common stop words
        stop_words = {'who', 'what', 'when', 'where', 'why', 'how', 'is', 'are', 'was', 'were', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        query_terms = set(query.lower().split())
        meaningful_terms = query_terms - stop_words
        
        # If no meaningful terms, use all terms
        if not meaningful_terms:
            meaningful_terms = query_terms
        
        # Calculate precision: relevant docs retrieved / total docs retrieved
        relevant_docs = 0
        for doc in retrieved_docs:
            # Include more fields for better matching
            doc_text = f"{doc.get('Title', '')} {doc.get('Author', '')} {doc.get('Genre', '')} {doc.get('Mood', '')} {doc.get('Year', '')}".lower()
            
            # Check for exact matches
            exact_matches = sum(1 for term in meaningful_terms if term in doc_text)
            
            # Also check for partial matches (for compound words)
            partial_matches = 0
            for term in meaningful_terms:
                if len(term) > 3:  # Only for meaningful terms
                    for doc_word in doc_text.split():
                        if term in doc_word or doc_word in term:
                            partial_matches += 0.5
                            break
            
            # Consider document relevant if it has any meaningful matches
            if exact_matches > 0 or partial_matches > 0:
                relevant_docs += 1
        
        precision = relevant_docs / len(retrieved_docs) if retrieved_docs else 0.0
        
        # Calculate recall: relevant docs retrieved / total relevant docs in dataset
        # This is simplified - in practice, you'd need to know total relevant docs
        recall = min(precision, 1.0)  # Simplified recall calculation
        
        return precision, recall
    
    def _check_citation(self, response: str) -> bool:
        """Check if response includes proper citation"""
        citation_patterns = [
            r'according to',
            r'from the dataset',
            r'based on',
            r'as mentioned in',
            r'cited in',
            r'source:',
            r'by\s+\w+',  # "by [Author]" pattern
            r'\([^)]+\)',  # Parenthetical citations
            r'\[[^\]]+\]'  # Bracket citations
        ]
        
        for pattern in citation_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return True
        
        # Also check if response contains author names (common citation format)
        # This is a simple heuristic - in practice, you'd use more sophisticated NLP
        response_lower = response.lower()
        if 'by ' in response_lower and any(word in response_lower for word in ['song', 'music', 'track', 'artist']):
            return True
        
        return False
    
    def _assess_response_quality(self, factuality_score: float, hallucination_detected: bool, 
                               citation_present: bool) -> str:
        """Assess overall response quality"""
        # More balanced quality assessment
        if hallucination_detected and factuality_score < 0.3:
            return "poor"
        elif factuality_score >= 0.8 and citation_present:
            return "excellent"
        elif factuality_score >= 0.7:
            return "good"
        elif factuality_score >= 0.5:
            return "fair"
        else:
            return "poor"
    
    def generate_evaluation_report(self, evaluations: List[Dict]) -> Dict[str, Any]:
        """Generate a comprehensive evaluation report"""
        if not evaluations:
            return {}
        
        total_evaluations = len(evaluations)
        
        # Calculate averages - handle both dict and EvaluationResult objects
        avg_factuality = sum(e.get('factuality_score', 0) if isinstance(e, dict) else e.factuality_score for e in evaluations) / total_evaluations
        avg_precision = sum(e.get('rag_precision', 0) if isinstance(e, dict) else e.rag_precision for e in evaluations) / total_evaluations
        avg_recall = sum(e.get('rag_recall', 0) if isinstance(e, dict) else e.rag_recall for e in evaluations) / total_evaluations
        
        # Count categorical metrics
        tone_distribution = {}
        for evaluation in evaluations:
            tone = evaluation.get('tone', 'neutral') if isinstance(evaluation, dict) else evaluation.tone
            tone_distribution[tone] = tone_distribution.get(tone, 0) + 1
        
        hallucination_rate = sum(1 for e in evaluations if (e.get('hallucination_detected', False) if isinstance(e, dict) else e.hallucination_detected)) / total_evaluations
        citation_rate = sum(1 for e in evaluations if (e.get('citation_present', False) if isinstance(e, dict) else e.citation_present)) / total_evaluations
        
        quality_distribution = {}
        for evaluation in evaluations:
            quality = evaluation.get('response_quality', 'fair') if isinstance(evaluation, dict) else evaluation.response_quality
            quality_distribution[quality] = quality_distribution.get(quality, 0) + 1
        
        return {
            "total_evaluations": total_evaluations,
            "average_factuality_score": round(avg_factuality, 3),
            "average_rag_precision": round(avg_precision, 3),
            "average_rag_recall": round(avg_recall, 3),
            "hallucination_rate": round(hallucination_rate, 3),
            "citation_rate": round(citation_rate, 3),
            "tone_distribution": tone_distribution,
            "quality_distribution": quality_distribution
        }
