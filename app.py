import streamlit as st
from groq import Groq
import sys

st.set_page_config(page_title="Helios Demo", page_icon="☀️")

# --- DEBUG INFO (Solo para nosotros) ---
with st.expander("🔍 Información de Sistema para Diagnóstico"):
    st.write(f"Versión de Python: {sys.version}")
    st.write(f"API Key detectada: {'✅ SI' if 'GROQ_API_KEY' in st.secrets else '❌ NO'}")

# --- CLIENTE ---
if 'GROQ_API_KEY' in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Falta la API Key en los Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- INTERFAZ ---
st.title("☀️ Helios Multi-Agent System")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Escribe 'Hola'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            # USAMOS EL MODELO MÁS PEQUEÑO Y ESTABLE PARA PROBAR
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Eres un tutor socrático."},
                    {"role": "user", "content": prompt}
                ],
                stream=False # Desactivamos el stream para la prueba inicial de error
            )
            
            full_response = completion.choices[0].message.content
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            # AQUÍ CAPTURAMOS EL ERROR REAL
            error_message = str(e)
            st.error(f"Error detectado: {error_message}")
            
            if "api_key" in error_message.lower():
                st.info("💡 Sugerencia: Revisa que la Key en Secrets no tenga comillas internas o caracteres invisibles.")
            elif "model_not_found" in error_message.lower():
                st.info("💡 Sugerencia: El modelo seleccionado no está disponible en tu región o cuenta.")
            else:
                st.info("💡 Sugerencia: El error 'BadRequest' con Python 3.14 indica que la librería falló al enviar los datos. El archivo runtime.txt debería corregirlo.")
