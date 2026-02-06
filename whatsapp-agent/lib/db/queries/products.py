from typing import Optional, List
from uuid import UUID
from lib.db.connection import execute_query
from lib.schemas.product import Product, Category, Recipe


class ProductQueries:
    """Product database operations"""

    @staticmethod
    async def get_all_categories() -> List[Category]:
        """Get all product categories"""
        results = await execute_query(
            "SELECT * FROM categories ORDER BY display_order, name"
        )
        return [Category(**r) for r in results]

    @staticmethod
    async def get_products_by_category(category_id: UUID) -> List[Product]:
        """Get products by category"""
        results = await execute_query(
            """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = $1 AND p.available = true
            ORDER BY p.name
            """,
            (str(category_id),)
        )
        return [Product(**r) for r in results]

    @staticmethod
    async def get_all_products() -> List[Product]:
        """Get all available products"""
        results = await execute_query(
            """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.available = true
            ORDER BY c.display_order, c.name, p.name
            """
        )
        return [Product(**r) for r in results]

    @staticmethod
    async def get_product_by_id(product_id: UUID) -> Optional[Product]:
        """Get product by ID"""
        result = await execute_query(
            """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = $1
            """,
            (str(product_id),),
            fetch_one=True
        )
        if result:
            return Product(**result)
        return None

    @staticmethod
    async def get_product_by_name(name: str) -> Optional[Product]:
        """Get product by name (case insensitive)"""
        result = await execute_query(
            """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE LOWER(p.name) LIKE LOWER($1)
            """,
            (f"%{name}%",),
            fetch_one=True
        )
        if result:
            return Product(**result)
        return None

    @staticmethod
    async def search_products(query: str) -> List[Product]:
        """Search products by name or description"""
        results = await execute_query(
            """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.available = true
            AND (LOWER(p.name) LIKE LOWER($1) OR LOWER(p.description) LIKE LOWER($2))
            ORDER BY p.name
            """,
            (f"%{query}%", f"%{query}%")
        )
        return [Product(**r) for r in results]

    @staticmethod
    async def get_recipes_by_product(product_id: UUID) -> List[Recipe]:
        """Get recipes for a product"""
        results = await execute_query(
            """
            SELECT r.*, p.name as product_name
            FROM recipes r
            JOIN products p ON r.product_id = p.id
            WHERE r.product_id = $1
            """,
            (str(product_id),)
        )
        return [Recipe(**r) for r in results]

    @staticmethod
    async def get_all_recipes() -> List[Recipe]:
        """Get all recipes"""
        results = await execute_query(
            """
            SELECT r.*, p.name as product_name
            FROM recipes r
            JOIN products p ON r.product_id = p.id
            ORDER BY p.name, r.name
            """
        )
        return [Recipe(**r) for r in results]
