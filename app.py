import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Traductor Inteligente Gemini", layout="wide", page_icon="🤟")

# --- CONEXIÓN SEGURA A GEMINI VIA SECORES ---
# Streamlit busca automáticamente la clave dentro de .streamlit/secrets.toml
try:
    if "GEMINI_API_KEY" in st.secrets:
        # Inicializa el cliente oficial usando la clave oculta de los secrets
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("🔑 No se encontró la clave en los Secrets. Verifica tu archivo .streamlit/secrets.toml")
        st.stop()
except Exception as e:
    st.error(f"❌ Error al inicializar el cliente de IA: {e}")
    st.stop()

# --- INTERFAZ DE USUARIO ---
st.title("🧠 Traductor Inclusivo Inteligente con Gemini")
st.markdown("### Traducción conceptual y descripción de señas en tiempo real (Argentina ⇄ EEUU)")
st.markdown("---")

# --- PANEL DE CONFIGURACIÓN DE ROLES ---
col_emisor, col_receptor = st.columns(2)
with col_emisor:
    st.markdown("#### **Emisor (Origen)**")
    idioma_origen = st.selectbox("Región/Idioma de Origen:", ["Español (Argentina)", "Inglés (EEUU)"], key="i_origen")

with col_receptor:
    st.markdown("#### **Receptor (Destino)**")
    idioma_destino = st.selectbox("Región/Idioma de Destino:", ["Inglés (EEUU)", "Español (Argentina)"], key="i_destino")

st.markdown("---")

# --- ENTRADA DE TEXTO ---
st.subheader("💬 Mensaje a traducir:")
texto_entrada = st.text_input("Escribí la palabra, frase o situación de emergencia que querés transmitir:")

# --- PROCESAMIENTO CON GEMINI ---
if st.button("🔄 Traducir con Inteligencia Artificial", type="primary", use_container_width=True):
    if texto_entrada:
        with st.spinner("Gemini está procesando y traduciendo el concepto cultural..."):
            
            # Diseñamos un prompt optimizado para el modelo más moderno (gemini-2.5-flash)
            prompt = f"""
            Actúa como un experto intérprete y traductor entre la cultura e idioma de {idioma_origen} y {idioma_destino}.
            Analiza el siguiente mensaje: "{texto_entrada}".
            
            Quiero que devuelvas una respuesta clara con la siguiente estructura:
            1. **TRADUCCIÓN LINEAL**: Traduce el texto directamente al idioma de destino.
            2. **DESCRIPCIÓN DE LA SEÑA**: Si el destino es 'Español (Argentina)', describe detalladamente cómo se realiza esta seña en la Lengua de Señas Argentina (LSA). Si el destino es 'Inglés (EEUU)', describe detalladamente cómo se realiza en American Sign Language (ASL). Sé muy específico con la forma de las manos, la ubicación en el cuerpo y el movimiento exacto.
            """
            
            try:
                # Ejecución de la consulta con el modelo estándar actual
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                st.markdown("---")
                st.subheader("🎯 Resultado del Intérprete Gemini")
                
                # Mostramos la respuesta generada dinámicamente por la IA
                st.markdown(response.text)
                
                # --- GENERACIÓN DE AUDIO DE RESPALDO (VOZ) ---
                st.markdown("---")
                st.subheader("🔊 Audio de respaldo:")
                
                dest_code = 'en' if "Inglés" in idioma_destino else 'es'
                
                # Creamos el archivo de voz temporal basándonos en la entrada traducible
                tts = gTTS(text=texto_entrada, lang=dest_code) 
                audio_path = "temp_gemini_voice.mp3"
                tts.save(audio_path)
                
                with open(audio_path, "rb") as f:
                    st.audio(f.read(), format='audio/mp3')
                os.remove(audio_path)
                
            except Exception as e:
                st.error(f"❌ Error al procesar la solicitud con Gemini: {e}")
    else:
        st.warning("⚠️ Por favor, escribe un mensaje primero.")

# --- FOOTER INFORMATIVO ---
st.markdown("---")
st.caption("🌐 **Ventaja del motor dinámico:** Al usar Gemini, el sistema no tiene un límite de palabras. Puede describir la seña cultural de cualquier frase o combinación compleja que el usuario ingrese.")
