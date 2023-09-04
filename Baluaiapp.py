import openai
import streamlit as st
import whisper
import os
import time


st.title("BALUAI")

openai.api_key = os.environ.get("OPENAI_API_KEY")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Cargar el modelo de transcripción de whisper
model = whisper.load_model("base")

# Ruta de la carpeta de textos
text_folder = "C:\\Users\\cleme\\Desktop\\Brave up\\Brave up transcripciones\\"

# Crea la carpeta de textos si no existe
if not os.path.exists(text_folder):
    os.makedirs(text_folder)

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

 with st.spinner("Transcribiendo... ⏳ _Demora entre 20 y 40% de la diración del audio_"):
        
    # Obtén el nombre del archivo sin extensión
    audio_filename = os.path.splitext(uploaded_file.name)[0]

    # Ruta para guardar el archivo de audio temporalmente
    temp_audio_path = os.path.join(text_folder, audio_filename + "_temp.wav")
    
    # Guarda el archivo de audio temporalmente
    with open(temp_audio_path, "wb") as temp_audio_file:
        temp_audio_file.write(uploaded_file.read())
    
    # Realiza la transcripción
    result = model.transcribe(temp_audio_path, language="es")

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
