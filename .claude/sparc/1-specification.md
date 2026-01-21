# Specification

## Goal
- Create an AI agent with the following requirements:
  - The agent shall interact with WhatsApp using Meta API
  - The agent needs to interact in Spanish
  - Debe contener las recetas que manejamos en producción de cada producto
  - Las recetas deben estar categorizadas
  - Debe tener un catálogo con precios para responder preguntas de los clientes
  - Debe mantener la historia relevante de cada interacción con el cliente para reconocerlo la próxima vez
  - Siempre debe ser cordial al saludarlo y darle un saludo personalizado al entender sus gustos
  - Si el cliente solicita algún producto, debe generar un pedido usando un API REST de un sistema externo
  - Siempre que se realiza un pedido se debe mostrar un resumen de lo pedido para que el cliente lo confirme
  - El agente debe ser adaptativo para en el futuro agregar más integraciones y nuevos comportamientos

## Constraints
- Must use Python as the programming language
- Must integrate with Meta WhatsApp Business API
- Must communicate in Spanish
- External order system via REST API (existing system)
- **Deployment: Vercel (serverless functions)**
  - No persistent connections
  - Stateless execution
  - Cold start considerations
  - Max execution time limits

## Success Criteria
- [ ] Agent can receive and respond to WhatsApp messages
- [ ] Agent responds in Spanish with cordial, personalized greetings
- [ ] Agent can provide recipe information categorized by product
- [ ] Agent can provide product catalog with prices
- [ ] Agent remembers customer history and preferences
- [ ] Agent can create orders via external REST API
- [ ] Agent shows order summary for customer confirmation
- [ ] Architecture supports future integrations and behaviors

## Context
- Language: Python
- Integration: Meta WhatsApp Business API
- External system: REST API for order management
- Target users: Customers asking about products, recipes, and placing orders

## Technical Decisions
- **LLM Provider:** Anthropic (Claude)
- **Database:** Vercel Postgres (Neon) - serverless optimized
- **Web Framework:** FastAPI (serverless functions)
- **Data Source:** Database tables for recipes and product catalog
- **Deployment:** Vercel (Python serverless functions)
- **External Order API:** https://panacea-one.vercel.app/costos/remitos

## Out of Scope
- Payment processing within the agent
- Delivery tracking
- Multi-language support (Spanish only for now)
- Web or mobile app interface (WhatsApp only)
