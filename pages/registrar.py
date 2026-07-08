import streamlit as st
from datetime import date
from utils import (
    CONCEPTOS_PAGO, FUENTES_PAGO, MOBILE_CSS,
    load_data, load_demo_data,
    append_pago, append_gasto,
)

st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Carga de datos
# ------------------------------------------------------------------
demo_mode = "gcp_service_account" not in st.secrets

if demo_mode:
    st.info("Conecta Google Sheets para habilitar el registro de datos.", icon="ℹ️")
    miembros, _, _, _ = load_demo_data()
else:
    miembros, _, _, _ = load_data()

st.title("Registrar")

nombres = sorted(miembros["Nombre"].dropna().unique().tolist()) if "Nombre" in miembros.columns else []

# ------------------------------------------------------------------
# Registrar pago
# ------------------------------------------------------------------
st.subheader("Registrar pago")
with st.form("form_pago", clear_on_submit=True):
    miembro_sel  = st.selectbox("Miembro",        nombres,        disabled=demo_mode)
    concepto_sel = st.selectbox("Concepto",       CONCEPTOS_PAGO, disabled=demo_mode)
    monto_val    = st.number_input("Monto (RD$)", min_value=0, step=100, value=0, disabled=demo_mode)
    fuente_sel   = st.selectbox("Fuente",         FUENTES_PAGO,   disabled=demo_mode)
    nota_val     = st.text_input("Nota (opcional)",               disabled=demo_mode)
    submitted    = st.form_submit_button("Guardar pago", type="primary",
                                         use_container_width=True, disabled=demo_mode)

if submitted and not demo_mode:
    if monto_val <= 0:
        st.error("El monto debe ser mayor a 0.")
    else:
        try:
            append_pago(miembro_sel, concepto_sel, monto_val, fuente_sel, nota_val)
            st.success(f"Pago de ${monto_val:,.0f} registrado para {miembro_sel}.")
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar: {e}")

st.divider()

# ------------------------------------------------------------------
# Registrar gasto
# ------------------------------------------------------------------
st.subheader("Registrar gasto")
with st.form("form_gasto", clear_on_submit=True):
    fecha_val   = st.date_input("Fecha", value=date.today(),       disabled=demo_mode)
    concepto_g  = st.text_input("Concepto",                        disabled=demo_mode)
    monto_g     = st.number_input("Monto (RD$)", min_value=0, step=100, value=0,
                                  key="monto_gasto",               disabled=demo_mode)
    fuente_g    = st.text_input("Fuente", value="Reporte Salidas", disabled=demo_mode)
    submitted_g = st.form_submit_button("Guardar gasto", type="primary",
                                        use_container_width=True,  disabled=demo_mode)

if submitted_g and not demo_mode:
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
