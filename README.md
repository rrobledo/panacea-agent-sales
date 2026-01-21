# Panacea WhatsApp Agent

Agente de inteligencia artificial para atención al cliente vía WhatsApp, desarrollado para Panacea.

## Descripción

Este proyecto implementa un agente conversacional que interactúa con los clientes a través de WhatsApp, utilizando la API de Meta y Claude AI de Anthropic. El agente puede:

- Responder consultas sobre productos y precios
- Mostrar recetas categorizadas por producto
- Crear y gestionar pedidos
- Recordar preferencias e historial de cada cliente
- Comunicarse de forma cordial y personalizada en español

## Características

- **Integración WhatsApp**: Comunicación bidireccional mediante Meta WhatsApp Business API
- **IA Conversacional**: Powered by Claude (Anthropic) para respuestas naturales en español
- **Catálogo de Productos**: Consulta de productos con precios y categorías
- **Gestión de Recetas**: Recetas detalladas asociadas a cada producto
- **Sistema de Pedidos**: Creación de pedidos con confirmación y envío a API externa
- **Memoria de Conversación**: Historial y preferencias por cliente
- **Arquitectura Extensible**: Diseñado para agregar nuevas integraciones fácilmente

## Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Runtime | Python 3.9+ (Vercel Serverless) |
| Framework | FastAPI |
| LLM | Anthropic Claude |
| Base de Datos | Vercel Postgres (Neon) |
| Validación | Pydantic |
| HTTP Client | httpx |

## Estructura del Proyecto

```
├── .claude/
│   ├── skills/
│   │   └── SPARC.md              # Metodología SPARC
│   └── sparc/
│       ├── 1-specification.md     # Especificación del proyecto
│       ├── 2-pseudocode.md        # Plan paso a paso
│       ├── 3-architecture.md      # Diseño de arquitectura
│       ├── 4-refinement.md        # Progreso de implementación
│       ├── 5-completion.md        # Documentación final
│       └── meta-whatsapp-setup.md # Tutorial configuración Meta
│
├── whatsapp-agent/
│   ├── api/
│   │   ├── webhook.py            # Endpoint WhatsApp webhook
│   │   └── health.py             # Health check
│   │
│   ├── lib/
│   │   ├── config.py             # Variables de entorno
│   │   │
│   │   ├── agent/
│   │   │   ├── core.py           # Lógica principal del agente
│   │   │   ├── tools.py          # Herramientas disponibles para Claude
│   │   │   ├── prompts.py        # System prompts en español
│   │   │   └── memory.py         # Gestión de memoria de conversación
│   │   │
│   │   ├── services/
│   │   │   ├── whatsapp.py       # Cliente Meta WhatsApp API
│   │   │   ├── claude.py         # Cliente Anthropic API
│   │   │   └── orders.py         # Cliente API externa de pedidos
│   │   │
│   │   ├── db/
│   │   │   ├── connection.py     # Conexión PostgreSQL
│   │   │   └── queries/          # Operaciones de base de datos
│   │   │
│   │   └── schemas/              # Modelos Pydantic
│   │
│   ├── scripts/
│   │   ├── init_db.sql           # Schema de base de datos
│   │   └── seed_data.py          # Datos de ejemplo
│   │
│   ├── vercel.json               # Configuración Vercel
│   ├── requirements.txt          # Dependencias Python
│   └── .env.example              # Variables de entorno ejemplo
│
├── CLAUDE.md                     # Guía para desarrollo con AI
└── README.md                     # Este archivo
```

## Requisitos Previos

- Cuenta de [Vercel](https://vercel.com)
- Cuenta de [Anthropic](https://anthropic.com) con API key
- Cuenta de [Meta for Developers](https://developers.facebook.com) con WhatsApp Business API
- Número de teléfono dedicado para WhatsApp Business

## Instalación

### 1. Clonar el repositorio

```bash
git clone git@github.com:rrobledo/panacea-agent-sales.git
cd panacea-agent-sales
```

### 2. Desplegar en Vercel

```bash
cd whatsapp-agent
vercel
```

### 3. Configurar Vercel Postgres

1. Ve a Vercel Dashboard > Storage > Create Database
2. Selecciona Postgres
3. Conecta la base de datos a tu proyecto
4. Ejecuta el script `scripts/init_db.sql` en la consola de Vercel Postgres

### 4. Configurar Variables de Entorno

En Vercel Dashboard > Settings > Environment Variables, agrega:

```env
ANTHROPIC_API_KEY=sk-ant-...
WHATSAPP_ACCESS_TOKEN=tu_access_token
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id
WHATSAPP_VERIFY_TOKEN=tu_token_secreto
ORDERS_API_URL=https://panacea-one.vercel.app/costos/remitos
```

### 5. Configurar Meta WhatsApp

Ver guía detallada en [`.claude/sparc/meta-whatsapp-setup.md`](.claude/sparc/meta-whatsapp-setup.md)

Resumen:
1. Crear app en Meta for Developers
2. Agregar producto WhatsApp
3. Configurar webhook URL: `https://tu-app.vercel.app/api/webhook`
4. Suscribirse a eventos `messages`

### 6. Cargar Datos Iniciales

```bash
cd whatsapp-agent
pip install -r requirements.txt
python scripts/seed_data.py
```

## Uso

Una vez configurado, el agente responderá automáticamente a los mensajes de WhatsApp.

### Capacidades del Agente

| Intención | Ejemplo de mensaje |
|-----------|-------------------|
| Ver catálogo | "¿Qué productos tienen?" |
| Ver categorías | "¿Qué categorías hay?" |
| Buscar producto | "¿Tienen pan integral?" |
| Ver receta | "¿Cómo se prepara el pan francés?" |
| Hacer pedido | "Quiero 2 croissants y un café" |
| Confirmar pedido | "Sí, confirmo" |

## Metodología SPARC

Este proyecto fue desarrollado siguiendo la metodología SPARC para agentes de IA:

- **S**pecification: Definición clara de objetivos y restricciones
- **P**seudocode: Plan paso a paso antes de implementar
- **A**rchitecture: Diseño de estructura y componentes
- **R**efinement: Implementación iterativa con pruebas
- **C**ompletion: Documentación y auditoría final

Los documentos SPARC están disponibles en `.claude/sparc/`.

## Extensibilidad

### Agregar nuevas herramientas al agente

1. Define la herramienta en `lib/agent/tools.py` (lista `TOOLS`)
2. Implementa el método `_tool_<nombre>` en la clase `ToolExecutor`

### Agregar nuevas integraciones

1. Crea un nuevo servicio en `lib/services/`
2. Importa y usa en las herramientas del agente

### Modificar comportamiento del agente

- Edita el prompt en `lib/agent/prompts.py`
- Ajusta la memoria en `lib/agent/memory.py`

## Limitaciones Conocidas

- Timeout de 10s en Vercel Hobby (60s en Pro)
- Mensajes WhatsApp limitados a 4096 caracteres
- Historial de conversación limitado a últimos 20 mensajes

## Roadmap

- [ ] Soporte para imágenes y documentos
- [ ] Integración de pagos
- [ ] Seguimiento de entregas
- [ ] Soporte multi-idioma
- [ ] Dashboard administrativo
- [ ] Tests unitarios e integración

## Licencia

Proyecto privado - Todos los derechos reservados.

## Contacto

Desarrollado para Panacea.
