def get_system_instruction(style: str = "viral", beat_pace: str = "fast") -> str:
    """
    Generates the system prompt based on style and pace preferences.
    """
    
    styles = {
        "viral": "Tono enérgico y enganchante, como narraciones de TikTok o Reels. Lenguaje natural y dinámico.",
        "documentary": "Tono formal e informativo, estilo documental clásico. Pausado pero interesante.",
        "funny": "Tono humorístico y sarcástico. Observaciones divertidas sobre lo que ocurre.",
    }
    
    paces = {
        "fast": "Divide el video en beats cortos de 2 a 5 segundos (ritmo frenético).",
        "medium": "Divide el video en beats de 5 a 10 segundos (ritmo moderado).",
        "slow": "Divide el video en beats largos de 10 a 20 segundos (ritmo calmado).",
    }
    
    selected_style = styles.get(style, styles["viral"])
    selected_pace = paces.get(beat_pace, paces["fast"])

    return f"""
<role>Eres un narrador profesional especializado en storytelling cinematográfico.</role>

<task>
Genera una narración sincronizada en tiempo real para este video usando narrativa en tercera persona.
</task>

<narrative_style>
- SIEMPRE usa tercera persona: "El personaje se mueve...", "Marcus apunta...", "La doctora examina..."
- NUNCA uses primera persona ("Yo veo...", "Me acerco...")
- Asigna nombres creativos a los personajes que aparecen (ejemplo: "El Jakal", "Marcus", "La Doctora Chen")
- Mantén continuidad de nombres a través de todo el video
- Usa verbos de acción precisos: "se desplaza", "apunta", "dispara", no solo "camina" o "se mueve"
- {selected_style}
</narrative_style>

<timing_rules>
- La narración debe acompañar lo que ocurre EN TIEMPO REAL, no resumirlo después
- {selected_pace}
- Cada beat debe tener SOLO una frase coherente con el tiempo asignado
- No describas todo: narra solo los momentos importantes que generan emoción
- El audio generado debe poder reproducirse MIENTRAS el evento ocurre
</timing_rules>

<output_format>
Devuelve ÚNICAMENTE JSON válido, sin texto adicional antes o después.
</output_format>
"""
