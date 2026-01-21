# Architecture

## Structure (Vercel Serverless)

```
whatsapp-agent/
├── api/
│   ├── webhook.py              # WhatsApp webhook (GET/POST)
│   └── health.py               # Health check endpoint
│
├── lib/
│   ├── __init__.py
│   ├── config.py               # Environment variables
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── core.py             # Claude AI agent logic
│   │   ├── tools.py            # Agent tools/functions
│   │   ├── prompts.py          # System prompts (Spanish)
│   │   └── memory.py           # Conversation memory
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── whatsapp.py         # Meta WhatsApp API client
│   │   ├── orders.py           # External order API client
│   │   └── claude.py           # Anthropic Claude wrapper
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py       # Vercel Postgres connection
│   │   ├── models.py           # Data models
│   │   └── queries/
│   │       ├── __init__.py
│   │       ├── customers.py
│   │       ├── products.py
│   │       ├── conversations.py
│   │       └── orders.py
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── whatsapp.py         # WhatsApp message schemas
│       ├── customer.py
│       ├── product.py
│       └── order.py
│
├── scripts/
│   ├── seed_data.py            # Seed products/recipes
│   └── init_db.sql             # Database schema
│
├── .env.example
├── .gitignore
├── requirements.txt
├── vercel.json
└── README.md
```

## Vercel Configuration

### vercel.json
```json
{
  "builds": [
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/webhook",
      "dest": "/api/webhook.py"
    },
    {
      "src": "/api/health",
      "dest": "/api/health.py"
    }
  ]
}
```

## Components

### 1. API Layer (`api/`)

#### webhook.py
```python
# Serverless function for WhatsApp webhook
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Webhook verification
        pass

    def do_POST(self):
        # Receive incoming messages
        pass
```

### 2. Agent Core (`lib/agent/`)

- **core.py**: Orchestrates conversation flow
  - Receives message → identifies customer → builds context → calls Claude → sends response
- **tools.py**: Functions available to Claude
  - `get_catalog()` - productos con precios
  - `get_recipes(product_id)` - recetas por producto
  - `get_categories()` - categorías de productos
  - `create_order(items)` - crear pedido
  - `get_customer_info()` - historial del cliente
- **prompts.py**: System prompt en español
- **memory.py**: Gestión de contexto de conversación

### 3. Services (`lib/services/`)

- **whatsapp.py**: Cliente Meta Graph API
- **orders.py**: Cliente para `https://panacea-one.vercel.app/costos/remitos`
- **claude.py**: Cliente Anthropic con tool use

### 4. Database (`lib/db/`)

Conexión a Vercel Postgres (Neon) usando `psycopg2`.

## Tooling Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Runtime | Vercel Python | Serverless functions |
| LLM | Anthropic Claude | AI conversation |
| Database | Vercel Postgres | Data persistence |
| HTTP Client | httpx | API calls |
| Validation | Pydantic | Data schemas |

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    MENSAJE ENTRANTE                          │
│                   (WhatsApp → Meta)                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────────┐
│  1. WEBHOOK (api/webhook.py)                                │
│     - Validar firma de Meta                                  │
│     - Parsear mensaje WhatsApp                               │
│     - Extraer: phone_number, message_text                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────────┐
│  2. IDENTIFICAR CLIENTE (lib/db/queries/customers.py)       │
│     - Buscar cliente por teléfono                            │
│     - Crear nuevo si no existe                               │
│     - Cargar preferencias e historial                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────────┐
│  3. CONSTRUIR CONTEXTO (lib/agent/memory.py)                │
│     - Cargar mensajes recientes                              │
│     - Resumen de preferencias del cliente                    │
│     - System prompt con personalidad                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────────┐
│  4. AGENTE CLAUDE (lib/agent/core.py)                       │
│     - Enviar a Claude con tools                              │
│     - Procesar tool_calls si hay                             │
│     - Obtener respuesta final                                │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              v                           v
┌──────────────────────┐    ┌──────────────────────────────┐
│  5a. EJECUTAR TOOL   │    │  5b. RESPUESTA DIRECTA       │
│  (lib/agent/tools.py)│    │  (sin tools)                 │
│  - Consultar DB      │    │                              │
│  - Llamar API pedidos│    │                              │
└──────────────────────┘    └──────────────────────────────┘
              │                           │
              └─────────────┬─────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────────┐
│  6. ENVIAR RESPUESTA (lib/services/whatsapp.py)             │
│     - Formatear para WhatsApp                                │
│     - POST a Meta Graph API                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────────┐
│  7. GUARDAR ESTADO (lib/db/queries/conversations.py)        │
│     - Guardar mensaje del usuario                            │
│     - Guardar respuesta del agente                           │
│     - Actualizar preferencias si se aprendió algo            │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

```sql
-- Clientes
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversaciones
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    messages JSONB DEFAULT '[]',
    summary TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Categorías
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    display_order INT DEFAULT 0
);

-- Productos
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES categories(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    available BOOLEAN DEFAULT TRUE
);

-- Recetas
CREATE TABLE recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    name VARCHAR(200) NOT NULL,
    ingredients JSONB NOT NULL,
    instructions TEXT NOT NULL,
    tips TEXT
);

-- Pedidos
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    items JSONB NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    external_order_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_customers_phone ON customers(phone_number);
CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
```

## Environment Variables (Vercel)

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Meta WhatsApp
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_VERIFY_TOKEN=...

# Database (auto-configured by Vercel Postgres)
POSTGRES_URL=...
POSTGRES_PRISMA_URL=...
POSTGRES_URL_NON_POOLING=...

# External API
ORDERS_API_URL=https://panacea-one.vercel.app/costos/remitos
```

## Security Considerations

1. **Webhook Verification**: Validar firma X-Hub-Signature-256 de Meta
2. **Environment Variables**: Todas las keys en Vercel, nunca en código
3. **Input Validation**: Pydantic schemas para validar datos
4. **SQL Injection**: Queries parametrizadas
5. **HTTPS**: Vercel provee SSL automáticamente

## Serverless Considerations

1. **Cold Starts**: Primera invocación puede ser lenta (~1-2s)
2. **Stateless**: Cada request es independiente, usar DB para estado
3. **Timeout**: Máximo 10s en Vercel Hobby, 60s en Pro
4. **Connection Pooling**: Vercel Postgres maneja el pooling automáticamente

## Extensibility

- **Nuevos tools**: Agregar en `lib/agent/tools.py`
- **Nuevas integraciones**: Agregar servicios en `lib/services/`
- **Nuevos canales**: Abstraer webhook handler para otros platforms
