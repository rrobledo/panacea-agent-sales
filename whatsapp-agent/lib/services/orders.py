import httpx
from typing import Optional, List, Dict, Any
from lib.config import ORDERS_API_URL


class OrdersService:
    """Service for interacting with external orders API"""

    def __init__(self):
        self.api_url = ORDERS_API_URL

    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create order in external system"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json=order_data,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_order_status(self, external_order_id: str) -> Optional[Dict[str, Any]]:
        """Get order status from external system"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/{external_order_id}",
                timeout=30.0
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

    def format_order_for_api(
        self,
        customer_phone: str,
        customer_name: Optional[str],
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format order data for external API"""
        return {
            "cliente": {
                "telefono": customer_phone,
                "nombre": customer_name or "Cliente"
            },
            "items": [
                {
                    "producto": item.get("product_name"),
                    "cantidad": item.get("quantity"),
                    "precio_unitario": float(item.get("unit_price", 0)),
                    "subtotal": float(item.get("subtotal", 0))
                }
                for item in items
            ],
            "total": sum(float(item.get("subtotal", 0)) for item in items)
        }
