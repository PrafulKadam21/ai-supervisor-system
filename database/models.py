from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class RequestStatus(str, Enum):
    """Status lifecycle for help requests"""
    PENDING = "pending"
    RESOLVED = "resolved"
    TIMEOUT = "timeout"


class HelpRequest(BaseModel):
    """Model for help requests from AI to supervisor"""
    id: Optional[str] = None
    caller_id: str = Field(..., description="Unique identifier for the caller")
    caller_phone: str = Field(..., description="Phone number of the caller")
    question: str = Field(..., description="Question the AI couldn't answer")
    context: Optional[str] = Field(None, description="Additional conversation context")
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    supervisor_answer: Optional[str] = None
    supervisor_name: Optional[str] = None
    
    class Config:
        use_enum_values = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firebase"""
        data = self.model_dump()
        data['created_at'] = self.created_at.isoformat()
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HelpRequest':
        """Create from Firebase dictionary"""
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('resolved_at') and isinstance(data['resolved_at'], str):
            data['resolved_at'] = datetime.fromisoformat(data['resolved_at'])
        return cls(**data)


class KnowledgeEntry(BaseModel):
    """Model for learned knowledge base entries"""
    id: Optional[str] = None
    question: str = Field(..., description="Original question or topic")
    answer: str = Field(..., description="Learned answer")
    source: str = Field(default="supervisor", description="How this was learned")
    help_request_id: Optional[str] = Field(None, description="Link to original help request")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    usage_count: int = Field(default=0, description="Times this answer was used")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firebase"""
        data = self.model_dump()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeEntry':
        """Create from Firebase dictionary"""
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class CallLog(BaseModel):
    """Model for tracking calls and interactions"""
    id: Optional[str] = None
    caller_id: str
    caller_phone: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    transcript: Optional[str] = None
    help_requests: list[str] = Field(default_factory=list, description="IDs of help requests during call")
    resolved_by_ai: bool = Field(default=True, description="Whether AI handled the call")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firebase"""
        data = self.model_dump()
        data['started_at'] = self.started_at.isoformat()
        if self.ended_at:
            data['ended_at'] = self.ended_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CallLog':
        """Create from Firebase dictionary"""
        if isinstance(data.get('started_at'), str):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('ended_at') and isinstance(data['ended_at'], str):
            data['ended_at'] = datetime.fromisoformat(data['ended_at'])
        return cls(**data)