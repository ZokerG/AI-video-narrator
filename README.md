# 🎬 AI Video Narrator (Quinesis)

**Plataforma de generación y análisis de video impulsada por IA.**  
Transforma videos en bruto en contenido viral narrado, analiza estructuras visuales y genera guiones optimizados para redes sociales (Reels, TikTok, Shorts).

---

## 🚀 Características Principales

### 🧠 Análisis de Video con IA
- **Visión Artificial (Gemini 2.0)**: Entiende lo que sucede en el video segundo a segundo.
- **Detección de "Beats"**: Identifica los momentos visuales clave para sincronizar la narración.
- **Generación de Guiones**: Crea narrativas coherentes en diferentes estilos (Viral, Horror, Curioso, Motivacional).

### 🗣️ Narración y Audio Pro
- **Text-to-Speech (ElevenLabs)**: Voces ultra-realistas clonadas o predefinidas.
- **Sincronización Automática**: Ajusta la velocidad del habla para encajar perfectamente con los segmentos de video.
- **Mezcla de Audio**: Combina voz, música de fondo (con ducking automático) y audio original.

### 📱 Viral Shorts Generator
- **Modo "Reel Instantáneo"**: Sube un video y obtén un Reel listo para publicar en minutos.
- **Hooks Virales**: Estructuras de guion diseñadas para retención (Hook 0-3s, Desarrollo, CTA).

### 🔐 Seguridad y Usuarios
- **OAuth 2.0**: Login con Google, Facebook, Instagram, TikTok.
- **Sistema de Créditos**: Gestión de cuotas por usuario.
- **Almacenamiento Seguro**: Integración con S3/MinIO para assets y resultados.

---

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una estructura **Monorepo** con **Clean Architecture** en el backend.

```
/
├── docker-compose.yml       # Orquestación de servicios
├── backend/                 # API REST (Python/FastAPI)
│   ├── src/
│   │   ├── domain/          # Entidades y reglas de negocio (Puro)
│   │   ├── application/     # Casos de uso (Lógica de la aplicación)
│   │   ├── infrastructure/  # Adaptadores (DB, MinIO, Gemini, ElevenLabs)
│   │   └── presentation/    # API Endpoints
│   └── Dockerfile
├── frontend/                # Interfaz de Usuario (Next.js 14)
│   ├── src/                 # App Router, Componentes, Hooks
│   └── Dockerfile
└── postgres_data/           # Persistencia de BD (Docker volume)
```

### Stack Tecnológico
- **Backend**: Python 3.11, FastAPI, SQLModel/SQLAlchemy, MoviePy.
- **Frontend**: Next.js 14, React, TailwindCSS, TypeScript.
- **IA**: Google Gemini 1.5/2.0 Pro.
- **Infraestructura**: Docker, PostgreSQL, MinIO (S3 Compatible).

---

## 🛠️ Instalación y Uso

### Opción A: Docker (Recomendada)
Levanta todo el sistema con un solo comando.

1. **Configura las variables de entorno**:
   Crea un archivo `backend/.env` (basado en `.env.example` si existiera) con tus keys de Gemini, ElevenLabs, DB, etc.

2. **Ejecuta Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Accede a la aplicación**:
   - **Frontend**: http://localhost:3000
   - **Backend API Docs**: http://localhost:8000/docs
   - **Base de Datos**: Puerto 5432

### Opción B: Ejecución Local (Desarrollo)

#### 1. Backend
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
uvicorn src.presentation.main:app --reload
```

#### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Variables de Entorno Clave

Asegúrate de configurar estas variables en `backend/.env`:

```env
# Base de Datos
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname

# IA & Servicios
GOOGLE_API_KEY=tu_api_key_gemini
ELEVENLABS_API_KEY=tu_api_key_elevenlabs

# Seguridad
JWT_SECRET_KEY=tu_secreto_super_seguro
JWT_ALGORITHM=HS256

# Almacenamiento
MINIO_ENDPOINT=play.min.io
MINIO_ACCESS_KEY=tu_access_key
MINIO_SECRET_KEY=tu_secret_key
BUCKET_NAME=quinesis-videos
```

---

## 🤝 Contribuir
1. Haz fork del repositorio.
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`).
3. Commit de tus cambios (`git commit -m 'Add amazing feature'`).
4. Push a la rama (`git push origin feature/amazing-feature`).
5. Abre un Pull Request.
