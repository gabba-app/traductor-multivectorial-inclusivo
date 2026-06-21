import streamlit as st
import mediapipe as mp
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Traductor Emergencia", layout="wide")

# Inicializar MediaPipe
hands = mp.Hands(min_detection_confidence=0.7, max_num_hands=1)

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
    """Reconoce gestos de mano basados en landmarks"""
    dedos = []
    ids_puntas = [8, 12, 16, 20]
    for id_punta in ids_puntas:
        if landmarks.landmark[id_punta].y < landmarks.landmark[id_punta - 2].y:
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

def procesar_imagen(media_image):
    """Procesa imagen de Streamlit con MediaPipe"""
    if media_image is None:
        return None, None
    
    # Convertir a numpy array
    image = np.array(media_image.data)
    
    # Convertir RGB a BGR (si es necesario) y procesar
    rgb = image.astype('uint8')
    results = hands.process(rgb)
    
    return results, image

# --- TÍTULO ---
st.title("🤟 Traductor Universal Inclusivo")
st.markdown("### Traducción de texto y reconocimiento de gestos para emergencias")
st.markdown("---")

# --- CONTROLES ---
col1, col2 = st.columns(2)

with col1:
    idioma_origen = st.selectbox("📌 Origen", ["Español (AR)", "Inglés (US)"])
    modo_entrada = st.radio("📥 Entrada", ["Texto", "Cámara"])

with col2:
    idioma_destino = st.selectbox("📍 Destino", ["Inglés (US)", "Español (AR)"])
    modo_salida = st.radio("📤 Salida", ["Texto y Voz", "Imagen (Señas)"])

st.markdown("---")

# --- ENTRADA DE TEXTO ---
texto_entrada = ""

if modo_entrada == "Texto":
    texto_entrada = st.text_input("💬 Escribe tu mensaje:")

elif modo_entrada == "Cámara":
    st.info("👆 Capturá una foto de tu mano mostrando el gesto")
    
    camera_image = st.camera_input("📸 Capturar foto de mano")
    
    if camera_image:
        try:
            results, image = procesar_imagen(camera_image)
            
            # Mostrar imagen
            st.image(image, caption="📷 Tu imagen", use_container_width=True)
            
            # Detectar gesto
            if results.multi_hand_landmarks:
                for hl in results.multi_hand_landmarks:
                    gesto = reconocer_gesto(hl)
                    if gesto:
                        st.success(f"✅ Gesto detectado: **{gesto}**")
                        texto_entrada = CONCEPTS[gesto][
                            "es" if "Español" in idioma_origen else "en"
                        ]
                    else:
                        st.warning("⚠️ Gesto no reconocido. Probá con: 4 dedos (AYUDA), 0 dedos (PELIGRO), o 1 dedo (HOSPITAL)")
            else:
                st.warning("⚠️ No se detectó ninguna mano. Probá de nuevo mostrando tu mano claramente.")
        except Exception as e:
            st.error(f"❌ Error procesando imagen: {e}")

# --- TRADUCCIÓN ---
if texto_entrada:
    src = 'es' if "Español" in idioma_origen else 'en'
    dest = 'en' if "Inglés" in idioma_destino else 'es'
    
    try:
        res = GoogleTranslator(source=src, target=dest).translate(texto_entrada)
    except Exception:
        res = texto_entrada
    
    st.markdown("---")
    st.write(f"### 🔄 Resultado: **{res}**")
    
    # --- SALIDA DE VOZ ---
    if modo_salida == "Texto y Voz":
        try:
            tts = gTTS(text=res, lang=dest)
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            tts.write_to_fp(temp_file.name)
            st.audio(temp_file.name, format='audio/mp3')
        except Exception as e:
            st.warning(f"⚠️ No se pudo generar voz: {e}")
    
    # --- SALIDA DE IMAGEN (SEÑAS) ---
    if modo_salida == "Imagen (Señas)":
        st.markdown("---")
        st.subheader("👋 Imagen de la seña:")
        
        for k, v in CONCEPTS.items():
            if v["es"].lower() in texto_entrada.lower() or v["en"].lower() in texto_entrada.lower():
                link = v["asl_gif" if "Inglés" in idioma_destino else "lsa_img"]
                st.image(link, width=400)
                break

# --- INFORMACIÓN ---
st.markdown("---")
st.markdown("### 📋 Gestos reconocidos:")

st.markdown(
    """
    | Gesto | Significado | Descripción |
    |-------|-------------|-------------|
    | 4 dedos ↑ | **AYUDA** | Todos los dedos abiertos |
    | 0 dedos ↑ | **PELIGRO** | Todos los dedos cerrados (puño) |
    | 1 dedo ↑ | **HOSPITAL** | Solo el índice abierto |
    """
)

st.markdown("---")
st.markdown("🌐 **Inclusivo:** ASL (American Sign Language) y LSA (Lengua de Señas Argentina)")
