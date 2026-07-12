import streamlit as st
import pandas as pd
from utils import MOBILE_CSS, get_sheet

st.markdown(MOBILE_CSS, unsafe_allow_html=True)

st.title("Registro de Actividad")
st.caption("Historial de acciones realizadas en el sistema.")

demo_mode = "gcp_service_account" not in st.secrets
if demo_mode:
    st.warning("Sin conexión al Sheet — no hay log disponible.", icon="⚠️")
    st.stop()

@st.cache_data(ttl=30)
def load_log():
    ws = get_sheet().worksheet("Log")
    vals = ws.get_all_values(value_render_option="UNFORMATTED_VALUE")
    if not vals or len(vals) < 2:
        return pd.DataFrame(columns=["Timestamp", "Usuario", "Acción", "Detalle"])
    df = pd.DataFrame(vals[1:], columns=vals[0])
    return df[::-1].reset_index(drop=True)  # más reciente primero

col_title, col_refresh = st.columns([5, 1])
if col_refresh.button("🔄 Refrescar", use_container_width=True):
    load_log.clear()
    st.rerun()

log = load_log()

if log.empty:
    st.info("No hay actividad registrada aún.")
    st.stop()

# ------------------------------------------------------------------
# Filtros
# ------------------------------------------------------------------
lf1, lf2 = st.columns(2)
usuarios_disp  = ["Todos"] + sorted(log["Usuario"].dropna().unique().tolist()) if "Usuario" in log.columns else ["Todos"]
acciones_disp  = ["Todos"] + sorted(log["Acción"].dropna().unique().tolist())  if "Acción"  in log.columns else ["Todos"]

usuario_sel = lf1.selectbox("Usuario", usuarios_disp, key="log_usuario")
accion_sel  = lf2.selectbox("Acción",  acciones_disp, key="log_accion")

log_f = log.copy()
if usuario_sel != "Todos":
    log_f = log_f[log_f["Usuario"] == usuario_sel]
if accion_sel  != "Todos":
    log_f = log_f[log_f["Acción"]  == accion_sel]

st.caption(f"{len(log_f)} de {len(log)} eventos")

# ------------------------------------------------------------------
# Tabla
# ------------------------------------------------------------------
st.dataframe(
    log_f,
    width='stretch',
    hide_index=True,
    height=min(36 * len(log_f) + 38, 500),
    column_config={
        "Timestamp": st.column_config.TextColumn("Fecha / Hora", width="medium"),
        "Usuario":   st.column_config.TextColumn("Usuario",      width="small"),
        "Acción":    st.column_config.TextColumn("Acción",       width="medium"),
        "Detalle":   st.column_config.TextColumn("Detalle",      width="large"),
    },
)
