# Tutorial: Configuración de Meta WhatsApp Business API

## Requisitos Previos

- [ ] Número de teléfono nuevo (NO vinculado a ninguna cuenta de WhatsApp personal o business)
- [ ] Cuenta de Facebook personal
- [ ] Información de tu negocio (nombre, dirección, etc.)

---

## Paso 1: Crear cuenta en Meta for Developers

1. Ve a [developers.facebook.com](https://developers.facebook.com)
2. Inicia sesión con tu cuenta de Facebook
3. Acepta los términos de desarrollador si es tu primera vez

---

## Paso 2: Crear una App

1. Click en **"Create App"** en el dashboard
2. Selecciona **"Other"** como tipo de app
3. Selecciona **"Business"** como caso de uso
4. Ingresa los datos:
   - **App name:** "Panacea WhatsApp Agent" (o el nombre que prefieras)
   - **App contact email:** tu email
   - **Business Account:** crea uno nuevo o selecciona existente
5. Click **"Create App"**

---

## Paso 3: Agregar WhatsApp a tu App

1. En el dashboard de tu app, busca **"WhatsApp"** en los productos
2. Click en **"Set up"**
3. Esto te llevará al panel de configuración de WhatsApp

---

## Paso 4: Configurar Meta Business Account

1. Si no tienes una cuenta de negocio, créala en [business.facebook.com](https://business.facebook.com)
2. Ve a **Business Settings > Security Center**
3. Habilita **Two-Step Verification** (verificación en dos pasos)
4. Crea un PIN de 6 dígitos (lo necesitarás después)

---

## Paso 5: Agregar tu número de teléfono

1. En el panel de WhatsApp de tu app, ve a **"Phone Numbers"**
2. Click en **"Add Phone Number"**
3. Ingresa tu número de teléfono nuevo
4. Verifica el número con el código SMS o llamada
5. Configura el **Display Name** de tu negocio
   - Debe incluir el nombre real del negocio (ej: "Panacea - Asistente")
   - Espera la aprobación del nombre

---

## Paso 6: Obtener credenciales

### Access Token (Temporal para pruebas)
1. En **WhatsApp > API Setup** encontrarás un token temporal
2. Este token expira en 24 horas (solo para pruebas)

### Access Token (Permanente para producción)
1. Ve a **Business Settings > System Users**
2. Crea un nuevo System User con rol de Admin
3. Click en **"Generate New Token"**
4. Selecciona tu app y los permisos:
   - `whatsapp_business_management`
   - `whatsapp_business_messaging`
5. Guarda el token de forma segura

### Phone Number ID
1. En **WhatsApp > Phone Numbers**, verás el `Phone Number ID`
2. Copia este ID, lo necesitarás para la API

### WhatsApp Business Account ID
1. En la configuración de WhatsApp encontrarás el `WhatsApp Business Account ID`

---

## Paso 7: Configurar Webhook

El webhook es la URL donde Meta enviará los mensajes entrantes.

### 7.1 Preparar tu endpoint

Tu servidor debe tener dos endpoints:

```
GET  /webhook  → Para verificación
POST /webhook  → Para recibir mensajes
```

### 7.2 Verificación del Webhook

Meta enviará una solicitud GET con estos parámetros:
- `hub.mode` = "subscribe"
- `hub.verify_token` = tu token secreto
- `hub.challenge` = código a devolver

Tu servidor debe:
1. Verificar que `hub.verify_token` coincida con tu token
2. Responder con el valor de `hub.challenge`

### 7.3 Configurar en Meta

1. Ve a **WhatsApp > Configuration**
2. Click en **"Edit"** en la sección Webhook
3. Ingresa:
   - **Callback URL:** `https://tu-app.vercel.app/api/webhook`
   - **Verify Token:** un token secreto que tú definas
4. Click en **"Verify and Save"**

### 7.4 Suscribirse a eventos

1. En la misma sección, click en **"Manage"**
2. Suscríbete a estos campos:
   - [x] `messages` (mensajes entrantes)
   - [x] `message_template_status_update` (estado de templates)
3. Click **"Done"**

---

## Paso 8: Verificar tu negocio (Para producción)

Para enviar mensajes a usuarios que no te han escrito primero:

1. Ve a **Business Settings > Business Info**
2. Completa toda la información del negocio
3. Sube documentos de verificación (RFC, comprobante de domicilio, etc.)
4. Espera la verificación (puede tomar días)

---

## Variables de entorno necesarias

Una vez completada la configuración, tendrás estas variables:

```env
# Meta WhatsApp API
WHATSAPP_ACCESS_TOKEN=tu_access_token_permanente
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=tu_business_account_id
WHATSAPP_VERIFY_TOKEN=tu_token_secreto_para_webhook

# API URLs
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
```

---

## Checklist final

- [ ] App creada en Meta for Developers
- [ ] WhatsApp agregado como producto
- [ ] Número de teléfono verificado y aprobado
- [ ] Display name aprobado
- [ ] Access token permanente generado
- [ ] Phone Number ID copiado
- [ ] Webhook URL configurado
- [ ] Eventos de webhook suscritos (messages)
- [ ] Negocio verificado (para producción)

---

## Recursos útiles

- [WhatsApp Developer Hub](https://business.whatsapp.com/developers/developer-hub)
- [Meta for Developers](https://developers.facebook.com)
- [Documentación oficial de Webhooks](https://business.whatsapp.com/blog/how-to-use-webhooks-from-whatsapp-business-api/)
- [Postman Collection para WhatsApp API](https://www.postman.com/meta/whatsapp-business-platform/collection/wlk6lh4/whatsapp-cloud-api)

---

## Modo de prueba (Sandbox)

Mientras configuras todo, puedes usar el número de prueba que Meta proporciona:
1. En **WhatsApp > API Setup** encontrarás un número de prueba
2. Agrega tu número personal como "Test Number"
3. Envía el código de verificación a tu WhatsApp
4. Ya puedes enviar/recibir mensajes de prueba
