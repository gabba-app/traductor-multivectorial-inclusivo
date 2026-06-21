import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
import os
from PIL import Image
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Traductor con Generación de Señas", layout="wide", page_icon="🤟")

# --- CONEXIÓN A GEMINI VIA SECRETS ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("🔑 Falta la clave en los Secrets de Streamlit.")
        st.stop()
except Exception as e:
    st.error(f"❌ Error de inicialización: {e}")
    st.stop()

# --- INTERFAZ ---
st.title("🧠 Traductor Inclusivo con Generación de Imágenes de IA")
st.markdown("### Traduce texto y genera la ilustración de la seña en tiempo real usando Google Imagen 3")
st.markdown("---")

col_emisor, col_receptor = st.columns(2)
with col_emisor:
    st.markdown("#### **Emisor (Origen)**")
    idioma_origen = st.selectbox("Región de Origen:", ["Español (Argentina)", "Inglés (EEUU)"], key="i_origen")

with col_receptor:
    st.markdown("#### **Receptor (Destino)**")
    idioma_destino = st.selectbox("Región de Destino:", ["Inglés (EEUU)", "Español (Argentina)"], key="i_destino")

st.markdown("---")

st.subheader("💬 Mensaje a transmitir:")
texto_entrada = st.text_input("Escribí acá tu frase o palabra (ej: Ayuda, Peligro, Hospital):")

if st.button("🔄 Traducir y Generar Imagen", type="primary", use_container_width=True):
    if texto_entrada:
        with st.spinner("La IA está traduciendo y dibujando la seña..."):
            
            # DETERMINAR EL TIPO DE SEÑA SEGÚN EL DESTINO
            tipo_seña = "Lengua de Señas Argentina (LSA)" if "Argentina" in idioma_destino else "American Sign Language (ASL)"
            
            # 1. GENERACIÓN DE TEXTO Y DESCRIPCIÓN CON GEMINI
            prompt_texto = f"""
            Actúa como un experto intérprete entre {idioma_origen} y {idioma_destino}.
            Mensaje: "{texto_entrada}".
            Devuelve:
            1. **TRADUCCIÓN**: La frase traducida linealmente.
            2. **EXPLICACIÓN TÉCNICA**: Una breve descripción de cómo se realiza la seña en {tipo_seña}.
            """
            
            try:
                # Consultamos al modelo de texto
                response_texto = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_texto)
                
                st.markdown("---")
                st.subheader("🎯 Resultado del Intérprete")
                st.markdown(response_texto.text)
                
                # 2. GENERACIÓN DE LA IMAGEN EN TIEMPO REAL CON IMAGEN 3
                st.markdown("---")
                st.subheader("🖼️ Ilustración de la Seña Generada por IA")
                
                # Diseñamos un prompt gráfico ultra detallado para que el dibujante artificial no falle
                prompt_imagen = f"""
                A clear, instructional vector style illustration or 2D drawing of a person's hands performing the sign for '{texto_entrada}' in {tipo_seña}. 
                White background, educational sign language dictionary style, focused on hand gestures and clear movement lines.
                """
                
                # Llamamos al modelo oficial de generación de imágenes de Google
                result_imagen = client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=prompt_imagen,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        output_mime_type="image/jpeg",
                        aspect_ratio="1:1"
                    )
                )
                
                # Procesamos los bytes devueltos por el servidor y los transformamos en imagen visible
                for generated_image in result_imagen.generated_images:
                    image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                    st.image(image, width=380, caption=f"Representación visual de la seña generada para: {texto_entrada}")
                
                # 3. AUDIO DE RESPALDO (VOZ)
                dest_code = 'en' if "Inglés" in idioma_destino else 'es'
                tts = gTTS(text=texto_entrada, lang=dest_code) 
                audio_path = "temp_voice.mp3"
                tts.save(audio_path)
                with open(audio_path, "rb") as f:
                    st.audio(f.read(), format='audio/mp3')
                os.remove(audio_path)
                
            except Exception as e:
                st.error(f"❌ Error en el procesamiento de IA: {e}")
                st.info("Nota: Asegúrate de que tu cuenta de Google AI Studio tenga habilitado el acceso al modelo Imagen 3.")
