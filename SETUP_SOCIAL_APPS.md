# Guía de Configuración de Apps Sociales

Para que la aplicación pueda publicar en redes sociales, necesitas crear "Apps" en las plataformas de desarrolladores de Meta y TikTok.

## 1. Facebook & Instagram (Meta for Developers)

**Objetivo:** Obtener `FACEBOOK_CLIENT_ID` y `FACEBOOK_CLIENT_SECRET`.

1.  Ve a [Meta for Developers](https://developers.facebook.com/).
2.  Haz clic en **"Mis Apps"** > **"Crear App"**.
3.  **Tipo de App:** Selecciona **"Negocios"** (Business) o "Otro" > "Negocios".
4.  **Detalles:** Ponle un nombre (ej: "AI Video Narrator") y tu email.
5.  **Añadir Productos:**
    *   Busca **"Inicio de sesión con Facebook"** (Facebook Login) y dale a "Configurar".
    *   Selecciona **"Web"**.
    *   **URL del sitio:** Pon `http://localhost:8000/` (para desarrollo).
6.  **Configuración del Login:**
    *   Ve al menú lateral: **Inicio de sesión con Facebook > Configuración**.
    *   En **"URI de redireccionamiento de OAuth válidos"**, añade:
        *   `http://localhost:8000/auth/facebook/callback`
        *   `http://localhost:8000/auth/instagram/callback`
    *   Guarda los cambios.
7.  **Obtener Credenciales:**
    *   Ve al menú lateral: **Configuración > Básica**.
    *   Copia el **Identificador de la app (App ID)** -> Esto es tu `FACEBOOK_CLIENT_ID`.
    *   Copia la **Clave secreta de la app (App Secret)** -> Esto es tu `FACEBOOK_CLIENT_SECRET`.
8.  **Usuarios de Prueba:**
    *   Como la app está en "Modo Desarrollo", solo tú podrás loguearte. Si quieres probar con otros usuarios, agrégalos en **Roles > Usuarios de prueba**.

---

## 2. TikTok for Developers

**Objetivo:** Obtener `TIKTOK_CLIENT_KEY` y `TIKTOK_CLIENT_SECRET`.

1.  Ve a [TikTok for Developers](https://developers.tiktok.com/).
2.  Regístrate/Inicia sesión y dale a **"My Apps"**.
3.  Haz clic en **"Connect a new app"** (o "Create App").
4.  **Detalles:**
    *   Sube un icono (obligatorio).
    *   Nombre: "AI Video Narrator".
    *   Categoría: Elige la que mejor encaje (ej. "Utilities").
5.  **Configuración de Productos (Capabilities):**
    *   Asegúrate de añadir **"Login Kit"** y **"Content Posting API"** (o "Share Kit").
    *   Necesitarás permisos como `user.info.basic` y `video.upload`.
6.  **Configuración OAuth:**
    *   Busca la sección de **Redirect URI**.
    *   Añade: `http://localhost:8000/auth/tiktok/callback`
7.  **Obtener Credenciales:**
    *   Una vez creada, verás el **Client Key** y **Client Secret** en el dashboard de la app.
8.  **Estado:**
    *   Al principio la app estará en revisión o sandbox. Para pruebas locales, asegúrate de añadir tu cuenta de TikTok como "Tester" si es requerido, o espera la aprobación para acceso público.

---

## 3. Configuración en tu Proyecto

Abre el archivo `.env` y pega los valores obtenidos:

```ini
# Meta Apps (Facebook & Instagram)
FACEBOOK_CLIENT_ID=1234567890...
FACEBOOK_CLIENT_SECRET=abcdef123456...

# TikTok for Developers
TIKTOK_CLIENT_KEY=aw345...
TIKTOK_CLIENT_SECRET=sq123...
```
