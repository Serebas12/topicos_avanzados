# app.py

import streamlit as st
import requests
import uuid
from langchain.schema import HumanMessage, AIMessage

# -----------------------------
# Configuración inicial
# -----------------------------
st.set_page_config(page_title="Chatea con nuestro asesor interno", layout="wide")
st.title("💬 Chatea con nuestro asesor interno")

# -----------------------------
# Inicializar sesión
# -----------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Botón para reiniciar conversación
# -----------------------------
if st.button("🗑️ Borrar conversación"):
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

# -----------------------------
# Mostrar historial de mensajes
# -----------------------------
for i, msg in enumerate(st.session_state.messages):
    alignment = "user" if i % 2 == 0 else "assistant"
    with st.chat_message(alignment):
        st.markdown(msg)

# -----------------------------
# Entrada inferior de texto
# -----------------------------
if prompt := st.chat_input("Escribe tu mensaje..."):
    # Mostrar mensaje del usuario inmediatamente
    st.session_state.messages.append(prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # ✅ Construir historial como objetos LangChain
    chat_history = []
    for i, msg in enumerate(st.session_state.messages[:-1]):  # Excluye el último (prompt actual)
        if i % 2 == 0:
            chat_history.append(HumanMessage(content=msg))
        else:
            chat_history.append(AIMessage(content=msg))

    # Enviar historial como JSON serializable
    response = requests.post(
        "http://localhost:8000/ask",
        json={
            "question": prompt,
            "session_id": st.session_state.session_id,
            "history": [m.dict() for m in chat_history]
        }
    )

    # Mostrar respuesta del asistente
    if response.status_code == 200:
        answer = response.json()["response"]
        st.session_state.messages.append(answer)
        with st.chat_message("assistant"):
            st.markdown(answer)
    else:
        st.error("❌ Error en el servidor")
