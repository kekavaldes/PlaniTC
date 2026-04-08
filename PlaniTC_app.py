
import streamlit as st
from pathlib import Path
from datetime import date
import base64
import re
from html import escape
from PIL import Image, ImageDraw

st.set_page_config(page_title="Simulador TC", layout="wide")


st.markdown("""
<style>
:root {
    --bg-main: #000000;
    --bg-secondary: #0f0f0f;
    --text-main: #ffffff;
    --text-secondary: #d9d9d9;
    --border-main: #2a2a2a;
    --input-bg: #ffffff;
    --input-text: #000000;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
    background: var(--bg-main) !important;
    color: var(--text-main) !important;
}

[data-testid="stAppViewContainer"] > .main,
[data-testid="stSidebar"],
section[data-testid="stSidebar"] {
    background: var(--bg-main) !important;
    color: var(--text-main) !important;
}

.block-container {
    background: var(--bg-main) !important;
    color: var(--text-main) !important;
    padding-top: 1.5rem;
}

h1, h2, h3, h4, h5, h6, p, label, span, div, small {
    color: var(--text-main);
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: var(--text-main) !important;
}

hr {
    border-color: var(--border-main) !important;
}

.stButton > button,
[data-testid="baseButton-secondary"],
[data-testid="baseButton-primary"] {
    background: #111111 !important;
    color: #ffffff !important;
    border: 1px solid #3a3a3a !important;
}

.stButton > button:hover,
[data-testid="baseButton-secondary"]:hover,
[data-testid="baseButton-primary"]:hover {
    background: #1d1d1d !important;
    color: #ffffff !important;
    border: 1px solid #5a5a5a !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="select"] input,
.stTextInput input,
.stNumberInput input,
.stDateInput input,
textarea {
    background: var(--input-bg) !important;
    color: var(--input-text) !important;
    border-radius: 12px !important;
}

div[data-baseweb="select"] * {
    color: var(--input-text) !important;
}

div[data-baseweb="select"] svg {
    fill: #000000 !important;
}

/* menú desplegable */
div[data-baseweb="popover"],
div[data-baseweb="popover"] *,
ul[role="listbox"],
ul[role="listbox"] *,
div[role="listbox"],
div[role="listbox"] *,
li[role="option"],
div[role="option"] {
    color: #000000 !important;
}

div[data-baseweb="popover"] {
    background: #ffffff !important;
}

ul[role="listbox"],
div[role="listbox"] {
    background: #ffffff !important;
    color: #000000 !important;
}

li[role="option"],
div[role="option"] {
    background: #ffffff !important;
    color: #000000 !important;
}

li[role="option"]:hover,
div[role="option"]:hover,
li[aria-selected="true"],
div[aria-selected="true"] {
    background: #eaeaea !important;
    color: #000000 !important;
}

ul[role="listbox"] {
    background: #ffffff !important;
    color: #000000 !important;
}

ul[role="listbox"] li,
ul[role="listbox"] div {
    background: #ffffff !important;
    color: #000000 !important;
}

[data-baseweb="popover"] {
    background: #ffffff !important;
    color: #000000 !important;
}

.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stSelectbox label,
.stTextArea label {
    color: #ffffff !important;
}

[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] button,
[data-testid="stFileUploader"] small {
    color: #ffffff !important;
}

[data-testid="stAlert"] {
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)


BASE_DIR = Path(__file__).parent
PORTADA_IMG = BASE_DIR / "tomografo_portada.png"
A_PRACTICAR_IMG = BASE_DIR / "a_practicar.png"
TOPOGRAMA_IMG = BASE_DIR / "topograma.png"
PACIENTE_IMG = next((p for p in [BASE_DIR / "paciente.png", BASE_DIR / "paciente.jpg"] if p.exists()), None)

# -----------------------------------------------------------------------------
# DATOS TOMADOS DEL EXCEL PlaniTC.xlsm + estructura del simulador del repositorio
# -----------------------------------------------------------------------------
REGION_TO_EXAMS = {
    "CABEZA": ["CEREBRO", "ORBITAS", "OIDOS", "SPN", "MAXILOFACIAL"],
    "CUELLO": ["CUELLO"],
    "EESS": ["HOMBRO", "BRAZO", "CODO", "ANTEBRAZO", "MUÑECA", "MANO"],
    "COLUMNA": ["CERVICAL", "DORSAL", "LUMBAR", "SACROCOXIS"],
    "CUERPO": ["TORAX", "ABDOMEN", "PELVIS", "ABDOMEN-PELVIS", "TORAX-ABDOMEN-PELVIS"],
    "EEII": ["CADERA", "MUSLO", "RODILLA", "TOBILLO", "PIE"],
    "ANGIO": ["CEREBRO", "CUELLO", "ART PULMONARES", "AORTA", "EESS", "EEII"],
}
POSICIONES_PACIENTE = [
    "DECUBITO SUPINO",
    "DECUBITO PRONO",
    "DECUBITO LATERAL DERECHO",
    "DECUBITO LATERAL IZQUIERDO",
]
POSICIONES_TUBO = ["ARRIBA 0°", "ABAJO 180°", "DERECHA 90°", "IZQUIERDA 90°"]
INSTRUCCIONES_VOZ = ["NINGUNA", "INSPIRACIÓN", "ESPIRACIÓN", "NO TRAGAR", "VALSALVA", "NO RESPIRE"]
RETARDOS = ["2 sg", "3 sg", "4 sg", "5 sg", "6 sg"]
LONGITUDES_TOPO = [128, 256, 512, 768, 1020, 1560]
APLICA_TOPO = ["SI", "NO"]
ML_INYECTORA = list(range(0, 151, 10))
CANTIDAD_CONTRASTE = list(range(0, 151, 5))

TIPOS_EXPLORACION = ["HELICOIDAL", "SECUENCIAL CONTIGUO", "SECUENCIAL ESPACIADO"]
DOBLE_MUESTREO = ["SI", "NO"]
MODULACION_CORRIENTE = ["CARE DOSE 4D", "AUTO mA", "MANUAL"]
KV_OPCIONES = [70, 80, 90, 100, 110, 120]
MAS_OPCIONES = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
RANGO_MA_OPCIONES = ["30 - 400", "40 - 300", "60 - 500", "130 - 400", "140 - 500"]
INDICE_RUIDO = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
INDICE_CALIDAD = [80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]
CONF_DETECTORES = [
    "8 x 1,25 mm", "16 x 0,625 mm", "32 x 0,6 mm", "32 x 0,625 mm",
    "32 x 1,2 mm", "32 x 1,25 mm", "64 x 0,6 mm", "64 x 0,625 mm"
]
COBERTURA_MAP = {
    "8 x 1,25 mm": "10 mm",
    "16 x 0,625 mm": "10 mm",
    "32 x 0,6 mm": "19,2 mm",
    "32 x 0,625 mm": "20 mm",
    "32 x 1,2 mm": "38,4 mm",
    "32 x 1,25 mm": "40 mm",
    "64 x 0,6 mm": "38,4 mm",
    "64 x 0,625 mm": "40 mm",
}
SFOV_OPCIONES = ["Cabeza", "Cuello", "Tórax", "Abdomen", "Pelvis", "Extremidades"]
ROTACION_TUBO = ["0,33 s", "0,4 s", "0,5 s", "0,75 s", "1 s"]
PITCH_OPCIONES = ["0,5", "0,6", "0,8", "1", "1,2", "1,4", "1,5"]

FASES_RECONS = [
    "SIN CONTRASTE", "ARTERIAL", "VENOSA", "TARDIA", "ANGIOGRÁFICA",
    "REPOSO", "VALSALVA", "INSPIRACIÓN", "ESPIRACIÓN",
]
TIPOS_RECONS = ["RETROP. FILTRADA", "RECONS. ITERATIVA"]
ITERATIVAS = ["SAFIRE", "ADMIRE", "VEO", "ASIR-V", "iDOSE", "AIDR 3D"]
INTENSIDADES = [
    "1", "2", "3", "4", "5", "6", "7",
    "0 (%)", "10 (%)", "20 (%)", "30 (%)", "40 (%)", "50 (%)", "60 (%)", "70 (%)", "80 (%)", "90 (%)",
    "Mild", "Standard", "Strong"
]
KERNELS = ["SUAVE 20f", "STANDARD 30f", "DEFINIDO 60f", "ULTRADEFINIDO 80f"]
GROSOR_RECONS = ["0,6 mm", "0,625 mm", "1 mm", "1,2 mm", "1,25 mm", "1,5 mm", "2 mm", "3 mm", "4 mm", "5 mm"]
INCREMENTO_RECONS = ["0,3 mm", "0,5 mm", "0,6 mm", "0,75 mm", "1 mm", "1,5 mm", "2 mm", "2,5 mm"]
VENTANAS = ["Partes blandas", "Ósea", "Pulmonar", "Cerebro", "Angiografía"]
WW_OPCIONES = ["80", "120", "350", "400", "1500", "2000"]
WL_OPCIONES = ["40", "50", "300", "-600", "35", "400"]
DFOV_OPCIONES = ["180 mm", "220 mm", "250 mm", "320 mm", "350 mm", "420 mm"]

REFORM_RECONSTRUCCION = ["Partes blandas", "Ósea", "Pulmonar", "Angiografía", "De cerebro"]
REFORM_FASE = ["Sin contraste", "Angiografía", "Arterial", "Venosa o portal", "Tardía"]
REFORM_TIPO = ["MPR", "VR", "MIP", "miniMIP"]
REFORM_PLANO = [
    "Axial", "Coronal", "Sagital", "Oblicuo", "Parasagital derecho",
    "Parasagital izquierdo", "Radial", "Coronal oblicuo derecho", "Coronal oblicuo izquierdo",
]

DEFAULTS = {
    "seccion": "Portada",
    "prep_nombres": "",
    "prep_apellidos": "",
    "prep_fecha_nac": date(2000, 1, 1),
    "prep_examen": "",
    "prep_peso": 70,
    "prep_embarazo": "Seleccionar",
    "prep_creatinina": "Seleccionar",
    "prep_medio_contraste_ev": "Seleccionar",
    "prep_via_venosa": "Seleccionar",
    "prep_cantidad_contraste": "Seleccionar",
    "prep_metodo_inyeccion": "Seleccionar",
    "prep_medio_contraste_oral": "Seleccionar",
    "topo_region_anatomica": "Seleccionar",
    "topo_region": "Seleccionar",
    "topo_posicionamiento": "Seleccionar",
    "topo_posicion_tubo": "Seleccionar",
    "topo_instruccion_voz": "Seleccionar",
    "topo_longitud": 512,
    "topo_retardo": "2 sg",
    "topo_aplica_topo2": "NO",
    "adq_fase_adquisicion": "Seleccionar",
    "adq_instruccion_voz": "Seleccionar",
    "adq_delay": "Seleccionar",
    "adq_tipo_exploracion": "Seleccionar",
    "adq_doble_muestreo": "NO",
    "adq_modulacion_corriente": "Seleccionar",
    "adq_kv": "Seleccionar",
    "adq_mas": "Seleccionar",
    "adq_rango_ma": "Seleccionar",
    "adq_indice_calidad": "Seleccionar",
    "adq_indice_ruido": "Seleccionar",
    "adq_matriz_detectores": "Seleccionar",
    "adq_colimacion": "",
    "adq_sfov": "Seleccionar",
    "adq_rotacion_tubo": "Seleccionar",
    "adq_pitch": "Seleccionar",
    "adq_inicio_adquisicion": "",
    "adq_fin_adquisicion": "",
    "recon_fase": "Seleccionar",
    "recon_tipo": "Seleccionar",
    "recon_iterativa": "Seleccionar",
    "recon_intensidad": "Seleccionar",
    "recon_kernel": "Seleccionar",
    "recon_grosor": "Seleccionar",
    "recon_incremento": "Seleccionar",
    "recon_ventana": "Seleccionar",
    "recon_ww": "Seleccionar",
    "recon_wl": "Seleccionar",
    "recon_dfov": "Seleccionar",
    "recon_inicio": "",
    "recon_fin": "",
    "recon_imagen_subida_bytes": None,
    "recon_imagen_subida_nombre": "",
    "recon_imagen_subida_mime": "",
    "reform_reconstruccion": "Seleccionar",
    "reform_fase": "Seleccionar",
    "reform_tipo": "Seleccionar",
    "reform_plano": "Seleccionar",
    "reform_grosor": "",
    "reform_distancia": "",
    "reform_rangos_img1_bytes": None,
    "reform_rangos_img1_nombre": "",
    "reform_rangos_img1_mime": "",
    "reform_rangos_img2_bytes": None,
    "reform_rangos_img2_nombre": "",
    "reform_rangos_img2_mime": "",
    "reform_rangos_img3_bytes": None,
    "reform_rangos_img3_nombre": "",
    "reform_rangos_img3_mime": "",
    "jer_tipo_contraste": "Yodado",
    "jer_volumen_contraste": 80.0,
    "jer_flujo": 3.5,
    "jer_flush": 30.0,
    "jer_tiempo_delay": 25.0,
    "jer_sitio_puncion": "Seleccionar",
    "jer_no_usare": False,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def mostrar_imagen_actualizada(ruta, **kwargs):
    ruta = Path(ruta) if ruta else None
    if ruta and ruta.exists():
        st.image(ruta.read_bytes(), **kwargs)


def mostrar_opcion(op):
    return str(op).lower() if isinstance(op, str) else str(op)


def sanitizar_decimal(valor):
    valor = "" if valor is None else str(valor)
    valor = re.sub(r"[^0-9.,]", "", valor).replace(",", ".")
    partes = valor.split(".")
    if len(partes) > 2:
        valor = partes[0] + "." + "".join(partes[1:])
    return valor


def persistent_decimal_text_input(label, key, placeholder=""):
    wkey = f"_{key}"
    if wkey not in st.session_state:
        st.session_state[wkey] = sanitizar_decimal(st.session_state.get(key, ""))
    nuevo = st.text_input(label, value=st.session_state[wkey], key=wkey, placeholder=placeholder)
    st.session_state[wkey] = sanitizar_decimal(nuevo)
    st.session_state[key] = st.session_state[wkey]


def cargar_imagen_en_estado(uploaded_file, key_prefix):
    if uploaded_file is not None:
        st.session_state[f"{key_prefix}_bytes"] = uploaded_file.getvalue()
        st.session_state[f"{key_prefix}_nombre"] = uploaded_file.name
        st.session_state[f"{key_prefix}_mime"] = getattr(uploaded_file, "type", "image/png") or "image/png"


def quitar_imagen_estado(key_prefix):
    st.session_state[f"{key_prefix}_bytes"] = None
    st.session_state[f"{key_prefix}_nombre"] = ""
    st.session_state[f"{key_prefix}_mime"] = ""


def reconstruir_uploaded_desde_estado(key_prefix):
    b = st.session_state.get(f"{key_prefix}_bytes")
    m = st.session_state.get(f"{key_prefix}_mime")
    n = st.session_state.get(f"{key_prefix}_nombre")
    if b:
        return {"bytes": b, "mime": m or "image/png", "name": n or "imagen.png"}
    return None


def imagen_a_data_uri(fuente):
    try:
        if not fuente:
            return None
        if isinstance(fuente, dict) and fuente.get("bytes"):
            return "data:%s;base64,%s" % (
                fuente.get("mime", "image/png"),
                base64.b64encode(fuente["bytes"]).decode("utf-8"),
            )
        if isinstance(fuente, Image.Image):
            from io import BytesIO
            buf = BytesIO()
            fuente.save(buf, format="PNG")
            return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
        ruta = Path(fuente)
        if ruta.exists():
            mime = "image/png" if ruta.suffix.lower() == ".png" else "image/jpeg"
            return "data:%s;base64,%s" % (mime, base64.b64encode(ruta.read_bytes()).decode("utf-8"))
    except Exception:
        return None
    return None


def render_rangos_paralelos_interactivos_html(image_source, key_suffix="rangos"):
    if image_source is None:
        st.info("Sube una imagen para trabajar los rangos paralelos.")
        return
    data_uri = imagen_a_data_uri(image_source)
    if not data_uri:
        st.warning("No fue posible cargar la imagen.")
        return
    html_code = f"""
    <div style="background:#4a4a4a;border:1px solid #7a7a7a;border-radius:12px;padding:14px;">
      <div style="color:white;font-weight:700;font-size:16px;margin-bottom:10px;">RANGOS</div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:end;margin-bottom:10px;">
        <div><label style="color:white;font-size:13px;display:block;margin-bottom:4px;">Cantidad de cortes</label>
        <input id="count-{key_suffix}" type="range" min="1" max="200" value="20" step="1" style="width:180px;" />
        <div id="count-value-{key_suffix}" style="color:#d8d8d8;font-size:12px;">1 a 20</div></div>
        <div><label style="color:white;font-size:13px;display:block;margin-bottom:4px;">Separación</label>
        <input id="spacing-{key_suffix}" type="range" min="4" max="60" value="14" step="1" style="width:160px;" />
        <div id="spacing-value-{key_suffix}" style="color:#d8d8d8;font-size:12px;">14 px</div></div>
        <div><label style="color:white;font-size:13px;display:block;margin-bottom:4px;">Ángulo</label>
        <input id="angle-{key_suffix}" type="range" min="0" max="360" value="0" step="1" style="width:160px;" />
        <div id="angle-value-{key_suffix}" style="color:#d8d8d8;font-size:12px;">0°</div></div>
      </div>
      <canvas id="canvas-{key_suffix}" style="max-width:100%;width:100%;border-radius:10px;background:#222;display:block;"></canvas>
    </div>
    <script>
    (() => {{
      const canvas = document.getElementById('canvas-{key_suffix}');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      const countInput = document.getElementById('count-{key_suffix}');
      const spacingInput = document.getElementById('spacing-{key_suffix}');
      const angleInput = document.getElementById('angle-{key_suffix}');
      const countValue = document.getElementById('count-value-{key_suffix}');
      const spacingValue = document.getElementById('spacing-value-{key_suffix}');
      const angleValue = document.getElementById('angle-value-{key_suffix}');
      let cssWidth = 0, cssHeight = 0;

      function getCssSize() {{
        const maxWidth = 760;
        const width = Math.min((canvas.parentElement?.clientWidth || maxWidth), maxWidth);
        const height = width * (img.height / img.width);
        return {{ width, height }};
      }}
      function resizeCanvas() {{
        if (!img.width) return;
        const dpr = window.devicePixelRatio || 1;
        const size = getCssSize();
        cssWidth = size.width; cssHeight = size.height;
        canvas.style.width = cssWidth + 'px';
        canvas.style.height = cssHeight + 'px';
        canvas.width = Math.round(cssWidth * dpr);
        canvas.height = Math.round(cssHeight * dpr);
        ctx.setTransform(dpr,0,0,dpr,0,0);
        draw();
      }}
      function draw() {{
        if (!img.width) return;
        const count = parseInt(countInput.value, 10);
        const spacing = parseFloat(spacingInput.value);
        const angleDeg = parseFloat(angleInput.value);
        countValue.textContent = '1 a ' + count;
        spacingValue.textContent = spacing + ' px';
        angleValue.textContent = angleDeg + '°';
        ctx.clearRect(0,0,cssWidth,cssHeight);
        ctx.drawImage(img,0,0,cssWidth,cssHeight);
        const cx = cssWidth/2, cy = cssHeight/2;
        const angle = angleDeg * Math.PI / 180;
        const dirX = Math.cos(angle), dirY = Math.sin(angle);
        const normalX = -dirY, normalY = dirX;
        const lineLength = Math.sqrt(cssWidth*cssWidth + cssHeight*cssHeight) * 1.5;
        ctx.strokeStyle = 'rgba(255, 80, 80, 0.95)';
        ctx.lineWidth = 2;
        ctx.font = 'bold 12px Arial';
        ctx.fillStyle = 'white';
        for (let i = 0; i < count; i++) {{
          const offset = (i - (count - 1) / 2) * spacing;
          const mx = cx + normalX * offset, my = cy + normalY * offset;
          const x1 = mx - dirX * lineLength, y1 = my - dirY * lineLength;
          const x2 = mx + dirX * lineLength, y2 = my + dirY * lineLength;
          ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
          if (i === 0) ctx.fillText('1', 12, 20);
          if (i === count - 1) ctx.fillText(String(count), cssWidth - 22, cssHeight - 12);
        }}
      }}
      countInput.addEventListener('input', draw);
      spacingInput.addEventListener('input', draw);
      angleInput.addEventListener('input', draw);
      img.onload = () => {{ resizeCanvas(); window.addEventListener('resize', resizeCanvas); }};
      img.src = '{data_uri}';
    }})();
    </script>
    """
    import streamlit.components.v1 as components
    components.html(html_code, height=780, scrolling=False)


def render_reformacion_obtenida_con_flechas(image_source, key_suffix="reform_obtenida"):
    if image_source is None:
        st.info("Sube una imagen de reformación obtenida.")
        return
    data_uri = imagen_a_data_uri(image_source)
    if not data_uri:
        st.warning("No fue posible cargar la imagen.")
        return
    html_code = f"""
    <div style="background:#4a4a4a;border:1px solid #7a7a7a;border-radius:12px;padding:14px;">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:10px;">
        <div style="color:white;font-weight:700;">REFORMACIÓN OBTENIDA</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <button id="add-arrow-{key_suffix}" style="background:#b8bec7;color:#1f1f1f;border:none;border-radius:8px;padding:8px 12px;font-weight:600;cursor:pointer;">Agregar flecha</button>
          <button id="clear-arrow-{key_suffix}" style="background:#b8bec7;color:#1f1f1f;border:none;border-radius:8px;padding:8px 12px;font-weight:600;cursor:pointer;">Quitar todas</button>
        </div>
      </div>
      <div style="color:#d8d8d8;font-size:13px;margin-bottom:10px;">Puedes agregar hasta 5 flechas. Arrastra la punta o la base para ubicarlas y escribe la anatomía en el recuadro.</div>
      <canvas id="canvas-{key_suffix}" style="max-width:100%;width:100%;border-radius:10px;background:#222;display:block;"></canvas>
      <div id="labels-{key_suffix}" style="display:grid;grid-template-columns:1fr;gap:8px;margin-top:10px;"></div>
    </div>
    <script>
    (() => {{
      const canvas = document.getElementById('canvas-{key_suffix}');
      const ctx = canvas.getContext('2d');
      const addBtn = document.getElementById('add-arrow-{key_suffix}');
      const clearBtn = document.getElementById('clear-arrow-{key_suffix}');
      const labelsBox = document.getElementById('labels-{key_suffix}');
      const img = new Image();
      let cssWidth = 0, cssHeight = 0;
      let arrows = [];
      let dragging = null;

      function getCssSize() {{
        const maxWidth = 1000;
        const width = Math.min((canvas.parentElement?.clientWidth || maxWidth), maxWidth);
        const height = width * (img.height / img.width);
        return {{ width, height }};
      }}
      function resizeCanvas() {{
        if (!img.width) return;
        const dpr = window.devicePixelRatio || 1;
        const size = getCssSize();
        cssWidth = size.width; cssHeight = size.height;
        canvas.style.width = cssWidth + 'px';
        canvas.style.height = cssHeight + 'px';
        canvas.width = Math.round(cssWidth * dpr);
        canvas.height = Math.round(cssHeight * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        draw();
      }}
      function drawArrow(x1,y1,x2,y2) {{
        const headlen = 14;
        const angle = Math.atan2(y2-y1, x2-x1);
        ctx.beginPath();
        ctx.moveTo(x1,y1);
        ctx.lineTo(x2,y2);
        ctx.lineTo(x2 - headlen*Math.cos(angle-Math.PI/6), y2 - headlen*Math.sin(angle-Math.PI/6));
        ctx.moveTo(x2,y2);
        ctx.lineTo(x2 - headlen*Math.cos(angle+Math.PI/6), y2 - headlen*Math.sin(angle+Math.PI/6));
        ctx.stroke();
      }}
      function draw() {{
        if (!img.width) return;
        ctx.clearRect(0,0,cssWidth,cssHeight);
        ctx.drawImage(img,0,0,cssWidth,cssHeight);
        ctx.strokeStyle = 'yellow';
        ctx.lineWidth = 3;
        arrows.forEach(a => drawArrow(a.x1,a.y1,a.x2,a.y2));
      }}
      function refreshLabels() {{
        labelsBox.innerHTML = '';
        arrows.forEach((a, idx) => {{
          const input = document.createElement('input');
          input.type = 'text';
          input.placeholder = 'Anatomía flecha ' + (idx+1);
          input.value = a.label || '';
          input.style.width = '100%';
          input.style.padding = '8px 10px';
          input.style.borderRadius = '8px';
          input.style.border = '1px solid #999';
          input.oninput = (e) => a.label = e.target.value;
          labelsBox.appendChild(input);
        }});
      }}
      function getPointerPos(event) {{
        const rect = canvas.getBoundingClientRect();
        return {{ x: event.clientX - rect.left, y: event.clientY - rect.top }};
      }}
      function dist(x1,y1,x2,y2) {{
        const dx = x2-x1, dy = y2-y1; return Math.sqrt(dx*dx + dy*dy);
      }}
      canvas.addEventListener('mousedown', (e) => {{
        const p = getPointerPos(e);
        dragging = null;
        arrows.forEach((a, idx) => {{
          if (dist(p.x,p.y,a.x1,a.y1) < 18) dragging = {{idx, point:'start'}};
          if (dist(p.x,p.y,a.x2,a.y2) < 18) dragging = {{idx, point:'end'}};
        }});
      }});
      window.addEventListener('mousemove', (e) => {{
        if (!dragging) return;
        const p = getPointerPos(e);
        const a = arrows[dragging.idx];
        if (!a) return;
        if (dragging.point === 'start') {{ a.x1 = p.x; a.y1 = p.y; }}
        else {{ a.x2 = p.x; a.y2 = p.y; }}
        draw();
      }});
      window.addEventListener('mouseup', () => dragging = null);
      addBtn.addEventListener('click', (e) => {{
        e.preventDefault();
        if (arrows.length >= 5) return;
        arrows.push({{ x1: cssWidth*0.75, y1: cssHeight*(0.20 + arrows.length*0.12), x2: cssWidth*0.55, y2: cssHeight*(0.20 + arrows.length*0.12), label:'' }});
        refreshLabels(); draw();
      }});
      clearBtn.addEventListener('click', (e) => {{
        e.preventDefault();
        arrows = []; refreshLabels(); draw();
      }});
      img.onload = () => {{ resizeCanvas(); window.addEventListener('resize', resizeCanvas); }};
      img.src = '{data_uri}';
    }})();
    </script>
    """
    import streamlit.components.v1 as components
    components.html(html_code, height=980, scrolling=False)


def ir_a(seccion):
    st.session_state.seccion = seccion


# -----------------------------------------------------------------------------
# PORTADA
# -----------------------------------------------------------------------------
if st.session_state.seccion == "Portada":
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.2, 1], vertical_alignment="center")
    with c1:
        mostrar_imagen_actualizada(PORTADA_IMG, use_container_width=True)
    with c2:
        st.markdown("<h1 style='margin-bottom:0'>Simulador TC</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:18px;color:#BFC5CE'>Base del repositorio + estructura académica del Excel PlaniTC</p>", unsafe_allow_html=True)
        if st.button("Ir a practicar", type="primary", use_container_width=True):
            ir_a("A practicar")
            st.rerun()
    st.stop()

# -----------------------------------------------------------------------------
# MENÚ PRINCIPAL
# -----------------------------------------------------------------------------
if st.session_state.seccion == "A practicar":
    st.markdown("## A practicar")
    c1, c2 = st.columns([1, 1], vertical_alignment="center")
    with c1:
        mostrar_imagen_actualizada(A_PRACTICAR_IMG if A_PRACTICAR_IMG.exists() else TOPOGRAMA_IMG, use_container_width=True)
    with c2:
        st.markdown("### Elige una etapa")
        for label in ["Preparación del paciente", "Topograma", "Adquisición", "Reconstrucción", "Reformación", "Jeringa inyectora", "Resumen"]:
            if st.button(label, use_container_width=True):
                ir_a(label)
                st.rerun()
    st.stop()

# barra superior
topc1, topc2, topc3 = st.columns([1, 1, 4])
with topc1:
    if st.button("🏠 Volver al inicio", use_container_width=True):
        ir_a("A practicar")
        st.rerun()
with topc2:
    secciones = ["Preparación del paciente", "Topograma", "Adquisición", "Reconstrucción", "Reformación", "Jeringa inyectora", "Resumen"]
    idx = secciones.index(st.session_state.seccion) if st.session_state.seccion in secciones else 0
    prev = "A practicar" if idx == 0 else secciones[idx-1]
    if st.button("Volver", use_container_width=True):
        ir_a(prev)
        st.rerun()

# -----------------------------------------------------------------------------
# PREPARACIÓN
# -----------------------------------------------------------------------------
if st.session_state.seccion == "Preparación del paciente":
    st.markdown("## Preparación del paciente")
    c1, c2 = st.columns([1,1])
    with c1:
        st.text_input("Nombres", key="prep_nombres")
        st.text_input("Apellidos", key="prep_apellidos")
        st.date_input("Fecha de nacimiento", key="prep_fecha_nac")
        st.text_input("Examen / motivo", key="prep_examen")
    with c2:
        st.number_input("Peso (kg)", min_value=1, max_value=250, key="prep_peso")
        st.selectbox("Embarazo", ["Seleccionar", "Sí", "No", "No aplica"], key="prep_embarazo", format_func=mostrar_opcion)
        st.selectbox("Creatinina", ["Seleccionar", "Normal", "Alterada", "No disponible"], key="prep_creatinina", format_func=mostrar_opcion)
        st.selectbox("Medio de contraste EV", ["Seleccionar", "Sí", "No"], key="prep_medio_contraste_ev", format_func=mostrar_opcion)
        st.selectbox("Vía venosa", ["Seleccionar", "Periférica", "Central", "No aplica"], key="prep_via_venosa", format_func=mostrar_opcion)
        st.selectbox("Cantidad de contraste", ["Seleccionar"] + CANTIDAD_CONTRASTE, key="prep_cantidad_contraste", format_func=mostrar_opcion)
        st.selectbox("Método de inyección", ["Seleccionar", "Manual", "Jeringa inyectora"], key="prep_metodo_inyeccion", format_func=mostrar_opcion)
        st.selectbox("Medio de contraste oral", ["Seleccionar", "Sí", "No"], key="prep_medio_contraste_oral", format_func=mostrar_opcion)

# -----------------------------------------------------------------------------
# TOPOGRAMA
# -----------------------------------------------------------------------------
elif st.session_state.seccion == "Topograma":
    st.markdown("## Ingreso y Topograma")
    c1, c2 = st.columns([1.1, 1], vertical_alignment="top")
    with c1:
        st.selectbox("Región anatómica", ["Seleccionar"] + list(REGION_TO_EXAMS.keys()), key="topo_region_anatomica", format_func=mostrar_opcion)
        exams = REGION_TO_EXAMS.get(st.session_state.topo_region_anatomica, [])
        st.selectbox("Examen", ["Seleccionar"] + exams, key="topo_region", format_func=mostrar_opcion)
        st.selectbox("Posición paciente", ["Seleccionar"] + POSICIONES_PACIENTE, key="topo_posicionamiento", format_func=mostrar_opcion)
        st.selectbox("Posición del tubo", ["Seleccionar"] + POSICIONES_TUBO, key="topo_posicion_tubo", format_func=mostrar_opcion)
        st.selectbox("Instrucción de voz", ["Seleccionar"] + INSTRUCCIONES_VOZ, key="topo_instruccion_voz", format_func=mostrar_opcion)
        st.selectbox("Longitud topograma", LONGITUDES_TOPO, key="topo_longitud")
        st.selectbox("Retardo", RETARDOS, key="topo_retardo")
        st.selectbox("Aplica segundo topograma", APLICA_TOPO, key="topo_aplica_topo2", format_func=mostrar_opcion)
    with c2:
        mostrar_imagen_actualizada(TOPOGRAMA_IMG, use_container_width=True)

# -----------------------------------------------------------------------------
# ADQUISICIÓN
# -----------------------------------------------------------------------------
elif st.session_state.seccion == "Adquisición":
    st.markdown("## Adquisición")
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("Instrucción de voz", ["Seleccionar"] + INSTRUCCIONES_VOZ, key="adq_instruccion_voz", format_func=mostrar_opcion)
        st.selectbox("Tipo de exploración", ["Seleccionar"] + TIPOS_EXPLORACION, key="adq_tipo_exploracion", format_func=mostrar_opcion)
        st.selectbox("Doble muestreo (eje Z)", DOBLE_MUESTREO, key="adq_doble_muestreo", format_func=mostrar_opcion)
        st.selectbox("Modulación corriente", ["Seleccionar"] + MODULACION_CORRIENTE, key="adq_modulacion_corriente", format_func=mostrar_opcion)
        st.selectbox("kV", ["Seleccionar"] + KV_OPCIONES, key="adq_kv", format_func=mostrar_opcion)
        if st.session_state.adq_modulacion_corriente == "MANUAL":
            st.selectbox("mAs", ["Seleccionar"] + MAS_OPCIONES, key="adq_mas", format_func=mostrar_opcion)
        elif st.session_state.adq_modulacion_corriente == "AUTO mA":
            st.selectbox("Rango mA", ["Seleccionar"] + RANGO_MA_OPCIONES, key="adq_rango_ma", format_func=mostrar_opcion)
            st.selectbox("Índice ruido", ["Seleccionar"] + INDICE_RUIDO, key="adq_indice_ruido", format_func=mostrar_opcion)
        elif st.session_state.adq_modulacion_corriente == "CARE DOSE 4D":
            st.selectbox("mAs ref", ["Seleccionar"] + MAS_OPCIONES, key="adq_mas", format_func=mostrar_opcion)
            st.selectbox("Índice calidad", ["Seleccionar"] + INDICE_CALIDAD, key="adq_indice_calidad", format_func=mostrar_opcion)
    with c2:
        st.selectbox("Configuración de detectores", ["Seleccionar"] + CONF_DETECTORES, key="adq_matriz_detectores", format_func=mostrar_opcion)
        st.text_input("Cobertura / colimación", value=COBERTURA_MAP.get(st.session_state.adq_matriz_detectores, ""), key="adq_colimacion")
        st.selectbox("SFOV", ["Seleccionar"] + SFOV_OPCIONES, key="adq_sfov", format_func=mostrar_opcion)
        st.selectbox("Rotación del tubo", ["Seleccionar"] + ROTACION_TUBO, key="adq_rotacion_tubo", format_func=mostrar_opcion)
        if st.session_state.adq_tipo_exploracion == "HELICOIDAL":
            st.selectbox("Pitch", ["Seleccionar"] + PITCH_OPCIONES, key="adq_pitch", format_func=mostrar_opcion)
        st.selectbox("Delay", ["Seleccionar"] + RETARDOS, key="adq_delay", format_func=mostrar_opcion)
        st.text_input("Inicio adquisición", key="adq_inicio_adquisicion")
        st.text_input("Fin adquisición", key="adq_fin_adquisicion")

# -----------------------------------------------------------------------------
# RECONSTRUCCIÓN
# -----------------------------------------------------------------------------
elif st.session_state.seccion == "Reconstrucción":
    st.markdown("## Reconstrucción")
    c1, c2 = st.columns([1,1], vertical_alignment="top")
    with c1:
        st.selectbox("Fase de adquisición que se reconstruirá", ["Seleccionar"] + FASES_RECONS, key="recon_fase", format_func=mostrar_opcion)
        st.selectbox("Tipo de reconstrucción", ["Seleccionar"] + TIPOS_RECONS, key="recon_tipo", format_func=mostrar_opcion)
        st.selectbox("Reconstrucción iterativa", ["Seleccionar"] + ITERATIVAS, key="recon_iterativa", format_func=mostrar_opcion)
        st.selectbox("Nivel / intensidad", ["Seleccionar"] + INTENSIDADES, key="recon_intensidad", format_func=mostrar_opcion)
        st.selectbox("Algoritmo (kernel)", ["Seleccionar"] + KERNELS, key="recon_kernel", format_func=mostrar_opcion)
        st.selectbox("Grosor de reconstrucción", ["Seleccionar"] + GROSOR_RECONS, key="recon_grosor", format_func=mostrar_opcion)
        st.selectbox("Incremento", ["Seleccionar"] + INCREMENTO_RECONS, key="recon_incremento", format_func=mostrar_opcion)
        st.selectbox("Ventana", ["Seleccionar"] + VENTANAS, key="recon_ventana", format_func=mostrar_opcion)
        st.selectbox("WW", ["Seleccionar"] + WW_OPCIONES, key="recon_ww", format_func=mostrar_opcion)
        st.selectbox("WL", ["Seleccionar"] + WL_OPCIONES, key="recon_wl", format_func=mostrar_opcion)
        st.selectbox("DFOV", ["Seleccionar"] + DFOV_OPCIONES, key="recon_dfov", format_func=mostrar_opcion)
        st.text_input("Inicio reconstrucción", key="recon_inicio")
        st.text_input("Fin reconstrucción", key="recon_fin")
    with c2:
        up = st.file_uploader("Subir imagen para reconstrucción", type=["png","jpg","jpeg","webp"], key="recon_imagen_uploader")
        if up is not None:
            cargar_imagen_en_estado(up, "recon_imagen_subida")
        rec = reconstruir_uploaded_desde_estado("recon_imagen_subida")
        if rec:
            st.image(rec["bytes"], caption=rec["name"], use_container_width=True)
            if st.button("Quitar imagen reconstrucción", use_container_width=True):
                quitar_imagen_estado("recon_imagen_subida")
                st.rerun()

# -----------------------------------------------------------------------------
# REFORMACIÓN
# -----------------------------------------------------------------------------
elif st.session_state.seccion == "Reformación":
    st.markdown("## Reformación")
    st.markdown("### Parámetros de reformación obtenida")
    left, right = st.columns([2,1], vertical_alignment="top")
    with left:
        up3 = st.file_uploader("Subir imagen de reformación obtenida", type=["png","jpg","jpeg","webp"], key="reform_img3_uploader")
        if up3 is not None:
            cargar_imagen_en_estado(up3, "reform_rangos_img3")
        img3 = reconstruir_uploaded_desde_estado("reform_rangos_img3")
        if img3:
            render_reformacion_obtenida_con_flechas(img3, key_suffix="reform3")
            if st.button("Quitar imagen reformación obtenida", use_container_width=True):
                quitar_imagen_estado("reform_rangos_img3")
                st.rerun()
        else:
            st.info("Sube una imagen para trabajar la reformación obtenida.")
    with right:
        st.selectbox("Reconstrucción a reformar", ["Seleccionar"] + REFORM_RECONSTRUCCION, key="reform_reconstruccion", format_func=mostrar_opcion)
        st.selectbox("Tipo de fase", ["Seleccionar"] + REFORM_FASE, key="reform_fase", format_func=mostrar_opcion)
        st.selectbox("Tipo de reformación", ["Seleccionar"] + REFORM_TIPO, key="reform_tipo", format_func=mostrar_opcion)
        st.selectbox("Plano de reformación", ["Seleccionar"] + REFORM_PLANO, key="reform_plano", format_func=mostrar_opcion)
        persistent_decimal_text_input("Grosor de corte (mm)", "reform_grosor", placeholder="Ej: 1.25")
        persistent_decimal_text_input("Distancia de corte (mm)", "reform_distancia", placeholder="Ej: 0.6")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        up1 = st.file_uploader("Subir imagen de rangos 1", type=["png","jpg","jpeg","webp"], key="reform_img1_uploader")
        if up1 is not None:
            cargar_imagen_en_estado(up1, "reform_rangos_img1")
        img1 = reconstruir_uploaded_desde_estado("reform_rangos_img1")
        if img1:
            render_rangos_paralelos_interactivos_html(img1, key_suffix="rangos1")
            if st.button("Quitar imagen rangos 1", use_container_width=True):
                quitar_imagen_estado("reform_rangos_img1")
                st.rerun()
    with c2:
        up2 = st.file_uploader("Subir imagen de rangos 2", type=["png","jpg","jpeg","webp"], key="reform_img2_uploader")
        if up2 is not None:
            cargar_imagen_en_estado(up2, "reform_rangos_img2")
        img2 = reconstruir_uploaded_desde_estado("reform_rangos_img2")
        if img2:
            render_rangos_paralelos_interactivos_html(img2, key_suffix="rangos2")
            if st.button("Quitar imagen rangos 2", use_container_width=True):
                quitar_imagen_estado("reform_rangos_img2")
                st.rerun()

# -----------------------------------------------------------------------------
# JERINGA
# -----------------------------------------------------------------------------
elif st.session_state.seccion == "Jeringa inyectora":
    st.markdown("## Jeringa inyectora")
    st.checkbox("No usaré jeringa inyectora", key="jer_no_usare")
    if not st.session_state.jer_no_usare:
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Tipo de contraste", ["Yodado", "No iónico", "Dilución"], key="jer_tipo_contraste", format_func=mostrar_opcion)
            st.number_input("Volumen de contraste (mL)", min_value=0.0, max_value=200.0, step=1.0, key="jer_volumen_contraste")
            st.number_input("Flujo (mL/s)", min_value=0.0, max_value=10.0, step=0.1, key="jer_flujo")
        with c2:
            st.number_input("Flush (mL)", min_value=0.0, max_value=200.0, step=1.0, key="jer_flush")
            st.number_input("Tiempo delay (s)", min_value=0.0, max_value=120.0, step=1.0, key="jer_tiempo_delay")
            st.selectbox("Sitio de punción", ["Seleccionar", "Fosa antecubital derecha", "Fosa antecubital izquierda", "Mano derecha", "Mano izquierda"], key="jer_sitio_puncion", format_func=mostrar_opcion)

# -----------------------------------------------------------------------------
# RESUMEN
# -----------------------------------------------------------------------------
elif st.session_state.seccion == "Resumen":
    st.markdown("## Resumen del simulador")
    st.markdown("### Preparación")
    st.write({
        "Nombres": st.session_state.prep_nombres,
        "Apellidos": st.session_state.prep_apellidos,
        "Fecha nacimiento": str(st.session_state.prep_fecha_nac),
        "Examen": st.session_state.prep_examen,
        "Peso": f"{st.session_state.prep_peso} kg",
    })
    st.markdown("### Topograma")
    st.write({
        "Región anatómica": st.session_state.topo_region_anatomica,
        "Examen": st.session_state.topo_region,
        "Posición paciente": st.session_state.topo_posicionamiento,
        "Posición tubo": st.session_state.topo_posicion_tubo,
        "Instrucción voz": st.session_state.topo_instruccion_voz,
        "Longitud topograma": st.session_state.topo_longitud,
        "Retardo": st.session_state.topo_retardo,
    })
    st.markdown("### Adquisición")
    st.write({
        "Tipo exploración": st.session_state.adq_tipo_exploracion,
        "Modulación corriente": st.session_state.adq_modulacion_corriente,
        "kV": st.session_state.adq_kv,
        "mAs": st.session_state.adq_mas,
        "Rango mA": st.session_state.adq_rango_ma,
        "Índice ruido": st.session_state.adq_indice_ruido,
        "Índice calidad": st.session_state.adq_indice_calidad,
        "Detectores": st.session_state.adq_matriz_detectores,
        "Cobertura": st.session_state.adq_colimacion,
        "SFOV": st.session_state.adq_sfov,
        "Rotación": st.session_state.adq_rotacion_tubo,
        "Pitch": st.session_state.adq_pitch,
        "Delay": st.session_state.adq_delay,
    })
    st.markdown("### Reconstrucción")
    st.write({
        "Fase": st.session_state.recon_fase,
        "Tipo": st.session_state.recon_tipo,
        "Iterativa": st.session_state.recon_iterativa,
        "Intensidad": st.session_state.recon_intensidad,
        "Kernel": st.session_state.recon_kernel,
        "Grosor": st.session_state.recon_grosor,
        "Incremento": st.session_state.recon_incremento,
        "Ventana": st.session_state.recon_ventana,
        "WW": st.session_state.recon_ww,
        "WL": st.session_state.recon_wl,
        "DFOV": st.session_state.recon_dfov,
    })
    st.markdown("### Reformación")
    st.write({
        "Reconstrucción a reformar": st.session_state.reform_reconstruccion,
        "Fase": st.session_state.reform_fase,
        "Tipo": st.session_state.reform_tipo,
        "Plano": st.session_state.reform_plano,
        "Grosor de corte (mm)": st.session_state.reform_grosor,
        "Distancia de corte (mm)": st.session_state.reform_distancia,
    })
    st.markdown("### Jeringa inyectora")
    st.write({
        "No usaré": st.session_state.jer_no_usare,
        "Tipo contraste": st.session_state.jer_tipo_contraste,
        "Volumen": st.session_state.jer_volumen_contraste,
        "Flujo": st.session_state.jer_flujo,
        "Flush": st.session_state.jer_flush,
        "Tiempo delay": st.session_state.jer_tiempo_delay,
        "Sitio punción": st.session_state.jer_sitio_puncion,
    })
