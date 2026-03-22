import streamlit as st
import replicate
import os
import requests
from PIL import Image, ImageDraw
from io import BytesIO
from streamlit_compare_images import compare_images

# --- CONFIGURACIÓN DE SEGURIDAD ---
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

st.set_page_config(page_title="Vision Archival Pro", page_icon="📽️", layout="wide")

# --- ESTILO PROFESIONAL ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00d1b2, #0097a7); color: white; font-weight: bold; border: none; height: 3em; border-radius: 8px; }
    h1 { text-align: center; color: white; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("📽️ VISION ARCHIVAL PRO")
st.markdown("<p style='text-align: center; color: #888;'>Laboratorio Autónomo de Restauración 4K</p>", unsafe_allow_html=True)

# --- FUNCIÓN DE MARCA DE AGUA ---
def add_watermark(image):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    # Dibujar un pequeño texto en la esquina inferior derecha
    text = "Restored by Vision Archival Pro"
    draw.text((width - 250, height - 30), text, fill=(255, 255, 255, 128))
    return image

# --- INTERFAZ DE CARGA ---
st.sidebar.header("⚙️ Parámetros de IA")
upscale = st.sidebar.slider("Escalado (Resolución)", 1, 4, 2)
fidelity = st.sidebar.slider("Fidelidad Facial", 0.0, 1.0, 0.7)

uploaded_file = st.file_uploader("Arrastra tu foto antigua aquí", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img_orig = Image.open(uploaded_file)
    st.image(img_orig, caption="Archivo Original", width=400)
    
    if st.button("✨ INICIAR PROCESO DE RESTAURACIÓN"):
        if "REPLICATE_API_TOKEN" not in os.environ:
            st.error("Falta el API Token de Replicate en los Secrets.")
        else:
            with st.spinner("Restaurando texturas y biometría..."):
                try:
                    output = replicate.run(
                        "tencentarc/gfpgan:9283608cc6b7be6b651febba7e7d20074f4c28f8a62002768a573295235f49f0",
                        input={"img": uploaded_file, "scale": upscale, "fidelity": fidelity}
                    )
                    
                    # Procesar descarga y marca de agua
                    response = requests.get(output)
                    res_img = Image.open(BytesIO(response.content))
                    res_img = add_watermark(res_img)
                    
                    st.success("¡Restauración Completa!")
                    compare_images(img_orig, res_img)
                    
                    # Botón de descarga
                    buf = BytesIO()
                    res_img.save(buf, format="PNG")
                    st.download_button("⬇️ Descargar Resultado 4K", data=buf.getvalue(), file_name="restored.png")
                except Exception as e:
                    st.error(f"Error: {e}")