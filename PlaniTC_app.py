# PlaniTC - versión con imagen más grande en inicio
import streamlit as st

st.set_page_config(layout="wide")

tabs = st.tabs(["Inicio", "Ingreso", "Adquisición"])

with tabs[0]:
    col1, col2 = st.columns([2.5, 1])  # imagen más grande

    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/8/8e/CT_head_scan.jpg", use_container_width=True)

    with col2:
        st.markdown("""
        <div style='
        background-color:#1e1e1e;
        padding:20px;
        border-radius:10px;
        font-size:13px;
        line-height:1.5;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.3);
        margin-top:40px;
        '>
        <b>¿Cómo usar PlaniTC?</b><br><br>
        <b>1.</b> Ingrese datos del paciente<br>
        <b>2.</b> Seleccione examen<br>
        <b>3.</b> Configure topograma<br>
        <b>4.</b> Programe adquisiciones<br>
        <b>5.</b> Revise resultados
        </div>
        """, unsafe_allow_html=True)

with tabs[1]:
    st.write("Ingreso paciente")

with tabs[2]:
    st.write("Adquisición")
