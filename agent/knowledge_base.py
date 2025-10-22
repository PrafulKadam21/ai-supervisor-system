from typing import Optional, List
from database.firebase_client import FirebaseClient
from database.models import KnowledgeEntry


class KnowledgeBase:
    """Manages the AI's knowledge base with learning capabilities"""
    
    def __init__(self, firebase_client: FirebaseClient):
        self.db = firebase_client
        self._cache = []
        self._load_cache()
    
    def _load_cache(self):
        """Load knowledge into memory for faster access"""
        self._cache = self.db.get_all_knowledge()
    
    def search(self, question: str) -> Optional[KnowledgeEntry]:
        """Search for an answer to a question"""
        # First check cache
        question_lower = question.lower()
        for entry in self._cache:
            if self._is_similar(question_lower, entry.question.lower()):
                self.db.increment_knowledge_usage(entry.id)
                return entry
        
        # If not in cache, search database
        results = self.db.search_knowledge(question)
        if results:
            best_match = results[0]
            self.db.increment_knowledge_usage(best_match.id)
            return best_match
        
        return None
    
    def _is_similar(self, q1: str, q2: str, threshold: float = 0.6) -> bool:
        """Simple similarity check (can be improved with embeddings)"""
        words1 = set(q1.split())
        words2 = set(q2.split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold
    
    def add_knowledge(self, question: str, answer: str, help_request_id: Optional[str] = None) -> str:
        """Add new knowledge learned from supervisor"""
        entry = KnowledgeEntry(
            question=question,
            answer=answer,
            source="supervisor",
            help_request_id=help_request_id
        )
        
        entry_id = self.db.add_knowledge(entry)
        entry.id = entry_id
        self._cache.append(entry)
        
        return entry_id
    
    def get_all_knowledge(self) -> List[KnowledgeEntry]:
        """Get all knowledge entries"""
        return self._cache
    
    def refresh_cache(self):
        """Refresh the knowledge cache"""
        self._load_cache()
    
    def get_context_for_prompt(self, limit: int = 10) -> str:
        """Generate context string for AI prompt from top knowledge"""
        top_knowledge = sorted(self._cache, key=lambda x: x.usage_count, reverse=True)[:limit]
        
        if not top_knowledge:
            return "No learned knowledge yet."
        
        context_parts = ["Learned Knowledge:"]
        for entry in top_knowledge:
            context_parts.append(f"Q: {entry.question}")
            context_parts.append(f"A: {entry.answer}")
            context_parts.append("")
        
        return "\n".join(context_parts)