Perfecto. Te dejo **EL ARCHIVO `.md` listo** para que se lo pases **tal cual** a tu ayudante de IA (o a otra IA encargada de implementar).
Está pensado **a nivel de producto + técnico**, sin relleno, y describe **exactamente** el flujo que planteamos.

Puedes copiarlo y guardarlo como, por ejemplo:

```
gemini-vision-video-narration.md
```

---

# 📽️ Sistema de Narración de Video Sincronizada con Gemini Vision

## 1. Objetivo del sistema

Construir un sistema que:

* Analice fragmentos de video cortos (**30 a 90 segundos**).
* Detecte eventos visuales relevantes a lo largo del tiempo.
* Genere una **narración progresiva**, que se reproduzca **mientras ocurren los eventos** (no un resumen posterior).
* Produzca una salida **estructurada en JSON**, lista para:

  * Generación de audio con **Text-to-Speech (TTS)**.
  * Sincronización precisa con el timeline del video.
* Oriente el resultado a **videos para redes sociales** (TikTok / Reels / Shorts).

---

## 2. Principios clave del diseño

Este sistema **NO** debe:

* Resumir el video al final.
* Generar un solo audio largo.
* Describir cada frame.

Este sistema **SÍ** debe:

* Acompañar lo que ocurre en el video.
* Usar frases cortas, naturales y reactivas.
* Dividir el video en **micro-beats temporales**.
* Mantener ritmo y atención.

> Regla de oro:
> **El narrador habla mientras el evento ocurre, no después.**

---

## 3. Concepto central: Micro-beats narrativos

Un **beat** es un segmento corto del video donde ocurre algo relevante.

Características:

* Duración: **2 a 5 segundos**
* Una sola idea
* Una sola frase de narración
* Tiempo aproximado (no necesita precisión de frame)

---

## 4. Flujo general del sistema

```text
Video (30–90s)
   ↓
Gemini Vision (análisis temporal del video)
   ↓
Salida JSON con beats y timestamps
   ↓
Text-to-Speech (1 audio por beat)
   ↓
Reproductor / Editor sincroniza audio + video
```

---

## 5. Rol del modelo de Visión (Gemini)

El modelo debe:

* Analizar el video como una **secuencia temporal**.
* Identificar:

  * Cambios de acción
  * Reacciones
  * Eventos inesperados
  * Texto en pantalla (si existe)
* Asociar **lenguaje a tiempo**, no solo a contenido.

---

## 6. Formato de salida requerido (JSON estricto)

El modelo debe devolver **SOLO JSON válido**, sin markdown ni explicaciones.

```json
{
  "language": "es",
  "duration_s": 0,
  "overall": {
    "hook": "Frase corta de apertura",
    "one_sentence_summary": "Resumen en una frase",
    "tone": "intriga | humor | drama | informativo",
    "content_warnings": []
  },
  "beats": [
    {
      "id": 1,
      "start_s": 0.0,
      "end_s": 3.2,
      "visual_summary": "Qué ocurre visualmente",
      "key_visuals": ["elemento", "acción"],
      "on_screen_text": null,
      "audio_context": {
        "dialogue_brief": null,
        "sound_cues": ["sonido ambiente"]
      },
      "voiceover": {
        "script": "Frase corta narrada",
        "subtitle": "Subtítulo corto (≤ 70 caracteres)"
      }
    }
  ],
  "final_cta": "Pregunta o llamada a la acción opcional"
}
```

---

## 7. Reglas estrictas para la narración

El modelo debe cumplir TODAS:

1. Usar **entre 3 y 6 beats**.
2. Cada `voiceover.script`:

   * Máximo **1 o 2 frases**.
   * Lenguaje conversacional.
   * Natural, no técnico.
3. No describir todo lo que se ve.
4. Reaccionar solo a lo importante.
5. Si algo no es claro:

   * Usar `null`
   * O marcarlo como aproximado
   * **Nunca inventar**

---

## 8. Prompt base para Gemini Vision (producción)

Este prompt debe usarse como instrucción principal:

```
Analiza este video y genera una narración sincronizada en tiempo real.

Reglas estrictas:
- La narración debe acompañar lo que ocurre, no resumirlo después.
- Divide el video en beats cortos de 2 a 5 segundos.
- Cada beat debe tener SOLO una frase corta.
- El lenguaje debe sonar natural, como narrador de TikTok o Reels.
- No describas todo: reacciona solo a los momentos importantes.
- Devuelve SOLO JSON válido, sin texto adicional.

El audio generado debe poder reproducirse mientras el evento ocurre.
```

---

## 9. Integración con Text-to-Speech (TTS)

* Generar **un archivo de audio por beat**.
* Nunca unir todos los beats en un solo audio.
* El reproductor debe:

  * Monitorear `currentTime` del video.
  * Disparar el audio cuando `currentTime >= start_s`.

Ejemplo lógico:

```js
if (video.currentTime >= beat.start_s) {
  play(beat.audio)
}
```

---

## 10. Resultado esperado

El resultado final debe sentirse como:

* Un narrador reaccionando en tiempo real.
* Ritmo ágil.
* Audio sincronizado con acción.
* Estilo viral y natural.

No debe sentirse como:

* Un documental.
* Un resumen leído.
* Un voice-over largo y plano.

---

## 11. Extensiones futuras (opcional)

* Ajustar estilo por prompt:

  * misterio
  * humor
  * deportivo
  * cine / recap
* Live API para análisis en streaming.
* Generación automática de subtítulos animados.
* Detección de momentos “clippeables”.

---

## 12. Métrica de éxito

* El audio entra **mientras ocurre el evento**.
* Las frases no se pisan entre sí.
* El espectador entiende sin mirar.
* Retención alta en los primeros segundos.

---

### ✅ Fin del documento

Si quieres, en el próximo mensaje puedo:

* Ajustar esto a **arquitectura concreta** (backend, colas, latencias).
* Traducirlo a un **prompt técnico para otra IA programadora**.
* Adaptarlo a **Gemini Live / streaming**.

Dime cómo lo vas a implementar (backend / frontend / stack) y lo bajamos a código.
