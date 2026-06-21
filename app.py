import streamlit as st
import cv2
import mediapipe as mp
from googletrans import Translator
from gtts import gTTS
import speech_recognition as sr
import os
import tempfile

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Traductor Universal de Emergencia", layout="wide")
translator = Translator()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=1)

# --- DICCIONARIO DE CONCEPTOS (Emergencia) ---
# Vinculamos la "Idea" con los idiomas y las imágenes/GIFs
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
    },
    "POLICIA": {
        "es": "Policia", "en": "Police",
        "asl_gif": "https://www.lifeprint.com/asl101/gifs/p/police.gif",
        "lsa_img": "https://media.spreadthesign.com/image/500/police-3136.jpg"
    }
}

# --- FUNCIONES DE APOYO ---

def reconocer_voz(idioma_cod):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.toast(f"Escuchando en {idioma_cod}...")
        try:
            audio = r.listen(source, timeout=5)
            return r.recognize_google(audio, language=idioma_cod)
        except: return None

def texto_a_audio(texto, lang):
    tts = gTTS(text=texto, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

def reconocer_gesto(puntos_mano):
    # Lógica simple: detecta si los dedos están arriba o abajo
    dedos = []
    ids_puntas = [8, 12, 16, 20] # Indice, Medio, Anular, Meñique
    for id in ids_puntas:
        if puntos_mano.landmark[id].y < puntos_mano.landmark[id-2].y:
            dedos.append(1)
        else: dedos.append(0)
    
    if sum(dedos) == 4: return "AYUDA"    # Palma abierta
    if sum(dedos) == 0: return "PELIGRO"  # Puño cerrado
    if dedos[0] == 1 and sum(dedos[1:]) == 0: return "HOSPITAL" # Solo índice
    return None

# --- INTERFAZ DE USUARIO ---
st.title("🤟 Traductor Universal Inclusivo")
st.write("Comunicación bilingüe: Sordos y Oyentes (Español/Inglés)")

col1, col2 = st.columns(2)

with col1:
    st.header("1. ¿Quién sos y qué usás?")
    idioma_origen = st.selectbox("Tu Idioma", ["Español (AR)", "Inglés (US)"])
    modo_entrada = st.radio("Tu forma de entrada", ["Texto", "Voz", "Cámara (Señas)"])

with col2:
    st.header("2. ¿Cómo querés traducir?")
    idioma_destino = st.selectbox("Idioma del otro", ["Inglés (US)", "Español (AR)"])
    modo_salida = st.radio("Formato de salida", ["Texto y Voz", "Imagen (Señas)"])

st.divider()

# --- LÓGICA PRINCIPAL ---
texto_entrada = ""
concepto_detectado = None

# A. CAPTURA DE ENTRADA
if modo_entrada == "Texto":
    texto_entrada = st.text_input("Escribí tu mensaje:")
    
elif modo_entrada == "Voz":
    if st.button("🎤 Empezar a hablar"):
        texto_entrada = reconocer_voz("es-AR" if "Español" in idioma_origen else "en-US")
        st.write(f"Escuchado: {texto_entrada}")

elif modo_entrada == "Cámara (Señas)":
    st.info("Palma = Ayuda | Puño = Peligro | Índice = Hospital")
    activar = st.toggle("Abrir Cámara")
    if activar:
        cap = cv2.VideoCapture(0)
        espacio_video = st.empty()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultados = hands.process(rgb)
            if resultados.multi_hand_landmarks:
                for puntos in resultados.multi_hand_landmarks:
                    gesto = reconocer_gesto(puntos)
                    if gesto:
                        concepto_detectado = gesto
                        texto_entrada = CONCEPTS[gesto]["es" if "Español" in idioma_origen else "en"]
            espacio_video.image(frame, channels="BGR")
            if concepto_detectado: 
                st.success(f"Seña detectada: {concepto_detectado}")
                break
        cap.release()

# B. TRADUCCIÓN Y SALIDA
if texto_entrada:
    cod_origen = 'es' if "Español" in idioma_origen else 'en'
    cod_destino = 'en' if "Inglés" in idioma_destino else 'es'
    
    # Traducción del texto
    texto_traducido = translator.translate(texto_entrada, src=cod_origen, dest=cod_destino).text

    st.subheader("Resultado de la traducción:")
    
    if modo_salida == "Texto y Voz":
        st.write(f"### {texto_traducido}")
        archivo_audio = texto_a_audio(texto_traducido, cod_destino)
        st.audio(archivo_audio)
        
    elif modo_salida == "Imagen (Señas)":
        # Buscamos si la palabra coincide con nuestros conceptos
        clave_encontrada = None
        for k, v in CONCEPTS.items():
            if v["es"].lower() in texto_entrada.lower() or v["en"].lower() in texto_entrada.lower():
                clave_encontrada = k
                break
        
        if clave_encontrada:
            st.write(f"Seña en {'ASL (EEUU)' if 'Inglés' in idioma_destino else 'LSA (Arg)'}:")
            # Elegimos el link de imagen correcto según el destino
            link_img = CONCEPTS[clave_encontrada]["asl_gif" if "Inglés" in idioma_destino else "lsa_img"]
            st.image(link_img, width=500)
        else:
            st.warning("No encontré una seña específica para esa palabra, pero aquí está el texto traducido: " + texto_traducido)