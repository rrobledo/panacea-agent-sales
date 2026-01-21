"""WhatsApp webhook endpoint for Vercel serverless"""

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.services.whatsapp import WhatsAppService
from lib.schemas.whatsapp import WhatsAppWebhookPayload
from lib.agent.core import process_message, send_response


class handler(BaseHTTPRequestHandler):
    """Vercel serverless handler for WhatsApp webhook"""

    def do_GET(self):
        """Handle webhook verification from Meta"""
        # Parse query parameters
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        mode = params.get("hub.mode", [None])[0]
        token = params.get("hub.verify_token", [None])[0]
        challenge = params.get("hub.challenge", [None])[0]

        whatsapp = WhatsAppService()
        result = whatsapp.verify_webhook(mode, token, challenge)

        if result:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(result.encode())
        else:
            self.send_response(403)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Forbidden")

    def do_POST(self):
        """Handle incoming WhatsApp messages"""
        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            # Parse webhook payload
            data = json.loads(body)
            payload = WhatsAppWebhookPayload(**data)

            # Extract messages
            messages = payload.get_messages()

            # Process each message
            for msg in messages:
                if msg.text and msg.type == "text":
                    # Process message and get response
                    response_text = process_message(
                        phone_number=msg.from_number,
                        message_text=msg.text,
                        message_id=msg.message_id
                    )

                    # Send response back
                    send_response(msg.from_number, response_text)

            # Always return 200 to acknowledge receipt
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())

        except Exception as e:
            print(f"Webhook error: {e}")
            # Still return 200 to prevent Meta from retrying
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
