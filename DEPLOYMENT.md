# Guía de Deployment en Vercel

Esta guía te llevará paso a paso para desplegar el agente de WhatsApp en Vercel.

## Índice

1. [Requisitos Previos](#1-requisitos-previos)
2. [Crear Cuenta en Vercel](#2-crear-cuenta-en-vercel)
3. [Importar Proyecto](#3-importar-proyecto)
4. [Configurar Vercel Postgres](#4-configurar-vercel-postgres)
5. [Configurar Variables de Entorno](#5-configurar-variables-de-entorno)
6. [Desplegar el Proyecto](#6-desplegar-el-proyecto)
7. [Inicializar Base de Datos](#7-inicializar-base-de-datos)
8. [Configurar Webhook en Meta](#8-configurar-webhook-en-meta)
9. [Verificar Deployment](#9-verificar-deployment)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Requisitos Previos

Antes de comenzar, asegúrate de tener:

- [ ] Cuenta de GitHub con acceso al repositorio
- [ ] API Key de Anthropic (Claude)
- [ ] Cuenta de Meta for Developers con WhatsApp Business API configurada
- [ ] Número de teléfono para WhatsApp Business

### Obtener API Key de Anthropic

1. Ve a [console.anthropic.com](https://console.anthropic.com)
2. Crea una cuenta o inicia sesión
3. Ve a **API Keys** > **Create Key**
4. Copia y guarda la key (empieza con `sk-ant-`)

---

## 2. Crear Cuenta en Vercel

1. Ve a [vercel.com](https://vercel.com)
2. Click en **Sign Up**
3. Selecciona **Continue with GitHub**
4. Autoriza Vercel para acceder a tu cuenta de GitHub

---

## 3. Importar Proyecto

### Opción A: Desde el Dashboard de Vercel

1. En el dashboard de Vercel, click en **Add New** > **Project**

2. Busca el repositorio `panacea-agent-sales`

3. Click en **Import**

4. Configura el proyecto:
   - **Framework Preset**: Other
   - **Root Directory**: `whatsapp-agent`
   - **Build Command**: (dejar vacío)
   - **Output Directory**: (dejar vacío)

5. Click en **Deploy** (fallará porque faltan variables de entorno, es normal)

### Opción B: Usando Vercel CLI

```bash
# Instalar Vercel CLI
npm install -g vercel

# Ir al directorio del proyecto
cd whatsapp-agent

# Login en Vercel
vercel login

# Iniciar deployment
vercel

# Seguir las instrucciones:
# - Set up and deploy? Yes
# - Which scope? (selecciona tu cuenta)
# - Link to existing project? No
# - Project name? panacea-agent-sales
# - Directory? ./
```

---

## 4. Configurar Vercel Postgres

### 4.1 Crear la Base de Datos

1. Ve a tu proyecto en Vercel Dashboard

2. Click en la pestaña **Storage**

3. Click en **Create Database**

4. Selecciona **Postgres**

5. Configura:
   - **Database Name**: `panacea-db`
   - **Region**: Selecciona la más cercana a tus usuarios

6. Click en **Create**

7. En la pantalla de conexión, selecciona tu proyecto y click en **Connect**

### 4.2 Verificar Variables de Conexión

Vercel agregará automáticamente estas variables de entorno:
- `POSTGRES_URL`
- `POSTGRES_PRISMA_URL`
- `POSTGRES_URL_NON_POOLING`
- `POSTGRES_USER`
- `POSTGRES_HOST`
- `POSTGRES_PASSWORD`
- `POSTGRES_DATABASE`

---

## 5. Configurar Variables de Entorno

1. Ve a tu proyecto en Vercel Dashboard

2. Click en **Settings** > **Environment Variables**

3. Agrega las siguientes variables:

| Variable | Valor | Entornos |
|----------|-------|----------|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` | Production, Preview, Development |
| `WHATSAPP_ACCESS_TOKEN` | Tu token de Meta | Production, Preview, Development |
| `WHATSAPP_PHONE_NUMBER_ID` | Tu Phone Number ID | Production, Preview, Development |
| `WHATSAPP_VERIFY_TOKEN` | Un token secreto (invéntalo) | Production, Preview, Development |
| `ORDERS_API_URL` | `https://panacea-one.vercel.app/costos/remitos` | Production, Preview, Development |

### Cómo agregar cada variable:

1. Click en **Add New**
2. En **Key**, escribe el nombre de la variable
3. En **Value**, pega el valor
4. Selecciona los entornos (Production, Preview, Development)
5. Click en **Save**

### Obtener credenciales de WhatsApp

Si aún no tienes las credenciales de WhatsApp, consulta la guía en:
[`.claude/sparc/meta-whatsapp-setup.md`](.claude/sparc/meta-whatsapp-setup.md)

---

## 6. Desplegar el Proyecto

### Redesplegar después de configurar variables

1. Ve a tu proyecto en Vercel Dashboard

2. Click en la pestaña **Deployments**

3. Encuentra el último deployment

4. Click en los **tres puntos** (⋮) > **Redeploy**

5. Marca **Use existing Build Cache** si quieres acelerar

6. Click en **Redeploy**

### Verificar el deployment

1. Espera a que el status sea **Ready** ✓

2. Click en el dominio generado (ej: `panacea-agent-sales.vercel.app`)

3. Agrega `/api/health` a la URL para verificar:
   ```
   https://panacea-agent-sales.vercel.app/api/health
   ```

4. Deberías ver:
   ```json
   {"status": "healthy", "service": "whatsapp-agent"}
   ```

---

## 7. Inicializar Base de Datos

### 7.1 Acceder a la consola de Postgres

1. Ve a tu proyecto en Vercel Dashboard

2. Click en **Storage** > tu base de datos

3. Click en la pestaña **Query**

### 7.2 Ejecutar el script de inicialización

1. Abre el archivo `whatsapp-agent/scripts/init_db.sql`

2. Copia todo el contenido

3. Pégalo en la consola de Query de Vercel

4. Click en **Run Query**

5. Deberías ver mensajes de éxito para cada tabla creada

### 7.3 Cargar datos de ejemplo (opcional)

Para cargar productos y recetas de ejemplo, ejecuta estas queries:

```sql
-- Insertar categorías
INSERT INTO categories (name, description, display_order) VALUES
('Panadería', 'Panes frescos y productos horneados', 1),
('Pastelería', 'Pasteles, tartas y postres', 2),
('Bebidas', 'Bebidas calientes y frías', 3);

-- Insertar productos (ajusta los UUIDs de categoría según corresponda)
-- Primero obtén los IDs de categorías:
SELECT id, name FROM categories;

-- Luego inserta productos usando los IDs correctos
```

O ejecuta el script de seed localmente:

```bash
cd whatsapp-agent

# Crear archivo .env con POSTGRES_URL de Vercel
echo "POSTGRES_URL=tu_postgres_url_de_vercel" > .env

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar seed
python scripts/seed_data.py
```

---

## 8. Configurar Webhook en Meta

### 8.1 Obtener tu URL de Webhook

Tu URL de webhook será:
```
https://tu-proyecto.vercel.app/api/webhook
```

Por ejemplo:
```
https://panacea-agent-sales.vercel.app/api/webhook
```

### 8.2 Configurar en Meta Developer Dashboard

1. Ve a [developers.facebook.com](https://developers.facebook.com)

2. Selecciona tu aplicación

3. En el menú lateral, ve a **WhatsApp** > **Configuration**

4. En la sección **Webhook**, click en **Edit**

5. Ingresa:
   - **Callback URL**: `https://tu-proyecto.vercel.app/api/webhook`
   - **Verify Token**: El mismo valor que pusiste en `WHATSAPP_VERIFY_TOKEN`

6. Click en **Verify and Save**

   > Si la verificación falla, revisa los logs en Vercel Dashboard > Deployments > Functions

7. En **Webhook Fields**, click en **Manage**

8. Suscríbete a:
   - [x] `messages`
   - [x] `message_template_status_update` (opcional)

9. Click en **Done**

---

## 9. Verificar Deployment

### 9.1 Probar el Health Check

```bash
curl https://tu-proyecto.vercel.app/api/health
```

Respuesta esperada:
```json
{"status": "healthy", "service": "whatsapp-agent"}
```

### 9.2 Probar el Webhook (verificación)

```bash
curl "https://tu-proyecto.vercel.app/api/webhook?hub.mode=subscribe&hub.verify_token=TU_VERIFY_TOKEN&hub.challenge=test123"
```

Respuesta esperada:
```
test123
```

### 9.3 Enviar mensaje de prueba

1. Desde tu teléfono, envía un mensaje al número de WhatsApp Business

2. Deberías recibir una respuesta del agente

3. Si no recibes respuesta, revisa los logs en:
   - Vercel Dashboard > Deployments > (último deployment) > Functions > Logs

---

## 10. Troubleshooting

### Error: "Webhook verification failed"

**Causa**: El verify token no coincide

**Solución**:
1. Verifica que `WHATSAPP_VERIFY_TOKEN` en Vercel sea exactamente igual al configurado en Meta
2. No debe tener espacios al inicio o final
3. Redespliega después de cambiar la variable

### Error: "Function timeout"

**Causa**: La función tarda más de 10 segundos (límite de Vercel Hobby)

**Solución**:
1. Upgrade a Vercel Pro (60s timeout)
2. O optimiza las consultas a la base de datos

### Error: "Database connection failed"

**Causa**: Variables de Postgres no configuradas

**Solución**:
1. Ve a Storage y verifica que la DB esté conectada al proyecto
2. Revisa que `POSTGRES_URL` esté en Environment Variables
3. Redespliega

### Error: "Anthropic API error"

**Causa**: API key inválida o sin créditos

**Solución**:
1. Verifica que `ANTHROPIC_API_KEY` sea correcta
2. Verifica que tengas créditos en tu cuenta de Anthropic

### El agente no responde

**Posibles causas**:
1. Webhook no configurado correctamente en Meta
2. Mensaje no es de tipo "text"
3. Error en la función (revisa logs)

**Diagnóstico**:
1. Ve a Vercel Dashboard > Deployments
2. Click en el deployment activo
3. Ve a la pestaña **Functions**
4. Click en `api/webhook.py`
5. Revisa los **Logs** en tiempo real mientras envías un mensaje

### Ver logs en tiempo real

```bash
vercel logs --follow
```

---

## Recursos Adicionales

- [Documentación de Vercel](https://vercel.com/docs)
- [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Anthropic API](https://docs.anthropic.com)

---

## Checklist Final

- [ ] Proyecto importado en Vercel
- [ ] Vercel Postgres creado y conectado
- [ ] Variables de entorno configuradas
- [ ] Base de datos inicializada (tablas creadas)
- [ ] Datos de productos/recetas cargados
- [ ] Webhook verificado en Meta
- [ ] Eventos de mensajes suscritos
- [ ] Prueba de mensaje exitosa

¡Tu agente de WhatsApp está listo! 🎉
