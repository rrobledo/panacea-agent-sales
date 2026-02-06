"""FastAPI application for WhatsApp webhook — deployed on Vercel."""

import sys
import os
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, BackgroundTasks, Query, Request
from fastapi.responses import PlainTextResponse, JSONResponse

from lib.services.whatsapp import WhatsAppService
from lib.schemas.whatsapp import WhatsAppWebhookPayload
from lib.agent.core import process_message, send_response


def log(message: str):
    """Print log with prefix for easy identification"""
    print(f"[WEBHOOK] {message}")


app = FastAPI(title="Panacea WhatsApp Agent")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "whatsapp-agent"}


# ---------------------------------------------------------------------------
# Webhook verification (GET)
# ---------------------------------------------------------------------------
@app.get("/api/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    log("=== GET Request received ===")
    log(f"Mode: {hub_mode}, Token: {hub_verify_token[:10] if hub_verify_token else 'None'}... Challenge: {hub_challenge}")

    whatsapp = WhatsAppService()
    result = whatsapp.verify_webhook(hub_mode, hub_verify_token, hub_challenge)

    if result:
        log("Verification SUCCESS")
        return PlainTextResponse(content=result)

    log("Verification FAILED")
    return PlainTextResponse(content="Forbidden", status_code=403)


# ---------------------------------------------------------------------------
# Incoming messages (POST)
# ---------------------------------------------------------------------------
async def handle_incoming_message(phone_number: str, message_text: str, message_id: str):
    """Background task: process message and send response."""
    try:
        response_text = await process_message(
            phone_number=phone_number,
            message_text=message_text,
            message_id=message_id,
        )
        log(f"Response generated: {response_text[:100]}...")

        await send_response(phone_number, response_text)
        log("Response sent successfully")
    except Exception as e:
        log(f"EXCEPTION in background task: {type(e).__name__}: {e}")
        log(f"Traceback: {traceback.format_exc()}")


@app.post("/api/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    log("=== POST Request received ===")

    try:
        body = await request.body()
        data = await request.json()
        log(f"Body length: {len(body)}")
        log(f"Parsed JSON keys: {list(data.keys())}")

        value = data["entry"][0]["changes"][0]["value"]
        if "messages" in value:
            log("Incoming USER message detected")
        if "statuses" in value:
            log("Status update received")

        payload = WhatsAppWebhookPayload(**data)
        log("Payload parsed successfully")

        messages = payload.get_messages()
        log(f"Messages found: {len(messages)}")

        for i, msg in enumerate(messages):
            log(f"Message {i+1}: type={msg.type}, from={msg.from_number}, text={msg.text[:50] if msg.text else 'None'}...")

            if msg.text and msg.type == "text":
                log(f"Dispatching background task for {msg.from_number}")
                background_tasks.add_task(
                    handle_incoming_message,
                    phone_number=msg.from_number,
                    message_text=msg.text,
                    message_id=msg.message_id,
                )
            else:
                log(f"Skipping message: type={msg.type}, has_text={bool(msg.text)}")

        return JSONResponse(content={"status": "ok"})

    except Exception as e:
        log(f"EXCEPTION: {type(e).__name__}: {e}")
        log(f"Traceback: {traceback.format_exc()}")
        # Still return 200 to prevent Meta from retrying
        return JSONResponse(content={"status": "error", "message": str(e)})

