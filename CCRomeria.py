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
    
    /* Bloqueo visual para dificultar la selección de elementos */
    body, .stApp {
        -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none;
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
    .card-auxilio { background-color: #d32f2f !important; border: none !important; }
    .text-auxilio { color: #ffffff !important; font-weight: bold; font-size: 15px; margin-top: 10px; }
    .card-normal { background-color: #ffffff !important; }
    .text-normal { color: #000000 !important; font-weight: bold; font-size: 15px; margin-top: 10px; }
    .icon { font-size: 30px; }
    
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

    /* ESTILO ORIGINAL OSCURO VINCULADO (image_28e31c.png) */
    .stExpander {
        background-color: #161a24 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 15px !important;
        margin-top: 20px !important;
    }
    .stExpander summary {
        background-color: #161a24 !important;
        border-radius: 15px !important;
    }
    .stExpander label p, .stExpander summary p {
        color: white !important;
    }
    [data-testid="stExpanderDetails"] input {
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpanderDetails"] button {
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS ---
sheet_id = "1QL7WXtX8i5i35ZxLRRdr7aCGM_cjAmU53gGRxyQTpAE"

def cargar_datos(gid):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        r = requests.get(url, timeout=10)
        return pd.read_csv(io.StringIO(r.text)).fillna("")
    except:
        return pd.DataFrame()

df = cargar_datos("0")
df_a = cargar_datos("222722358")

# --- CONTROL DE ACCESO FIJO POR PARÁMETROS INTERNOS ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'datos' not in st.session_state:
    st.session_state.datos = None

# Script inyectado para guardar y persistir la sesión directo en el teléfono
cookie_js = """
<script>
    const emailGuardado = localStorage.getItem('ccr_email_v2');
    if (emailGuardado && !window.location.href.includes('logged=')) {
        const separator = window.location.href.includes('?') ? '&' : '?';
        window.location.href = window.location.href + separator + 'logged=' + encodeURIComponent(emailGuardado);
    }
</script>
"""
st.html(cookie_js)

# Leer parámetros silenciosos si se refresca la pantalla
query_params = st.query_params
if "logged" in query_params and not st.session_state.autenticado:
    correo_recuperado = query_params["logged"].strip().lower()
    if not df.empty:
        df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip().str.lower()
        u = df[df.iloc[:, 0] == correo_recuperado]
        if not u.empty:
            st.session_state.datos = u.iloc[0]
            st.session_state.autenticado = True

# Procesamiento de Tokens de Seguridad
if 'ccr_email_input' in st.session_state and st.session_state.ccr_email_input:
    correo_base = st.session_state.ccr_email_input
elif "logged" in query_params:
    correo_base = query_params["logged"]
elif st.session_state.datos is not None:
    correo_base = str(st.session_state.datos.iloc[0])
else:
    correo_base = "invitado"

hash_correo = hashlib.md5(correo_base.strip().lower().encode()).hexdigest().upper()
id_del_celular_actual = f"CCR-{hash_correo[:5]}-DISP"

st.title("🏠 Intranet CCR")

if not st.session_state.autenticado:
    email_input = st.text_input("Ingresa tu correo:", key="ccr_email_input").strip().lower()
    if st.button("Entrar"):
        if not df.empty:
            df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip().str.lower()
            u = df[df.iloc[:, 0] == email_input]
            
            if not u.empty:
                st.session_state.datos = u.iloc[0]
                st.session_state.autenticado = True
                
                # Fijar permanentemente en el almacenamiento del celular
                st.html(f"""
                <script>
                    localStorage.setItem('ccr_email_v2', '{email_input}');
                    const separator = window.location.href.includes('?') ? '&' : '?';
                    window.location.href = window.location.href + separator + 'logged={email_input}';
                </script>
                """)
                st.rerun()
            else:
                st.error("Correo no registrado.")
else:
    u = st.session_state.datos
    nombre, casa = u.iloc[1], u.iloc[2]
    
    esta_pagado = "pagado" in str(u.iloc[3]).lower()
    ids_autorizados = [i.strip() for i in str(u.iloc[7]).split(",") if i.strip()]
    dispositivo_valido = id_del_celular_actual in ids_autorizados

    if not esta_pagado:
        st.markdown(f"""
            <div class="aviso-pago">
                <h2>⚠️ Acceso Restringido</h2>
                <p>Hola <b>{nombre}</b> (Casa {casa}), favor de contactar a la <b>coordinación</b> por adeudo.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Cerrar"):
            st.session_state.autenticado = False
            st.session_state.datos = None
            st.query_params.clear()
            st.html("""<script>localStorage.removeItem('ccr_email_v2'); window.location.href = window.location.pathname;</script>""")
            st.rerun()
            
    elif not dispositivo_valido:
        st.markdown(f"""
            <div class="bloqueo-dispositivo">
                <h2>🔒 Dispositivo No Vinculado</h2>
                <p>Hola <b>{nombre}</b>, este dispositivo no está autorizado para usar tu cuenta.</p>
                <p>Para solicitar el acceso, envía este código exacto a la <b>coordinación</b>:</p>
                <div class="codigo-token">{id_del_celular_actual}</div>
                <p>Una vez validado, podrás ingresar a la plataforma.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Salir"):
            st.session_state.autenticado = False
            st.session_state.datos = None
            st.query_params.clear()
            st.html("""<script>localStorage.removeItem('ccr_email_v2'); window.location.href = window.location.pathname;</script>""")
            st.rerun()
            
    else:
        # --- ACCESO CORRECTO ---
        st.markdown(f"### Hola, {nombre.split()[0]}")
        
        msg_aux = urllib.parse.quote(f"🚨 EMERGENCIA: {nombre}, Casa {casa}")
        msg_rep = urllib.parse.quote("Hola, quiero levantar un reporte")
        msg_paq = urllib.parse.quote(f"Hola, soy {nombre} de Casa {casa}, ¿me podrían recibir un paquete?")

        st.markdown(f'''
            <div class="app-grid">
                <a href="https://wa.me/525527706348?text={msg_aux}" target="_blank" class="card card-auxilio">
                    <div class="icon">🚨</div><p class="text-auxilio">PÁNICO</p></a>
                <a href="tel:911" class="card card-normal">
                    <div class="icon">📞</div><p class="text-normal">911</p></a>
                <a href="https://wa.me/525619955000?text={msg_rep}" target="_blank" class="card card-normal">
                    <div class="icon">🛠️</div><p class="text-normal">REPORTAR</p></a>
                <a href="#registro" target="_self" class="card card-normal">
                    <div class="icon">📝</div><p class="text-normal">VISITA</p></a>
                <a href="https://wa.me/525527706348?text={msg_paq}" target="_blank" class="card card-normal">
                    <div class="icon">📦</div><p class="text-normal">PAQUETERÍA</p></a>
                <a href="https://drive.google.com/file/d/1mcrDdLxQWIVzo77rfMU1RFJOEad_blNQ/view" target="_blank" class="card card-normal">
                    <div class="icon">📊</div><p class="text-normal">REPORTE</p></a>
            </div>
        ''', unsafe_allow_html=True)

        # --- SECCIÓN DE VISITAS ---
        st.markdown('<div id="registro"></div>', unsafe_allow_html=True)
        with st.expander("📝 Generar Pase QR"):
            v_nom = st.text_input("Nombre completo del visitante:", key="v_nom")
            v_plat = st.text_input("Placas del vehículo (Opcional):", key="v_plat").upper()
            v_tipo = st.text_input("Tipo/Modelo de vehículo (Opcional):", key="v_tipo")
            
            if st.button("Generar Pase QR", key="btn_gen_qr"):
                if v_nom.strip() == "":
                    st.warning("Por favor ingresa el nombre de la visita.")
                else:
                    datos_qr = f"AUTORIZA: {nombre} | CASA: {casa} | VISITA: {v_nom}"
                    if v_plat: datos_qr += f" | PLACAS: {v_plat}"
                    if v_tipo: datos_qr += f" | CARRO: {v_tipo}"
                    
                    img = qrcode.make(datos_qr)
                    buf = BytesIO()
                    img.save(buf)
                    
                    st.image(buf)
                    st.download_button(
                        label="📥 Descargar pase para enviar por WhatsApp",
                        data=buf.getvalue(),
                        file_name=f"Pase_{v_nom.replace(' ', '_')}.png",
                        mime="image/png"
                    )

        # Avisos
        if not df_a.empty:
            st.markdown(f'<div class="aviso"><strong>📢 AVISO:</strong><br>{df_a.iloc[0,0]}</div>', unsafe_allow_html=True)

        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.session_state.datos = None
            st.query_params.clear()
            st.html("""<script>localStorage.removeItem('ccr_email_v2'); window.location.href = window.location.pathname;</script>""")
            st.rerun()
