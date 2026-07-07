import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

st.set_page_config(page_title="ETC 88 · Panel de Finanzas", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=EB+Garamond:wght@400;700&display=swap');

:root {
  --bg:         #EAE0C4;
  --surface:    #F2EAD3;
  --dim:        #DDD3B2;
  --navy:       #111328;
  --navy2:      #1A1C38;
  --text:       #1A1C38;
  --text2:      #5C5F7A;
  --accent:     #C49020;
  --accent-bg:  #F5DFA0;
  --accent-lt:  #F0C84A;
  --border:     #C8BDA0;
  --pos-bg:     #DCEFE2;
  --pos-tx:     #1E4A36;
  --neg-bg:     #FBE9E4;
  --neg-tx:     #A34430;
}

/* Base */
.main, [data-testid="stAppViewContainer"] { background: var(--bg) !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; }
[data-testid="stHeader"] { background: var(--navy) !important; }

/* KPI cards */
[data-testid="stMetric"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 1rem !important;
}
[data-testid="stMetricLabel"] p {
  font-size: 0.65rem !important; font-weight: 600 !important;
  text-transform: uppercase !important; letter-spacing: 0.1em !important;
  color: var(--accent) !important;
}
[data-testid="stMetricValue"] > div {
  font-family: 'EB Garamond', Georgia, serif !important;
  font-size: 1.8rem !important; color: var(--navy) !important;
}

/* Tabs */
[data-baseweb="tab-list"] { background: transparent !important; border-bottom: 2px solid var(--border) !important; }
[data-baseweb="tab"] { background: transparent !important; color: var(--text2) !important; font-size: 0.875rem !important; font-weight: 500 !important; margin-bottom: -2px !important; }
[data-baseweb="tab"][aria-selected="true"] { color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important; font-weight: 600 !important; }

/* Dropdowns */
[data-testid="stSelectbox"] > div > div { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
[data-testid="stSelectbox"] label { font-size: 0.75rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; color: var(--text2) !important; }

/* Buttons */
.stButton > button {
  background: var(--accent-bg) !important; color: var(--navy2) !important;
  border: 1px solid var(--border) !important; border-radius: 8px !important;
  font-size: 0.75rem !important; font-weight: 600 !important;
  text-transform: uppercase !important; letter-spacing: 0.08em !important;
  transition: all 0.15s ease !important;
}
.stButton > button:hover { background: var(--accent-lt) !important; border-color: var(--accent) !important; }
.stFormSubmitButton > button { background: var(--navy) !important; color: var(--accent-lt) !important; border-color: var(--navy) !important; }
.stFormSubmitButton > button:hover { background: var(--navy2) !important; }

/* Tables */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 10px !important; overflow: hidden !important; }

/* Expanders */
[data-testid="stExpander"] { border: 1px solid var(--border) !important; border-radius: 8px !important; background: var(--surface) !important; }

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
  background: var(--surface) !important; border: 1px solid var(--border) !important;
  border-radius: 8px !important; color: var(--text) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(196,144,32,0.2) !important; }
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stDateInput"] label { font-size: 0.75rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; color: var(--text2) !important; }

/* Alerts */
[data-testid="stAlert"] { border-radius: 8px !important; border-left: 4px solid var(--accent) !important; }

/* Divider */
hr { border-color: var(--border) !important; opacity: 0.5 !important; }

/* Mobile ≤768px */
@media (max-width: 768px) {
  .block-container { padding: 1rem 0.75rem 3rem !important; }
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 0.5rem !important; }
  [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: calc(45% - 0.25rem) !important; flex: 1 1 calc(45% - 0.25rem) !important; }
  [data-testid="stMetricValue"] > div { font-size: 1.2rem !important; }
  [data-testid="stMetricLabel"] p { font-size: 0.6rem !important; }
  [data-testid="stDataFrame"] > div { overflow-x: auto !important; }
  .stButton > button { width: 100% !important; }
}

/* Mobile ≤420px */
@media (max-width: 420px) {
  [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Constantes
# ------------------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CUOTA_ESPERADA = 2000
CONCEPTOS_PAGO = [
    "Cuota 1", "Cuota 2", "Cuota 3", "Cuota 4",
    "Formacion 1", "Formacion 2", "Formacion 3", "Formacion 4",
]
FUENTES_PAGO = ["Control de Cuotas", "Tardanzas", "Otro"]

# ------------------------------------------------------------------
# Conexión a Google Sheets
# ------------------------------------------------------------------
@st.cache_resource
def get_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(creds).open_by_key(st.secrets["sheet_id"])


def _ws_to_df(ws):
    """Lee worksheet y agrega columna _row_num con la fila real en el Sheet."""
    vals = ws.get_all_values(value_render_option="UNFORMATTED_VALUE")
    if not vals:
        return pd.DataFrame()
    if len(vals) < 2:
        return pd.DataFrame(columns=vals[0])
    headers = vals[0]
    rows = vals[1:]
    df = pd.DataFrame(rows, columns=headers)
    df["_row_num"] = range(2, len(rows) + 2)
    return df


@st.cache_data(ttl=60)
def load_data():
    sh = get_sheet()
    miembros = _ws_to_df(sh.worksheet("Miembros"))
    pagos    = _ws_to_df(sh.worksheet("Pagos"))
    gastos   = _ws_to_df(sh.worksheet("Gastos"))

    if not miembros.empty and "Nombre" in miembros.columns:
        miembros = miembros[miembros["Nombre"].astype(str).str.strip() != ""]
    if not pagos.empty and "Miembro" in pagos.columns:
        pagos = pagos[pagos["Miembro"].astype(str).str.strip() != ""]
    if not gastos.empty and "Concepto" in gastos.columns:
        gastos = gastos[gastos["Concepto"].astype(str).str.strip() != ""]

    if "Activo" in pagos.columns:
        pagos = pagos[pagos["Activo"].astype(str).str.upper() != "FALSE"]
    if "Activo" in gastos.columns:
        gastos = gastos[gastos["Activo"].astype(str).str.upper() != "FALSE"]

    if "Total Aportado" in miembros.columns:
        miembros["Total Aportado"] = pd.to_numeric(miembros["Total Aportado"], errors="coerce").fillna(0)
    if "Monto" in pagos.columns:
        pagos["Monto"] = pd.to_numeric(pagos["Monto"], errors="coerce").fillna(0)
    if "Monto" in gastos.columns:
        gastos["Monto"] = pd.to_numeric(gastos["Monto"], errors="coerce").fillna(0)

    return miembros, pagos, gastos


# ------------------------------------------------------------------
# Datos de muestra (modo demo sin secrets)
# ------------------------------------------------------------------
def load_demo_data():
    miembros = pd.DataFrame([
        {"Nombre": "Juan Manuel De La Cruz", "Rol": "Director", "Total Aportado": 2000, "Status": "PAGO COMPLETO"},
        {"Nombre": "Jean Carlos De La Cruz", "Rol": "Director", "Total Aportado": 0,    "Status": "PENDIENTE"},
        {"Nombre": "Laura Fernandez",        "Rol": "Asesor",   "Total Aportado": 1000, "Status": "PENDIENTE"},
        {"Nombre": "Fernando Cordero",       "Rol": "Guia",     "Total Aportado": 2000, "Status": "PAGO COMPLETO"},
        {"Nombre": "Paloma Mendez",          "Rol": "Cocinero", "Total Aportado": 500,  "Status": "PENDIENTE"},
        {"Nombre": "Tommy",                  "Rol": "Cocinero", "Total Aportado": 0,    "Status": "PENDIENTE"},
    ])
    pagos = pd.DataFrame([
        {"Miembro": "Juan Manuel De La Cruz", "Concepto": "Cuota 1",     "Monto": 2000, "Fuente": "Control de Cuotas", "Nota": ""},
        {"Miembro": "Fernando Cordero",       "Concepto": "Cuota 1",     "Monto": 2000, "Fuente": "Control de Cuotas", "Nota": ""},
        {"Miembro": "Laura Fernandez",        "Concepto": "Cuota 1",     "Monto": 1000, "Fuente": "Control de Cuotas", "Nota": ""},
        {"Miembro": "Paloma Mendez",          "Concepto": "Cuota 1",     "Monto": 500,  "Fuente": "Control de Cuotas", "Nota": ""},
        {"Miembro": "Tommy",                  "Concepto": "Formacion 1", "Monto": 100,  "Fuente": "Tardanzas",         "Nota": ""},
    ])
    gastos = pd.DataFrame([
        {"Fecha": "No especificada", "Concepto": "Merienda formacion 3", "Monto": 2500, "Fuente": "Reporte Salidas"},
    ])
    return miembros, pagos, gastos


# ------------------------------------------------------------------
# Operaciones de escritura
# ------------------------------------------------------------------
def _col_idx(ws, col_name):
    headers = ws.row_values(1)
    return headers.index(col_name) + 1 if col_name in headers else None


def append_pago(miembro, concepto, monto, fuente, nota):
    ws = get_sheet().worksheet("Pagos")
    headers = ws.row_values(1)
    mapping = {"Miembro": miembro, "Concepto": concepto, "Monto": monto,
               "Fuente": fuente, "Nota": nota, "Activo": "TRUE"}
    ws.append_row([mapping.get(h, "") for h in headers], value_input_option="USER_ENTERED")
    load_data.clear()


def append_gasto(fecha, concepto, monto, fuente):
    ws = get_sheet().worksheet("Gastos")
    headers = ws.row_values(1)
    mapping = {"Fecha": str(fecha), "Concepto": concepto,
               "Monto": monto, "Fuente": fuente, "Activo": "TRUE"}
    ws.append_row([mapping.get(h, "") for h in headers], value_input_option="USER_ENTERED")
    load_data.clear()


def soft_delete(worksheet_name, row_num):
    ws = get_sheet().worksheet(worksheet_name)
    idx = _col_idx(ws, "Activo")
    if idx is None:
        return False, "Columna 'Activo' no existe. Agrégala al Sheet primero."
    ws.update_cell(row_num, idx, "FALSE")
    load_data.clear()
    return True, ""


# ------------------------------------------------------------------
# Carga de datos
# ------------------------------------------------------------------
demo_mode = "gcp_service_account" not in st.secrets

if demo_mode:
    st.warning(
        "Mostrando datos de demostración — no hay credenciales configuradas (`st.secrets`).",
        icon="⚠️",
    )
    miembros, pagos, gastos = load_demo_data()
else:
    miembros, pagos, gastos = load_data()

# ------------------------------------------------------------------
# Encabezado
# ------------------------------------------------------------------
col_title, col_refresh = st.columns([5, 1])
col_title.title("Panel de Finanzas — Equipo ETC 88")
col_title.caption(
    "Vista interna. Datos en vivo desde Google Sheets." if not demo_mode
    else "Vista interna — modo demo."
)
if not demo_mode and col_refresh.button("🔄 Refrescar", use_container_width=True):
    load_data.clear()
    st.rerun()

# ------------------------------------------------------------------
# Tabs
# ------------------------------------------------------------------
tab_dashboard, tab_registrar = st.tabs(["📊 Dashboard", "➕ Registrar"])

# ══════════════════════════════════════════════════════════════════
# TAB: DASHBOARD
# ══════════════════════════════════════════════════════════════════
with tab_dashboard:

    # Filtros
    col_f1, col_f2 = st.columns(2)
    roles_disponibles  = ["Todos"] + sorted(miembros["Rol"].dropna().unique().tolist())
    status_disponibles = ["Todos"] + sorted(miembros["Status"].dropna().unique().tolist())
    rol_sel    = col_f1.selectbox("Filtrar por rol",    roles_disponibles)
    status_sel = col_f2.selectbox("Filtrar por status", status_disponibles)

    miembros_f = miembros.copy()
    if rol_sel    != "Todos":
        miembros_f = miembros_f[miembros_f["Rol"]    == rol_sel]
    if status_sel != "Todos":
        miembros_f = miembros_f[miembros_f["Status"] == status_sel]

    # KPIs
    total_miembros  = len(miembros)
    total_esperado  = total_miembros * CUOTA_ESPERADA
    total_cuotas    = pagos.loc[pagos["Concepto"].astype(str).str.startswith("Cuota"), "Monto"].sum()
    pendiente       = total_esperado - total_cuotas
    total_tardanzas = pagos.loc[~pagos["Concepto"].astype(str).str.startswith("Cuota"), "Monto"].sum()
    entradas        = total_cuotas + total_tardanzas
    salidas         = gastos["Monto"].sum()
    balance         = entradas - salidas

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total esperado",    f"${total_esperado:,.0f}")
    k2.metric("Cuotas recaudadas", f"${total_cuotas:,.0f}")
    k3.metric("Pendiente",         f"${pendiente:,.0f}")
    k4.metric("Entradas totales",  f"${entradas:,.0f}")
    k5.metric("Balance",           f"${balance:,.0f}")

    st.divider()

    # Tabla miembros
    st.subheader(f"Miembros ({len(miembros_f)} de {total_miembros})")

    def resaltar_status(val):
        if val == "PAGO COMPLETO":
            return "background-color: #DCEFE2; color: #1E4A36; font-weight: 600;"
        if val == "PENDIENTE":
            return "background-color: #FBE9E4; color: #A34430; font-weight: 600;"
        return ""

    cols_miembros = [c for c in ["Nombre", "Rol", "Total Aportado", "Status"] if c in miembros_f.columns]
    st.dataframe(
        miembros_f[cols_miembros]
        .style.map(resaltar_status, subset=["Status"])
        .format({"Total Aportado": "${:,.0f}"}),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # Tabla pagos + eliminar
    st.subheader("Pagos registrados")
    cols_pagos = [c for c in ["Miembro", "Concepto", "Monto", "Fuente", "Nota"] if c in pagos.columns]
    st.dataframe(
        pagos[cols_pagos].style.format({"Monto": "${:,.0f}"}),
        use_container_width=True,
        hide_index=True,
    )

    if not demo_mode and not pagos.empty and "_row_num" in pagos.columns:
        with st.expander("🗑️ Eliminar pago"):
            labels = (
                pagos["Miembro"].astype(str)
                + " — " + pagos["Concepto"].astype(str)
                + " — $" + pagos["Monto"].apply(lambda x: f"{x:,.0f}")
            ).tolist()
            row_nums = pagos["_row_num"].tolist()
            sel_idx = st.selectbox("Seleccionar pago", range(len(labels)),
                                   format_func=lambda i: labels[i], key="del_pago")
            if st.button("Eliminar pago seleccionado", type="primary", key="btn_del_pago"):
                ok, msg = soft_delete("Pagos", row_nums[sel_idx])
                if ok:
                    st.success("Pago eliminado.")
                    st.rerun()
                else:
                    st.error(msg)

    st.divider()

    # Tabla gastos + eliminar
    st.subheader("Gastos registrados")
    cols_gastos = [c for c in ["Fecha", "Concepto", "Monto", "Fuente"] if c in gastos.columns]
    st.dataframe(
        gastos[cols_gastos].style.format({"Monto": "${:,.0f}"}),
        use_container_width=True,
        hide_index=True,
    )

    if not demo_mode and not gastos.empty and "_row_num" in gastos.columns:
        with st.expander("🗑️ Eliminar gasto"):
            labels_g = (
                gastos["Concepto"].astype(str)
                + " — $" + gastos["Monto"].apply(lambda x: f"{x:,.0f}")
            ).tolist()
            row_nums_g = gastos["_row_num"].tolist()
            sel_idx_g = st.selectbox("Seleccionar gasto", range(len(labels_g)),
                                     format_func=lambda i: labels_g[i], key="del_gasto")
            if st.button("Eliminar gasto seleccionado", type="primary", key="btn_del_gasto"):
                ok, msg = soft_delete("Gastos", row_nums_g[sel_idx_g])
                if ok:
                    st.success("Gasto eliminado.")
                    st.rerun()
                else:
                    st.error(msg)

    st.divider()

    # Gráfico por rol
    st.subheader("Progreso de recaudo por rol")
    resumen_rol = (
        miembros.groupby("Rol")
        .agg(Miembros=("Nombre", "count"), Recaudado=("Total Aportado", "sum"))
        .reset_index()
    )
    resumen_rol["Esperado"]    = resumen_rol["Miembros"] * CUOTA_ESPERADA
    resumen_rol["% Recaudado"] = (resumen_rol["Recaudado"] / resumen_rol["Esperado"] * 100).round(1)
    st.bar_chart(resumen_rol.set_index("Rol")[["Esperado", "Recaudado"]])

# ══════════════════════════════════════════════════════════════════
# TAB: REGISTRAR
# ══════════════════════════════════════════════════════════════════
with tab_registrar:

    if demo_mode:
        st.info("Conecta Google Sheets para habilitar el registro de datos.", icon="ℹ️")
    else:
        col_pago, col_gasto = st.columns(2)

        with col_pago:
            st.subheader("Registrar pago")
            nombres = sorted(miembros["Nombre"].dropna().unique().tolist()) if "Nombre" in miembros.columns else []
            with st.form("form_pago", clear_on_submit=True):
                miembro_sel  = st.selectbox("Miembro",        nombres)
                concepto_sel = st.selectbox("Concepto",       CONCEPTOS_PAGO)
                monto_val    = st.number_input("Monto (RD$)", min_value=0, step=100, value=0)
                fuente_sel   = st.selectbox("Fuente",         FUENTES_PAGO)
                nota_val     = st.text_input("Nota (opcional)")
                submitted    = st.form_submit_button("Guardar pago", type="primary", use_container_width=True)
            if submitted:
                if monto_val <= 0:
                    st.error("El monto debe ser mayor a 0.")
                else:
                    try:
                        append_pago(miembro_sel, concepto_sel, monto_val, fuente_sel, nota_val)
                        st.success(f"Pago de ${monto_val:,.0f} registrado para {miembro_sel}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

        with col_gasto:
            st.subheader("Registrar gasto")
            with st.form("form_gasto", clear_on_submit=True):
                fecha_val   = st.date_input("Fecha", value=date.today())
                concepto_g  = st.text_input("Concepto")
                monto_g     = st.number_input("Monto (RD$)", min_value=0, step=100, value=0, key="monto_gasto")
                fuente_g    = st.text_input("Fuente", value="Reporte Salidas")
                submitted_g = st.form_submit_button("Guardar gasto", type="primary", use_container_width=True)
            if submitted_g:
                if not concepto_g.strip():
                    st.error("El concepto no puede estar vacío.")
                elif monto_g <= 0:
                    st.error("El monto debe ser mayor a 0.")
                else:
                    try:
                        append_gasto(str(fecha_val), concepto_g.strip(), monto_g, fuente_g.strip())
                        st.success(f"Gasto de ${monto_g:,.0f} registrado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

# ------------------------------------------------------------------
# Instrucciones conexión (solo demo)
# ------------------------------------------------------------------
if demo_mode:
    with st.expander("Cómo conectar tu Google Sheets real"):
        st.markdown("""
        1. Sube el archivo a Google Drive y ábrelo con Google Sheets.
        2. Crea cuenta de servicio en Google Cloud Console con acceso a la Sheets API.
           Comparte el Sheet con el correo de esa cuenta (permiso **editor**).
        3. En las hojas **Pagos** y **Gastos**, agrega columna `Activo` (solo el header).
        4. En Streamlit Community Cloud → **Settings → Secrets**:
        ```toml
        sheet_id = "TU_ID_DE_GOOGLE_SHEET"

        [gcp_service_account]
        type = "service_account"
        project_id = "..."
        private_key_id = "..."
        private_key = "..."
        client_email = "..."
        client_id = "..."
        token_uri = "https://oauth2.googleapis.com/token"
        ```
        5. Redespliega — el aviso de demo desaparece automáticamente.
        """)
