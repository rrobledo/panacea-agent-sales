"""Conversation memory management"""

from typing import List, Dict, Any
from uuid import UUID
from lib.db.queries import ConversationQueries


class ConversationMemory:
    """Manages conversation history and context"""

    def __init__(self, customer_id: UUID):
        self.customer_id = customer_id
        self._conversation = None

    @property
    def conversation(self) -> Dict[str, Any]:
        """Get or create conversation"""
        if self._conversation is None:
            self._conversation = ConversationQueries.get_or_create(self.customer_id)
        return self._conversation

    def get_messages(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent messages formatted for Claude"""
        messages = ConversationQueries.get_recent_messages(self.customer_id, limit)
        return messages

    def add_user_message(self, content: str) -> None:
        """Add user message to conversation"""
        ConversationQueries.add_message(
            UUID(str(self.conversation["id"])),
            "user",
            content
        )

    def add_assistant_message(self, content: str) -> None:
        """Add assistant message to conversation"""
        ConversationQueries.add_message(
            UUID(str(self.conversation["id"])),
            "assistant",
            content
        )

    def get_summary(self) -> str:
        """Get conversation summary if available"""
        return self.conversation.get("summary", "")

    def update_summary(self, summary: str) -> None:
        """Update conversation summary"""
        ConversationQueries.update_summary(
            UUID(str(self.conversation["id"])),
            summary
        )
