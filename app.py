import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Traductor de Señas e Idiomas Cruzado", 
    layout="wide", 
    page_icon="🤟"
)

# --- BASE DE DATOS DE CONCEPTOS CRUZADOS ---
# Cada objeto representa un concepto abstracto con sus respectivas palabras y señas por región.
DATABASE = {
    "AYUDA": {
        "es": "Ayuda", 
        "en": "Help", 
        "seña_lsa": "https://media.spreadthesign.com/image/500/help-2763.jpg",      # LSA (Argentina)
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
    },
    "BAÑO": {
        "es": "Baño",
        "en": "Bathroom",
        "seña_lsa": "https://media.spreadthesign.com/image/500/toilet-9252.jpg",
        "seña_asl": "https://www.lifeprint.com/asl101/gifs/t/toilet.gif"
    }
}

# --- INICIALIZACIÓN DEL ESTADO DE STREAMLIT ---
# Se utiliza session_state para evitar que los datos se borren al interactuar con los botones
if "concepto_seleccionado" not in st.session_state:
    st.session_state.concepto_seleccionado = None
if "texto_libre" not in st.session_state:
    st.session_state.texto_libre = ""

# --- INTERFAZ DE USUARIO ---
st.title("🤟 Conector Universal de Comunicación Inclusiva")
st.markdown("### Traducción lingüística y cultural multidireccional (Argentina ⇄ EEUU)")
st.markdown("---")

# --- PANEL DE CONFIGURACIÓN DE ROLES ---
st.subheader("⚙️ Configuración de los Canales de Comunicación")
col_emisor, col_receptor = st.columns(2)

with col_emisor:
    st.markdown("#### **Emisor (Quien envía el mensaje)**")
    formato_origen = st.radio(
        "¿Cómo se expresa el emisor?", 
        ["Usa Lenguaje de Señas", "Escribe Texto / Habla por Voz"], 
        key="f_origen"
    )
    idioma_origen = st.selectbox(
        "Cultura / Región de Origen:", 
        ["Español (Argentina)", "Inglés (EEUU)"], 
        key="i_origen"
    )

with col_receptor:
    st.markdown("#### **Receptor (Quien recibe el mensaje)**")
    formato_destino = st.radio(
        "¿Cómo quiere recibirlo el receptor?", 
        ["Ver Lenguaje de Señas", "Leer Texto y Escuchar Voz"], 
        key="f_destino"
    )
    idioma_destino = st.selectbox(
        "Cultura / Región de Destino:", 
        ["Español (Argentina)", "Inglés (EEUU)"], 
        key="i_destino"
    )

st.markdown("---")

# Variables lógicas simplificadas para el procesamiento
origen_es_arg = "Argentina" in idioma_origen
destino_es_arg = "Argentina" in idioma_destino

src_lang_code = 'es' if origen_es_arg else 'en'
dest_lang_code = 'en' if destino_es_arg else 'es'

# --- ENTRADA DE DATOS (INPUT) ---
texto_a_traducir = ""

if formato_origen == "Usa Lenguaje de Señas":
    st.subheader("👋 Panel Teclado de Señas de Entrada")
    st.caption("Presioná la seña que estás realizando para que el sistema procese su significado:")
    
    # Identificar qué tipo de imágenes mostrar en los botones según el emisor
    key_foto_origen = "seña_lsa" if origen_es_arg else "seña_asl"
    
    # Dibujar la cuadrícula dinámica de botones de señas
    columnas = st.columns(len(DATABASE))
    for i, (clave_concepto, datos) in enumerate(DATABASE.items()):
        with columnas[i]:
            st.image(datos[key_foto_origen], width=130)
            if st.button(f"Hacer Seña: {clave_concepto}", key=f"btn_{clave_concepto}", use_container_width=True):
                st.session_state.concepto_seleccionado = clave_concepto
                st.session_state.texto_libre = ""  # Limpia el texto manual si usa señas
                
    if st.session_state.concepto_seleccionado:
        # Extraemos la palabra exacta en el idioma del origen según el concepto pulsado
        texto_a_traducir = DATABASE[st.session_state.concepto_seleccionado][src_lang_code]
        st.info(f"Concepto de seña registrado en origen: **{texto_a_traducir}**")

else:
    st.subheader("💬 Entrada por Texto o Dictado de Voz")
    st.session_state.texto_libre = st.text_input(
        "Escribí el mensaje o frase aquí:", 
        value=st.session_state.texto_libre,
        placeholder="Ej: Necesito ayuda urgente..."
    )
    if st.session_state.texto_libre:
        texto_a_traducir = st.session_state.texto_libre
        st.session_state.concepto_seleccionado = None  # Limpia la seña si escribe manualmente

# --- PROCESAMIENTO Y TRADUCCIÓN ---
if texto_a_traducir:
    st.markdown("---")
    st.subheader("🎯 Resultado de la Conversión en Destino")
    
    # 1. Ejecutar la pasarela de traducción de texto a nivel lingüístico
    try:
        if src_lang_code == dest_lang_code:
            texto_final_traducido = texto_a_traducir
        else:
            texto_final_traducido = GoogleTranslator(source=src_lang_code, target=dest_lang_code).translate(texto_a_traducir)
    except Exception as e:
        texto_final_traducido = texto_a_traducir
        st.error(f"Error en el motor de traducción: {e}")

    # 2. RENDERIZAR LAS SALIDAS SOLICITADAS POR EL RECEPTOR
    
    if formato_destino == "Leer Texto y Escuchar Voz":
        # Bloque de salida estructurado para personas oyentes
        st.success(f"🗣️ **Mensaje Traducido:** {texto_final_traducido}")
        
        # Procesamiento del motor de Voz (gTTS) sin interrupciones del sistema
        try:
            tts = gTTS(text=texto_final_traducido, lang=dest_lang_code)
            audio_path = "temp_output_voice.mp3"
            tts.save(audio_path)
            
            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
            os.remove(audio_path) # Limpieza inmediata del buffer
        except Exception as e:
            st.caption(f"(Voz de lectura no disponible momentáneamente: {e})")

    else:
        # Bloque de salida estructurado para personas sordas (Muestra señas de la cultura destino)
        st.info(f"📋 **Texto de apoyo:** {texto_final_traducido}")
        
        # Buscar correspondencia del mensaje con los diccionarios gráficos de señas
        seña_localizada = False
        key_foto_destino = "seña_lsa" if destino_es_arg else "seña_asl"
        
        for clave, datos in DATABASE.items():
            # Validación inteligente: verifica si coincide por concepto activo o por palabras clave del texto
            if (st.session_state.concepto_seleccionado == clave or
                datos["es"].lower() in texto_a_traducir.lower() or 
                datos["en"].lower() in texto_a_traducir.lower() or
                datos["es"].lower() in texto_final_traducido.lower() or
                datos["en"].lower() in texto_final_traducido.lower()):
                
                nombre_cultura_destino = "LSA (Argentina)" if destino_es_arg else "ASL (EEUU)"
                st.markdown(f"#### 👋 Seña equivalente en el idioma destino ({nombre_cultura_destino}):")
                st.image(datos[key_foto_destino], width=380, caption=f"Seña correspondiente a '{datos[dest_lang_code]}'")
                seña_localizada = True
                break
                
        if not seña_localizada:
            st.warning("⚠️ El texto se tradujo correctamente, pero este término no cuenta con un registro gráfico de seña incorporado en la base de datos local.")

# --- FOOTER INFORMATIVO ---
st.markdown("---")
st.caption("💡 **Ejemplo de uso de matriz cruzada:** Configurá Emisor en 'Lenguaje de Señas' + 'Inglés (EEUU)' y Receptor en 'Ver Lenguaje de Señas' + 'Español (Argentina)' para ver cómo el sistema traduce una seña americana (ASL) directamente a una seña argentina (LSA).")
