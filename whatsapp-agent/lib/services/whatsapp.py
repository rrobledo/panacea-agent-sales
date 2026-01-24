import httpx
import hashlib
import hmac
from typing import Optional
from lib.config import (
    WHATSAPP_ACCESS_TOKEN,
    WHATSAPP_PHONE_NUMBER_ID,
    WHATSAPP_API_URL,
    WHATSAPP_VERIFY_TOKEN,
)


def log(message: str):
    """Print log with prefix"""
    print(f"[WHATSAPP] {message}")


class WhatsAppService:
    """Service for interacting with Meta WhatsApp Business API"""

    def __init__(self):
        self.api_url = WHATSAPP_API_URL
        self.phone_number_id = WHATSAPP_PHONE_NUMBER_ID
        self.access_token = WHATSAPP_ACCESS_TOKEN
        self.verify_token = WHATSAPP_VERIFY_TOKEN
        log(f"Initialized - API URL: {self.api_url}")
        log(f"Phone Number ID: {self.phone_number_id}")
        log(f"Access Token: {self.access_token[:20] if self.access_token else 'MISSING'}...")
        log(f"Verify Token: {self.verify_token[:10] if self.verify_token else 'MISSING'}...")

    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify webhook subscription from Meta"""
        log(f"verify_webhook: mode={mode}, token_match={token == self.verify_token}")
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook payload signature"""
        if not signature.startswith("sha256="):
            return False

        expected_signature = hmac.new(
            self.access_token.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature[7:], expected_signature)

    def send_message(self, to: str, text: str) -> dict:
        """Send text message to WhatsApp number"""
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        log(f"send_message to {to}, text length: {len(text)}")
        log(f"URL: {url}")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }

        with httpx.Client() as client:
            log("Sending HTTP POST...")
            response = client.post(url, json=payload, headers=headers)
            log(f"Response status: {response.status_code}")
            if response.status_code != 200:
                log(f"Response body: {response.text}")
            response.raise_for_status()
            return response.json()

    def send_interactive_buttons(
        self,
        to: str,
        body_text: str,
        buttons: list[dict]
    ) -> dict:
        """Send interactive message with buttons"""
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        # Format buttons (max 3)
        formatted_buttons = [
            {
                "type": "reply",
                "reply": {
                    "id": btn.get("id", str(i)),
                    "title": btn["title"][:20]  # Max 20 chars
                }
            }
            for i, btn in enumerate(buttons[:3])
        ]

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": formatted_buttons}
            }
        }

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    def send_interactive_list(
        self,
        to: str,
        body_text: str,
        button_text: str,
        sections: list[dict]
    ) -> dict:
        """Send interactive message with list"""
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": body_text},
                "action": {
                    "button": button_text[:20],
                    "sections": sections
                }
            }
        }

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    def mark_as_read(self, message_id: str) -> dict:
        """Mark message as read"""
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        log(f"mark_as_read: {message_id}")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers)
            log(f"mark_as_read response: {response.status_code}")
            response.raise_for_status()
            return response.json()
