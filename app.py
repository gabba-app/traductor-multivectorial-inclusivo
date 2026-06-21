import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Traductor Emergencia", layout="wide")

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

# --- TÍTULO ---
st.title("🤟 Traductor Universal Inclusivo")
st.markdown("### Traducción de texto emergente con voz y señas")
st.markdown("---")

# --- CONTROLES ---
col1, col2 = st.columns(2)

with col1:
    idioma_origen = st.selectbox("📌 Origen", ["Español (AR)", "Inglés (US)"])
    
with col2:
    idioma_destino = st.selectbox("📍 Destino", ["Inglés (US)", "Español (AR)"])

st.markdown("---")

# --- ENTRADA DE TEXTO ---
st.subheader("💬 Escribe tu mensaje de emergencia:")
texto_entrada = st.text_input(
    "Mensaje:", 
    placeholder="Ej: Ayuda, Hospital, Peligro...",
    help="Seleccioná una de las opciones predefinidas o escribí tu propio mensaje"
)

# --- BOTÓN DE TRADUCCIÓN ---
if st.button("🔄 Traducir", type="primary", use_container_width=True):
    if texto_entrada:
        src = 'es' if "Español" in idioma_origen else 'en'
        dest = 'en' if "Inglés" in idioma_destino else 'es'
        
        try:
            res = GoogleTranslator(source=src, target=dest).translate(texto_entrada)
        except Exception as e:
            st.error(f"❌ Error de traducción: {e}")
            res = texto_entrada
        
        st.markdown("---")
        st.success(f"### ✅ Resultado: **{res}**")
        
        # --- SALIDA DE VOZ ---
        st.subheader("🔊 Voz:")
        try:
            tts = gTTS(text=res, lang=dest)
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            tts.write_to_fp(temp_file.name)
            st.audio(temp_file.name, format='audio/mp3')
        except Exception as e:
            st.warning(f"⚠️ No se pudo generar voz: {e}")
        
        # --- SALIDA DE IMAGEN (SEÑAS) ---
        st.subheader("👋 Seña visual:")
        
        gesto_encontrado = False
        for k, v in CONCEPTS.items():
            if v["es"].lower() in texto_entrada.lower() or v["en"].lower() in texto_entrada.lower():
                link = v["asl_gif" if "Inglés" in idioma_destino else "lsa_img"]
                st.image(link, width=400)
                gesto_encontrado = True
                break
        
        if not gesto_encontrado:
            st.info("ℹ️ Este mensaje no tiene seña visual predefinida. Las señas disponibles son: AYUDA, HOSPITAL, PELIGRO")
        
        # --- INFORMACIÓN ---
        st.markdown("---")
        st.markdown("### 📋 Opciones predefinidas con señas:")
        
        st.markdown(
            """
            | Opción | Español | Inglés |
            |--------|---------|--------|
            | AYUDA | Ayuda | Help |
            | HOSPITAL | Hospital | Hospital |
            | PELIGRO | Peligro | Danger |
            """
        )
        
        st.markdown("---")
        st.markdown("🌐 **Inclusivo:** ASL (American Sign Language) y LSA (Lengua de Señas Argentina)")
    else:
        st.warning("⚠️ Por favor, escribí un mensaje para traducir.")

# --- BOTONES DE EMERGENCIA RÁPIDA ---
st.markdown("---")
st.subheader("🚨 Emergencia rápida (seleccioná una opción):")

col3, col4, col5 = st.columns(3)

with col3:
    if st.button("🆘 AYUDA", use_container_width=True):
        texto_entrada = "Ayuda"
        st.rerun()

with col4:
    if st.button("🏥 HOSPITAL", use_container_width=True):
        texto_entrada = "Hospital"
        st.rerun()

with col5:
    if st.button("⚠️ PELIGRO", use_container_width=True):
        texto_entrada = "Peligro"
        st.rerun()
