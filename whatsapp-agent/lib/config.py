import os
from typing import Optional

# Anthropic
ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")

# Meta WhatsApp
WHATSAPP_ACCESS_TOKEN: str = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID: str = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_VERIFY_TOKEN: str = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"

# Database
POSTGRES_URL: str = os.environ.get("POSTGRES_URL", "")

# External API
ORDERS_API_URL: str = os.environ.get("ORDERS_API_URL", "https://panacea-one.vercel.app/costos/remitos")
