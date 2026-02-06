from typing import Optional, Dict, Any
from uuid import UUID
import json
from lib.db.connection import execute_query, execute_write
from lib.schemas.customer import Customer


class CustomerQueries:
    """Customer database operations"""

    @staticmethod
    async def get_by_phone(phone_number: str) -> Optional[Customer]:
        """Get customer by phone number"""
        result = await execute_query(
            "SELECT * FROM customers WHERE phone_number = $1",
            (phone_number,),
            fetch_one=True
        )
        if result:
            return Customer(**result)
        return None

    @staticmethod
    async def get_by_id(customer_id: UUID) -> Optional[Customer]:
        """Get customer by ID"""
        result = await execute_query(
            "SELECT * FROM customers WHERE id = $1",
            (str(customer_id),),
            fetch_one=True
        )
        if result:
            return Customer(**result)
        return None

    @staticmethod
    async def create(phone_number: str, name: Optional[str] = None) -> Customer:
        """Create new customer"""
        result = await execute_write(
            """
            INSERT INTO customers (phone_number, name, preferences)
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            (phone_number, name, json.dumps({}))
        )
        return Customer(**result)

    @staticmethod
    async def update_preferences(customer_id: UUID, preferences: Dict[str, Any]) -> Customer:
        """Update customer preferences"""
        result = await execute_write(
            """
            UPDATE customers
            SET preferences = $1, updated_at = NOW()
            WHERE id = $2
            RETURNING *
            """,
            (json.dumps(preferences), str(customer_id))
        )
        return Customer(**result)

    @staticmethod
    async def update_name(customer_id: UUID, name: str) -> Customer:
        """Update customer name"""
        result = await execute_write(
            """
            UPDATE customers
            SET name = $1, updated_at = NOW()
            WHERE id = $2
            RETURNING *
            """,
            (name, str(customer_id))
        )
        return Customer(**result)

    @staticmethod
    async def get_or_create(phone_number: str) -> Customer:
        """Get existing customer or create new one"""
        customer = await CustomerQueries.get_by_phone(phone_number)
        if customer:
            return customer
        return await CustomerQueries.create(phone_number)
