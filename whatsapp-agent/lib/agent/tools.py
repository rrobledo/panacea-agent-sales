"""Tools available for the Claude agent"""

from typing import Any, Dict, List
from decimal import Decimal
from uuid import UUID
from lib.db.queries import ProductQueries, OrderQueries, CustomerQueries
from lib.services.orders import OrdersService
from lib.schemas.order import OrderItem
from lib.data.recipes import RecipesData


# Tool definitions for Claude
TOOLS = [
    {
        "name": "get_categories",
        "description": "Obtiene todas las categorías de productos disponibles",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_catalog",
        "description": "Obtiene el catálogo completo de productos con precios. Opcionalmente puede filtrar por categoría.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category_id": {
                    "type": "string",
                    "description": "ID de la categoría para filtrar (opcional)"
                }
            },
            "required": []
        }
    },
    {
        "name": "search_products",
        "description": "Busca productos por nombre o descripción",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Texto a buscar en productos"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "list_recipes",
        "description": "Lista todas las recetas disponibles de la panadería",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_recipe",
        "description": "Obtiene una receta específica por nombre o ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Nombre o número de la receta a buscar"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_recipes",
        "description": "Busca recetas por nombre o ingrediente",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Texto a buscar en recetas (nombre o ingrediente)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_order",
        "description": "Crea un nuevo pedido para el cliente. Devuelve un resumen para confirmar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "description": "Lista de productos a pedir",
                    "items": {
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "string",
                                "description": "ID del producto"
                            },
                            "quantity": {
                                "type": "integer",
                                "description": "Cantidad"
                            }
                        },
                        "required": ["product_id", "quantity"]
                    }
                }
            },
            "required": ["items"]
        }
    },
    {
        "name": "confirm_order",
        "description": "Confirma un pedido pendiente y lo envía al sistema",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "ID del pedido a confirmar"
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "cancel_order",
        "description": "Cancela un pedido pendiente",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "ID del pedido a cancelar"
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "get_customer_info",
        "description": "Obtiene información del cliente actual incluyendo historial de pedidos",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


class ToolExecutor:
    """Executes tools called by Claude"""

    def __init__(self, customer_id: UUID, customer_phone: str):
        self.customer_id = customer_id
        self.customer_phone = customer_phone
        self.orders_service = OrdersService()

    def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return result as string"""
        method = getattr(self, f"_tool_{tool_name}", None)
        if method:
            return method(tool_input)
        return f"Error: Herramienta '{tool_name}' no encontrada"

    def _tool_get_categories(self, input: Dict) -> str:
        """Get all categories"""
        categories = ProductQueries.get_all_categories()
        if not categories:
            return "No hay categorías disponibles"

        result = "Categorías disponibles:\n"
        for cat in categories:
            result += f"- {cat.name}"
            if cat.description:
                result += f": {cat.description}"
            result += f" (ID: {cat.id})\n"
        return result

    def _tool_get_catalog(self, input: Dict) -> str:
        """Get product catalog"""
        category_id = input.get("category_id")

        if category_id:
            products = ProductQueries.get_products_by_category(UUID(category_id))
        else:
            products = ProductQueries.get_all_products()

        if not products:
            return "No hay productos disponibles"

        result = "Catálogo de productos:\n\n"
        current_category = None

        for p in products:
            if p.category_name != current_category:
                current_category = p.category_name
                result += f"\n📦 {current_category}\n"

            result += f"  • {p.name} - ${p.price:.2f}"
            if p.description:
                result += f"\n    {p.description}"
            result += f"\n    (ID: {p.id})\n"

        return result

    def _tool_search_products(self, input: Dict) -> str:
        """Search products"""
        query = input.get("query", "")
        products = ProductQueries.search_products(query)

        if not products:
            return f"No se encontraron productos con '{query}'"

        result = f"Productos encontrados para '{query}':\n\n"
        for p in products:
            result += f"• {p.name} - ${p.price:.2f}"
            if p.description:
                result += f"\n  {p.description}"
            result += f"\n  (ID: {p.id})\n"

        return result

    def _tool_list_recipes(self, input: Dict) -> str:
        """List all available recipes"""
        recipes_data = RecipesData()
        return recipes_data.format_recipe_list()

    def _tool_get_recipe(self, input: Dict) -> str:
        """Get a specific recipe by name or ID"""
        query = input.get("query", "")
        if not query:
            return "Error: Se requiere el nombre o número de la receta"

        recipes_data = RecipesData()

        # Try to parse as ID first
        try:
            recipe_id = int(query)
            recipe = recipes_data.get_recipe_by_id(recipe_id)
            if recipe:
                return recipes_data.format_recipe(recipe)
        except ValueError:
            pass

        # Search by name
        recipe = recipes_data.get_recipe_by_name(query)
        if recipe:
            return recipes_data.format_recipe(recipe)

        return f"No se encontró la receta '{query}'. Usa 'list_recipes' para ver todas las recetas disponibles."

    def _tool_search_recipes(self, input: Dict) -> str:
        """Search recipes by name or ingredient"""
        query = input.get("query", "")
        if not query:
            return "Error: Se requiere un texto para buscar"

        recipes_data = RecipesData()
        results = recipes_data.search_recipes(query)

        if not results:
            return f"No se encontraron recetas con '{query}'"

        if len(results) == 1:
            return recipes_data.format_recipe(results[0])

        return recipes_data.format_recipe_list(results)

    def _tool_create_order(self, input: Dict) -> str:
        """Create a new order"""
        items_input = input.get("items", [])
        if not items_input:
            return "Error: Se requiere al menos un producto"

        order_items = []
        total = Decimal("0")

        for item in items_input:
            product = ProductQueries.get_product_by_id(UUID(item["product_id"]))
            if not product:
                return f"Error: Producto no encontrado (ID: {item['product_id']})"

            quantity = item.get("quantity", 1)
            subtotal = product.price * quantity
            total += subtotal

            order_items.append(OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=quantity,
                unit_price=product.price,
                subtotal=subtotal
            ))

        # Create order in DB
        order = OrderQueries.create(self.customer_id, order_items, total)

        # Format summary
        result = "📋 RESUMEN DEL PEDIDO\n"
        result += "=" * 25 + "\n\n"
        for item in order_items:
            result += f"• {item.product_name}\n"
            result += f"  {item.quantity} x ${item.unit_price:.2f} = ${item.subtotal:.2f}\n"
        result += "\n" + "-" * 25 + "\n"
        result += f"TOTAL: ${total:.2f}\n"
        result += "=" * 25 + "\n\n"
        result += f"ID del pedido: {order.id}\n\n"
        result += "⚠️ Este pedido está PENDIENTE de confirmación.\n"
        result += "Por favor pregunta al cliente si desea confirmar."

        return result

    def _tool_confirm_order(self, input: Dict) -> str:
        """Confirm an order"""
        order_id = input.get("order_id")
        if not order_id:
            return "Error: Se requiere el ID del pedido"

        order = OrderQueries.get_by_id(UUID(order_id))
        if not order:
            return "Error: Pedido no encontrado"

        if order.status != "pending":
            return f"Error: El pedido ya fue {order.status}"

        # Get customer info
        customer = CustomerQueries.get_by_id(self.customer_id)

        # Send to external API
        try:
            order_data = self.orders_service.format_order_for_api(
                customer_phone=self.customer_phone,
                customer_name=customer.name if customer else None,
                items=[item.model_dump() for item in order.items]
            )
            response = self.orders_service.create_order(order_data)
            external_id = response.get("id", response.get("numero", str(order.id)))

            # Update local order
            OrderQueries.confirm(order.id, str(external_id))

            return f"✅ ¡Pedido confirmado!\n\nNúmero de pedido: {external_id}\nTotal: ${order.total:.2f}\n\n¡Gracias por tu compra!"

        except Exception as e:
            return f"Error al procesar el pedido: {str(e)}. Por favor intenta de nuevo."

    def _tool_cancel_order(self, input: Dict) -> str:
        """Cancel an order"""
        order_id = input.get("order_id")
        if not order_id:
            return "Error: Se requiere el ID del pedido"

        order = OrderQueries.get_by_id(UUID(order_id))
        if not order:
            return "Error: Pedido no encontrado"

        if order.status != "pending":
            return f"Error: El pedido ya fue {order.status} y no puede cancelarse"

        OrderQueries.cancel(order.id)
        return "❌ Pedido cancelado. ¿Hay algo más en lo que pueda ayudarte?"

    def _tool_get_customer_info(self, input: Dict) -> str:
        """Get customer info"""
        customer = CustomerQueries.get_by_id(self.customer_id)
        if not customer:
            return "No se encontró información del cliente"

        orders = OrderQueries.get_customer_orders(self.customer_id, limit=3)

        result = "📊 Información del cliente:\n"
        result += f"- Teléfono: {customer.phone_number}\n"
        if customer.name:
            result += f"- Nombre: {customer.name}\n"

        if customer.preferences:
            result += "\nPreferencias guardadas:\n"
            for key, value in customer.preferences.items():
                result += f"- {key}: {value}\n"

        if orders:
            result += "\nÚltimos pedidos:\n"
            for order in orders:
                result += f"- {order.created_at.strftime('%d/%m/%Y')}: ${order.total:.2f} ({order.status})\n"

        return result
