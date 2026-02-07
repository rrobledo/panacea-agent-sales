from typing import Optional, List, Dict, Any
from uuid import UUID
import json
from lib.db.connection import execute_query, execute_write


def _ensure_list(messages) -> list:
    """Safely parse messages that may be a str (legacy double-encoded) or list."""
    if isinstance(messages, list):
        return messages
    if isinstance(messages, str):
        try:
            parsed = json.loads(messages)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
    return []


class ConversationQueries:
    """Conversation database operations"""

    @staticmethod
    async def get_by_customer(customer_id: UUID) -> Optional[Dict[str, Any]]:
        """Get conversation by customer ID"""
        result = await execute_query(
            """
            SELECT * FROM conversations
            WHERE customer_id = $1
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (str(customer_id),),
            fetch_one=True
        )
        return dict(result) if result else None

    @staticmethod
    async def create(customer_id: UUID) -> Dict[str, Any]:
        """Create new conversation"""
        result = await execute_write(
            """
            INSERT INTO conversations (customer_id, messages, summary)
            VALUES ($1, $2, NULL)
            RETURNING *
            """,
            (str(customer_id), [])
        )
        return dict(result)

    @staticmethod
    async def add_message(conversation_id: UUID, role: str, content: str) -> Dict[str, Any]:
        """Add message to conversation"""
        # Get current messages
        current = await execute_query(
            "SELECT messages FROM conversations WHERE id = $1",
            (str(conversation_id),),
            fetch_one=True
        )

        messages = _ensure_list(current["messages"]) if current else []
        messages.append({"role": role, "content": content})

        # Keep only last 20 messages to manage context window
        if len(messages) > 20:
            messages = messages[-20:]

        result = await execute_write(
            """
            UPDATE conversations
            SET messages = $1, updated_at = NOW()
            WHERE id = $2
            RETURNING *
            """,
            (messages, str(conversation_id))
        )
        return dict(result)

    @staticmethod
    async def get_recent_messages(customer_id: UUID, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent messages for a customer"""
        conversation = await ConversationQueries.get_by_customer(customer_id)
        if not conversation:
            return []

        messages = _ensure_list(conversation.get("messages", []))
        return messages[-limit:] if messages else []

    @staticmethod
    async def update_summary(conversation_id: UUID, summary: str) -> Dict[str, Any]:
        """Update conversation summary"""
        result = await execute_write(
            """
            UPDATE conversations
            SET summary = $1, updated_at = NOW()
            WHERE id = $2
            RETURNING *
            """,
            (summary, str(conversation_id))
        )
        return dict(result)

    @staticmethod
    async def get_or_create(customer_id: UUID) -> Dict[str, Any]:
        """Get existing conversation or create new one"""
        conversation = await ConversationQueries.get_by_customer(customer_id)
        if conversation:
            return conversation
        return await ConversationQueries.create(customer_id)
