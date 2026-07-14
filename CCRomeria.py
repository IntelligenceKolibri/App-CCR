import streamlit as st
import pandas as pd
import urllib.parse
import requests
import io
import qrcode
import hashlib
from io import BytesIO

# Configuración de página y limpieza total de la interfaz de Streamlit
st.set_page_config(page_title="Intranet CCR", page_icon="🏠", layout="centered")

# --- NÚMERO DE SEGURIDAD (WHATSAPP DE CONTROL) ---
TELEFONO_CONTROL = "524461292988"

# CSS Estricto para recuperar tu diseño exacto y ocultar marcas de desarrollo
st.markdown("""
<style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display:none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important;}
    .stApp { background-color: #0e1117; }
    
    body, .stApp {
        -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none;
    }
    
    .titulo-grande {
        font-size: 42px !important;
        font-weight: bold !important;
        color: white !important;
        margin-bottom: 5px !important;
    }
    
    .app-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;
    }
    .card {
        border-radius: 20px; padding: 20px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; text-align: center;
        text-decoration: none !important; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        min-height: 140px; border: 1px solid rgba(255,255,255,0.1);
    }
    .card-auxilio { 
        background-color: #d32f2f !important; 
        border: none !important; 
        grid-column: span 2; 
    }
    .text-auxilio { color: #ffffff !important; font-weight: bold; font-size: 18px; margin-top: 10px; }
    .card-normal { background-color: #ffffff !important; }
    .text-normal { color: #000000 !important; font-weight: bold; font-size: 15px; margin-top: 10px; }
    .icon { font-size: 35px; }
    
    .stExpander {
        background-color: #ffffff !important;
        border: none !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
        margin-top: 25px !important;
        overflow: hidden !important;
    }
    .stExpander summary {
        background-color: #ffffff !important;
        padding: 15px 20px !important;
    }
    .stExpander summary span p, .stExpander summary p {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    [data-testid="stExpanderDetails"] {
        padding: 20px !important;
        background-color: #ffffff !important;
    }
    [data-testid="stExpanderDetails"] label p {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpanderDetails"] input {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 10px !important;
    }
    
    /* CONTROL ESTRICTO DE BOTONES PARA EVITAR DESFASE EN TEMA CLARO */
    .stButton>button, .stDownloadButton>button {
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
    }
    
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #31333F !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
    }
    
    .aviso-pago {
        background-color: rgba(211, 47, 47, 0.2); border-radius: 15px; padding: 25px;
        margin-top: 20px; color: #ff5252; border: 2px solid #d32f2f; text-align: center;
    }
    .aviso {
        background-color: rgba(255, 243, 205, 0.1); border-radius: 10px; padding: 15px;
        margin-top: 30px; color: #ffffff; border-left: 5px solid #ffc107;
    }
    .bloqueo-dispositivo {
        background-color: rgba(255, 193, 7, 0.1); border-radius: 15px; padding: 25px;
        color: #ffffff; border: 2px solid #ffc107; text-align: center; margin-top: 20px;
    }
    .codigo-token {
        font-size: 24px; font-weight: bold; color: #ffc107 !important; 
        background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; display: inline-block; margin: 15px 0;
    }
    h1, h3, p, span, label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS (CONEXIÓN EN VIVO AL SEGUNDO) ---
sheet_id = "1QL7WXtX8i5i35ZxLRRdr7aCGM_cjAmU53gGRxyQTpAE"

def cargar_datos(gid, tiene_header=True):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
        r = requests.get(url, timeout=10)
        if tiene_header:
            return pd.read_csv(io.StringIO(r.text)).fillna("")
        else:
            return pd.read_csv(io.StringIO(r.text), header=None).fillna("")
    except:
        return pd.DataFrame()

df = cargar_datos("0", tiene_header=True)
df_a = cargar_datos("222722358", tiene_header=False)

# --- SISTEMA DE PERSISTENCIA Y VARIABLES DE CONTROL ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'datos' not in st.session_state:
    st.session_state.datos = None

# Script inyectado: Mantiene activa la sesión en LocalStorage, corrige teclados e impide que la app se duerma
html_cookie_handler = """
<script>
    const readMail = localStorage.getItem('ccr_ios_mail');
    if (readMail) {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: readMail
        }, '*');
    }
    
    setInterval(() => {
        const inputs = window.parent.document.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            if(input.parentElement.innerText.toLowerCase().includes('correo')) {
                input.setAttribute('autocapitalize', 'none');
                input.setAttribute('autocomplete', 'email');
                input.setAttribute('autocorrect', 'off');
                input.setAttribute('spellcheck', 'false');
            }
        });
    }, 1000);

    // Si bloqueas el teléfono y la app se duerme, fuerza recarga limpia con su sesión al volver a entrar
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            const appCrashed = !window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
            const overlayError = window.parent.document.body.innerText.includes('Connection timeout')
