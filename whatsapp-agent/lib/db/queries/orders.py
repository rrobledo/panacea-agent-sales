from typing import Optional, List
from uuid import UUID
from decimal import Decimal
import json
from lib.db.connection import execute_query, execute_write
from lib.schemas.order import Order, OrderItem


class OrderQueries:
    """Order database operations"""

    @staticmethod
    async def create(customer_id: UUID, items: List[OrderItem], total: Decimal) -> Order:
        """Create new order"""
        items_json = [item.model_dump(mode="json") for item in items]
        result = await execute_write(
            """
            INSERT INTO orders (customer_id, items, total, status)
            VALUES ($1, $2, $3, 'pending')
            RETURNING *
            """,
            (str(customer_id), json.dumps(items_json), float(total))
        )
        result["items"] = items
        return Order(**result)

    @staticmethod
    async def get_by_id(order_id: UUID) -> Optional[Order]:
        """Get order by ID"""
        result = await execute_query(
            "SELECT * FROM orders WHERE id = $1",
            (str(order_id),),
            fetch_one=True
        )
        if result:
            result["items"] = [OrderItem(**item) for item in result["items"]]
            return Order(**result)
        return None

    @staticmethod
    async def get_pending_by_customer(customer_id: UUID) -> Optional[Order]:
        """Get pending order for customer"""
        result = await execute_query(
            """
            SELECT * FROM orders
            WHERE customer_id = $1 AND status = 'pending'
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (str(customer_id),),
            fetch_one=True
        )
        if result:
            result["items"] = [OrderItem(**item) for item in result["items"]]
            return Order(**result)
        return None

    @staticmethod
    async def confirm(order_id: UUID, external_order_id: str) -> Order:
        """Confirm order and set external ID"""
        result = await execute_write(
            """
            UPDATE orders
            SET status = 'confirmed', external_order_id = $1
            WHERE id = $2
            RETURNING *
            """,
            (external_order_id, str(order_id))
        )
        result["items"] = [OrderItem(**item) for item in result["items"]]
        return Order(**result)

    @staticmethod
    async def cancel(order_id: UUID) -> Order:
        """Cancel order"""
        result = await execute_write(
            """
            UPDATE orders
            SET status = 'cancelled'
            WHERE id = $1
            RETURNING *
            """,
            (str(order_id),)
        )
        result["items"] = [OrderItem(**item) for item in result["items"]]
        return Order(**result)

    @staticmethod
    async def get_customer_orders(customer_id: UUID, limit: int = 5) -> List[Order]:
        """Get recent orders for customer"""
        results = await execute_query(
            """
            SELECT * FROM orders
            WHERE customer_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            (str(customer_id), limit)
        )
        orders = []
        for r in results:
            r["items"] = [OrderItem(**item) for item in r["items"]]
            orders.append(Order(**r))
        return orders
