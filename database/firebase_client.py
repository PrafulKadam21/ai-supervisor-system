import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import HelpRequest, KnowledgeEntry, CallLog, RequestStatus


class FirebaseClient:
    """Firebase client for managing help requests and knowledge base"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize Firebase client"""
        if not firebase_admin._apps:
            cred_path = credentials_path or os.getenv('FIREBASE_CREDENTIALS_PATH')
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self.help_requests_ref = self.db.collection('help_requests')
        self.knowledge_ref = self.db.collection('knowledge_base')
        self.call_logs_ref = self.db.collection('call_logs')
    
    # Help Request Operations
    def create_help_request(self, help_request: HelpRequest) -> str:
        """Create a new help request"""
        doc_ref = self.help_requests_ref.document()
        help_request.id = doc_ref.id
        doc_ref.set(help_request.to_dict())
        return doc_ref.id
    
    def get_help_request(self, request_id: str) -> Optional[HelpRequest]:
        """Get a help request by ID"""
        doc = self.help_requests_ref.document(request_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return HelpRequest.from_dict(data)
        return None
    
    def get_pending_requests(self) -> List[HelpRequest]:
        """Get all pending help requests"""
        docs = self.help_requests_ref.where('status', '==', RequestStatus.PENDING.value).stream()
        requests = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            requests.append(HelpRequest.from_dict(data))
        return sorted(requests, key=lambda x: x.created_at, reverse=True)
    
    def get_all_requests(self, limit: int = 50) -> List[HelpRequest]:
        """Get all help requests (for history view)"""
        docs = self.help_requests_ref.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
        requests = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            requests.append(HelpRequest.from_dict(data))
        return requests
    
    def resolve_help_request(self, request_id: str, answer: str, supervisor_name: str = "Supervisor") -> bool:
        """Mark a help request as resolved with an answer"""
        try:
            self.help_requests_ref.document(request_id).update({
                'status': RequestStatus.RESOLVED.value,
                'supervisor_answer': answer,
                'supervisor_name': supervisor_name,
                'resolved_at': datetime.utcnow().isoformat()
            })
            return True
        except Exception as e:
            print(f"Error resolving help request: {e}")
            return False
    
    def timeout_help_request(self, request_id: str) -> bool:
        """Mark a help request as timed out"""
        try:
            self.help_requests_ref.document(request_id).update({
                'status': RequestStatus.TIMEOUT.value,
                'resolved_at': datetime.utcnow().isoformat()
            })
            return True
        except Exception as e:
            print(f"Error timing out help request: {e}")
            return False
    
    # Knowledge Base Operations
    def add_knowledge(self, knowledge: KnowledgeEntry) -> str:
        """Add a new knowledge entry"""
        doc_ref = self.knowledge_ref.document()
        knowledge.id = doc_ref.id
        doc_ref.set(knowledge.to_dict())
        return doc_ref.id
    
    def search_knowledge(self, query: str) -> List[KnowledgeEntry]:
        """Search knowledge base (simple text matching for now)"""
        # Note: For production, you'd use a vector database or full-text search
        docs = self.knowledge_ref.stream()
        results = []
        query_lower = query.lower()
        
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            entry = KnowledgeEntry.from_dict(data)
            
            if query_lower in entry.question.lower() or query_lower in entry.answer.lower():
                results.append(entry)
        
        return sorted(results, key=lambda x: x.usage_count, reverse=True)
    
    def get_all_knowledge(self) -> List[KnowledgeEntry]:
        """Get all knowledge entries"""
        docs = self.knowledge_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        entries = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            entries.append(KnowledgeEntry.from_dict(data))
        return entries
    
    def increment_knowledge_usage(self, knowledge_id: str):
        """Increment usage count for a knowledge entry"""
        doc_ref = self.knowledge_ref.document(knowledge_id)
        doc_ref.update({
            'usage_count': firestore.Increment(1),
            'updated_at': datetime.utcnow().isoformat()
        })
    
    # Call Log Operations
    def create_call_log(self, call_log: CallLog) -> str:
        """Create a new call log"""
        doc_ref = self.call_logs_ref.document()
        call_log.id = doc_ref.id
        doc_ref.set(call_log.to_dict())
        return doc_ref.id
    
    def update_call_log(self, call_id: str, updates: Dict[str, Any]) -> bool:
        """Update a call log"""
        try:
            if 'ended_at' in updates and isinstance(updates['ended_at'], datetime):
                updates['ended_at'] = updates['ended_at'].isoformat()
            self.call_logs_ref.document(call_id).update(updates)
            return True
        except Exception as e:
            print(f"Error updating call log: {e}")
            return False
    
    def get_call_logs(self, limit: int = 50) -> List[CallLog]:
        """Get recent call logs"""
        docs = self.call_logs_ref.order_by('started_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
        logs = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            logs.append(CallLog.from_dict(data))
        return logs