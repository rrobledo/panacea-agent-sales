# Pseudocode

## Step-by-Step Plan

### 1. Project Setup
1. Initialize Python project with requirements.txt (Vercel compatible)
2. Set up FastAPI application for Vercel serverless
3. Configure environment variables in Vercel dashboard
4. Set up Vercel Postgres connection (Neon)

### 2. Database Schema
1. Create `customers` table (id, phone_number, name, preferences, created_at)
2. Create `conversations` table (id, customer_id, messages_json, context, updated_at)
3. Create `categories` table (id, name, description)
4. Create `products` table (id, category_id, name, description, price, available)
5. Create `recipes` table (id, product_id, ingredients, instructions, tips)
6. Create `orders` table (id, customer_id, items_json, status, external_order_id, created_at)

### 3. WhatsApp Integration (Meta API)
1. Set up webhook endpoint to receive messages: `POST /webhook`
2. Set up verification endpoint: `GET /webhook`
3. Implement message sender using Meta Graph API
4. Handle incoming message types (text, buttons, lists)

### 4. AI Agent Core
1. Initialize Anthropic Claude client
2. Build system prompt with:
   - Agent personality (cordial, Spanish)
   - Available tools/functions
   - Context about products and recipes
3. Implement conversation memory manager
4. Create function calling tools:
   - `get_product_catalog()` - returns products with prices
   - `get_recipes(product_id)` - returns recipes for a product
   - `get_categories()` - returns product categories
   - `create_order(items)` - creates order via external API
   - `get_customer_history(phone)` - retrieves customer preferences

### 5. Conversation Flow
```
RECEIVE message from WhatsApp
  |
  v
IDENTIFY customer by phone number
  |
  v
LOAD customer history and preferences
  |
  v
BUILD context for Claude:
  - System prompt (personality, tools)
  - Customer history summary
  - Recent conversation messages
  |
  v
SEND to Claude API with tools
  |
  v
IF Claude calls a tool:
  - Execute tool (query DB, call external API)
  - Return result to Claude
  - Continue conversation
  |
  v
EXTRACT response text
  |
  v
SEND response via WhatsApp API
  |
  v
SAVE conversation to database
```

### 6. Order Flow
```
CUSTOMER requests product
  |
  v
AGENT confirms items and quantities
  |
  v
AGENT calls create_order tool
  |
  v
SHOW order summary to customer
  |
  v
CUSTOMER confirms (yes/no)
  |
  v
IF confirmed:
  - Call external REST API to create order
  - Save order reference
  - Confirm to customer
ELSE:
  - Cancel or modify order
```

### 7. External API Integration
1. Create HTTP client for order system
2. Implement `POST /orders` call
3. Handle response and error cases
4. Store external order ID in local database

## Logic Flow

```
┌─────────────────┐
│   WhatsApp      │
│   (Customer)    │
└────────┬────────┘
         │ Message
         v
┌─────────────────┐
│  FastAPI        │
│  Webhook        │
└────────┬────────┘
         │
         v
┌─────────────────┐     ┌─────────────────┐
│  Customer       │────>│  PostgreSQL     │
│  Identifier     │<────│  Database       │
└────────┬────────┘     └─────────────────┘
         │
         v
┌─────────────────┐
│  Context        │
│  Builder        │
└────────┬────────┘
         │
         v
┌─────────────────┐     ┌─────────────────┐
│  Claude AI      │────>│  Tool Executor  │
│  Agent          │<────│  (Functions)    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │              ┌────────┴────────┐
         │              │                 │
         │              v                 v
         │     ┌─────────────┐   ┌─────────────┐
         │     │  Database   │   │  External   │
         │     │  Queries    │   │  Order API  │
         │     └─────────────┘   └─────────────┘
         │
         v
┌─────────────────┐
│  Response       │
│  Formatter      │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  WhatsApp       │
│  API Sender     │
└─────────────────┘
```

## Edge Cases

1. **New customer**: Create customer record, use default greeting
2. **Customer not responding**: Conversation timeout handling
3. **Invalid product request**: Suggest similar products
4. **External API down**: Queue order, notify customer of delay
5. **WhatsApp rate limits**: Implement retry with exponential backoff
6. **Long conversations**: Summarize old messages to fit context window
7. **Multiple orders in progress**: Track order state per customer
8. **Unclear customer intent**: Ask clarifying questions

## Dependencies

### Python Packages
- `fastapi` - Web framework
- `mangum` - ASGI adapter for serverless (Vercel)
- `anthropic` - Claude API client
- `psycopg2-binary` - PostgreSQL driver (Vercel Postgres compatible)
- `sqlalchemy` - ORM
- `httpx` - Async HTTP client for external APIs
- `pydantic` - Data validation

### External Services
- Meta WhatsApp Business API account
- Anthropic API key
- Vercel Postgres database
- External order system API (endpoint, credentials)

### Deployment
- Vercel (Python serverless functions)
- `vercel.json` configuration file
