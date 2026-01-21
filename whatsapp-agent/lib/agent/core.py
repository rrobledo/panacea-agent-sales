"""Core agent logic"""

from typing import Optional
from uuid import UUID
from lib.db.queries import CustomerQueries
from lib.services.claude import ClaudeService
from lib.services.whatsapp import WhatsAppService
from lib.agent.prompts import get_personalized_prompt
from lib.agent.tools import TOOLS, ToolExecutor
from lib.agent.memory import ConversationMemory


def process_message(phone_number: str, message_text: str, message_id: str) -> str:
    """
    Process incoming WhatsApp message and return response.

    Args:
        phone_number: Customer's phone number
        message_text: The message content
        message_id: WhatsApp message ID

    Returns:
        Response text to send back
    """
    # Initialize services
    claude_service = ClaudeService()
    whatsapp_service = WhatsAppService()

    # Mark message as read
    try:
        whatsapp_service.mark_as_read(message_id)
    except Exception:
        pass  # Non-critical

    # Get or create customer
    customer = CustomerQueries.get_or_create(phone_number)

    # Initialize memory
    memory = ConversationMemory(customer.id)

    # Add user message to history
    memory.add_user_message(message_text)

    # Get conversation history
    messages = memory.get_messages(limit=10)

    # Build personalized prompt
    system_prompt = get_personalized_prompt(
        customer_name=customer.name,
        preferences=customer.preferences
    )

    # Initialize tool executor
    tool_executor = ToolExecutor(customer.id, phone_number)

    # Get response from Claude
    response = claude_service.chat_with_tools(
        messages=messages,
        system_prompt=system_prompt,
        tools=TOOLS,
        tool_executor=lambda name, input: tool_executor.execute(name, input)
    )

    # Save assistant response
    memory.add_assistant_message(response)

    return response


def send_response(phone_number: str, response_text: str) -> bool:
    """
    Send response back via WhatsApp.

    Args:
        phone_number: Customer's phone number
        response_text: Text to send

    Returns:
        True if successful
    """
    whatsapp_service = WhatsAppService()

    try:
        # WhatsApp has a 4096 character limit
        if len(response_text) > 4000:
            # Split into multiple messages
            chunks = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for chunk in chunks:
                whatsapp_service.send_message(phone_number, chunk)
        else:
            whatsapp_service.send_message(phone_number, response_text)
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False
