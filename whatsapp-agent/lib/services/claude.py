import anthropic
from typing import List, Dict, Any, Optional
from lib.config import ANTHROPIC_API_KEY


def log(message: str):
    """Print log with prefix"""
    print(f"[CLAUDE] {message}")


class ClaudeService:
    """Service for interacting with Anthropic Claude API"""

    def __init__(self):
        log(f"Initializing with API key: {ANTHROPIC_API_KEY[:20] if ANTHROPIC_API_KEY else 'MISSING'}...")
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
        log(f"Using model: {self.model}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 1024
    ) -> anthropic.types.Message:
        """Send chat request to Claude"""
        log(f"chat() called with {len(messages)} messages, {len(tools) if tools else 0} tools")

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": messages,
        }

        if tools:
            kwargs["tools"] = tools

        log("Calling Anthropic API...")
        try:
            response = self.client.messages.create(**kwargs)
            log(f"API response: stop_reason={response.stop_reason}, content_blocks={len(response.content)}")
            return response
        except Exception as e:
            log(f"API ERROR: {type(e).__name__}: {e}")
            raise

    def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: List[Dict[str, Any]],
        tool_executor: callable,
        max_iterations: int = 5
    ) -> str:
        """Chat with tool use, handling tool calls automatically"""
        log(f"chat_with_tools() called, max_iterations={max_iterations}")
        current_messages = messages.copy()

        for iteration in range(max_iterations):
            log(f"Iteration {iteration + 1}/{max_iterations}")

            response = self.chat(
                messages=current_messages,
                system_prompt=system_prompt,
                tools=tools
            )

            # Check if we need to handle tool calls
            if response.stop_reason == "tool_use":
                log("Response requires tool use")

                # Add assistant response to messages
                current_messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Process each tool call
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        log(f"Executing tool: {block.name} with input: {block.input}")
                        try:
                            result = tool_executor(block.name, block.input)
                            log(f"Tool result: {str(result)[:100]}...")
                        except Exception as e:
                            log(f"Tool execution ERROR: {e}")
                            result = f"Error: {e}"

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
                log(f"Final response, stop_reason={response.stop_reason}")
                # Extract final text response
                for block in response.content:
                    if hasattr(block, "text"):
                        log(f"Extracted text: {block.text[:100]}...")
                        return block.text
                log("No text block found, returning empty")
                return ""

        # Max iterations reached
        log("Max iterations reached!")
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
