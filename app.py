import streamlit as st
from groq import Groq
import json

# Configuración de la página e identidad visual
st.set_page_config(page_title="Helios: El Giro del Pensamiento", layout="wide")

# Estilo para el "Epistemic Passport"
st.markdown("""
    <style>
    .passport-box { background-color: #1e1e1e; border-radius: 10px; padding: 15px; border: 1px solid #ffaa00; }
    .stamp-active { color: #00ff00; font-weight: bold; }
    .stamp-inactive { color: #555555; }
    </style>
""", unsafe_allow_html=True)

# Inicialización de Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- LÓGICA DE AGENTES (EPISTEMIC ROUTER SIMPLIFICADO) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "passport" not in st.session_state:
    st.session_state.passport = {"Ptolomeo": False, "Aristarco": False, "Cambio de Paradigma": 0}

def epistemic_router(user_input):
    # Detecta a quién se refiere el usuario
    user_input = user_input.lower()
    if "ptolomeo" in user_input:
        return "Ptolomeo", "Eres Ptolomeo (150 d.C.). Defiendes el geocentrismo basándote en los sentidos: la Tierra no se siente moverse, no hay paralaje estelar. Usa un tono autoritario y empírico."
    elif "aristarco" in user_input:
        return "Aristarco", "Eres Aristarco de Samos. Defiendes que el Sol es el centro porque tus cálculos de tamaño muestran que el Sol es mucho más grande que la Tierra. Eres un visionario matemático."
    else:
        return "Helios", "Eres Helios, el mediador socrático. No das respuestas, haces preguntas que obliguen al estudiante a dudar de sus sentidos y usar la lógica."

# --- UI INTERFACE ---
with st.sidebar:
    st.title("☀️ Helios System")
    st.markdown("### Epistemic Passport")
    with st.container():
        p = st.session_state.passport
        st.markdown(f"""
        <div class="passport-box">
            <p class="{'stamp-active' if p['Ptolomeo'] else 'stamp-inactive'}">{'✓' if p['Ptolomeo'] else '○'} Perspectiva Ptolomeo</p>
            <p class="{'stamp-active' if p['Aristarco'] else 'stamp-inactive'}">{'✓' if p['Aristarco'] else '○'} Perspectiva Aristarco</p>
            <hr>
            <p>Paradigm Shifts: {p['Cambio de Paradigma']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("Reiniciar Experiencia"):
        st.session_state.messages = []
        st.session_state.passport = {"Ptolomeo": False, "Aristarco": False, "Cambio de Paradigma": 0}
        st.rerun()

st.title("Desmontando la Carreta de Helios")
st.info("Pregunta a Ptolomeo por qué la Tierra es fija, o a Aristarco por qué debería moverse.")

# Chat Display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Escribe tu duda aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Lógica del Router
    agent_name, system_prompt = epistemic_router(prompt)
    
    # Actualizar Pasaporte
    if agent_name in st.session_state.passport:
        st.session_state.passport[agent_name] = True
    if "duda" in prompt or "entiendo" in prompt:
        st.session_state.passport["Cambio de Paradigma"] += 1

    # Respuesta del Agente vía Groq
    with st.chat_message("assistant", avatar="☀️"):
        full_response = ""
        stream = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            ],
            stream=True,
        )
        response_placeholder = st.empty()
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(f"**[{agent_name}]:** " + full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": f"**[{agent_name}]:** " + full_response})