# QUINESIS AI - Video Narrator 🎬🧠

> **Transforma videos en historias virales impulsadas por IA.**

Quinesis es una plataforma de última generación que automatiza la creación de contenido narrativo. Utilizando modelos multimodales avanzados (Gemini 2.0 Flash) y síntesis de voz hiperrealista (ElevenLabs), Quinesis analiza tus videos, entiende el contexto visual y genera narraciones cautivadoras perfectamente sincronizadas.

![Quinesis Banner](frontend/src/app/logo/logo.png) (Logo Placeholder)

---

## 🚀 Características Principales

*   **👁️ Análisis Visual Profundo con IA**: Nuestra IA "mira" tu video cuadro a cuadro, entendiendo acciones, emociones y contextos para generar guiones coherentes.
*   **✍️ Generación de Guiones Creativos**: No más bloqueo del escritor. Obtén guiones optimizados para diferentes estilos:
    *   *Viral/TikTok*: Dinámico, rápido y enganchador.
    *   *Documental*: Informativo, serio y elegante.
    *   *Comedia*: Divertido, sarcástico y entretenido.
*   **🗣️ Voces Ultra-Realistas**: Integración nativa con ElevenLabs para voces que suenan humanas, con entonación y emoción real.
*   **🔌 Integración Social (Multi-Plataforma)**: Conecta tus cuentas y publica directamente:
    *   Facebook Pages
    *   Instagram Reels
    *   TikTok
*   **⚡ Arquitectura Moderna y Escalable**: Construido sobre microservicios containerizados listos para escalar.

## 🛠️ Stack Tecnológico

La arquitectura de Quinesis está diseñada para rendimiento y mantenibilidad.

### **Backend (Python & FastAPI)**
*   **Framework**: FastAPI (Alto rendimiento, asíncrono).
*   **IA Core**: Google Gemini 2.0 Flash (Visión + Texto).
*   **TTS Engine**: ElevenLabs API.
*   **Base de Datos**: PostgreSQL (Persistencia de usuarios y videos) + SQLAlchemy (ORM Async).
*   **Almacenamiento**: MinIO (Compatible con S3) para gestión de archivos de video y audio.
*   **Autenticación**: JWT + OAuth 2.0 (Redes Sociales).

### **Frontend (Next.js & TypeScript)**
*   **Framework**: Next.js 16 (React Server Components).
*   **Estilos**: TailwindCSS + Framer Motion.
*   **UI Components**: Diseño minimalista "Premium", iconos Lucide-React.
*   **Gestión de Estado**: Context API para Auth y UX fluida.

### **Infraestructura**
*   **Contenedores**: Docker & Docker Compose.
*   **Servicios Externos**: Google Cloud (Vertex AI/Studio), Meta Graph API, TikTok Developers.

---

## 🏁 Instalación y Despliegue Local

### Prerrequisitos
*   Docker & Docker Compose
*   Node.js 18+
*   Python 3.10+
*   Claves de API: Google Gemini, ElevenLabs.

### 1. Configuración del Entorno
Clona el repositorio y configura las variables de entorno.

```bash
git clone https://github.com/tu-usuario/quinesis.git
cd quinesis
cp .env.example .env
```

Edita `.env` con tus claves (Ver `SETUP_SOCIAL_APPS.md` para configurar redes sociales).

### 2. Levantar Servicios Base (DB & MinIO)
```bash
docker-compose up -d
```

### 3. Iniciar Backend
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python api.py
```

### 4. Iniciar Frontend
```bash
cd frontend
npm install
npm run dev
```

Visita `http://localhost:3000` y ¡listo!

---

## 🔮 Roadmap: Hacia Dónde Vamos

Quinesis está en constante evolución. Aquí está nuestra visión para el futuro:

*   [ ] **Editor de Guiones en Tiempo Real**: Permitir al usuario ajustar el guion generado antes de sintetizar el audio.
*   [ ] **Doblaje Automático (AI Dubbing)**: Traducir y doblar videos manteniendo la voz original del usuario.
*   [ ] **Subtítulos Animados**: Generación automática de subtítulos estilo "Karaoke" quemados en el video.
*   [ ] **Música de Fondo Inteligente**: Selección automática de banda sonora libre de derechos basada en el "mood" del video.
*   [ ] **SaaS Multi-Tenant**: Paneles de administración para equipos y agencias.

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor, abre un issue para discutir cambios mayores antes de enviar un Pull Request.

---

**Quinesis AI** - *Donde la visión se encuentra con la voz.*
© 2026 Tu Nombre / Tu Organización.
