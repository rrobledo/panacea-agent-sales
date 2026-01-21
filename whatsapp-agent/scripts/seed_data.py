"""Seed database with sample products and recipes"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.db.connection import execute_write


def seed_categories():
    """Insert sample categories"""
    categories = [
        ("Panadería", "Panes frescos y productos horneados", 1),
        ("Pastelería", "Pasteles, tartas y postres", 2),
        ("Bebidas", "Bebidas calientes y frías", 3),
    ]

    for name, description, order in categories:
        execute_write(
            """
            INSERT INTO categories (name, description, display_order)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING id
            """,
            (name, description, order)
        )
    print("✓ Categorías insertadas")


def seed_products():
    """Insert sample products"""
    # Get category IDs
    from lib.db.connection import execute_query

    categories = execute_query("SELECT id, name FROM categories")
    cat_map = {c["name"]: c["id"] for c in categories}

    products = [
        # Panadería
        (cat_map.get("Panadería"), "Pan Francés", "Pan crujiente tradicional", 15.00),
        (cat_map.get("Panadería"), "Pan Integral", "Pan saludable con granos", 20.00),
        (cat_map.get("Panadería"), "Croissant", "Croissant de mantequilla", 25.00),

        # Pastelería
        (cat_map.get("Pastelería"), "Pastel de Chocolate", "Delicioso pastel de chocolate", 180.00),
        (cat_map.get("Pastelería"), "Tarta de Frutas", "Tarta con frutas frescas de temporada", 150.00),
        (cat_map.get("Pastelería"), "Cheesecake", "Cheesecake cremoso estilo New York", 160.00),

        # Bebidas
        (cat_map.get("Bebidas"), "Café Americano", "Café negro clásico", 35.00),
        (cat_map.get("Bebidas"), "Cappuccino", "Espresso con leche espumada", 45.00),
        (cat_map.get("Bebidas"), "Té Verde", "Té verde orgánico", 30.00),
    ]

    for cat_id, name, description, price in products:
        if cat_id:
            execute_write(
                """
                INSERT INTO products (category_id, name, description, price, available)
                VALUES (%s, %s, %s, %s, true)
                ON CONFLICT DO NOTHING
                RETURNING id
                """,
                (str(cat_id), name, description, price)
            )
    print("✓ Productos insertados")


def seed_recipes():
    """Insert sample recipes"""
    from lib.db.connection import execute_query

    products = execute_query("SELECT id, name FROM products")
    prod_map = {p["name"]: p["id"] for p in products}

    recipes = [
        (
            prod_map.get("Pan Francés"),
            "Pan Francés Clásico",
            [
                {"nombre": "Harina", "cantidad": "500g"},
                {"nombre": "Agua", "cantidad": "300ml"},
                {"nombre": "Levadura", "cantidad": "10g"},
                {"nombre": "Sal", "cantidad": "10g"},
            ],
            "1. Mezclar harina, levadura y sal. 2. Agregar agua gradualmente. 3. Amasar 10 minutos. 4. Dejar reposar 1 hora. 5. Hornear a 220°C por 25 minutos.",
            "Para una corteza más crujiente, coloca un recipiente con agua en el horno."
        ),
        (
            prod_map.get("Pastel de Chocolate"),
            "Pastel de Chocolate Esponjoso",
            [
                {"nombre": "Harina", "cantidad": "200g"},
                {"nombre": "Cacao en polvo", "cantidad": "50g"},
                {"nombre": "Azúcar", "cantidad": "200g"},
                {"nombre": "Huevos", "cantidad": "3 piezas"},
                {"nombre": "Mantequilla", "cantidad": "100g"},
                {"nombre": "Leche", "cantidad": "200ml"},
            ],
            "1. Precalentar horno a 180°C. 2. Mezclar ingredientes secos. 3. Batir huevos con azúcar. 4. Combinar todo y agregar mantequilla derretida. 5. Hornear 35 minutos.",
            "No abras el horno durante los primeros 25 minutos para que no se baje."
        ),
    ]

    for product_id, name, ingredients, instructions, tips in recipes:
        if product_id:
            execute_write(
                """
                INSERT INTO recipes (product_id, name, ingredients, instructions, tips)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id
                """,
                (str(product_id), name, json.dumps(ingredients), instructions, tips)
            )
    print("✓ Recetas insertadas")


def main():
    """Run all seeders"""
    print("Seeding database...")
    seed_categories()
    seed_products()
    seed_recipes()
    print("\n✅ Database seeded successfully!")


if __name__ == "__main__":
    main()
