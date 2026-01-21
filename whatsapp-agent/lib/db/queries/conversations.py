from typing import Optional, List, Dict, Any
from uuid import UUID
import json
from lib.db.connection import execute_query, execute_write


class ConversationQueries:
    """Conversation database operations"""

    @staticmethod
    def get_by_customer(customer_id: UUID) -> Optional[Dict[str, Any]]:
        """Get conversation by customer ID"""
        result = execute_query(
            """
            SELECT * FROM conversations
            WHERE customer_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (str(customer_id),),
            fetch_one=True
        )
        return dict(result) if result else None

    @staticmethod
    def create(customer_id: UUID) -> Dict[str, Any]:
        """Create new conversation"""
        result = execute_write(
            """
            INSERT INTO conversations (customer_id, messages, summary)
            VALUES (%s, %s, NULL)
            RETURNING *
            """,
            (str(customer_id), json.dumps([]))
        )
        return dict(result)

    @staticmethod
    def add_message(conversation_id: UUID, role: str, content: str) -> Dict[str, Any]:
        """Add message to conversation"""
        # Get current messages
        current = execute_query(
            "SELECT messages FROM conversations WHERE id = %s",
            (str(conversation_id),),
            fetch_one=True
        )

        messages = current["messages"] if current else []
        messages.append({"role": role, "content": content})

        # Keep only last 20 messages to manage context window
        if len(messages) > 20:
            messages = messages[-20:]

        result = execute_write(
            """
            UPDATE conversations
            SET messages = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING *
            """,
            (json.dumps(messages), str(conversation_id))
        )
        return dict(result)

    @staticmethod
    def get_recent_messages(customer_id: UUID, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent messages for a customer"""
        conversation = ConversationQueries.get_by_customer(customer_id)
        if not conversation:
            return []

        messages = conversation.get("messages", [])
        return messages[-limit:] if messages else []

    @staticmethod
    def update_summary(conversation_id: UUID, summary: str) -> Dict[str, Any]:
        """Update conversation summary"""
        result = execute_write(
            """
            UPDATE conversations
            SET summary = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING *
            """,
            (summary, str(conversation_id))
        )
        return dict(result)

    @staticmethod
    def get_or_create(customer_id: UUID) -> Dict[str, Any]:
        """Get existing conversation or create new one"""
        conversation = ConversationQueries.get_by_customer(customer_id)
        if conversation:
            return conversation
        return ConversationQueries.create(customer_id)
