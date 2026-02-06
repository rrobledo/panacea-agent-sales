"""Conversation memory management"""

from typing import List, Dict, Any
from uuid import UUID
from lib.db.queries import ConversationQueries


class ConversationMemory:
    """Manages conversation history and context"""

    def __init__(self, customer_id: UUID):
        self.customer_id = customer_id
        self._conversation = None

    async def get_conversation(self) -> Dict[str, Any]:
        """Get or create conversation"""
        if self._conversation is None:
            self._conversation = await ConversationQueries.get_or_create(self.customer_id)
        return self._conversation

    async def get_messages(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent messages formatted for Claude"""
        messages = await ConversationQueries.get_recent_messages(self.customer_id, limit)
        return messages

    async def add_user_message(self, content: str) -> None:
        """Add user message to conversation"""
        conversation = await self.get_conversation()
        await ConversationQueries.add_message(
            UUID(str(conversation["id"])),
            "user",
            content
        )

    async def add_assistant_message(self, content: str) -> None:
        """Add assistant message to conversation"""
        conversation = await self.get_conversation()
        await ConversationQueries.add_message(
            UUID(str(conversation["id"])),
            "assistant",
            content
        )

    async def get_summary(self) -> str:
        """Get conversation summary if available"""
        conversation = await self.get_conversation()
        return conversation.get("summary", "")

    async def update_summary(self, summary: str) -> None:
        """Update conversation summary"""
        conversation = await self.get_conversation()
        await ConversationQueries.update_summary(
            UUID(str(conversation["id"])),
            summary
        )
