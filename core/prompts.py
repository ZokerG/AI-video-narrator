def get_system_instruction(style: str = "viral", beat_pace: str = "fast") -> str:
    """
    Generates the system prompt based on style and pace preferences.
    """
    
    styles = {
        "viral": "El lenguaje debe sonar natural, como narrador de TikTok o Reels. Enérgico y enganchante.",
        "documentary": "El lenguaje debe ser más formal, informativo y pausado, estilo documental clásico.",
        "funny": "El lenguaje debe ser humorístico, sarcástico y divertido. Haz chistes sobre lo que ocurre.",
    }
    
    paces = {
        "fast": "Divide el video en beats cortos de 2 a 5 segundos (ritmo frenético).",
        "medium": "Divide el video en beats de 5 a 10 segundos (ritmo moderado).",
        "slow": "Divide el video en beats largos de 10 a 20 segundos (ritmo calmado).",
    }
    
    selected_style = styles.get(style, styles["viral"])
    selected_pace = paces.get(beat_pace, paces["fast"])

    return f"""
Analiza este video y genera una narración sincronizada en tiempo real.

Reglas estrictas:
- La narración debe acompañar lo que ocurre, no resumirlo después.
- {selected_pace}
- Cada beat debe tener SOLO una frase coherente con el tiempo asignado.
- {selected_style}
- No describas todo: reacciona solo a los momentos importantes.
- Devuelve SOLO JSON válido, sin texto adicional.

El audio generado debe poder reproducirse mientras el evento ocurre.
"""
