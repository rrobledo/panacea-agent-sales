# Session: Extraccion de Recetas 2025

**Fecha:** 2026-01-23

## Objetivo
Extraer todas las recetas del archivo PDF `Recetas2025.pdf` y generar un archivo JSON estructurado con la informacion completa de cada receta, individualizando ingredientes, cantidades y medidas.

## Archivos Involucrados

### Entrada
- `/home/ubuntu/workspaces/panacea/panacea-agent-sales/tasks/Recetas2025.pdf` (535.6KB)

### Salida
- `/home/ubuntu/workspaces/panacea/panacea-agent-sales/tasks/recetas2025.json`

## Resultado

Se extrajeron **44 recetas** del PDF de Panacea Gluten Free Bakery.

### Estructura del JSON generado

```json
{
  "panaderia": "Panacea Gluten Free Bakery",
  "tipo": "Recetas Sin Gluten",
  "total_recetas": 44,
  "recetas": [
    {
      "id": number,
      "nombre": string,
      "rendimiento": string,
      "ingredientes": [
        {
          "nombre": string,
          "cantidad": number | null,
          "unidad": string
        }
      ],
      "procedimiento": string,
      "coccion": {
        "temperatura_horno": number,
        "tiempo": string,
        ...
      }
    }
  ]
}
```

### Categorias de Recetas Extraidas

| Categoria | Cantidad | Recetas |
|-----------|----------|---------|
| Panes | 8 | Pan de Molde, Chip/Pancho, Lomo, Frances, Miga, Criollos, Chipa, Pizzetas |
| Budines | 2 | Clasicos (7 sabores), Zanahoria |
| Cookies | 5 | Chocolate, Coco, Limon, Naranja, Marmoladas |
| Galletitas | 5 | Pepas de Membrillo, Scones, Queso, Talitas, Coquitos |
| Alfajores | 5 | Maicena, Chocolate, Coco, Cordobeses*, Mil Hojas |
| Postres | 6 | Brownie, Pasta Frola, Chocotorta, Cheesecake Frutilla, Balcarces, Cuadrados (3 tipos) |
| Bizcochuelos | 2 | Vainilla, Chocolate |
| Facturas | 2 | Medialunas/Facturas, Palmeritas |
| Pastas | 7 | Noquis, Fideos al Huevo, Ravioles (2 tipos), Sorrentinos (4 tipos) |

*Nota: Alfajores Cordobeses marcados como "2025 no se realiza"

### Unidades de Medida Utilizadas

- `grs` - gramos
- `kg` - kilogramos
- `ml` - mililitros
- `litros` - litros
- `unidades` - unidades (huevos, limones, etc.)
- `cucharadas` - cucharadas
- `tapas` - tapas del envase
- `gotas` - gotas
- `atado` - atado (espinaca)
- `cantidad necesaria` - sin cantidad especifica

## Observaciones

1. Algunas recetas tienen ingredientes con cantidad "null" cuando el PDF indica "cantidad necesaria"
2. La receta de Alfajores Cordobeses tiene una nota indicando que en 2025 no se realiza
3. El Brownie tiene una nota sobre el bicarbonato: "2025 no se le agrega"
4. Los Noquis tienen nota sobre polvo de hornear: "no se coloca"
5. Algunas recetas de pastas tienen campos de relleno incompletos en el PDF original (marcados con "?")
