"""
Conversation service for managing chat history and messages.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select
from database.models import Conversation, Message, User
from database.connection import get_db_session


class ConversationService:
    """Service for managing conversations and messages."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _parse_uuid(self, uuid_str: Union[str, uuid.UUID]) -> uuid.UUID:
        """Convert string UUID to UUID object if needed."""
        if isinstance(uuid_str, str):
            return uuid.UUID(uuid_str)
        return uuid_str
    
    async def create_conversation(
        self, 
        user_id: int, 
        title: Optional[str] = None,
        model_used: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new conversation."""
        conversation = Conversation(
            user_id=user_id,
            title=title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            model_used=model_used
        )
        
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        
        return self._conversation_to_dict(conversation, message_count=0)
    
    async def get_conversation(
        self, 
        conversation_id: str, 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get a specific conversation with its messages."""
        query = select(Conversation).where(
            Conversation.id == self._parse_uuid(conversation_id),
            Conversation.user_id == user_id
        )
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            return None
        
        # Get message count
        count_query = select(func.count(Message.id)).where(
            Message.conversation_id == self._parse_uuid(conversation_id)
        )
        count_result = await self.db.execute(count_query)
        message_count = count_result.scalar() or 0
        
        # Get messages
        messages_query = select(Message).where(
            Message.conversation_id == self._parse_uuid(conversation_id)
        ).order_by(Message.created_at)
        messages_result = await self.db.execute(messages_query)
        messages = messages_result.scalars().all()
        
        # Create response
        result_dict = self._conversation_to_dict(conversation, include_messages=False, message_count=message_count)
        result_dict["messages"] = [self._message_to_dict(msg) for msg in messages]
        
        return result_dict
    
    async def get_user_conversations(
        self, 
        user_id: int, 
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a user."""
        query = select(
            Conversation,
            func.count(Message.id).label('message_count')
        ).outerjoin(Message).where(
            Conversation.user_id == user_id
        ).group_by(Conversation.id).order_by(
            desc(Conversation.updated_at)
        ).offset(offset).limit(limit)
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            self._conversation_to_dict(row[0], message_count=row[1] or 0) 
            for row in rows
        ]
    
    async def update_conversation(
        self, 
        conversation_id: str, 
        user_id: int,
        title: Optional[str] = None,
        model_used: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update conversation details."""
        query = select(Conversation).where(
            Conversation.id == self._parse_uuid(conversation_id),
            Conversation.user_id == user_id
        )
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            return None
        
        if title is not None:
            conversation.title = title
        if model_used is not None:
            conversation.model_used = model_used
        
        conversation.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(conversation)
        
        # Get message count
        count_query = select(func.count(Message.id)).where(
            Message.conversation_id == self._parse_uuid(conversation_id)
        )
        count_result = await self.db.execute(count_query)
        message_count = count_result.scalar() or 0
        
        return self._conversation_to_dict(conversation, message_count=message_count)
    
    async def delete_conversation(
        self, 
        conversation_id: str, 
        user_id: int
    ) -> bool:
        """Delete a conversation and all its messages."""
        query = select(Conversation).where(
            Conversation.id == self._parse_uuid(conversation_id),
            Conversation.user_id == user_id
        )
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            return False
        
        await self.db.delete(conversation)
        await self.db.commit()
        return True
    
    async def add_message(
        self, 
        conversation_id: str,
        user_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Add a message to a conversation."""
        # Verify conversation belongs to user
        query = select(Conversation).where(
            Conversation.id == self._parse_uuid(conversation_id),
            Conversation.user_id == user_id
        )
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            return None
        
        message = Message(
            conversation_id=self._parse_uuid(conversation_id),
            role=role,
            content=content,
            message_metadata=metadata or {}
        )
        
        self.db.add(message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(message)
        
        return self._message_to_dict(message)
    
    async def get_conversation_messages(
        self, 
        conversation_id: str,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get messages from a conversation."""
        # Verify conversation belongs to user
        query = select(Conversation).where(
            Conversation.id == self._parse_uuid(conversation_id),
            Conversation.user_id == user_id
        )
        result = await self.db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            return []
        
        query = select(Message).where(
            Message.conversation_id == self._parse_uuid(conversation_id)
        ).order_by(
            Message.created_at
        ).offset(offset).limit(limit)
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        return [self._message_to_dict(msg) for msg in messages]
    
    async def search_conversations(
        self, 
        user_id: int,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search conversations by title or message content."""
        # Search in conversation titles
        title_query = select(
            Conversation,
            func.count(Message.id).label('message_count')
        ).outerjoin(Message).where(
            Conversation.user_id == user_id,
            Conversation.title.ilike(f"%{query}%")
        ).group_by(Conversation.id).order_by(desc(Conversation.updated_at)).limit(limit)
        title_result = await self.db.execute(title_query)
        title_matches = title_result.all()
        
        # Search in message content
        content_query = select(
            Conversation,
            func.count(Message.id).label('message_count')
        ).join(Message).where(
            Conversation.user_id == user_id,
            Message.content.ilike(f"%{query}%")
        ).group_by(Conversation.id).order_by(desc(Conversation.updated_at)).limit(limit)
        content_result = await self.db.execute(content_query)
        content_matches = content_result.all()
        
        # Combine and deduplicate results
        all_conversations = {}
        for row in title_matches + content_matches:
            conv_id = row[0].id
            if conv_id not in all_conversations:
                all_conversations[conv_id] = (row[0], row[1] or 0)
        
        return [
            self._conversation_to_dict(conv, message_count=count) 
            for conv, count in all_conversations.values()
        ]
    
    async def get_conversation_stats(self, user_id: int) -> Dict[str, Any]:
        """Get conversation statistics for a user."""
        # Count total conversations
        total_query = select(func.count(Conversation.id)).where(
            Conversation.user_id == user_id
        )
        total_result = await self.db.execute(total_query)
        total_conversations = total_result.scalar()
        
        # Count total messages
        messages_query = select(func.count(Message.id)).join(Conversation).where(
            Conversation.user_id == user_id
        )
        messages_result = await self.db.execute(messages_query)
        total_messages = messages_result.scalar()
        
        # Count recent conversations
        recent_query = select(func.count(Conversation.id)).where(
            Conversation.user_id == user_id,
            Conversation.created_at >= datetime.utcnow().replace(day=1)  # This month
        )
        recent_result = await self.db.execute(recent_query)
        recent_conversations = recent_result.scalar()
        
        return {
            "total_conversations": total_conversations or 0,
            "total_messages": total_messages or 0,
            "recent_conversations": recent_conversations or 0
        }
    
    def _conversation_to_dict(
        self, 
        conversation: Conversation, 
        include_messages: bool = False,
        message_count: int = 0
    ) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        result = {
            "id": str(conversation.id),
            "user_id": conversation.user_id,
            "title": conversation.title,
            "model_used": conversation.model_used,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "message_count": message_count
        }
        
        if include_messages:
            # Only include messages if they're already loaded
            try:
                messages = conversation.messages
                if messages:
                    result["messages"] = [
                        self._message_to_dict(msg) for msg in 
                        sorted(messages, key=lambda x: x.created_at)
                    ]
                else:
                    result["messages"] = []
            except:
                # If messages aren't loaded, return empty list
                result["messages"] = []
        
        return result
    
    def _message_to_dict(self, message: Message) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "role": message.role,
            "content": message.content,
            "metadata": message.message_metadata or {},
            "created_at": message.created_at.isoformat()
        }


async def get_conversation_service(db: AsyncSession = None) -> ConversationService:
    """Get conversation service instance."""
    if db is None:
        db = await get_db_session()
    return ConversationService(db)
