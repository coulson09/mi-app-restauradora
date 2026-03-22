import streamlit as st
import replicate
import os
import requests
from PIL import Image, ImageDraw
from io import BytesIO

# Configuración de seguridad para el Token
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

st.set_page_config(page_title="Vision Archival Pro", page_icon="📽️", layout="wide")

st.title("📽️ VISION ARCHIVAL PRO")
st.markdown("<p style='text-align: center; color: #888;'>Laboratorio de Restauración 4K (Versión Estable)</p>", unsafe_allow_html=True)

def add_watermark(image):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    text = "Restored by Vision Archival Pro"
    draw.text((width - 250, height - 30), text, fill=(255, 255, 255, 128))
    return image

st.sidebar.header("⚙️ Parámetros")
upscale = st.sidebar.slider("Resolución", 1, 4, 2)
fidelity = st.sidebar.slider("Fidelidad Facial", 0.0, 1.0, 0.7)

uploaded_file = st.file_uploader("Sube tu foto antigua", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img_orig = Image.open(uploaded_file)
    
    if st.button("✨ INICIAR RESTAURACIÓN"):
        if "REPLICATE_API_TOKEN" not in os.environ:
            st.error("Configura tu Token en 'Secrets' de Streamlit.")
        else:
            with st.spinner("Procesando..."):
                try:
                    output = replicate.run(
                        "tencentarc/gfpgan:9283608cc6b7be6b651febba7e7d20074f4c28f8a62002768a573295235f49f0",
                        input={"img": uploaded_file, "scale": upscale, "fidelity": fidelity}
                    )
                    
                    response = requests.get(output)
                    res_img = Image.open(BytesIO(response.content))
                    res_img = add_watermark(res_img)
                    
                    st.success("¡Completado!")
                    
                    # Mostrar comparativa lado a lado
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(img_orig, caption="Original")
                    with col2:
                        st.image(res_img, caption="Restaurada 4K")
                    
                    buf = BytesIO()
                    res_img.save(buf, format="PNG")
                    st.download_button("⬇️ Descargar PNG 4K", data=buf.getvalue(), file_name="restaurada.png")
                except Exception as e:
                    st.error(f"Error: {e}")
