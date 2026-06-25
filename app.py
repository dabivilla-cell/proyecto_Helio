import streamlit as st
from groq import Groq

# 1. Configuración de página e identidad visual
st.set_page_config(page_title="Helios System", page_icon="☀️", layout="wide")

# 2. Verificación de Seguridad de la API Key
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ No se encontró la API Key en los Secrets de Streamlit.")
    st.stop()

# 3. Inicialización del cliente
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 4. Estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []
if "passport" not in st.session_state:
    st.session_state.passport = {"Ptolomeo": False, "Aristarco": False, "Cambio": 0}

# --- LÓGICA DEL ROUTER ---
def epistemic_router(user_input):
    u = user_input.lower()
    if "ptolomeo" in u:
        return "Ptolomeo", "Eres Claudio Ptolomeo. Defiendes el sistema geocéntrico. La Tierra es el centro inmóvil. Ignora descubrimientos después del año 150 d.C."
    elif "aristarco" in u:
        return "Aristarco", "Eres Aristarco de Samos. Defiendes el sistema heliocéntrico. El Sol es mucho más grande que la Tierra y debe estar en el centro."
    else:
        return "Helios", "Eres Helios, el mediador socrático. Haz preguntas para que el estudiante reflexione sobre la evidencia."

# --- UI SIDEBAR ---
with st.sidebar:
    st.title("☀️ Helios")
    st.subheader("Epistemic Passport")
    p = st.session_state.passport
    st.write(f"{'✅' if p['Ptolomeo'] else '⭕'} Ptolomeo")
    st.write(f"{'✅' if p['Aristarco'] else '⭕'} Aristarco")
    st.metric("Cambios de Paradigma", p["Cambio"])
    if st.button("Reiniciar Sistema"):
        st.session_state.messages = []
        st.session_state.passport = {"Ptolomeo": False, "Aristarco": False, "Cambio": 0}
        st.rerun()

# --- CHAT INTERFACE ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Dile 'Hola' a Ptolomeo o Aristarco..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    agent_name, sys_prompt = epistemic_router(prompt)
    
    # Marcado en pasaporte
    if agent_name in st.session_state.passport:
        st.session_state.passport[agent_name] = True

    with st.chat_message("assistant", avatar="☀️"):
        resp_placeholder = st.empty()
        full_response = ""
        
        # Lista de modelos a intentar (en orden de robustez)
        models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        
        success = False
        for model_id in models_to_try:
            if success: break
            try:
                # Limpieza estricta de mensajes para la API
                api_messages = [{"role": "system", "content": sys_prompt}]
                for m in st.session_state.messages[-6:]: # Solo últimos 6 para evitar errores de contexto
                    api_messages.append({"role": m["role"], "content": m["content"]})

                stream = client.chat.completions.create(
                    model=model_id,
                    messages=api_messages,
                    stream=True,
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        resp_placeholder.markdown(full_response + "▌")
                success = True
            except Exception as e:
                continue # Si falla un modelo, intenta el siguiente
        
        if success:
            final_text = f"**[{agent_name}]:** {full_response}"
            resp_placeholder.markdown(final_text)
            st.session_state.messages.append({"role": "assistant", "content": final_text})
        else:
            st.error("Lo siento, los motores de Helios están saturados. Intenta de nuevo en un minuto.")
