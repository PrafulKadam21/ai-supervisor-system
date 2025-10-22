from typing import Optional
from datetime import datetime
from database.firebase_client import FirebaseClient
from database.models import HelpRequest, RequestStatus
from agent.knowledge_base import KnowledgeBase
from services.notification_service import NotificationService
from agent.prompts import build_escalation_message, build_followup_message


class HelpRequestService:
    """Service for managing help requests and their lifecycle"""
    
    def __init__(self, firebase_client: FirebaseClient, knowledge_base: KnowledgeBase, 
                 notification_service: NotificationService):
        self.db = firebase_client
        self.knowledge_base = knowledge_base
        self.notification_service = notification_service
    
    def create_request(self, caller_id: str, caller_phone: str, question: str, 
                      context: Optional[str] = None) -> str:
        """Create a new help request and notify supervisor"""
        
        # Create the help request
        help_request = HelpRequest(
            caller_id=caller_id,
            caller_phone=caller_phone,
            question=question,
            context=context,
            status=RequestStatus.PENDING
        )
        
        request_id = self.db.create_help_request(help_request)
        
        # Notify supervisor
        message = build_escalation_message(question, caller_phone)
        self.notification_service.notify_supervisor(message, request_id)
        
        print(f"\n{'='*60}")
        print(f"📞 HELP REQUEST CREATED")
        print(f"{'='*60}")
        print(f"Request ID: {request_id}")
        print(f"Caller: {caller_phone}")
        print(f"Question: {question}")
        print(f"{'='*60}\n")
        
        return request_id
    
    def resolve_request(self, request_id: str, answer: str, 
                       supervisor_name: str = "Supervisor") -> bool:
        """Resolve a help request with an answer"""
        
        # Get the request
        request = self.db.get_help_request(request_id)
        if not request:
            print(f"Error: Help request {request_id} not found")
            return False
        
        # Mark as resolved
        success = self.db.resolve_help_request(request_id, answer, supervisor_name)
        if not success:
            return False
        
        # Add to knowledge base
        self.knowledge_base.add_knowledge(
            question=request.question,
            answer=answer,
            help_request_id=request_id
        )
        
        # Send follow-up to caller
        followup_message = build_followup_message(request.question, answer)
        self.notification_service.send_to_caller(request.caller_phone, followup_message)
        
        print(f"\n{'='*60}")
        print(f"✅ HELP REQUEST RESOLVED")
        print(f"{'='*60}")
        print(f"Request ID: {request_id}")
        print(f"Question: {request.question}")
        print(f"Answer: {answer}")
        print(f"Resolved by: {supervisor_name}")
        print(f"{'='*60}\n")
        
        return True
    
    def get_pending_requests(self):
        """Get all pending help requests"""
        return self.db.get_pending_requests()
    
    def get_all_requests(self, limit: int = 50):
        """Get all help requests"""
        return self.db.get_all_requests(limit)
    
    def timeout_old_requests(self, hours: int = 24):
        """Mark old pending requests as timed out"""
        pending = self.get_pending_requests()
        now = datetime.utcnow()
        
        for request in pending:
            age_hours = (now - request.created_at).total_seconds() / 3600
            if age_hours > hours:
                self.db.timeout_help_request(request.id)
                print(f"⏱️  Timed out request {request.id} (age: {age_hours:.1f}h)")
    
    def get_stats(self) -> dict:
        """Get statistics about help requests"""
        all_requests = self.get_all_requests(limit=1000)
        
        total = len(all_requests)
        pending = sum(1 for r in all_requests if r.status == RequestStatus.PENDING)
        resolved = sum(1 for r in all_requests if r.status == RequestStatus.RESOLVED)
        timeout = sum(1 for r in all_requests if r.status == RequestStatus.TIMEOUT)
        
        # Calculate average resolution time for resolved requests
        resolution_times = []
        for r in all_requests:
            if r.status == RequestStatus.RESOLVED and r.resolved_at:
                delta = (r.resolved_at - r.created_at).total_seconds() / 60
                resolution_times.append(delta)
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            "total_requests": total,
            "pending": pending,
            "resolved": resolved,
            "timeout": timeout,
            "avg_resolution_time_minutes": round(avg_resolution_time, 1),
            "resolution_rate": round(resolved / total * 100, 1) if total > 0 else 0
        }