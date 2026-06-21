import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Traductor Inclusivo Cruzado", layout="wide", page_icon="🤟")

# --- BASE DE DATOS DE ENLACES PÚBLICOS (WIKIPEDIA) ---
DATABASE = {
    "AYUDA": {
        "es": "Ayuda", "en": "Help", 
        "seña_lsa": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Sign_language_HELP.jpg/220px-Sign_language_HELP.jpg", 
        "seña_asl": "https://upload.wikimedia.org/wikipedia/commons/4/41/Sign_language_HELP.gif"
    },
    "HOSPITAL": {
        "es": "Hospital", "en": "Hospital",
        "seña_lsa": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Sign_language_HOSPITAL.jpg/220px-Sign_language_HOSPITAL.jpg",
        "seña_asl": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Sign_language_HOSPITAL.gif"
    },
    "PELIGRO": {
        "es": "Peligro", "en": "Danger",
        "seña_lsa": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Sign_language_DANGER.jpg/220px-Sign_language_DANGER.jpg",
        "seña_asl": "https://upload.wikimedia.org/wikipedia/commons/1/1b/Sign_language_DANGER.gif"
    }
}

# --- INICIALIZACIÓN DE ESTADOS INTERNOS ---
if "concepto_seleccionado" not in st.session_state:
    st.session_state.concepto_seleccionado = None
if "texto_libre" not in st.session_state:
    st.session_state.texto_libre = ""

# --- INTERFAZ ---
st.title("🤟 Conector Universal de Comunicación Inclusiva")
st.markdown("### Traducción Bidireccional Cruzada (Seña ⇄ Seña ⇄ Texto ⇄ Voz)")
st.markdown("---")

# --- PANEL DE CONFIGURACIÓN DE ROLES ---
col_emisor, col_receptor = st.columns(2)

with col_emisor:
    st.markdown("#### **Emisor (Quien envía el mensaje)**")
    formato_origen = st.radio("¿Cómo se expresa el emisor?:", ["Usa Lenguaje de Señas", "Escribe Texto / Usa Voz"], key="f_origen")
    idioma_origen = st.selectbox("Región de Origen:", ["Español (Argentina)", "Inglés (EEUU)"], key="i_origen")

with col_receptor:
    st.markdown("#### **Receptor (Quien recibe el mensaje)**")
    formato_destino = st.radio("¿Cómo quiere recibirlo el receptor?:", ["Ver Lenguaje de Señas", "Leer Texto y Escuchar Voz"], key="f_destino")
    idioma_destino = st.selectbox("Región de Destino:", ["Español (Argentina)", "Inglés (EEUU)"], key="i_destino")

st.markdown("---")

# Lógica de banderas de idioma
origen_es_arg = "Argentina" in idioma_origen
destino_es_arg = "Argentina" in idioma_destino
src_lang_code = 'es' if origen_es_arg else 'en'
dest_lang_code = 'en' if destino_es_arg else 'es'

# --- GESTIÓN DE ENTRADAS ---
texto_a_traducir = ""

if formato_origen == "Usa Lenguaje de Señas":
    st.subheader("👋 Teclado de Señas del Emisor")
    st.caption("Presioná sobre tu seña para cargarla al sistema:")
    
    key_foto_origen = "seña_lsa" if origen_es_arg else "seña_asl"
    columnas = st.columns(len(DATABASE))
    
    for i, (clave_concepto, datos) in enumerate(DATABASE.items()):
        with columnas[i]:
            st.image(datos[key_foto_origen], width=140)
            if st.button(f"Firmar: {clave_concepto}", key=f"btn_{clave_concepto}", use_container_width=True):
                st.session_state.concepto_seleccionado = clave_concepto
                st.session_state.texto_libre = ""  # Limpiamos el campo manual si se usa el teclado
                
    if st.session_state.concepto_seleccionado:
        texto_a_traducir = DATABASE[st.session_state.concepto_seleccionado][src_lang_code]
        st.info(f"Seña de entrada capturada en origen: **{texto_a_traducir}**")

else:
    st.subheader("💬 Entrada Manual por Texto / Voz")
    st.session_state.texto_libre = st.text_input("Escribí acá tu mensaje (ej: ayuda, hospital, peligro):", value=st.session_state.texto_libre)
    if st.session_state.texto_libre:
        texto_a_traducir = st.session_state.texto_libre
        st.session_state.concepto_seleccionado = None  # Limpiamos el estado del botón si escribe

# --- TRADUCCIÓN Y DESPLIEGUE DE SALIDAS ---
if texto_a_traducir:
    st.markdown("---")
    st.subheader("🎯 Resultado en el Destino")
    
    # 1. Ejecución de la pasarela lingüística de traducción
    try:
        if src_lang_code == dest_lang_code:
            texto_final_traducido = texto_a_traducir
        else:
            texto_final_traducido = GoogleTranslator(source=src_lang_code, target=dest_lang_code).translate(texto_a_traducir)
    except Exception as e:
        texto_final_traducido = texto_a_traducir
        st.error(f"Error en el motor de traducción: {e}")

    # 2. Renderizado de salida según la preferencia del receptor
    if formato_destino == "Leer Texto y Escuchar Voz":
        st.success(f"🗣️ **Mensaje Traducido:** {texto_final_traducido}")
        try:
            tts = gTTS(text=texto_final_traducido, lang=dest_lang_code)
            audio_path = "temp_voice.mp3"
            tts.save(audio_path)
            with open(audio_path, "rb") as f:
                st.audio(f.read(), format='audio/mp3')
            os.remove(audio_path)
        except Exception as e:
            st.caption(f"(Voz de lectura no disponible: {e})")
    else:
        st.info(f"📋 **Texto de respaldo:** {texto_final_traducido}")
        seña_localizada = False
        key_foto_destino = "seña_lsa" if destino_es_arg else "seña_asl"
        
        for clave, datos in DATABASE.items():
            if (st.session_state.concepto_seleccionado == clave or
                datos["es"].lower() in texto_a_traducir.lower() or 
                datos["en"].lower() in texto_a_traducir.lower() or
                datos["es"].lower() in texto_final_traducido.lower() or
                datos["en"].lower() in texto_final_traducido.lower()):
                
                nom_destino = "LSA (Argentina)" if destino_es_arg else "ASL (EEUU)"
                st.markdown(f"#### 👋 Seña traducida al sistema {nom_destino}:")
                st.image(datos[key_foto_destino], width=320, caption=f"Seña de '{datos[dest_lang_code]}'")
                seña_localizada = True
                break
                
        if not seña_localizada:
            st.warning("⚠️ Texto traducido con éxito, pero este concepto no está guardado en el diccionario de señas.")
