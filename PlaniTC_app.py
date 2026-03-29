"""
PlaniTC — Simulador Educativo de Tomografía Computada
Creado por TM Angélica Valdés y TM Evelyn Oyarzún
Versión web: Python + Streamlit
"""

import streamlit as st
import numpy as np
import math

# ─── Configuración de página ────────────────────────────────────────────────
st.set_page_config(
    page_title="PlaniTC · Simulador TC",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS personalizado ───────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fondo negro general */
    .stApp {
        background-color: #000000;
    }
    /* Sidebar negro */
    [data-testid="stSidebar"] {
        background-color: #111111;
    }
    /* Todo el texto blanco */
    html, body, [class*="css"], .stMarkdown, .stText,
    label, .stSelectbox label, .stNumberInput label,
    .stTextInput label, .stTextArea label, .stCheckbox label,
    .stSlider label, p, span, div {
        color: #FFFFFF !important;
    }
    /* Inputs y selectboxes oscuros */
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #444444 !important;
    }
    /* Título principal */
    .main-title {
        font-size: 2rem; font-weight: 700; color: #FFFFFF;
        border-bottom: 3px solid #888888; padding-bottom: 0.3rem; margin-bottom: 0.2rem;
    }
    .subtitle { font-size: 0.95rem; color: #AAAAAA; margin-bottom: 1.5rem; }
    /* Banners de sección en gris */
    .section-header {
        background: #3A3A3A;
        color: #FFFFFF; padding: 0.5rem 1rem;
        border-radius: 6px; font-weight: 600;
        margin: 1rem 0 0.8rem 0; font-size: 1rem;
    }
    /* Tarjetas métricas */
    .metric-card {
        background: #1A1A1A; border-left: 4px solid #888888;
        border-radius: 6px; padding: 0.6rem 1rem; margin: 0.3rem 0;
    }
    .metric-label { font-size: 0.75rem; color: #AAAAAA; font-weight: 600; text-transform: uppercase; }
    .metric-value { font-size: 1.4rem; font-weight: 700; color: #FFFFFF; }
    /* Alertas */
    .alert-info {
        background: #0A2A0A; border-left: 4px solid #2E7D32;
        border-radius: 6px; padding: 0.8rem 1rem; margin: 0.5rem 0;
        color: #88CC88; font-size: 0.9rem;
    }
    .alert-warn {
        background: #2A1500; border-left: 4px solid #E65100;
        border-radius: 6px; padding: 0.8rem 1rem; margin: 0.5rem 0;
        color: #FFAA66; font-size: 0.9rem;
    }
    /* Resumen parámetros */
    .param-summary {
        background: #1A1A1A; border: 1px solid #444444;
        border-radius: 8px; padding: 1rem; font-size: 0.85rem;
        color: #FFFFFF;
    }
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-size: 0.95rem; font-weight: 600;
        color: #FFFFFF !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #111111;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3A3A3A !important;
    }
    /* Métricas de Streamlit */
    [data-testid="metric-container"] {
        background-color: #1A1A1A;
        border: 1px solid #444444;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
    }
    /* Divisor */
    hr { border-color: #444444; }
    canvas { border-radius: 50%; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATOS DEL SISTEMA (extraídos de PlaniTC.xlsm)
# ═══════════════════════════════════════════════════════════════════════════════

REGIONES = {
    "CABEZA":   ["CEREBRO", "ORBITAS", "OIDOS", "SPN", "MAXILOFACIAL"],
    "CUELLO":   ["CUELLO"],
    "EESS":     ["HOMBRO", "BRAZO", "CODO", "ANTEBRAZO", "MUÑECA", "MANO"],
    "COLUMNA":  ["CERVICAL", "DORSAL", "LUMBAR", "SACROCOXIS"],
    "CUERPO":   ["TORAX", "ABDOMEN", "PELVIS", "ABDOMEN-PELVIS", "TORAX-ABDOMEN-PELVIS"],
    "EEII":     ["CADERA", "MUSLO", "RODILLA", "TOBILLO", "PIE"],
    "ANGIO":    ["CEREBRO", "CUELLO", "ART PULMONARES", "AORTA", "EESS", "EEII"],
}

POSICIONES_PACIENTE = [
    "DECUBITO SUPINO",
    "DECUBITO PRONO",
    "DECUBITO LATERAL DERECHO",
    "DECUBITO LATERAL IZQUIERDO",
]

ENTRADAS_PACIENTE = ["CABEZA PRIMERO", "PIES PRIMERO"]

DIRECCIONES = ["CAUDO-CRANEAL", "CRANEO-CAUDAL"]

LONGITUDES_TOPO = [128, 256, 512, 768, 1020, 1560]

POS_TUBO = ["ARRIBA 0°", "ABAJO 180°", "DERECHA 90°", "IZQUIERDA 90°"]

INSTRUCCIONES_VOZ = ["NINGUNA", "INSPIRACIÓN", "ESPIRACIÓN", "NO TRAGAR", "VALSALVA", "NO RESPIRE"]

RETARDOS = ["2 sg", "3 sg", "4 sg", "5 sg", "6 sg"]

# Adquisición
TIPOS_EXPLORACION = ["HELICOIDAL", "SECUENCIAL CONTIGUO", "SECUENCIAL ESPACIADO"]

MODULACION_CORRIENTE = ["MANUAL", "AUTO mA", "CARE DOSE 4D"]

KVP_OPCIONES = [70, 80, 90, 100, 110, 120]

MAS_OPCIONES = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]

RANGO_MA = ["30 - 400", "40 - 300", "60 - 500", "130 - 400", "140 - 500"]

INDICE_RUIDO = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

INDICE_CALIDAD = [80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]

CONF_DETECTORES = [
    "8 x 1,25 mm", "16 x 0,625 mm", "32 x 0.6 mm",
    "32 x 0,625 mm", "32 x 1,2 mm", "32 x 1,25 mm",
    "64 x 0,6 mm", "64 x 0,625 mm",
]

SFOV_OPCIONES = ["SMALL (200 mm)", "HEAD (300 mm)", "LARGE (500 mm)"]

PITCH_OPCIONES = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]

ROT_TUBO = [0.3, 0.5, 0.7, 1.0]

GROSOR_PROSP = [0.6, 0.625, 1.0, 1.2, 1.25, 1.5, 2.0, 3.0, 4.0, 5.0]

# Inicio/fin por región y región anatómica
REFS_INICIO = {
    "CABEZA":  ["VERTEX", "SOBRE SENO FRONTAL", "TECHO ORBITARIO", "CAE",
                "PISO ORBITARIO", "SOBRE REGION PETROSA", "ARCADA DENTARIA SUPERIOR",
                "BAJO BASE DE CRÁNEO", "MENTON", "ARCO AÓRTICO"],
    "CUELLO":  ["TECHO ORBITARIO", "CAE", "ARCO AÓRTICO"],
    "EESS":    ["SOBRE ART. ACROMIOCLAV.", "BAJO ESCÁPULA", "TERCIO DISTAL HÚMERO",
                "TERCIO PROXIMAL RADIO-CUBITO", "TERCIO PROXIMAL MTC", "COMPLETAR FALANGES DISTALES"],
    "COLUMNA": ["CAE", "SOBRE BASE DE CRÁNEO", "C6-C7", "T1-T2", "T11-T12", "L1-L2", "L4-L5", "S1-S2"],
    "CUERPO":  ["SOBRE ÁPICES PULMONARES", "SOBRE CÚPULAS DIAF.", "ARCO AÓRTICO",
                "BAJO ANGULOS COSTOFR.", "L5-S1"],
    "EEII":    ["EIAS", "TERCIO PROXIMAL FEMUR", "TERCIO DISTAL FEMUR",
                "TERCIO PROXIMAL TIBIA-PERONÉ", "TERCIO DISTAL TIBIA-PERONÉ",
                "BAJO CALCÁNEO", "HASTA COMPLETAR ORTEJOS"],
    "ANGIO":   ["SOBRE ÁPICES PULMONARES", "ARCO AÓRTICO", "SOBRE CÚPULAS DIAF.",
                "BAJO ANGULOS COSTOFR.", "L5-S1", "COMPLETAR FALANGE DISTAL"],
}

REFS_FIN = {
    "CABEZA":  ["BAJO BASE DE CRÁNEO", "MENTON", "ARCO AÓRTICO", "PISO ORBITARIO",
                "SOBRE REGION PETROSA", "ARCADA DENTARIA SUPERIOR"],
    "CUELLO":  ["CAE", "ARCO AÓRTICO", "MENTON"],
    "EESS":    ["BAJO ESCÁPULA", "TERCIO DISTAL HÚMERO", "TERCIO PROXIMAL MTC",
                "COMPLETAR FALANGES DISTALES"],
    "COLUMNA": ["SOBRE BASE DE CRÁNEO", "T1-T2", "T11-T12", "L4-L5", "S1-S2",
                "1 CM BAJO COXIS", "L5-S1"],
    "CUERPO":  ["SOBRE CÚPULAS DIAF.", "BAJO ANGULOS COSTOFR.", "L5-S1", "BAJO PELVIS OSEA"],
    "EEII":    ["TERCIO PROXIMAL FEMUR", "TERCIO DISTAL FEMUR",
                "TERCIO PROXIMAL TIBIA-PERONÉ", "BAJO CALCÁNEO",
                "HASTA COMPLETAR ORTEJOS", "COMPLETAR ORTEJOS"],
    "ANGIO":   ["BAJO ANGULOS COSTOFR.", "L5-S1", "BAJO PELVIS OSEA",
                "COMPLETAR FALANGE DISTAL", "COMPLETAR ORTEJOS"],
}

# Reconstrucción
FASES_RECONS = [
    "SIN CONTRASTE", "ARTERIAL", "VENOSA", "TARDIA",
    "ANGIOGRÁFICA", "REPOSO", "VALSALVA", "INSPIRACIÓN", "ESPIRACIÓN",
]

TIPOS_RECONS = ["RETROP. FILTRADA", "RECONS. ITERATIVA"]

ALGORITMOS_ITERATIVOS = ["SAFIRE", "ADMIRE", "iDOSE", "ASIR-V", "AIDR-3D", "VEO"]

NIVEL_ITERATIVO = {
    "SAFIRE":  [1, 2, 3, 4, 5],
    "ADMIRE":  [1, 2, 3, 4, 5],
    "iDOSE":   [1, 2, 3, 4, 5, 6, 7],
    "ASIR-V":  ["0 (%)", "10 (%)", "20 (%)", "30 (%)", "40 (%)",
                "50 (%)", "60 (%)", "70 (%)", "80 (%)", "90 (%)"],
    "AIDR-3D": ["Mild", "Standard", "Strong"],
    "VEO":     ["—"],
}

KERNELS = ["SUAVE 20f", "STANDARD 30f", "DEFINIDO 60f", "ULTRADEFINIDO 80f"]

GROSORES_RECONS = [
    "0,6 mm", "0,625 mm", "1 mm", "1,2 mm", "1,25 mm",
    "1,5 mm", "2 mm", "3 mm", "4 mm", "5 mm",
]

INCREMENTOS_RECONS = [
    "0,3 mm", "0,5 mm", "0,6 mm", "0,75 mm", "1 mm",
    "1,5 mm", "2 mm", "2,5 mm",
]

VENTANAS = {
    "PULMONAR":      {"ww": 1500, "wl": -600},
    "PARTES BLANDAS": {"ww": 400,  "wl": 40},
    "CEREBRO":       {"ww": 80,   "wl": 35},
    "OSEO":          {"ww": 2000, "wl": 400},
    "ANGIOGRÁFICA":  {"ww": 600,  "wl": 150},
}

DFOV_OPCIONES = ["Mayor al SFOV", "Igual a SFOV", "Menor a SFOV"]

# Inyectora
ML_INYECTORA = list(range(0, 160, 10))
CAUDAL_OPCIONES = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0]
VVP_GAUGE = [18, 20, 22, 24]

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE CÁLCULO
# ═══════════════════════════════════════════════════════════════════════════════

def calcular_cobertura_helical(conf_det, pitch):
    """Calcula cobertura en mm para exploración helicoidal."""
    try:
        partes = conf_det.replace(",", ".").split("x")
        n_det = int(partes[0].strip())
        ancho = float(partes[1].strip().replace(" mm", ""))
        return round(n_det * ancho * pitch, 2)
    except Exception:
        return "—"

def calcular_duracion(inicio_mm, fin_mm, cobertura_rot, rot_tubo):
    """Duración estimada del scan en segundos."""
    try:
        longitud = abs(fin_mm - inicio_mm)
        if cobertura_rot > 0 and rot_tubo > 0:
            return round(longitud / cobertura_rot * rot_tubo, 1)
        return "—"
    except Exception:
        return "—"

def estimar_dosis_ctdi(kvp, mas, conf_det):
    """Estimación simplificada de CTDIvol en mGy."""
    try:
        partes = conf_det.replace(",", ".").split("x")
        n_det = int(partes[0].strip())
        ancho = float(partes[1].strip().replace(" mm", ""))
        col = n_det * ancho
        base = (mas / 200) * ((kvp / 120) ** 2) * (col / 20) * 8
        return round(base, 1)
    except Exception:
        return "—"

def nivel_ruido_estimado(mas, kvp, grosor_mm):
    """Estima nivel de ruido relativo (menor = mejor)."""
    try:
        ruido = 100 / math.sqrt(mas) * (120 / kvp) * (1 / math.sqrt(grosor_mm))
        return round(ruido, 1)
    except Exception:
        return "—"

def grosor_a_float(grosor_str):
    try:
        return float(grosor_str.replace(",", ".").replace(" mm", ""))
    except Exception:
        return 1.0

def duracion_inyeccion(vol_mc, caudal_mc, vol_sf, caudal_sf):
    """Calcula duración de cada fase de inyección."""
    dur_mc = round(vol_mc / caudal_mc, 1) if caudal_mc > 0 and vol_mc > 0 else 0
    dur_sf = round(vol_sf / caudal_sf, 1) if caudal_sf > 0 and vol_sf > 0 else 0
    return dur_mc, dur_sf

# ═══════════════════════════════════════════════════════════════════════════════
# SIMULACIÓN VISUAL DE IMAGEN CT (canvas HTML)
# ═══════════════════════════════════════════════════════════════════════════════

HU_PROFILES = {
    "CABEZA": {
        "bg": 35, "structs": [
            {"label": "Cráneo", "hu": 700, "r": 0.48, "ring": True, "ring_w": 0.06},
            {"label": "Cerebro", "hu": 35, "r": 0.40},
            {"label": "Sustancia blanca", "hu": 28, "cx": 0.5, "cy": 0.5, "r": 0.25},
            {"label": "Ventrículos", "hu": 0, "cx": 0.5, "cy": 0.5, "r": 0.07},
        ]
    },
    "CUERPO": {
        "bg": -80, "structs": [
            {"label": "Grasa", "hu": -100, "r": 0.45},
            {"label": "Hígado", "hu": 55, "cx": 0.38, "cy": 0.42, "r": 0.15},
            {"label": "Bazo", "hu": 45, "cx": 0.62, "cy": 0.42, "r": 0.09},
            {"label": "Riñón D", "hu": 25, "cx": 0.65, "cy": 0.55, "r": 0.07},
            {"label": "Riñón I", "hu": 25, "cx": 0.35, "cy": 0.55, "r": 0.07},
            {"label": "Aorta", "hu": 45, "cx": 0.5, "cy": 0.52, "r": 0.04},
            {"label": "Vértebra", "hu": 700, "cx": 0.5, "cy": 0.72, "r": 0.1},
        ]
    },
    "COLUMNA": {
        "bg": -80, "structs": [
            {"label": "Cuerpo vert.", "hu": 700, "r": 0.22},
            {"label": "Médula", "hu": 50, "r": 0.08},
            {"label": "Disco", "hu": -50, "cx": 0.5, "cy": 0.35, "r": 0.12},
            {"label": "M.paravert.", "hu": 50, "cx": 0.3, "cy": 0.5, "r": 0.12},
            {"label": "M.paravert.", "hu": 50, "cx": 0.7, "cy": 0.5, "r": 0.12},
            {"label": "Apófisis", "hu": 700, "cx": 0.5, "cy": 0.7, "r": 0.08},
        ]
    },
    "CUELLO": {
        "bg": -80, "structs": [
            {"label": "Grasa", "hu": -100, "r": 0.45},
            {"label": "Tiroides", "hu": 80, "cx": 0.5, "cy": 0.42, "r": 0.10},
            {"label": "Tráquea", "hu": -700, "cx": 0.5, "cy": 0.5, "r": 0.07},
            {"label": "Carótida D", "hu": 45, "cx": 0.62, "cy": 0.45, "r": 0.05},
            {"label": "Carótida I", "hu": 45, "cx": 0.38, "cy": 0.45, "r": 0.05},
            {"label": "Vértebra", "hu": 700, "cx": 0.5, "cy": 0.68, "r": 0.12},
        ]
    },
    "EESS": {
        "bg": -100, "structs": [
            {"label": "Grasa", "hu": -80, "r": 0.4},
            {"label": "Músculo", "hu": 50, "r": 0.3},
            {"label": "Hueso", "hu": 700, "ring": True, "r": 0.22, "ring_w": 0.08},
            {"label": "Médula ósea", "hu": 50, "r": 0.14},
        ]
    },
    "EEII": {
        "bg": -100, "structs": [
            {"label": "Grasa", "hu": -80, "r": 0.43},
            {"label": "Músculo", "hu": 50, "r": 0.33},
            {"label": "Fémur", "hu": 700, "ring": True, "r": 0.24, "ring_w": 0.09},
            {"label": "Médula ósea", "hu": 50, "r": 0.15},
        ]
    },
    "ANGIO": {
        "bg": -80, "structs": [
            {"label": "Grasa", "hu": -100, "r": 0.45},
            {"label": "Aorta", "hu": 350, "cx": 0.5, "cy": 0.5, "r": 0.12},
            {"label": "V. cava", "hu": 120, "cx": 0.62, "cy": 0.5, "r": 0.08},
            {"label": "Riñón D", "hu": 200, "cx": 0.65, "cy": 0.42, "r": 0.09},
            {"label": "Riñón I", "hu": 200, "cx": 0.35, "cy": 0.42, "r": 0.09},
            {"label": "Vértebra", "hu": 700, "cx": 0.5, "cy": 0.72, "r": 0.1},
        ]
    },
}

PHASE_HU_BOOST = {
    "ARTERIAL":     {"Aorta": 250, "Carótida D": 280, "Carótida I": 280},
    "VENOSA":       {"Hígado": 120, "Bazo": 100, "Aorta": 160, "V. cava": 200},
    "TARDIA":       {"Riñón D": 250, "Riñón I": 250},
    "ANGIOGRÁFICA": {"Aorta": 400, "Carótida D": 400, "Carótida I": 400,
                     "V. cava": 220, "Riñón D": 300, "Riñón I": 300},
}

def render_ct_canvas(region, fase, ww, wl, ruido_nivel, kernel, grosor_mm, width=260):
    """Genera HTML/JS con canvas CT simulado."""
    profile_key = region if region in HU_PROFILES else "CUERPO"
    profile = HU_PROFILES[profile_key]
    boost = PHASE_HU_BOOST.get(fase, {})

    structs_js = []
    for s in profile["structs"]:
        hu = boost.get(s["label"], s["hu"])
        cx = s.get("cx", 0.5)
        cy = s.get("cy", 0.5)
        ring = s.get("ring", False)
        ring_w = s.get("ring_w", 0)
        structs_js.append(
            f'{{hu:{hu},cx:{cx},cy:{cy},r:{s["r"]},ring:{str(ring).lower()},rw:{ring_w}}}'
        )

    structs_str = "[" + ",".join(structs_js) + "]"
    noise = max(2, ruido_nivel) if isinstance(ruido_nivel, (int, float)) else 12
    bg_hu = profile["bg"]
    edge_boost = 1.5 if "DEFINIDO" in kernel or "ULTRA" in kernel else 1.0
    html = f"""
<canvas id="ctCanvas" width="{width}" height="{width}"
  style="border-radius:50%;display:block;margin:auto;"></canvas>
<script>
(function(){{
  var c = document.getElementById('ctCanvas');
  var ctx = c.getContext('2d');
  var W = {width}, H = {width};
  var ww = {ww}, wl = {wl};
  var noise = {noise};
  var bgHu = {bg_hu};
  var structs = {structs_str};
  var edgeBoost = {edge_boost};
  var seed = {hash(region+fase) % 9999};

  function pseudoRand(x, y) {{
    var n = Math.sin(x * 127.1 + y * 311.7 + seed) * 43758.5453;
    return n - Math.floor(n);
  }}

  function huToGray(hu) {{
    var lo = wl - ww/2, hi = wl + ww/2;
    var g = Math.round((hu - lo) / ww * 255);
    return Math.max(0, Math.min(255, g));
  }}

  var imgData = ctx.createImageData(W, H);
  var d = imgData.data;

  for (var y = 0; y < H; y++) {{
    for (var x = 0; x < W; x++) {{
      var nx = x/W, ny = y/H;
      var dx = nx-0.5, dy = ny-0.5;
      var dist = Math.sqrt(dx*dx+dy*dy);

      var i = (y*W+x)*4;
      if (dist > 0.49) {{
        d[i]=d[i+1]=d[i+2]=0; d[i+3]=255; continue;
      }}

      var hu = bgHu;
      for (var s=structs.length-1; s>=0; s--) {{
        var st = structs[s];
        var sdx = nx - st.cx, sdy = ny - st.cy;
        var sr = Math.sqrt(sdx*sdx + sdy*sdy);
        if (st.ring) {{
          if (sr < st.r && sr > st.r - st.rw) hu = st.hu;
        }} else if (sr < st.r) {{
          var b = Math.max(0, 1 - sr/st.r);
          hu = hu*(1-b*0.85) + st.hu*b*0.85;
        }}
      }}

      var nr = (pseudoRand(x,y) - 0.5) * 2 * noise * edgeBoost;
      hu += nr;

      var g = huToGray(hu);
      d[i]=d[i+1]=d[i+2]=g; d[i+3]=255;
    }}
  }}
  ctx.putImageData(imgData, 0, 0);
}})();
</script>
"""
    return html

# ═══════════════════════════════════════════════════════════════════════════════
# INTERFAZ PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

# Header
st.markdown('<div class="main-title">🔬 PlaniTC — Simulador Educativo de TC</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Creado por TM Angélica Valdés y TM Evelyn Oyarzún</div>', unsafe_allow_html=True)

# Tabs principales
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 Ingreso y Topograma",
    "⚡ Adquisición",
    "🔄 Reconstrucción",
    "💉 Jeringa Inyectora",
    "🖼️ Imagen Simulada",
])

# ───────────────────────────────────────────────────────────────
# TAB 1: INGRESO Y TOPOGRAMA
# ───────────────────────────────────────────────────────────────
with tab1:
    col_datos, col_topo = st.columns([1, 1])

    with col_datos:
        st.markdown('<div class="section-header">📋 Datos del Paciente</div>', unsafe_allow_html=True)
        nombre = st.text_input("Nombre del paciente", placeholder="Ej: Juan Pérez")
        col_e, col_p = st.columns(2)
        with col_e:
            edad = st.number_input("Edad (años)", min_value=0, max_value=120, value=45)
        with col_p:
            peso = st.number_input("Peso (kg)", min_value=0, max_value=250, value=70)
        diagnostico = st.text_area("Diagnóstico", placeholder="Indicación clínica del examen", height=80)

        st.markdown('<div class="section-header">🏥 Datos del Examen</div>', unsafe_allow_html=True)
        region_anat = st.selectbox("Región anatómica", list(REGIONES.keys()))
        st.session_state["region_anat"] = region_anat

        examenes_disp = REGIONES[region_anat]
        examen = st.selectbox("Examen", examenes_disp)
        st.session_state["examen"] = examen

        col_pos, col_ent = st.columns(2)
        with col_pos:
            posicion = st.selectbox("Posición paciente", POSICIONES_PACIENTE)
        with col_ent:
            entrada = st.selectbox("Entrada", ENTRADAS_PACIENTE)

        direccion = st.selectbox("Dirección de exploración", DIRECCIONES)

    with col_topo:
        st.markdown('<div class="section-header">📡 Topograma 1</div>', unsafe_allow_html=True)
        col_t1a, col_t1b = st.columns(2)
        with col_t1a:
            topo1_long = st.selectbox("Longitud (mm)", LONGITUDES_TOPO, index=1, key="t1l")
            topo1_kv   = st.selectbox("kV", [80, 100, 120], index=1, key="t1kv")
        with col_t1b:
            topo1_ma   = st.selectbox("mA", [30, 40, 50, 60, 80, 100], index=2, key="t1ma")
            topo1_pos  = st.selectbox("Posición tubo", POS_TUBO, key="t1pt")
        topo1_voz  = st.selectbox("Instrucción de voz", INSTRUCCIONES_VOZ, key="t1vz")
        topo1_dir  = st.selectbox("Dirección topograma", DIRECCIONES, key="t1dir")

        aplica_topo2 = st.checkbox("¿Aplica Topograma 2?", value=False)

        if aplica_topo2:
            st.markdown('<div class="section-header">📡 Topograma 2</div>', unsafe_allow_html=True)
            col_t2a, col_t2b = st.columns(2)
            with col_t2a:
                topo2_long = st.selectbox("Longitud (mm)", LONGITUDES_TOPO, index=1, key="t2l")
                topo2_kv   = st.selectbox("kV", [80, 100, 120], index=1, key="t2kv")
            with col_t2b:
                topo2_ma   = st.selectbox("mA", [30, 40, 50, 60, 80, 100], index=1, key="t2ma")
                topo2_pos  = st.selectbox("Posición tubo", POS_TUBO, key="t2pt")
            topo2_voz  = st.selectbox("Instrucción de voz", INSTRUCCIONES_VOZ, key="t2vz")
            topo2_dir  = st.selectbox("Dirección topograma", DIRECCIONES, key="t2dir")

    st.markdown("""<div class="alert-info">
    ✅ Complete los datos del paciente y la región anatómica antes de continuar
    a la pestaña de <b>Adquisición</b>.
    </div>""", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────
# TAB 2: ADQUISICIÓN
# ───────────────────────────────────────────────────────────────
with tab2:
    region_anat = st.session_state.get("region_anat", "CUERPO")

    col_adq1, col_adq2 = st.columns([1, 1])

    with col_adq1:
        st.markdown('<div class="section-header">⚙️ Parámetros Generales</div>', unsafe_allow_html=True)
        tipo_exp = st.selectbox("Tipo de exploración", TIPOS_EXPLORACION)
        st.session_state["tipo_exp"] = tipo_exp

        voz_adq = st.selectbox("Instrucción de voz", INSTRUCCIONES_VOZ, key="voz_adq")

        if tipo_exp == "HELICOIDAL":
            doble_muestreo = st.selectbox("Doble muestreo (eje Z)", ["NO", "SI"])
        else:
            doble_muestreo = "NO"
        st.session_state["doble_muestreo"] = doble_muestreo

        st.markdown('<div class="section-header">⚡ Modulación de Corriente</div>', unsafe_allow_html=True)
        mod_corriente = st.selectbox("Modulación", MODULACION_CORRIENTE)
        st.session_state["mod_corriente"] = mod_corriente

        col_kv, col_mas = st.columns(2)
        with col_kv:
            if mod_corriente == "CARE DOSE 4D":
                st.selectbox("CARE kV", KVP_OPCIONES, index=3, key="kvp_sel")
            elif mod_corriente == "AUTO mA":
                st.selectbox("AUTO kV", KVP_OPCIONES, index=3, key="kvp_sel")
            else:
                st.selectbox("kV", KVP_OPCIONES, index=3, key="kvp_sel")
        kvp = st.session_state.get("kvp_sel", 120)

        with col_mas:
            if mod_corriente == "CARE DOSE 4D":
                mas_ref = st.selectbox("mAs REF", MAS_OPCIONES, index=3)
                st.session_state["mas_val"] = mas_ref
                ind_cal = st.selectbox("Índice de calidad", INDICE_CALIDAD, index=4)
            elif mod_corriente == "AUTO mA":
                rango_ma = st.selectbox("Rango mA", RANGO_MA, index=2)
                st.session_state["mas_val"] = int(rango_ma.split("-")[1].strip())
                ind_ruido = st.selectbox("Índice de ruido", INDICE_RUIDO, index=2)
                st.session_state["ind_ruido"] = ind_ruido
            else:
                mas_manual = st.selectbox("mAs", MAS_OPCIONES, index=3)
                st.session_state["mas_val"] = mas_manual

        mas_val = st.session_state.get("mas_val", 200)

    with col_adq2:
        st.markdown('<div class="section-header">🔧 Configuración Técnica</div>', unsafe_allow_html=True)
        conf_det = st.selectbox("Configuración de detectores", CONF_DETECTORES, index=4)
        st.session_state["conf_det"] = conf_det

        sfov = st.selectbox("SFOV", SFOV_OPCIONES, index=2)
        grosor_prosp = st.selectbox("Corte prospectivo (mm)",
                                     [str(g) for g in GROSOR_PROSP], index=2)
        st.session_state["grosor_prosp"] = grosor_prosp

        col_p, col_r = st.columns(2)
        with col_p:
            if tipo_exp == "HELICOIDAL":
                pitch = st.selectbox("Pitch", PITCH_OPCIONES, index=6)
            else:
                pitch = 1.0
                st.info("Pitch no aplica")
        with col_r:
            rot_tubo = st.selectbox("Rotación tubo (sg)", ROT_TUBO, index=1)

        st.session_state["pitch"] = pitch
        st.session_state["rot_tubo"] = rot_tubo

        retardo = st.selectbox("Retardo (Delay)", RETARDOS, index=0)

        st.markdown('<div class="section-header">📍 Rango de Exploración</div>', unsafe_allow_html=True)
        refs_ini = REFS_INICIO.get(region_anat, REFS_INICIO["CUERPO"])
        refs_fin_lista = REFS_FIN.get(region_anat, REFS_FIN["CUERPO"])

        col_ini, col_fin = st.columns(2)
        with col_ini:
            inicio_ref = st.selectbox("Inicio exploración", refs_ini, key="inicio_ref")
            inicio_mm  = st.number_input("mm inicio", value=0, step=10, key="ini_mm")
        with col_fin:
            fin_ref = st.selectbox("Fin exploración", refs_fin_lista, key="fin_ref")
            fin_mm  = st.number_input("mm fin", value=400, step=10, key="fin_mm")

    # Cálculos automáticos
    cob = calcular_cobertura_helical(conf_det, pitch)
    cob_str = f"{cob} mm/rot" if isinstance(cob, float) else "—"

    grosor_float = float(grosor_prosp.replace(",", ".")) if grosor_prosp else 1.0
    ctdi = estimar_dosis_ctdi(kvp, mas_val, conf_det)
    duracion = calcular_duracion(inicio_mm, fin_mm, cob if isinstance(cob, float) else 1, rot_tubo)
    ruido_est = nivel_ruido_estimado(mas_val, kvp, grosor_float)

    st.session_state["kvp"] = kvp
    st.session_state["mas_val"] = mas_val
    st.session_state["ctdi"] = ctdi
    st.session_state["ruido_est"] = ruido_est

    st.markdown("---")
    st.markdown("**Resumen calculado automáticamente**")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Cobertura/rot.", cob_str)
    with col_m2:
        st.metric("CTDIvol estimado", f"{ctdi} mGy" if ctdi != "—" else "—")
    with col_m3:
        st.metric("Duración scan", f"{duracion} sg" if duracion != "—" else "—")
    with col_m4:
        st.metric("Ruido relativo", f"{ruido_est}" if ruido_est != "—" else "—")

    if isinstance(ctdi, float) and ctdi > 30:
        st.markdown('<div class="alert-warn">⚠️ Dosis estimada elevada. Considere reducir mAs o usar modulación automática.</div>', unsafe_allow_html=True)
    elif isinstance(ctdi, float):
        st.markdown('<div class="alert-info">✅ Dosis dentro de rangos aceptables para este protocolo.</div>', unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────
# TAB 3: RECONSTRUCCIÓN
# ───────────────────────────────────────────────────────────────
with tab3:
    col_r1, col_r2 = st.columns([1, 1])

    with col_r1:
        st.markdown('<div class="section-header">🔄 Parámetros de Reconstrucción</div>', unsafe_allow_html=True)
        fase_recons = st.selectbox("Fase a reconstruir", FASES_RECONS)
        st.session_state["fase_recons"] = fase_recons

        tipo_recons = st.selectbox("Tipo de reconstrucción", TIPOS_RECONS)

        if tipo_recons == "RECONS. ITERATIVA":
            algoritmo_iter = st.selectbox("Algoritmo iterativo", ALGORITMOS_ITERATIVOS)
            niveles_disp = NIVEL_ITERATIVO.get(algoritmo_iter, [1])
            nivel_iter = st.selectbox("Nivel / Porcentaje / Modo", niveles_disp)
        else:
            algoritmo_iter = "—"
            nivel_iter = "—"

        kernel_sel = st.selectbox("Algoritmo (Kernel)", KERNELS, index=1)
        st.session_state["kernel_sel"] = kernel_sel

        col_gr, col_inc = st.columns(2)
        with col_gr:
            grosor_recons = st.selectbox("Grosor reconstrucción", GROSORES_RECONS, index=6)
            st.session_state["grosor_recons"] = grosor_recons
        with col_inc:
            incremento = st.selectbox("Incremento", INCREMENTOS_RECONS, index=4)

    with col_r2:
        st.markdown('<div class="section-header">🪟 Ventana de Visualización</div>', unsafe_allow_html=True)

        ventana_preset = st.selectbox("Ventana preset", list(VENTANAS.keys()))
        ww_default = VENTANAS[ventana_preset]["ww"]
        wl_default = VENTANAS[ventana_preset]["wl"]

        col_ww, col_wl = st.columns(2)
        with col_ww:
            ww_val = st.number_input("WW (Ancho)", min_value=1, max_value=4000,
                                      value=ww_default, key="ww_input")
        with col_wl:
            wl_val = st.number_input("WL / Nivel", min_value=-1500, max_value=3000,
                                      value=wl_default, key="wl_input")

        st.session_state["ww_val"] = ww_val
        st.session_state["wl_val"] = wl_val

        dfov = st.selectbox("DFOV", DFOV_OPCIONES, index=2)

        st.markdown('<div class="section-header">📍 Rango de Reconstrucción</div>', unsafe_allow_html=True)
        region_anat_r = st.session_state.get("region_anat", "CUERPO")
        refs_ini_r = REFS_INICIO.get(region_anat_r, REFS_INICIO["CUERPO"])
        refs_fin_r = REFS_FIN.get(region_anat_r, REFS_FIN["CUERPO"])

        col_ir, col_fr = st.columns(2)
        with col_ir:
            inicio_recons = st.selectbox("Inicio reconstrucción", refs_ini_r, key="ini_rec")
        with col_fr:
            fin_recons = st.selectbox("Fin reconstrucción", refs_fin_r, key="fin_rec")

    st.markdown("---")
    st.markdown('<div class="param-summary">', unsafe_allow_html=True)
    st.markdown(f"""
**Resumen de reconstrucción:**
- Fase: `{fase_recons}` | Tipo: `{tipo_recons}`
- Algoritmo iterativo: `{algoritmo_iter}` — Nivel: `{nivel_iter}`
- Kernel: `{kernel_sel}` | Grosor: `{grosor_recons}` | Incremento: `{incremento}`
- Ventana: WW `{ww_val}` / WL `{wl_val}` | DFOV: `{dfov}`
- Reconstrucción: de `{inicio_recons}` a `{fin_recons}`
""")
    st.markdown('</div>', unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────
# TAB 4: JERINGA INYECTORA
# ───────────────────────────────────────────────────────────────
with tab4:
    col_inj1, col_inj2 = st.columns([1.2, 1])

    with col_inj1:
        st.markdown('<div class="section-header">💉 Configuración de la Inyectora</div>', unsafe_allow_html=True)
        st.markdown("**Acceso venoso**")
        col_vvp, col_g = st.columns(2)
        with col_vvp:
            vvp_gauge = st.selectbox("VVP (Gauge)", VVP_GAUGE, index=1)
        with col_g:
            vol_max_mc = st.selectbox("Vol. máx. contraste (mL)", [20, 30, 40, 50, 60, 80, 100, 120, 150], index=2)
            vol_max_sf = st.selectbox("Vol. máx. suero (mL)", [20, 30, 40, 50, 60, 80, 100, 120, 150], index=6)

        st.markdown("---")
        st.markdown("**Fases de inyección**")

        n_fases = st.number_input("Número de fases", min_value=1, max_value=6, value=2)

        fases_data = []
        for i in range(int(n_fases)):
            with st.expander(f"Fase {i+1}", expanded=(i == 0)):
                col_sol, col_vol, col_caud = st.columns(3)
                with col_sol:
                    sol = st.selectbox("Solución", ["MC", "SF", "PAUSA"], key=f"sol_{i}")
                with col_vol:
                    vol = st.selectbox("Volumen (mL)", list(range(0, 160, 5)), index=10, key=f"vol_{i}")
                with col_caud:
                    caud = st.selectbox("Caudal (mL/sg)", CAUDAL_OPCIONES, index=5, key=f"caud_{i}")
                duracion_fase = round(vol / caud, 1) if caud > 0 and sol != "PAUSA" else vol
                st.caption(f"Duración: {duracion_fase} sg")
                fases_data.append({"solucion": sol, "volumen": vol, "caudal": caud, "duracion": duracion_fase})

    with col_inj2:
        st.markdown('<div class="section-header">📊 Resumen del Protocolo</div>', unsafe_allow_html=True)

        vol_total_mc = sum(f["volumen"] for f in fases_data if f["solucion"] == "MC")
        vol_total_sf = sum(f["volumen"] for f in fases_data if f["solucion"] == "SF")
        dur_total = sum(f["duracion"] for f in fases_data)

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Vol. total MC", f"{vol_total_mc} mL")
            st.metric("Duración total", f"{dur_total} sg")
        with col_m2:
            st.metric("Vol. total SF", f"{vol_total_sf} mL")
            st.metric("Vol. total", f"{vol_total_mc + vol_total_sf} mL")

        if vol_total_mc > vol_max_mc:
            st.markdown(f'<div class="alert-warn">⚠️ Volumen de contraste ({vol_total_mc} mL) supera el máximo configurado ({vol_max_mc} mL)</div>', unsafe_allow_html=True)
        elif vol_total_mc > 0:
            st.markdown(f'<div class="alert-info">✅ Volumen de contraste dentro del límite ({vol_total_mc}/{vol_max_mc} mL)</div>', unsafe_allow_html=True)

        if vvp_gauge >= 22 and any(f["caudal"] > 3.0 for f in fases_data):
            st.markdown('<div class="alert-warn">⚠️ Calibre VVP puede ser insuficiente para el caudal seleccionado. Se recomienda VVP 18-20G para caudales altos.</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Diagrama de fases:**")
        for i, f in enumerate(fases_data):
            color = "#1565C0" if f["solucion"] == "MC" else "#2E7D32" if f["solucion"] == "SF" else "#757575"
            st.markdown(
                f'<div style="background:{color};color:white;border-radius:6px;'
                f'padding:6px 10px;margin:3px 0;font-size:0.85rem;">'
                f'Fase {i+1} — {f["solucion"]} | {f["volumen"]} mL | {f["caudal"]} mL/sg | {f["duracion"]} sg'
                f'</div>', unsafe_allow_html=True
            )

# ───────────────────────────────────────────────────────────────
# TAB 5: IMAGEN SIMULADA
# ───────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">🖼️ Simulación de Imagen CT</div>', unsafe_allow_html=True)

    region_img  = st.session_state.get("region_anat", "CUERPO")
    fase_img    = st.session_state.get("fase_recons", "SIN CONTRASTE")
    ww_img      = st.session_state.get("ww_val", 400)
    wl_img      = st.session_state.get("wl_val", 40)
    kernel_img  = st.session_state.get("kernel_sel", "STANDARD 30f")
    ruido_img   = st.session_state.get("ruido_est", 12)
    grosor_img  = grosor_a_float(st.session_state.get("grosor_recons", "3 mm"))

    st.info(f"Simulando: **{region_img}** | Fase: **{fase_img}** | Ventana WW {ww_img} / WL {wl_img} | Kernel: {kernel_img}")

    # Mostrar múltiples cortes
    col_ctrl = st.columns([1, 3])
    with col_ctrl[0]:
        n_cortes = st.slider("Número de cortes a mostrar", 2, 6, 4)

    col_imgs = st.columns(n_cortes)
    nombres_cortes = {
        "CABEZA":   ["Fosa posterior", "Ganglios basales", "Ventrículos", "Semioval", "Corona radiada", "Vértex"],
        "CUERPO":   ["Domo hepático", "Hígado / bazo", "Riñones", "Mesogastrio", "Pelvis", "Periné"],
        "COLUMNA":  ["C3", "C5-C6", "T4", "T10", "L2", "L4-L5"],
        "CUELLO":   ["Supraglótico", "Glótico", "Infrahiodeo", "Tiroides", "Cervical bajo", "Torácico alto"],
        "EESS":     ["Hombro", "Húmero proximal", "Tercio medio", "Codo", "Antebrazo", "Muñeca"],
        "EEII":     ["Cadera", "Fémur proximal", "Tercio medio", "Rodilla", "Tibia/Peroné", "Tobillo"],
        "ANGIO":    ["Arco aórtico", "Aorta torácica", "Tronco celíaco", "Mesentérica", "Ilíacas", "Femoral"],
    }

    region_key = region_img if region_img in nombres_cortes else "CUERPO"
    nombres = nombres_cortes[region_key]

    for i, col in enumerate(col_imgs):
        with col:
            st.caption(f"**{nombres[i % len(nombres)]}**")
            html_canvas = render_ct_canvas(
                region=region_key,
                fase=fase_img,
                ww=ww_img, wl=wl_img,
                ruido_nivel=ruido_img,
                kernel=kernel_img,
                grosor_mm=grosor_img,
                width=200,
            )
            st.components.v1.html(html_canvas, height=220)

    st.markdown("---")
    st.markdown("### 📄 Resumen completo del protocolo")

    region_sum  = st.session_state.get("region_anat", "—")
    examen_sum  = st.session_state.get("examen", "—")
    tipo_sum    = st.session_state.get("tipo_exp", "—")
    kvp_sum     = st.session_state.get("kvp", "—")
    mas_sum     = st.session_state.get("mas_val", "—")
    ctdi_sum    = st.session_state.get("ctdi", "—")
    conf_sum    = st.session_state.get("conf_det", "—")
    pitch_sum   = st.session_state.get("pitch", "—")
    rot_sum     = st.session_state.get("rot_tubo", "—")
    fase_sum    = st.session_state.get("fase_recons", "—")
    kernel_sum  = st.session_state.get("kernel_sel", "—")
    grosor_sum  = st.session_state.get("grosor_recons", "—")
    ww_sum      = st.session_state.get("ww_val", "—")
    wl_sum      = st.session_state.get("wl_val", "—")

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown(f"""
**Ingreso**
- Región: `{region_sum}`
- Examen: `{examen_sum}`

**Adquisición**
- Tipo: `{tipo_sum}`
- kVp: `{kvp_sum}` | mAs: `{mas_sum}`
- Detectores: `{conf_sum}`
- Pitch: `{pitch_sum}` | Rot. tubo: `{rot_sum} sg`
        """)
    with col_s2:
        st.markdown(f"""
**Reconstrucción**
- Fase: `{fase_sum}`
- Kernel: `{kernel_sum}`
- Grosor: `{grosor_sum}`
- WW: `{ww_sum}` / WL: `{wl_sum}`

**Dosis estimada**
- CTDIvol: `{ctdi_sum} mGy`
        """)
    with col_s3:
        ruido_sum = st.session_state.get("ruido_est", "—")
        if isinstance(ruido_sum, float):
            if ruido_sum < 10:
                calidad = "🟢 Excelente"
            elif ruido_sum < 20:
                calidad = "🟡 Aceptable"
            else:
                calidad = "🔴 Ruido elevado"
        else:
            calidad = "—"

        st.markdown(f"""
**Calidad de imagen**
- Ruido relativo: `{ruido_sum}`
- Evaluación: {calidad}

**Consejo educativo**
- {"Mayor mAs → menor ruido → mayor dosis" if isinstance(ruido_sum, float) and ruido_sum > 15 else "Balance dosis-calidad adecuado para este protocolo"}
        """)
