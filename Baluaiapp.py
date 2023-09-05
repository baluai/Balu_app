import openai
import streamlit as st
import openai-whisper
import os
import time
import tempfile

st.title("BALUAI")

st.title("Verificación de Instalación de Whisper")

try:
    st.write(f"Módulo 'whisper' importado correctamente.")
    st.write(f"Directorio del módulo: {whisper.__file__}")
except Exception as e:
    st.error("Error al verificar la instalación de Whisper.")
    st.write(str(e))

openai.api_key = os.environ.get("OPENAI_API_KEY")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Cargar el modelo de transcripción de whisper
model = whisper.load_model("small")

# Subir archivo de audio
uploaded_file = st.file_uploader("Sube un archivo de audio (mp3 o wav)", type=["mp3", "wav"])

# Inicializar la transcripción
transcription_text = ""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.chat_message("assistant").write("Sube tu archivos aqui")

if uploaded_file is not None:

    # Crea un archivo temporal
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False)
    temp_audio_path = temp_audio_file.name
    temp_audio_file.write(uploaded_file.read())
    temp_audio_file.close()

    with st.spinner("Transcribiendo... ⏳ _Demora entre 20 y 40% de la diración del audio_"):

        _, probs = model.detect_language(mel)
        
        # Realiza la transcripción
        result = model.transcribe(temp_audio_path) #, language="es")

        # Obtén el texto de la transcripción
        transcription_text = result["text"]

    # Mostrar mensaje de transcripción exitosa en el chat
    st.chat_message("assistant").write("Transcripción exitosa! ✅")

# Mostrar las primeras 25 palabras de la transcripción en el chat
if transcription_text:
    words = transcription_text.split()
    display_text = ' '.join(words[:50]) + "..." if len(words) > 50 else transcription_text
    st.chat_message("assistant").write(f"Transcripción: {display_text}")

    # React to user input # Display user message in chat message container
if prompt := st.chat_input("Haz una pregunta"):
    additional_info = " [Esta es una transcripcion que no es perfecta, tu objetivo es rescatar insights valiosos y informacion relevante]"
    prompt_with_info = prompt + additional_info
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": transcription_text})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Crea un espacio vacío para la respuesta del asistente
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            max_tokens=1000,
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
