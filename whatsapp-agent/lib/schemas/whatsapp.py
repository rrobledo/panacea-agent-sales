from pydantic import BaseModel
from typing import Optional, List, Any


class WhatsAppMessage(BaseModel):
    """Incoming WhatsApp message"""
    from_number: str
    message_id: str
    timestamp: str
    text: Optional[str] = None
    type: str = "text"


class WhatsAppContact(BaseModel):
    """WhatsApp contact info"""
    wa_id: str
    profile: Optional[dict] = None


class WhatsAppWebhookMessage(BaseModel):
    """Message in webhook payload"""
    from_: str
    id: str
    timestamp: str
    text: Optional[dict] = None
    type: str

    class Config:
        populate_by_name = True

    def __init__(self, **data):
        if "from" in data:
            data["from_"] = data.pop("from")
        super().__init__(**data)


class WhatsAppWebhookValue(BaseModel):
    """Value object in webhook"""
    messaging_product: str
    metadata: dict
    contacts: Optional[List[dict]] = None
    messages: Optional[List[dict]] = None
    statuses: Optional[List[dict]] = None


class WhatsAppWebhookChange(BaseModel):
    """Change object in webhook"""
    field: str
    value: WhatsAppWebhookValue


class WhatsAppWebhookEntry(BaseModel):
    """Entry in webhook payload"""
    id: str
    changes: List[WhatsAppWebhookChange]


class WhatsAppWebhookPayload(BaseModel):
    """Full webhook payload from Meta"""
    object: str
    entry: List[WhatsAppWebhookEntry]

    def get_messages(self) -> List[WhatsAppMessage]:
        """Extract messages from webhook payload"""
        messages = []
        for entry in self.entry:
            for change in entry.changes:
                if change.value.messages:
                    for msg in change.value.messages:
                        messages.append(WhatsAppMessage(
                            from_number=msg.get("from", ""),
                            message_id=msg.get("id", ""),
                            timestamp=msg.get("timestamp", ""),
                            text=msg.get("text", {}).get("body") if msg.get("text") else None,
                            type=msg.get("type", "text")
                        ))
        return messages
