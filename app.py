import streamlit as st
import cv2
import mediapipe as mp
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
import os
import tempfile

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Traductor Emergencia", layout="wide")

# Inicializar MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=1)

# Diccionario de emergencia
CONCEPTS = {
    "AYUDA": {
        "es": "Ayuda", "en": "Help", 
        "asl_gif": "https://www.lifeprint.com/asl101/gifs/h/help.gif",
        "lsa_img": "https://media.spreadthesign.com/image/500/help-2763.jpg"
    },
    "HOSPITAL": {
        "es": "Hospital", "en": "Hospital",
        "asl_gif": "https://media.spreadthesign.com/image/500/hospital-2.jpg",
        "lsa_img": "https://media.spreadthesign.com/image/500/hospital-2275.jpg"
    },
    "PELIGRO": {
        "es": "Peligro", "en": "Danger",
        "asl_gif": "https://media.spreadthesign.com/image/500/danger-1520.jpg",
        "lsa_img": "https://media.spreadthesign.com/image/500/danger-12534.jpg"
    }
}

def reconocer_gesto(landmarks):
    dedos = []
    ids_puntas = [8, 12, 16, 20]
    for id in ids_puntas:
        if landmarks.landmark[id].y < landmarks.landmark[id-2].y:
            dedos.append(1)
        else: 
            dedos.append(0)
    if sum(dedos) == 4: 
        return "AYUDA"
    if sum(dedos) == 0: 
        return "PELIGRO"
    if dedos[0] == 1 and sum(dedos[1:]) == 0: 
        return "HOSPITAL"
    return None

st.title("🤟 Traductor Universal Inclusivo")

col1, col2 = st.columns(2)
with col1:
    idioma_origen = st.selectbox("Origen", ["Español (AR)", "Inglés (US)"])
    modo_entrada = st.radio("Entrada", ["Texto", "Cámara"])
with col2:
    idioma_destino = st.selectbox("Destino", ["Inglés (US)", "Español (AR)"])
    modo_salida = st.radio("Salida", ["Texto y Voz", "Imagen (Señas)"])

texto_entrada = ""

if modo_entrada == "Texto":
    texto_entrada = st.text_input("Mensaje:")

elif modo_entrada == "Cámara":
    activar = st.toggle("Activar Cámara")
    if activar:
        cap = cv2.VideoCapture(0)
        frame_placeholder = st.empty()
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)
            if results.multi_hand_landmarks:
                for hl in results.multi_hand_landmarks:
                    gesto = reconocer_gesto(hl)
                    if gesto:
                        st.success(f"Detectado: {gesto}")
                        texto_entrada = CONCEPTS[gesto]["es" if "Español" in idioma_origen else "en"]
            frame_placeholder.image(frame, channels="BGR")
        cap.release()

if texto_entrada:
    src = 'es' if "Español" in idioma_origen else 'en'
    dest = 'en' if "Inglés" in idioma_destino else 'es'
    
    res = GoogleTranslator(source=src, target=dest).translate(texto_entrada)
    st.write(f"### Resultado: {res}")
    
    # Generar voz con gTTS
    if modo_salida == "Texto y Voz":
        tts = gTTS(text=res, lang=dest)
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        tts.write_to_fp(temp_file.name)
        st.audio(temp_file.name, format='audio/mp3')
    
    if modo_salida == "Imagen (Señas)":
        for k, v in CONCEPTS.items():
            if v["es"].lower() in texto_entrada.lower() or v["en"].lower() in texto_entrada.lower():
                link = v["asl_gif" if "Inglés" in idioma_destino else "lsa_img"]
                st.image(link, width=400)
