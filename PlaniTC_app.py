
# Versión integrada con ajuste de tamaño de topogramas en Adquisición

import streamlit as st

st.set_page_config(layout="wide")

st.title("Simulador TC - Adquisición")

# Simulación de estado (ejemplo)
if "topogramas" not in st.session_state:
    st.session_state.topogramas = ["topo1.jpg"]  # puede haber 1 o 2

st.header("Topogramas programados")

topos = st.session_state.topogramas

# ---- LÓGICA NUEVA ----
if len(topos) == 1:
    col_centro = st.columns([1,2,1])[1]
    with col_centro:
        st.image(topos[0], width=450)

elif len(topos) == 2:
    col1, col2 = st.columns(2)
    with col1:
        st.image(topos[0], width=350)
    with col2:
        st.image(topos[1], width=350)

# ----------------------

st.info("Aquí iría el resto de tu simulador completo (mantiene toda tu lógica previa).")
