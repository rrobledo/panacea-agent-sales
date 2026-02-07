"""Recipes data loader from JSON file"""

import json
import os
from typing import List, Optional, Dict, Any


class RecipesData:
    """Load and query recipes from JSON file"""

    _instance = None
    _recipes: List[Dict[str, Any]] = []
    _metadata: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_recipes()
        return cls._instance

    def _load_recipes(self):
        """Load recipes from JSON file"""
        # Path relative to whatsapp-agent/ root
        json_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "recetas2025.json"
        )

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._recipes = data.get("recetas", [])
                self._metadata = {
                    "panaderia": data.get("panaderia", ""),
                    "tipo": data.get("tipo", ""),
                    "total_recetas": data.get("total_recetas", len(self._recipes))
                }
        except FileNotFoundError:
            print(f"Warning: Recipes file not found at {json_path}")
            self._recipes = []
            self._metadata = {}
        except json.JSONDecodeError as e:
            print(f"Warning: Error parsing recipes JSON: {e}")
            self._recipes = []
            self._metadata = {}

    def get_all_recipes(self) -> List[Dict[str, Any]]:
        """Get all recipes"""
        return self._recipes

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """Get a recipe by its ID"""
        for recipe in self._recipes:
            if recipe.get("id") == recipe_id:
                return recipe
        return None

    def get_recipe_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a recipe by name (case insensitive partial match)"""
        name_lower = name.lower()
        for recipe in self._recipes:
            if name_lower in recipe.get("nombre", "").lower():
                return recipe
        return None

    def search_recipes(self, query: str) -> List[Dict[str, Any]]:
        """Search recipes by name or ingredients"""
        query_lower = query.lower()
        results = []

        for recipe in self._recipes:
            # Search in name
            if query_lower in recipe.get("nombre", "").lower():
                results.append(recipe)
                continue

            # Search in ingredients
            ingredientes = recipe.get("ingredientes", [])
            for ing in ingredientes:
                if query_lower in ing.get("nombre", "").lower():
                    results.append(recipe)
                    break

        return results

    def get_recipe_names(self) -> List[str]:
        """Get list of all recipe names"""
        return [r.get("nombre", "") for r in self._recipes if r.get("nombre")]

    def get_metadata(self) -> Dict[str, Any]:
        """Get recipes metadata (bakery name, type, count)"""
        return self._metadata

    def format_recipe(self, recipe: Dict[str, Any]) -> str:
        """Format a recipe for display"""
        if not recipe:
            return "Receta no encontrada"

        result = f"🍞 {recipe.get('nombre', 'Sin nombre')}\n"
        result += "=" * 30 + "\n\n"

        if recipe.get("rendimiento"):
            result += f"📊 Rendimiento: {recipe['rendimiento']}\n\n"

        # Ingredients — names only, no quantities (confidential)
        result += "📝 INGREDIENTES:\n"
        ingredientes = recipe.get("ingredientes", [])
        for ing in ingredientes:
            result += f"  • {ing.get('nombre', '')}\n"

        # Additional ingredient lists — names only
        for key, label in [
            ("ingredientes_vainilla", "Ingredientes Vainilla"),
            ("ingredientes_chocolate", "Ingredientes Chocolate"),
            ("ingredientes_empaste", "Ingredientes Empaste"),
            ("ingredientes_pastelera", "Ingredientes Pastelera"),
        ]:
            if recipe.get(key):
                result += f"\n  {label}:\n"
                for ing in recipe[key]:
                    result += f"    • {ing.get('nombre', '')}\n"

        # Relleno — names only
        if recipe.get("relleno"):
            result += "\n🥧 RELLENO:\n"
            relleno = recipe["relleno"]
            if isinstance(relleno, list):
                for item in relleno:
                    result += f"  • {item}\n"
            elif isinstance(relleno, dict):
                if relleno.get("ingredientes"):
                    result += "  Ingredientes:\n"
                    for item in relleno["ingredientes"]:
                        result += f"    • {item}\n"
                if relleno.get("condimentos"):
                    result += "  Condimentos:\n"
                    for item in relleno["condimentos"]:
                        result += f"    • {item}\n"

        result += "\n⚠️ Las cantidades y el procedimiento son parte de nuestras fórmulas exclusivas.\n"

        # Variants
        if recipe.get("variantes"):
            result += "\n🔄 VARIANTES:\n"
            for key, value in recipe["variantes"].items():
                result += f"  • {key}: {value}\n"

        # Flavors
        if recipe.get("sabores"):
            result += f"\n🎨 SABORES: {', '.join(recipe['sabores'])}\n"

        # Notes
        if recipe.get("nota"):
            result += f"\n⚠️ NOTA: {recipe['nota']}\n"

        return result

    def format_recipe_list(self, recipes: List[Dict[str, Any]] = None) -> str:
        """Format a list of recipes (names only)"""
        if recipes is None:
            recipes = self._recipes

        if not recipes:
            return "No hay recetas disponibles"

        result = f"📚 RECETAS DISPONIBLES ({len(recipes)}):\n"
        result += "=" * 30 + "\n\n"

        for recipe in recipes:
            result += f"  {recipe.get('id', '?')}. {recipe.get('nombre', 'Sin nombre')}\n"

        result += "\n💡 Para ver una receta, indica el nombre o número."
        return result
