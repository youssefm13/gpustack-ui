"""
API routes for conversation management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from database.connection import get_database
from services.conversation_service import ConversationService
from middleware.auth_enhanced import get_current_user_enhanced
from database.models import User


router = APIRouter(prefix="/api/conversations", tags=["conversations"])


# Pydantic models for request/response
class ConversationCreate(BaseModel):
    title: Optional[str] = None
    model_used: Optional[str] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    model_used: Optional[str] = None


class MessageCreate(BaseModel):
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    id: str
    user_id: int
    title: str
    model_used: Optional[str]
    created_at: str
    updated_at: str
    message_count: int
    messages: Optional[List[Dict[str, Any]]] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    metadata: Dict[str, Any]
    created_at: str


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user_enhanced),
    db: AsyncSession = Depends(get_database)
):
    """Create a new conversation."""
    service = ConversationService(db)
    conversation = await service.create_conversation(
        user_id=current_user.id,
        title=data.title,
        model_used=data.model_used
    )
    return conversation


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user_enhanced),
    db: AsyncSession = Depends(get_database)
):
    """Get all conversations for the current user."""
    service = ConversationService(db)
    conversations = await service.get_user_conversations(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    return conversations


@router.get("/search", response_model=List[ConversationResponse])
async def search_conversations(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user_enhanced),
    db: AsyncSession = Depends(get_database)
):
    """Search conversations by title or content."""
    service = ConversationService(db)
    conversations = await service.search_conversations(
        user_id=current_user.id,
        query=q,
        limit=limit
    )
    return conversations


@router.get("/stats")
async def get_conversation_stats(
    current_user: User = Depends(get_current_user_enhanced),
    db: AsyncSession = Depends(get_database)
):
    """Get conversation statistics for the current user."""
    service = ConversationService(db)
    stats = await service.get_conversation_stats(user_id=current_user.id)
    return stats


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user_enhanced),
    db: AsyncSession = Depends(get_database)
):
    """Get a specific conversation with messages."""
    service = ConversationService(db)
    conversation = await service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    current_user: User = Depends(get_current_user_enhanced),
    db: AsyncSession = Depends(get_database)
):
    """Update a conversation."""
    service = ConversationService(db)
    conversation = await service.update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        title=data.title,
        model_used=data.model_used
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user_enhanced),
    db: AsyncSession = Depends(get_database)
):
    """Delete a conversation."""
    service = ConversationService(db)
    success = await service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"message": "Conversation deleted successfully"}


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user_enhanced),
    db: AsyncSession = Depends(get_database)
):
    """Add a message to a conversation."""
    service = ConversationService(db)
    message = await service.add_message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        role=data.role,
        content=data.content,
        metadata=data.metadata
    )
    
    if not message:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return message


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user_enhanced),
    db: AsyncSession = Depends(get_database)
):
    """Get messages from a conversation."""
    service = ConversationService(db)
    messages = await service.get_conversation_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return messages


@router.get("/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = Query("json", description="Export format: json or text"),
    current_user: User = Depends(get_current_user_enhanced),
    db: AsyncSession = Depends(get_database)
):
    """Export a conversation."""
    service = ConversationService(db)
    conversation = await service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if format == "json":
        return conversation
    elif format == "text":
        # Convert to readable text format
        text_content = f"Conversation: {conversation['title']}\n"
        text_content += f"Created: {conversation['created_at']}\n"
        text_content += f"Model: {conversation.get('model_used', 'Unknown')}\n\n"
        
        for message in conversation.get('messages', []):
            text_content += f"{message['role'].upper()}: {message['content']}\n\n"
        
        return {"content": text_content, "format": "text"}
    else:
        raise HTTPException(status_code=400, detail="Invalid export format")
