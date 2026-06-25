import streamlit as st
from groq import Groq

# 1. Configuración visual y de página
st.set_page_config(page_title="Helios System — Piloto", page_icon="☀️", layout="wide")

# Estilo personalizado para el Pasaporte
st.markdown("""
    <style>
    .stChatFloatingInputContainer { background-color: rgba(0,0,0,0); }
    .passport-card {
        background-color: #1e1e2e;
        border: 1px solid #44475a;
        border-radius: 10px;
        padding: 20px;
        color: white;
    }
    .stamp-on { color: #50fa7b; font-weight: bold; }
    .stamp-off { color: #6272a4; }
    </style>
""", unsafe_allow_html=True)

# 2. Inicialización de API y Estado
if "GROQ_API_KEY" not in st.secrets:
    st.error("Falta la API Key en los Secrets de Streamlit.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "passport" not in st.session_state:
    st.session_state.passport = {"Ptolomeo": False, "Aristarco": False, "Shifts": 0}

# 3. Lógica del Epistemic Router
def epistemic_router(user_input):
    u = user_input.lower()
    if "ptolomeo" in u:
        return "Ptolomeo", "Eres Claudio Ptolomeo (año 150 d.C.). Defiendes firmemente que la Tierra es el centro inmóvil del universo. Tus argumentos son empíricos: 'si la tierra se moviera, sentiríamos el viento' y 'las estrellas no muestran paralaje'. Habla con autoridad antigua."
    elif "aristarco" in u:
        return "Aristarco", "Eres Aristarco de Samos (siglo III a.C.). Eres un revolucionario matemático. Defiendes que el Sol es mucho más grande que la Tierra y por lo tanto la Tierra debe girar a su alrededor. Tu tono es curioso y geométrico."
    else:
        return "Helios", "Eres Helios, un mediador socrático. Tu objetivo es que el estudiante dude de lo obvio. No des respuestas directas; haz preguntas que obliguen a contrastar las opiniones de Ptolomeo y Aristarco."

# 4. Interfaz - Barra Lateral (Pasaporte Epistémico)
with st.sidebar:
    st.title("☀️ Helios System")
    st.markdown("### Pasaporte Epistémico")
    st.markdown("Este panel registra el recorrido cognitivo del evaluador.")
    
    p = st.session_state.passport
    st.markdown(f"""
    <div class="passport-card">
        <p class="{'stamp-on' if p['Ptolomeo'] else 'stamp-off'}">{'●' if p['Ptolomeo'] else '○'} Perspectiva Geocéntrica</p>
        <p class="{'stamp-on' if p['Aristarco'] else 'stamp-off'}">{'●' if p['Aristarco'] else '○'} Perspectiva Heliocéntrica</p>
        <hr>
        <p style='font-size: 0.8em;'>Giros de Pensamiento: {p['Shifts']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    if st.button("Reiniciar Sesión"):
        st.session_state.messages = []
        st.session_state.passport = {"Ptolomeo": False, "Aristarco": False, "Shifts": 0}
        st.rerun()

# 5. Interfaz - Chat Principal
st.title("Desmontando la Carreta de Helios")
st.caption("Arquitectura Multi-Agente para el Giro del Pensamiento Científico")

# Mostrar historial
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Entrada de usuario
if prompt := st.chat_input("Pregúntale algo a Ptolomeo o Aristarco..."):
    # Guardar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Determinar agente y prompt
    agent_name, sys_prompt = epistemic_router(prompt)
    
    # Actualizar Pasaporte
    if agent_name in st.session_state.passport:
        st.session_state.passport[agent_name] = True
    if any(word in prompt.lower() for word in ["pero", "por qué", "duda", "entonces", "cambio"]):
        st.session_state.passport["Shifts"] += 1

    # Respuesta del asistente con Streaming
    with st.chat_message("assistant", avatar="☀️"):
        full_response = ""
        placeholder = st.empty()
        
        try:
            # Intentamos con el modelo grande, si falla por límites, el bloque except lo manejará
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-8:]]
                ],
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            final_content = f"**[{agent_name}]:** {full_response}"
            placeholder.markdown(final_content)
            st.session_state.messages.append({"role": "assistant", "content": final_content})

        except Exception as e:
            st.error(f"Error de conexión: {str(e)}")
            st.info("Intentando reconectar con motor de reserva...")
            # Aquí podrías repetir la llamada con el modelo 8b-instant si fuera necesario
