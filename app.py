import streamlit as st
from groq import Groq
 
# ═══════════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Desmontando la Carreta de Helios",
    page_icon="☀️",
    layout="wide",
)
 
# ═══════════════════════════════════════════════════════════════════════
# 2. ESTILOS GLOBALES
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Sidebar ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #12121f 100%);
}
 
/* ── Passport card ────────────────────────────────────── */
.passport-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #252545 100%);
    border: 1px solid #383860;
    border-radius: 14px;
    padding: 18px 20px 14px;
    color: #e0e0ff;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.5);
    margin-bottom: 14px;
}
.passport-row { margin: 7px 0; font-size: 0.97em; }
 
/* ── Stamps con color por personaje ──────────────────── */
.stamp-ptolemy   { color: #ff79c6; font-weight: 700; }
.stamp-aristarco { color: #8be9fd; font-weight: 700; }
.stamp-off       { color: #555570; }
 
/* ── Badges de personaje (aparecen sobre cada mensaje) ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 20px;
    padding: 3px 14px 3px 10px;
    font-weight: 700;
    font-size: 0.92em;
    margin-bottom: 8px;
    letter-spacing: 0.04em;
}
.badge-ptolomeo  { background: #3a0e3a; color: #ff79c6; border: 1px solid #ff79c6; }
.badge-aristarco { background: #0b2438; color: #8be9fd; border: 1px solid #8be9fd; }
.badge-helios    { background: #352d00; color: #f1fa8c; border: 1px solid #f1fa8c; }
 
/* ── Subtítulo de capítulo ────────────────────────────── */
.chapter-subtitle {
    font-size: 1.35rem;
    color: #8892b0;
    margin-top: -8px;
    margin-bottom: 6px;
    font-style: italic;
    letter-spacing: 0.05em;
}
.chapter-divider {
    text-align: center;
    color: #383860;
    font-size: 0.8rem;
    margin-bottom: 22px;
    letter-spacing: 0.35em;
}
</style>
""", unsafe_allow_html=True)
 
# ═══════════════════════════════════════════════════════════════════════
# 3. DEFINICIÓN DE PERSONAJES
#    avatar: emoji que aparece en la burbuja de chat
#    badge_class: clase CSS para el badge de color
#    label: texto del badge
#    stamp_class: clase CSS para el pasaporte epistémico
# ═══════════════════════════════════════════════════════════════════════
CHARS = {
    "Ptolomeo": {
        "avatar": "🏛️",                  # templo clásico → autoridad antigua
        "badge_class": "badge-ptolomeo",
        "label": "🏛️ Ptolomeo",
        "stamp_class": "stamp-ptolemy",
        "description": "Perspectiva Geocéntrica",
    },
    "Aristarco": {
        "avatar": "🔭",                   # telescopio → astrónomo visionario
        "badge_class": "badge-aristarco",
        "label": "🔭 Aristarco",
        "stamp_class": "stamp-aristarco",
        "description": "Perspectiva Heliocéntrica",
    },
    "Helios": {
        "avatar": "☀️",                   # sol → mediador socrático
        "badge_class": "badge-helios",
        "label": "☀️ Helios",
        "stamp_class": None,              # Helios no se sella en el pasaporte
        "description": "Mediador Socrático",
    },
}
 
# ═══════════════════════════════════════════════════════════════════════
# 4. INICIALIZACIÓN
# ═══════════════════════════════════════════════════════════════════════
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()
 
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
 
if "messages" not in st.session_state:
    st.session_state.messages = []
if "passport" not in st.session_state:
    st.session_state.passport = {"Ptolomeo": False, "Aristarco": False, "Shifts": 0}
 
# ═══════════════════════════════════════════════════════════════════════
# 5. ROUTER EPISTÉMICO
# ═══════════════════════════════════════════════════════════════════════
def epistemic_router(user_input: str):
    u = user_input.lower()
    if "ptolomeo" in u:
        return "Ptolomeo", (
            "Eres Claudio Ptolomeo (año 150 d.C.). Defiendes firmemente que la Tierra es el centro "
            "inmóvil del universo. Tus argumentos son empíricos: 'si la tierra se moviera, sentiríamos "
            "el viento' y 'las estrellas no muestran paralaje'. Habla con autoridad antigua, eres un "
            "científico cuidadoso y escéptico."
        )
    elif "aristarco" in u:
        return "Aristarco", (
            "Eres Aristarco de Samos (siglo III a.C.). Eres un revolucionario matemático. Defiendes "
            "que el Sol es mucho más grande que la Tierra y por lo tanto la Tierra debe girar a su "
            "alrededor. Tu tono es curioso y apasionado. Eres un visionario dispuesto a hacer hipótesis "
            "incluso cuando contradicen la intuición."
        )
    else:
        return "Helios", (
            "Eres Helios, un mediador socrático. Tu objetivo es que el estudiante dude de lo obvio. "
            "No des respuestas directas; haz preguntas que obliguen a contrastar las opiniones de "
            "Ptolomeo y Aristarco. Pregunta al usuario qué opina y también interésate por cómo "
            "llegó a esa opinión."
        )
 
# ═══════════════════════════════════════════════════════════════════════
# 6. HELPERS DE RENDERIZADO
# ═══════════════════════════════════════════════════════════════════════
def detect_agent(content: str) -> str:
    """Detecta qué personaje habla según el prefijo almacenado."""
    for name in ("Ptolomeo", "Aristarco", "Helios"):
        if f"[{name}]" in content:
            return name
    return "Helios"
 
def strip_prefix(content: str, agent_name: str) -> str:
    """Quita el prefijo **[Nombre]:** del texto almacenado."""
    prefix = f"**[{agent_name}]:** "
    return content[len(prefix):] if content.startswith(prefix) else content
 
# ═══════════════════════════════════════════════════════════════════════
# 7. BARRA LATERAL — PASAPORTE EPISTÉMICO
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("☀️ Helios está atento")
    st.markdown("### 📜 Pasaporte Epistémico")
    st.caption("Tu recorrido cognitivo en este capítulo")
 
    p = st.session_state.passport
 
    def stamp_html(visited: bool, char_key: str) -> str:
        char = CHARS[char_key]
        icon = "●" if visited else "○"
        css  = char["stamp_class"] if (visited and char["stamp_class"]) else "stamp-off"
        return (
            f'<div class="passport-row">'
            f'<span class="{css}">{icon} {char["label"]} — {char["description"]}</span>'
            f'</div>'
        )
 
    st.markdown(f"""
    <div class="passport-card">
        {stamp_html(p["Ptolomeo"], "Ptolomeo")}
        {stamp_html(p["Aristarco"], "Aristarco")}
        <hr style="border:none; border-top:1px solid #383860; margin:12px 0 10px;">
        <div style="font-size:0.85em; color:#bd93f9;">
            🔄 Giros de Pensamiento: <strong>{p["Shifts"]}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    with st.expander("🗺️ Guía de personajes"):
        st.markdown("""
        - 🎓 **Tú** — El viajero epistémico
        - 🏛️ **Ptolomeo** — Defensor del geocentrismo
        - 🔭 **Aristarco** — Defensor del heliocentrismo
        - ☀️ **Helios** — El mediador socrático
 
        *Tip: mencioná el nombre de cada personaje en tu mensaje para hablar con él.*
        """)
 
    st.write("---")
    if st.button("🔄 Reiniciar Sesión", use_container_width=True):
        st.session_state.messages = []
        st.session_state.passport = {"Ptolomeo": False, "Aristarco": False, "Shifts": 0}
        st.rerun()
 
# ═══════════════════════════════════════════════════════════════════════
# 8. ENCABEZADO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════
st.title("🌞 Desmontando la Carreta de Helios")
st.markdown(
    '<p class="chapter-subtitle">✦ Capítulo 1: El debate comienza ✦</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="chapter-divider">· · · ✦ · · ·</div>',
    unsafe_allow_html=True,
)
 
# ═══════════════════════════════════════════════════════════════════════
# 9. HISTORIAL DEL CHAT
# ═══════════════════════════════════════════════════════════════════════
for m in st.session_state.messages:
    if m["role"] == "user":
        with st.chat_message("user", avatar="🎓"):
            st.markdown(m["content"])
    else:
        agent = detect_agent(m["content"])
        char  = CHARS[agent]
        with st.chat_message("assistant", avatar=char["avatar"]):
            st.markdown(
                f'<span class="badge {char["badge_class"]}">{char["label"]}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(strip_prefix(m["content"], agent))
 
# ═══════════════════════════════════════════════════════════════════════
# 10. INPUT Y LÓGICA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════
if prompt := st.chat_input("🗣️ Habla con Ptolomeo, Aristarco o Helios…"):
 
    # ── guardar y mostrar mensaje del usuario ──
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🎓"):
        st.markdown(prompt)
 
    # ── routing y actualización del pasaporte ──
    agent_name, sys_prompt = epistemic_router(prompt)
    char = CHARS[agent_name]
 
    if agent_name in st.session_state.passport:
        st.session_state.passport[agent_name] = True
    if any(w in prompt.lower() for w in ["pero", "por qué", "duda", "entonces", "cambio"]):
        st.session_state.passport["Shifts"] += 1
 
    # ── respuesta con streaming ──
    with st.chat_message("assistant", avatar=char["avatar"]):
        # Badge con color del personaje aparece antes del texto
        st.markdown(
            f'<span class="badge {char["badge_class"]}">{char["label"]}</span>',
            unsafe_allow_html=True,
        )
        full_response = ""
        placeholder  = st.empty()
 
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    *[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages[-8:]
                    ],
                ],
                stream=True,
            )
 
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    placeholder.markdown(full_response + " ▌")
 
            placeholder.markdown(full_response)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**[{agent_name}]:** {full_response}",
            })
 
        except Exception as e:
            placeholder.empty()
            st.error(f"⚠️ Error de conexión: {e}")
            st.info("💡 Intentando reconectar con motor de reserva…")

