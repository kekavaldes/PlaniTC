"""
PlaniTC — Simulador Educativo de Tomografía Computada
Versión modificada: SIN imagen automática de topograma
"""

import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).parent

def check_password():
    return

check_password()

if "topograma_adquirido" not in st.session_state:
    st.session_state["topograma_adquirido"] = False

st.title("Simulador TC — Topograma")

st.markdown('<div class="section-header">☢️ Parámetros del topograma</div>', unsafe_allow_html=True)

POS_TUBO = [
    "ARRIBA 0°",
    "ABAJO 180°",
    "DERECHA 90°",
    "IZQUIERDA 90°"
]

LONGITUDES_TOPO = [100, 150, 200, 250, 300]

pos_tubo = st.selectbox("Posición del tubo", POS_TUBO, key="t1pt")

col1, col2 = st.columns(2)

with col1:
    topo1_long = st.selectbox("Longitud (mm)", LONGITUDES_TOPO, key="topo1_long")

with col2:
    topo1_kv = st.selectbox("kV", [80, 100, 120, 140], key="topo1_kv")
    topo1_ma = st.selectbox("mA", [20, 35, 50, 100], key="topo1_ma")

if st.button("INICIAR TOPOGRAMA", use_container_width=True):
    st.session_state["topograma_adquirido"] = True

if not st.session_state.get("topograma_adquirido", False):

    st.markdown('<div class="section-header">🖼️ Topograma</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="
        border: 1px solid #333; border-radius: 8px;
        background: #0A0A0A; height: 380px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        text-align: center; gap: 16px;">

        <div style="font-size: 3.5rem; opacity: 0.25;">☢️</div>

        <div style="color: #555; font-size: 0.95rem;">
            Configure los parámetros del topograma<br>
            y presione <strong style="color:#FFD700;">INICIAR TOPOGRAMA</strong>
        </div>

    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown('<div class="section-header">✅ Topograma iniciado</div>', unsafe_allow_html=True)
    st.info("Topograma iniciado. Aquí puedes agregar tu nueva lógica de imágenes.")
