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


def log(message: str):
    """Print log with prefix for easy identification"""
    print(f"[WEBHOOK] {message}")


class handler(BaseHTTPRequestHandler):
    """Vercel serverless handler for WhatsApp webhook"""

    def do_GET(self):
        """Handle webhook verification from Meta"""
        log("=== GET Request received ===")

        # Parse query parameters
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        mode = params.get("hub.mode", [None])[0]
        token = params.get("hub.verify_token", [None])[0]
        challenge = params.get("hub.challenge", [None])[0]

        log(f"Mode: {mode}, Token: {token[:10]}... Challenge: {challenge}")

        whatsapp = WhatsAppService()
        result = whatsapp.verify_webhook(mode, token, challenge)

        if result:
            log("Verification SUCCESS")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(result.encode())
        else:
            log("Verification FAILED")
            self.send_response(403)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Forbidden")

    def do_POST(self):
        """Handle incoming WhatsApp messages"""
        log("=== POST Request received ===")

        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            log(f"Body length: {content_length}")
            log(f"Raw body: {body.decode()[:500]}")  # First 500 chars

            # Parse webhook payload
            data = json.loads(body)
            log(f"Parsed JSON keys: {list(data.keys())}")

            payload = WhatsAppWebhookPayload(**data)
            log("Payload parsed successfully")

            # Extract messages
            messages = payload.get_messages()
            log(f"Messages found: {len(messages)}")

            # Process each message
            for i, msg in enumerate(messages):
                log(f"Message {i+1}: type={msg.type}, from={msg.from_number}, text={msg.text[:50] if msg.text else 'None'}...")

                if msg.text and msg.type == "text":
                    log(f"Processing message from {msg.from_number}")

                    # Process message and get response
                    try:
                        response_text = process_message(
                            phone_number=msg.from_number,
                            message_text=msg.text,
                            message_id=msg.message_id
                        )
                        log(f"Response generated: {response_text[:100]}...")
                    except Exception as proc_err:
                        log(f"ERROR in process_message: {proc_err}")
                        raise

                    # Send response back
                    try:
                        send_response(msg.from_number, response_text)
                        log("Response sent successfully")
                    except Exception as send_err:
                        log(f"ERROR in send_response: {send_err}")
                        raise
                else:
                    log(f"Skipping message: type={msg.type}, has_text={bool(msg.text)}")

            # Always return 200 to acknowledge receipt
            log("Returning 200 OK")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())

        except Exception as e:
            log(f"EXCEPTION: {type(e).__name__}: {e}")
            import traceback
            log(f"Traceback: {traceback.format_exc()}")

            # Still return 200 to prevent Meta from retrying
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
