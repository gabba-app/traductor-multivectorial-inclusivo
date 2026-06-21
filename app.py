import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Traductor Inclusivo Cruzado", layout="wide", page_icon="🤟")

# --- BASE DE DATOS DE CONCEPTOS (CRUZADA) ---
# Contiene el texto y la seña correspondiente para cada cultura
DATABASE = {
    "AYUDA": {
        "es": "Ayuda", 
        "en": "Help", 
        "seña_lsa": "https://media.spreadthesign.com/image/500/help-2763.jpg",      # LSA (Arg)
        "seña_asl": "https://www.lifeprint.com/asl101/gifs/h/help.gif"             # ASL (EEUU)
    },
    "HOSPITAL": {
        "es": "Hospital", 
        "en": "Hospital",
        "seña_lsa": "https://media.spreadthesign.com/image/500/hospital-2275.jpg",
        "seña_asl": "https://media.spreadthesign.com/image/500/hospital-2.jpg"
    },
    "PELIGRO": {
        "es": "Peligro", 
        "en": "Danger",
        "seña_lsa": "https://media.spreadthesign.com/image/500/danger-12534.jpg",
        "seña_asl": "https://media.spreadthesign.com/image/500/danger-1520.jpg"
    },
    "GRACIAS": {
        "es": "Gracias",
        "en": "Thank you",
        "seña_lsa": "https://media.spreadthesign.com/image/500/thank-you-2342.jpg",
        "seña_asl": "https://www.lifeprint.com/asl101/gifs/t/thankyou.gif"
    }
}

# --- TÍTULO ---
st.title("🤟 Conector Universal de Comunicación")
st.markdown("### Traducción Cruzada: Señas ⇄ Texto ⇄ Voz (Argentina ⇄ EEUU)")
st.markdown("---")

# --- PANEL DE CONFIGURACIÓN DE CANALES ---
st.subheader("⚙️ Configuración del Canal de Comunicación")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### **Emisor (Quien envía el mensaje)**")
    tipo_origen = st.radio("Formato de entrada:", ["Texto / Voz de un Oyente", "Lengua de Señas de un Mudo"], key="origen_tipo")
    idioma_origen = st.selectbox("Cultura/Idioma de Origen:", ["Español (Argentina)", "Inglés (EEUU)"], key="origen_lang")

with col2:
    st.markdown("#### **Receptor (Quien recibe el mensaje)**")
    tipo_destino = st.radio("Formato de salida deseado:", ["Texto y Voz (Para Oyentes)", "Lengua de Señas (Para Mudos)"], key="destino_tipo")
    idioma_destino = st.selectbox("Cultura/Idioma de Destino:", ["Español (Argentina)", "Inglés (EEUU)"], key="destino_lang")

st.markdown("---")

# Variables lógicas simplificadas
es_origen_latam = "Argentina" in idioma_origen
es_destino_latam = "Argentina" in idioma_destino

# --- ENTRADA DE DATOS SEGÚN EL TIPO DE EMISOR ---
texto_a_procesar = ""

if tipo_origen == "Lengua de Señas de un Mudo":
    st.subheader("👋 Panel de Señas de Entrada")
    st.info("Hacé clic en la seña que estás realizando para enviarla al sistema:")
    
    # Determinar qué imágenes de señas mostrar en el teclado según el origen seleccionado
    key_foto_origen = "seña_lsa" if es_origen_latam else "seña_asl"
    idioma_clave_origen = "es" if es_origen_latam else "en"
    
    # Renderizar los botones con las señas correspondientes
    columnas_señas = st.columns(len(DATABASE))
    for i, (clave_concepto, datos) in enumerate(DATABASE.items()):
        with columnas_señas[i]:
            st.image(datos[key_foto_origen], width=140)
            if st.button(f"Firmar: {clave_concepto}", key=f"btn_{clave_concepto}", use_container_width=True):
                # El sistema detecta el concepto exacto mapeado internamente
                texto_a_procesar = datos[idioma_clave_origen]

else:
    st.subheader("💬 Entrada por Texto o Voz")
    texto_a_procesar = st.text_input(
        "Escribí tu mensaje aquí (ej: Hola, necesito ayuda, hospital...):",
        placeholder="Escribí acá..."
    )

# --- PROCESAMIENTO Y TRADUCCIÓN MULTIDIRECCIONAL ---
if texto_a_procesar:
    st.markdown("---")
    st.subheader("🎯 Resultado de la Traducción")
    
    # 1. Definir códigos de idioma para el motor de traducción de texto
    src_code = 'es' if es_origen_latam else 'en'
    dest_code = 'en' if es_destino_latam else 'es'
    
    # 2. Traducir el texto base
    try:
        if src_code == dest_code:
            texto_traducido = texto_a_procesar
        else:
            texto_traducido = GoogleTranslator(source=src_code, target=dest_code).translate(texto_a_procesar)
    except Exception as e:
        texto_traducido = texto_a_procesar
        st.error(f"Error en la pasarela de traducción: {e}")

    # --- MOSTRAR SALIDAS SEGÚN LO SOLICITADO POR EL RECEPTOR ---
    
    if tipo_destino == "Texto y Voz (Para Oyentes)":
        # Salida pensada para el oyente
        st.success(f"🗣️ **Mensaje Traducido:** {texto_traducido}")
        
        # Generar audio hablado en el idioma de destino
        try:
            tts = gTTS(text=texto_traducido, lang=dest_code)
            filename = "output_speech.mp3"
            tts.save(filename)
            with open(filename, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format='audio/mp3')
            os.remove(filename)
        except Exception as e:
            st.caption(f"(Audio no disponible de momento: {e})")
            
    else:
        # Salida pensada para el mudo (Señas del país de destino)
        st.info(f"📋 **Texto de respaldo:** {texto_traducido}")
        
        # Buscar la seña equivalente en la base de datos para el idioma destino
        seña_encontrada = False
        key_foto_destino = "seña_lsa" if es_destino_latam else "seña_asl"
        
        for clave, datos in DATABASE.items():
            # Buscamos si la palabra ingresada o traducida coincide con el diccionario
            if (datos["es"].lower() in texto_a_procesar.lower() or 
                datos["en"].lower() in texto_a_procesar.lower() or
                datos["es"].lower() in texto_traducido.lower() or
                datos["en"].lower() in texto_traducido.lower()):
                
                st.markdown(f"#### 👋 Interpretación en Señas para el receptor:")
                st.image(datos[key_foto_destino], width=350, caption=f"Seña oficial en {'LSA (Argentina)' if es_destino_latam else 'ASL (EEUU)'}")
                seña_encontrada = True
                break
                
        if not seña_encontrada:
            st.warning("⚠️ El mensaje se tradujo a texto, pero no poseemos el registro visual de esa seña exacta en el sistema adaptado.")

st.markdown("---")
st.caption("💡 **Tip de uso:** Podés combinar cualquier Entrada con cualquier Salida. Por ejemplo: Configurar Origen en 'Lengua de Señas' + 'Inglés (EEUU)' y Destino en 'Texto y Voz' + 'Español (Argentina)' para que un usuario sordo norteamericano se comunique fluidamente con un argentino oyente.")
