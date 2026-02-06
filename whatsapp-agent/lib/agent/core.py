"""Core agent logic"""

from lib.db.queries import CustomerQueries
from lib.services.claude import ClaudeService
from lib.services.whatsapp import WhatsAppService
from lib.agent.prompts import get_personalized_prompt
from lib.agent.tools import TOOLS, ToolExecutor
from lib.agent.memory import ConversationMemory


def log(message: str):
    """Print log with prefix"""
    print(f"[CORE] {message}")


async def process_message(phone_number: str, message_text: str, message_id: str) -> str:
    """
    Process incoming WhatsApp message and return response.

    Args:
        phone_number: Customer's phone number
        message_text: The message content
        message_id: WhatsApp message ID

    Returns:
        Response text to send back
    """
    log(f"=== Processing message from {phone_number} ===")
    log(f"Message: {message_text[:100]}...")

    # Initialize services
    log("Initializing ClaudeService...")
    claude_service = ClaudeService()
    log("Initializing WhatsAppService...")
    whatsapp_service = WhatsAppService()

    # Mark message as read
    try:
        log("Marking message as read...")
        await whatsapp_service.mark_as_read(message_id)
        log("Message marked as read")
    except Exception as e:
        log(f"Failed to mark as read (non-critical): {e}")

    # Get or create customer
    log("Getting/creating customer...")
    customer = await CustomerQueries.get_or_create(phone_number)
    log(f"Customer ID: {customer.id}, Name: {customer.name}")

    # Initialize memory
    log("Initializing conversation memory...")
    memory = ConversationMemory(customer.id)

    # Add user message to history
    log("Adding user message to history...")
    await memory.add_user_message(message_text)

    # Get conversation history
    log("Getting conversation history...")
    messages = await memory.get_messages(limit=10)
    log(f"History messages count: {len(messages)}")

    # Build personalized prompt
    log("Building personalized prompt...")
    system_prompt = get_personalized_prompt(
        customer_name=customer.name,
        preferences=customer.preferences
    )

    # Initialize tool executor
    log("Initializing tool executor...")
    tool_executor = ToolExecutor(customer.id, phone_number)

    # Get response from Claude
    log("Calling Claude API...")
    response = await claude_service.chat_with_tools(
        messages=messages,
        system_prompt=system_prompt,
        tools=TOOLS,
        tool_executor=lambda name, input: tool_executor.execute(name, input)
    )
    log(f"Claude response: {response[:100]}...")

    # Save assistant response
    log("Saving assistant response to memory...")
    await memory.add_assistant_message(response)

    log("=== Message processing complete ===")
    return response


async def send_response(phone_number: str, response_text: str) -> bool:
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
                await whatsapp_service.send_message(phone_number, chunk)
        else:
            await whatsapp_service.send_message(phone_number, response_text)
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False
