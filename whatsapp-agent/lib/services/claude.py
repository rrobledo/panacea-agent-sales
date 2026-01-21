import anthropic
from typing import List, Dict, Any, Optional
from lib.config import ANTHROPIC_API_KEY


class ClaudeService:
    """Service for interacting with Anthropic Claude API"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 1024
    ) -> anthropic.types.Message:
        """Send chat request to Claude"""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": messages,
        }

        if tools:
            kwargs["tools"] = tools

        return self.client.messages.create(**kwargs)

    def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: List[Dict[str, Any]],
        tool_executor: callable,
        max_iterations: int = 5
    ) -> str:
        """Chat with tool use, handling tool calls automatically"""
        current_messages = messages.copy()

        for _ in range(max_iterations):
            response = self.chat(
                messages=current_messages,
                system_prompt=system_prompt,
                tools=tools
            )

            # Check if we need to handle tool calls
            if response.stop_reason == "tool_use":
                # Add assistant response to messages
                current_messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Process each tool call
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = tool_executor(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result)
                        })

                # Add tool results to messages
                current_messages.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                # Extract final text response
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                return ""

        # Max iterations reached
        return "Lo siento, no pude completar tu solicitud. Por favor intenta de nuevo."

    def format_messages_for_claude(
        self,
        conversation_messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Format conversation messages for Claude API"""
        formatted = []
        for msg in conversation_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ["user", "assistant"]:
                formatted.append({"role": role, "content": content})
        return formatted
