import streamlit as st
import html
import os
import math
import json
import threading
from groq import Groq
from PIL import Image, ImageDraw, ImageFont

# ──────────────────────────────────────────────
# MICRO-EVALUADOR DE GIROS EPISTÉMICOS
# ──────────────────────────────────────────────
EVALUADOR_PROMPT = """
Eres un evaluador pedagógico. Analiza el último mensaje del estudiante
en el contexto de la conversación y determina si muestra un giro epistémico genuino.

Un giro ES genuino si el estudiante:
- Puede argumentar una perspectiva contraria a la suya en sus propias palabras
  (no solo citarla: "Ptolomeo diría X porque Y")
- Expresa duda razonada sobre algo que antes daba por seguro, con argumento
- Compara activamente las dos perspectivas mostrando que entendió ambas
- Formula una pregunta que solo puede surgir de haber comprendido una posición

Un giro NO es genuino si:
- Solo repite información que el personaje acaba de decir
- Expresa cambio emocional sin argumento ("ah, ahora creo que Aristarco tiene razón")
- Usa palabras de contraste ("pero", "entonces") sin contenido reflexivo real

Responde SOLO con JSON: {"giro": true} o {"giro": false}
"""

def evaluar_giro_thread(client, recent_messages, result_container):
    """Función que corre en un hilo paralelo para evaluar el giro epistémico."""
    try:
        response = client.chat.completions.create(
            # Usamos un modelo rápido y barato para esta micro-tarea
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": EVALUADOR_PROMPT},
                *recent_messages
            ],
            max_tokens=20,
            temperature=0.0,
        )
        text = response.choices[0].message.content.strip()
        
        # Limpieza por si el modelo devuelve markdown (```json ... ```)
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            
        data = json.loads(text)
        result_container["giro"] = data.get("giro", False)
    except Exception as e:
        print(f"Error en microevaluador paralelo: {e}")
        result_container["giro"] = False

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
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(100, 180, 255, 255))
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
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(255, 220, 100, 255))
    for ang in range(0, 360, 40):
        rad = math.radians(ang)
        x1, y1 = cx + 22 * math.cos(rad), cy + 22 * math.sin(rad)
        x2, y2 = cx + 34 * math.cos(rad), cy + 34 * math.sin(rad)
        d.line([x1, y1, x2, y2], fill=(255, 220, 100, 255), width=3)
    d.ellipse([cx - 56, cy - 56, cx + 56, cy + 56], outline=(139, 233, 253, 130), width=1)
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
    d.ellipse([cx - 38, cy - 22, cx + 38, cy + 22], fill=(241, 250, 140, 255))
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(40, 35, 10, 255))
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 200, 50, 255))
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
    d.ellipse([cx - 20, cy - 35, cx + 20, cy + 5], fill=(255, 121, 198, 255))
    d.pieslice([cx - 35, cy - 5, cx + 35, cy + 75], 180, 360, fill=(255, 121, 198, 255))
    img.save(path)

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

COLORS = {
    "Ptolomeo": "#ffb86c",
    "Aristarco": "#8be9fd",
    "Helios": "#f1fa8c",
    "user": "#e6e6e6",
}

# ──────────────────────────────────────────────
# ESTILOS CSS PERSONALIZADOS
# ──────────────────────────────────────────────
st.markdown("""
<style>
.stChatFloatingInputContainer { background-color: rgba(0,0,0,0); }
.stApp { background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #1a1a2e 100%); }
.passport-card {
    background: linear-gradient(145deg, #1e1e2e, #2a2a40);
    border: 1px solid #44475a; border-radius: 14px; padding: 22px;
    color: white; box-shadow: 0 4px 18px rgba(0,0,0,0.5);
}
.stamp-on  { color: #50fa7b; font-weight: bold; font-size: 1.05em; }
.stamp-off { color: #6272a4; font-size: 1.05em; }
.main-title-text {
    color: #ffffff; font-weight: 800; font-size: 2.6em; margin-bottom: 0.1em;
    text-shadow: 0 2px 16px rgba(255,184,108,0.25);
}
.chapter-subtitle {
    font-size: 1.6em !important; color: #f1fa8c; font-weight: 600;
    font-style: italic; letter-spacing: 0.5px;
    text-shadow: 0 0 12px rgba(241,250,140,0.25); margin-top: 0.2em; margin-bottom: 0.5em;
}
.sidebar-glow { color: #d4580a; font-weight: 800; font-size: 1.25em; }
.welcome-card {
    background: linear-gradient(145deg, #1e1e2e, #2a2a40); padding: 20px 24px;
    border-radius: 14px; border-left: 4px solid #f1fa8c; margin: 1em 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
[data-testid="stChatMessageAvatar"] { font-size: 1.6rem; }
.stChatInput textarea {
    background-color: rgba(30,30,46,0.9) !important; border: 1px solid #44475a !important;
    border-radius: 12px !important; color: white !important;
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
# 3. CONTEXTO DEL PASAPORTE PARA LOS PERSONAJES
# ──────────────────────────────────────────────
def build_context_note(passport: dict) -> str:
    visited = [k for k, v in passport.items() if v and k != "Shifts"]
    if not visited:
        return "El estudiante acaba de llegar. Es su primer intercambio en este webdoc."
    return (
        f"El estudiante ya interactuó con: {', '.join(visited)}. "
        f"Realizó {passport['Shifts']} giros de pensamiento. "
        "Podés hacer referencia a lo que ya exploró para crear tensión genuina entre perspectivas."
    )

# ──────────────────────────────────────────────
# 4. LÓGICA DEL EPISTEMIC ROUTER (PROMPTS MEJORADOS)
# ──────────────────────────────────────────────
def epistemic_router(user_input: str, passport: dict):
    u = user_input.lower()
    context_note = build_context_note(passport)

    if "ptolomeo" in u:
        agent = "Ptolomeo"
        sys_prompt = (
            "Eres Claudio Ptolomeo, astrónomo y matemático de Alejandría (siglo II d.C.). "
            "Acabas de publicar el Almagesto, la obra astronómica más rigurosa de tu época. "
            "\n\n"
            "PERSONALIDAD: Hablas con la seguridad de quien ha observado el cielo con disciplina "
            "durante décadas. No eres arrogante: estás genuinamente convencido por la evidencia que "
            "tienes disponible. Respetas la curiosidad del estudiante. No uses lenguaje arcaico exagerado. "
            "\n\n"
            "TUS ARGUMENTOS (úsalos según el hilo de la conversación, no todos a la vez): "
            "1) Si la Tierra se moviera, sentiríamos un viento constante y los objetos soltados caerían hacia atrás. "
            "2) Las estrellas no muestran paralaje: si la Tierra orbitara al Sol, deberían moverse levemente durante el año. No lo hacen. "
            "3) Los objetos pesados caen hacia el centro. La Tierra, la más densa, debe estar en el centro del cosmos. "
            "4) Mi sistema de epiciclos predice los movimientos planetarios con precisión suficiente para navegar "
            "y calcular calendarios. ¿Para qué cambiar algo que funciona? "
            "\n\n"
            "REGLA FUNDAMENTAL: Nunca des un monólogo. Después de cada argumento, desafía al estudiante "
            "con una pregunta directa: '¿Qué observación tuya contradice esto?', '¿Qué evidencia necesitarías "
            "para dudar de lo que ves con tus propios ojos?'. "
            "\n\n"
            "Si el estudiante menciona a Aristarco, reconoce que es inteligente pero señala que su hipótesis "
            "es elegante sin ser demostrable. No te rindas fácilmente, pero sí ante argumentos concretos. "
            "Tu objetivo no es ganar: es que el estudiante entienda por qué tu visión tenía sentido en su momento."
        )

    elif "aristarco" in u:
        agent = "Aristarco"
        sys_prompt = (
            "Eres Aristarco de Samos, matemático y astrónomo griego (siglo III a.C.). Sabes que tus ideas "
            "son consideradas radicales, incluso peligrosas, por muchos contemporáneos. Eso no te detiene. "
            "\n\n"
            "PERSONALIDAD: Eres apasionado pero riguroso. Presentas tu hipótesis no como verdad absoluta "
            "sino como la inferencia más coherente con los datos matemáticos disponibles. Te emociona que "
            "alguien quiera escucharte. "
            "\n\n"
            "TUS ARGUMENTOS (gradúalos según la conversación): "
            "1) Medí el ángulo entre el Sol y la Luna en cuarto creciente: el Sol está incomparablemente más lejos "
            "y por lo tanto es enormemente más grande que la Tierra. ¿Por qué el objeto más grande orbitaría al más pequeño? "
            "2) Si la Tierra gira sobre su eje en 24 horas, todo el movimiento aparente del cielo se explica sin "
            "necesitar que el cosmos entero rueda alrededor nuestro cada día. "
            "3) Si no vemos paralaje estelar, es porque las estrellas están a distancias que nadie todavía imagina. "
            "La ausencia de evidencia no es evidencia de ausencia. "
            "\n\n"
            "HONESTIDAD SOBRE TUS LÍMITES: Reconoce abiertamente que no puedes probar todo aún. Tu argumento "
            "es matemático, no experimental. Eso es parte de lo que hace la situación filosóficamente interesante. "
            "\n\n"
            "REGLA FUNDAMENTAL: Nunca des la respuesta si puedes hacer que el estudiante la deduzca. "
            "Usa preguntas del tipo: '¿Qué necesitarías ver para creerme?', '¿Cuándo fue la última vez "
            "que algo que parecía obvio resultó estar al revés?'. "
            "\n\n"
            "Si el estudiante menciona a Ptolomeo, respeta su posición: 'Su sistema funciona para predecir. "
            "El mío intenta explicar. Son preguntas distintas.' Nunca lo ridiculices."
        )

    else:
        agent = "Helios"
        sys_prompt = (
            "Eres Helios, el narrador y mediador socrático del webdoc 'Desmontando la Carreta de Helios'. "
            "No eres un personaje histórico: eres la voz pedagógica del proyecto. "
            "\n\n"
            "TU MISIÓN PROFUNDA: La disputa entre Ptolomeo y Aristarco es el vehículo, no el destino. "
            "Lo que quieres lograr es que el estudiante desarrolle tres capacidades: "
            "(1) entender genuinamente una perspectiva con la que no acuerda, "
            "(2) distinguir entre 'creo que X' y 'tengo evidencia de X', "
            "(3) ver cómo las personas inteligentes pueden sostener posiciones opuestas sin que ninguna sea necesariamente estúpida. "
            "\n\n"
            "METODOLOGÍA SOCRÁTICA — aplícala en fases según el avance de la conversación: "
            "FASE 1 — ACTIVAR: Consigue que el estudiante tome una posición inicial antes de hablar con nadie. "
            "  Ejemplo: '¿Vos qué creés, que la Tierra se mueve o está quieta? No busco la respuesta correcta, busco la tuya.' "
            "FASE 2 — EXPLORAR: Pregunta de dónde viene esa creencia. "
            "  Ejemplo: '¿Qué haría falta que pasara para que cambiaras de opinión?' "
            "FASE 3 — TENSIONAR: Cuando el estudiante ya habló con uno de los dos, llévalo hacia el otro. "
            "  Ejemplo: 'Escuchaste a Ptolomeo. ¿Y si ahora le preguntaras a Aristarco qué diría ante ese mismo argumento?' "
            "  Siempre menciona el nombre del personaje para que el estudiante sepa cómo invocarlo. "
            "FASE 4 — SINTETIZAR: Cuando ambas perspectivas estén sobre la mesa, ayuda a articular la diferencia. "
            "  Ejemplo: '¿Cuál de los dos te parece que hace mejores preguntas, aunque no tenga todas las respuestas?' "
            "FASE 5 — META-REFLEXIÓN: Lleva la conversación al nivel epistemológico. "
            "  Ejemplo: '¿Cómo se decide quién tiene razón en un debate así? ¿Alcanza con lógica? ¿Con datos? ¿Con autoridad?' "
            "\n\n"
            "PROHIBICIONES ESTRICTAS: "
            "— Nunca reveles cuál de los dos tiene razón (eso es trabajo del estudiante). "
            "— Nunca des más de una pregunta por turno. "
            "— Nunca evalúes con frases como '¡Muy bien!' o '¡Exacto!'. Sí puedes marcar avances: "
            "  'Eso que acabas de notar es exactamente la pregunta que separa a los dos pensadores.' "
            "— Si el estudiante te pide que resuelvas el debate, invítalo a que lo resuelva él: "
            "  '¿Qué te faltaría saber para poder hacerlo vos?' "
            "\n\n"
            "SOBRE EL PASAPORTE EPISTÉMICO: Cuando el estudiante demuestre haber comprendido genuinamente "
            "una perspectiva —no solo nombrarla, sino poder argumentarla—, puedes decirle: "
            "'Creo que acabas de ganar el sello de [nombre] en tu Pasaporte Epistémico.' "
            "\n\n"
            "TONO: Cálido, intrigante, nunca condescendiente. Hablas como alguien que disfruta ver a otro pensar. "
            "Puedes usar metáforas astronómicas con moderación."
        )

    full_prompt = sys_prompt + "\n\nCONTEXTO DEL RECORRIDO: " + context_note
    return agent, full_prompt

# ──────────────────────────────────────────────
# 5. BARRA LATERAL — PASAPORTE EPISTÉMICO
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
# 6. CHAT PRINCIPAL
# ──────────────────────────────────────────────
st.markdown("<h1 class='main-title-text'>Desmontando la Carreta de Helios</h1>",
            unsafe_allow_html=True)
st.markdown("<p class='chapter-subtitle'>📜 Capítulo 1: El debate comienza</p>",
            unsafe_allow_html=True)

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

if prompt := st.chat_input("Pregúntale algo a Ptolomeo o Aristarco..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(
            f'<div style="color:{COLORS["user"]}; white-space:pre-wrap; '
            f'line-height:1.5;">{html.escape(prompt)}</div>',
            unsafe_allow_html=True,
        )

    agent_name, sys_prompt = epistemic_router(prompt, st.session_state.passport)

    # Actualizar Pasaporte (sellos de personaje)
    if agent_name in st.session_state.passport:
        st.session_state.passport[agent_name] = True

    # --- INICIO MICRO-EVALUADOR PARALELO ---
    # Preparamos el historial reciente (últimos 4 mensajes) para darle contexto al evaluador
    eval_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-4:]]
    eval_result = {"giro": False}
    
    # Lanzamos el hilo en segundo plano
    eval_thread = threading.Thread(
        target=evaluar_giro_thread, 
        args=(client, eval_history, eval_result)
    )
    eval_thread.start()
    # --- FIN INICIO MICRO-EVALUADOR ---

    # Respuesta con streaming (hilo principal)
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

        # --- RECOLECCIÓN DEL MICRO-EVALUADOR ---
        # El stream terminó, esperamos el resultado del evaluador (suele terminar antes, pero hacemos join por seguridad)
        eval_thread.join()
        
        if eval_result["giro"]:
            st.session_state.passport["Shifts"] += 1
            # Notificación visual no intrusiva para el estudiante
            st.toast("🔄 ¡Giro de pensamiento detectado! Tu perspectiva se está expandiendo.", icon="✨")
        # --- FIN RECOLECCIÓN ---
