import streamlit as st
import html
import os
import math
from groq import Groq
from PIL import Image, ImageDraw, ImageFont

# 1. Configuración visual y de página
st.set_page_config(page_title="Helios System — Piloto", page_icon="☀️", layout="wide")

# ──────────────────────────────────────────────
# GENERACIÓN DE AVATARES PERSONALIZADOS CON PIL
# ──────────────────────────────────────────────
AVATAR_DIR = ".avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)

def _font(size):
    for name in ["arial.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()

def _avatar_ptolomeo(path):
    """🌍 Tierra en el centro — geocéntrico, tonos dorados."""
    s = 200
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, s, s], fill=(201, 162, 39, 255))
    d.ellipse([8, 8, s - 8, s - 8], fill=(30, 20, 8, 255))
    cx, cy = s // 2, s // 2
    for r in (32, 48, 64):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(201, 162, 39, 160), width=1)
    # Tierra en el centro
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(100, 180, 255, 255))
    # Planetas en órbitas
    for ang, r in [(30, 32), (160, 48), (280, 64)]:
        rad = math.radians(ang)
        x, y = cx + r * math.cos(rad), cy + r * math.sin(rad)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 230, 150, 255))
    img.save(path)

def _avatar_aristarco(path):
    """☀️ Sol en el centro — heliocéntrico, tonos celestes."""
    s = 200
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, s, s], fill=(139, 233, 253, 255))
    d.ellipse([8, 8, s - 8, s - 8], fill=(8, 25, 40, 255))
    cx, cy = s // 2, s // 2
    # Sol
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(255, 220, 100, 255))
    for ang in range(0, 360, 40):
        rad = math.radians(ang)
        x1, y1 = cx + 22 * math.cos(rad), cy + 22 * math.sin(rad)
        x2, y2 = cx + 34 * math.cos(rad), cy + 34 * math.sin(rad)
        d.line([x1, y1, x2, y2], fill=(255, 220, 100, 255), width=3)
    # Órbita terrestre
    d.ellipse([cx - 56, cy - 56, cx + 56, cy + 56], outline=(139, 233, 253, 130), width=1)
    # Tierra
    ex, ey = cx + 56, cy
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(100, 180, 255, 255))
    img.save(path)

def _avatar_helios(path):
    """👁️ Mediador solar — ojo omnisciente, tonos amarillos."""
    s = 200
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, s, s], fill=(241, 250, 140, 255))
    d.ellipse([8, 8, s - 8, s - 8], fill=(40, 35, 10, 255))
    cx, cy = s // 2, s // 2
    # Ojo
    d.ellipse([cx - 38, cy - 22, cx + 38, cy + 22], fill=(241, 250, 140, 255))
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(40, 35, 10, 255))
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 200, 50, 255))
    # Rayos solares
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        x1, y1 = cx + 48 * math.cos(rad), cy + 32 * math.sin(rad)
        x2, y2 = cx + 60 * math.cos(rad), cy + 42 * math.sin(rad)
        d.line([x1, y1, x2, y2], fill=(241, 250, 140, 200), width=2)
    img.save(path)

def _avatar_user(path):
    """🧑 Viajero — silueta, tonos rosados."""
    s = 200
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, s, s], fill=(255, 121, 198, 255))
    d.ellipse([8, 8, s - 8, s - 8], fill=(30, 30, 46, 255))
    cx, cy = s // 2, s // 2
    # Cabeza
    d.ellipse([cx - 20, cy - 35, cx + 20, cy + 5], fill=(255, 121, 198, 255))
    # Cuerpo
    d.pieslice([cx - 35, cy - 5, cx + 35, cy + 75], 180, 360, fill=(255, 121, 198, 255))
    img.save(path)

# Generar o cargar avatares (con fallback a emoji)
_AVATAR_CREATORS = {
    "Ptolomeo": ("ptolomeo.png", _avatar_ptolomeo),
    "Aristarco": ("aristarco.png", _avatar_aristarco),
    "Helios": ("helios.png", _avatar_helios),
    "user": ("user.png", _avatar_user),
}
_EMOJI_FALLBACK = {"Ptolomeo": "🌍", "Aristarco": "🌟", "Helios": "🏛️", "user": "🧭"}

AVATARS = {}
for _name, (_fname, _creator) in _AVATAR_CREATORS.items():
    _path = os.path.join(AVATAR_DIR, _fname)
    try:
        if not os.path.exists(_path):
            _creator(_path)
        AVATARS[_name] = _path
    except Exception:
        AVATARS[_name] = _EMOJI_FALLBACK[_name]

# Paleta de colores por personaje
COLORS = {
    "Ptolomeo": "#ffb86c",   # Ámbar dorado
    "Aristarco": "#8be9fd",  # Cian celeste
    "Helios": "#f1fa8c",     # Amarillo solar
    "user": "#e6e6e6",       # Blanco suave
}

# ──────────────────────────────────────────────
# ESTILOS CSS PERSONALIZADOS
# ──────────────────────────────────────────────
st.markdown("""
<style>
.stChatFloatingInputContainer { background-color: rgba(0,0,0,0); }

.stApp {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #1a1a2e 100%);
}

/* —— Pasaporte Epistémico —— */
.passport-card {
    background: linear-gradient(145deg, #1e1e2e, #2a2a40);
    border: 1px solid #44475a;
    border-radius: 14px;
    padding: 22px;
    color: white;
    box-shadow: 0 4px 18px rgba(0,0,0,0.5);
}
.stamp-on  { color: #50fa7b; font-weight: bold; font-size: 1.05em; }
.stamp-off { color: #6272a4; font-size: 1.05em; }

/* —— Título principal con degradado —— */
.main-title-text {
    background: linear-gradient(90deg, #ffb86c, #ff79c6, #bd93f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    font-size: 2.6em;
    margin-bottom: 0.1em;
}

/* —— Subtítulo del Capítulo (MÁS GRANDE) —— */
.chapter-subtitle {
    font-size: 1.6em !important;
    color: #f1fa8c;
    font-weight: 600;
    font-style: italic;
    letter-spacing: 0.5px;
    text-shadow: 0 0 12px rgba(241,250,140,0.25);
    margin-top: 0.2em;
    margin-bottom: 0.5em;
}

/* —— Título del sidebar —— */
.sidebar-glow {
    background: linear-gradient(90deg, #f1fa8c, #ffb86c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
}

/* —— Caja de bienvenida —— */
.welcome-card {
    background: linear-gradient(145deg, #1e1e2e, #2a2a40);
    padding: 20px 24px;
    border-radius: 14px;
    border-left: 4px solid #f1fa8c;
    margin: 1em 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

/* —— Avatares un poco más grandes —— */
[data-testid="stChatMessageAvatar"] { font-size: 1.6rem; }

/* —— Input del chat más vistoso —— */
.stChatInput textarea {
    background-color: rgba(30,30,46,0.9) !important;
    border: 1px solid #44475a !important;
    border-radius: 12px !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 2. INICIALIZACIÓN DE API Y ESTADO
# ──────────────────────────────────────────────
if "GROQ_API_KEY" not in st.secrets:
    st.error("Falta la API Key en los Secrets de Streamlit.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "passport" not in st.session_state:
    st.session_state.passport = {"Ptolomeo": False, "Aristarco": False, "Shifts": 0}

# ──────────────────────────────────────────────
# 3. LÓGICA DEL EPISTEMIC ROUTER
# ──────────────────────────────────────────────
def epistemic_router(user_input):
    u = user_input.lower()
    if "ptolomeo" in u:
        return "Ptolomeo", (
            "Eres Claudio Ptolomeo (año 150 d.C.). Defiendes firmemente que la Tierra es "
            "el centro inmóvil del universo. Tus argumentos son empíricos: 'si la tierra "
            "se moviera, sentiríamos el viento' y 'las estrellas no muestran paralaje'. "
            "Habla con autoridad antigua, eres un científico cuidadoso y escéptico."
        )
    elif "aristarco" in u:
        return "Aristarco", (
            "Eres Aristarco de Samos (siglo III a.C.). Eres un revolucionario matemático. "
            "Defiendes que el Sol es mucho más grande que la Tierra y por lo tanto la "
            "Tierra debe girar a su alrededor. Tu tono es curioso. Eres un visionario "
            "dispuesto a hacer hipótesis incluso cuando contradicen la intuición."
        )
    else:
        return "Helios", (
            "Eres Helios, un mediador socrático. Tu objetivo es que el estudiante dude "
            "de lo obvio. No des respuestas directas; haz preguntas que obliguen a "
            "contrastar las opiniones de Ptolomeo y Aristarco. Pregunta al usuario qué "
            "opina y también te interesas por cómo llegó a esa opinión."
        )

# ──────────────────────────────────────────────
# 4. BARRA LATERAL — PASAPORTE EPISTÉMICO
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h1 class='sidebar-glow'>☀️ Helios está atento</h1>", unsafe_allow_html=True)
    st.markdown("### 🧭 Progreso del Viajero Epistémico")
    st.markdown("En este panel se registra tu recorrido cognitivo.")

    p = st.session_state.passport
    st.markdown(f"""
    <div class="passport-card">
        <p class="{'stamp-on' if p['Ptolomeo'] else 'stamp-off'}">
            {'🟢' if p['Ptolomeo'] else '⚪'} <b>Ptolomeo</b> · Perspectiva Geocéntrica 🌍
        </p>
        <p class="{'stamp-on' if p['Aristarco'] else 'stamp-off'}">
            {'🟢' if p['Aristarco'] else '⚪'} <b>Aristarco</b> · Perspectiva Heliocéntrica 🌟
        </p>
        <hr>
        <p style='font-size:0.95em;'>
            🔄 Giros de Pensamiento: <b style='color:#ff79c6'>{p['Shifts']}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    if st.button("🔄 Reiniciar Sesión", use_container_width=True):
        st.session_state.messages = []
        st.session_state.passport = {"Ptolomeo": False, "Aristarco": False, "Shifts": 0}
        st.rerun()

# ──────────────────────────────────────────────
# 5. CHAT PRINCIPAL
# ──────────────────────────────────────────────
st.markdown("<h1 class='main-title-text'>Desmontando la Carreta de Helios</h1>",
            unsafe_allow_html=True)
st.markdown("<p class='chapter-subtitle'>📜 Capítulo 1: El debate comienza</p>",
            unsafe_allow_html=True)

# Mensaje de bienvenida si no hay historial
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <p style='color:#f1fa8c; font-size:1.1em; line-height:1.6;'>
            <b>🏛️ [Helios]:</b> Bienvenido, viajero. Hoy te encuentras en la plaza donde
            dos astrónomos separados por siglos debaten sobre el cosmos.<br><br>
            Escribe <b style="color:#ffb86c;">"Ptolomeo"</b> para escuchar al defensor de
            la Tierra como centro del universo.<br>
            Escribe <b style="color:#8be9fd;">"Aristarco"</b> para invocar al visionario
            que pone al Sol en el centro.<br><br>
            ¿Quién crees que tiene razón? 🤔
        </p>
    </div>
    """, unsafe_allow_html=True)

# Mostrar historial con colores y avatares por personaje
for m in st.session_state.messages:
    if m["role"] == "user":
        with st.chat_message("user", avatar=AVATARS["user"]):
            st.markdown(
                f'<div style="color:{COLORS["user"]}; white-space:pre-wrap; '
                f'line-height:1.5;">{html.escape(m["content"])}</div>',
                unsafe_allow_html=True,
            )
    else:
        agent = m.get("agent", "Helios")
        color = COLORS.get(agent, COLORS["Helios"])
        with st.chat_message("assistant", avatar=AVATARS.get(agent, AVATARS["Helios"])):
            st.markdown(
                f'<div style="color:{color}; white-space:pre-wrap; line-height:1.5;">'
                f'<b>[{agent}]:</b> {html.escape(m["content"])}</div>',
                unsafe_allow_html=True,
            )

# Entrada de usuario
if prompt := st.chat_input("Pregúntale algo a Ptolomeo o Aristarco..."):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(
            f'<div style="color:{COLORS["user"]}; white-space:pre-wrap; '
            f'line-height:1.5;">{html.escape(prompt)}</div>',
            unsafe_allow_html=True,
        )

    # Determinar agente
    agent_name, sys_prompt = epistemic_router(prompt)

    # Actualizar Pasaporte
    if agent_name in st.session_state.passport:
        st.session_state.passport[agent_name] = True
    if any(w in prompt.lower() for w in ["pero", "por qué", "duda", "entonces", "cambio"]):
        st.session_state.passport["Shifts"] += 1

    # Respuesta con streaming
    with st.chat_message("assistant", avatar=AVATARS.get(agent_name, AVATARS["Helios"])):
        color = COLORS.get(agent_name, COLORS["Helios"])
        full_response = ""
        placeholder = st.empty()

        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    *[{"role": m["role"], "content": m["content"]}
                      for m in st.session_state.messages[-8:]],
                ],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(
                        f'<div style="color:{color}; white-space:pre-wrap; '
                        f'line-height:1.5;"><b>[{agent_name}]:</b> '
                        f'{html.escape(full_response)}▌</div>',
                        unsafe_allow_html=True,
                    )

            placeholder.markdown(
                f'<div style="color:{color}; white-space:pre-wrap; line-height:1.5;">'
                f'<b>[{agent_name}]:</b> {html.escape(full_response)}</div>',
                unsafe_allow_html=True,
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response, "agent": agent_name}
            )

        except Exception as e:
            st.error(f"Error de conexión: {str(e)}")
            st.info("Intentando reconectar con motor de reserva...")
