"""Tools available for the Claude agent"""

from typing import Any, Dict
from lib.data.recipes import RecipesData


# Tool definitions for Claude
TOOLS = [
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
]


class ToolExecutor:
    """Executes tools called by Claude"""

    async def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return result as string"""
        method = getattr(self, f"_tool_{tool_name}", None)
        if method:
            return await method(tool_input)
        return f"Error: Herramienta '{tool_name}' no encontrada"

    async def _tool_list_recipes(self, input: Dict) -> str:
        """List all available recipes"""
        recipes_data = RecipesData()
        return recipes_data.format_recipe_list()

    async def _tool_get_recipe(self, input: Dict) -> str:
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

    async def _tool_search_recipes(self, input: Dict) -> str:
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
