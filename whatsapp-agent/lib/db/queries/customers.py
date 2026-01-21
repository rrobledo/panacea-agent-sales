from typing import Optional, Dict, Any
from uuid import UUID
import json
from lib.db.connection import execute_query, execute_write
from lib.schemas.customer import Customer


class CustomerQueries:
    """Customer database operations"""

    @staticmethod
    def get_by_phone(phone_number: str) -> Optional[Customer]:
        """Get customer by phone number"""
        result = execute_query(
            "SELECT * FROM customers WHERE phone_number = %s",
            (phone_number,),
            fetch_one=True
        )
        if result:
            return Customer(**result)
        return None

    @staticmethod
    def get_by_id(customer_id: UUID) -> Optional[Customer]:
        """Get customer by ID"""
        result = execute_query(
            "SELECT * FROM customers WHERE id = %s",
            (str(customer_id),),
            fetch_one=True
        )
        if result:
            return Customer(**result)
        return None

    @staticmethod
    def create(phone_number: str, name: Optional[str] = None) -> Customer:
        """Create new customer"""
        result = execute_write(
            """
            INSERT INTO customers (phone_number, name, preferences)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (phone_number, name, json.dumps({}))
        )
        return Customer(**result)

    @staticmethod
    def update_preferences(customer_id: UUID, preferences: Dict[str, Any]) -> Customer:
        """Update customer preferences"""
        result = execute_write(
            """
            UPDATE customers
            SET preferences = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING *
            """,
            (json.dumps(preferences), str(customer_id))
        )
        return Customer(**result)

    @staticmethod
    def update_name(customer_id: UUID, name: str) -> Customer:
        """Update customer name"""
        result = execute_write(
            """
            UPDATE customers
            SET name = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING *
            """,
            (name, str(customer_id))
        )
        return Customer(**result)

    @staticmethod
    def get_or_create(phone_number: str) -> Customer:
        """Get existing customer or create new one"""
        customer = CustomerQueries.get_by_phone(phone_number)
        if customer:
            return customer
        return CustomerQueries.create(phone_number)
