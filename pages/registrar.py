import streamlit as st
from datetime import date
from utils import (
    CONCEPTOS_PAGO, FUENTES_PAGO, CONCEPTOS_PARTICIPANTE, MOBILE_CSS,
    load_data, load_demo_data, load_participantes, load_demo_participantes,
    append_pago, append_gasto, append_donacion, append_participante, append_pago_participante,
)

st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Carga de datos
# ------------------------------------------------------------------
demo_mode = "gcp_service_account" not in st.secrets

if demo_mode:
    st.info("Conecta Google Sheets para habilitar el registro de datos.", icon="ℹ️")
    miembros, _, _, _ = load_demo_data()
    participantes, _  = load_demo_participantes()
else:
    miembros, _, _, _ = load_data()
    participantes, _  = load_participantes()

st.title("Registrar")

nombres      = sorted(miembros["Nombre"].dropna().unique().tolist()) if "Nombre" in miembros.columns else []
nombres_part = sorted(participantes["Nombre"].dropna().unique().tolist()) if "Nombre" in participantes.columns and not participantes.empty else []

# ------------------------------------------------------------------
# Tabs
# ------------------------------------------------------------------
tab_pago, tab_gasto, tab_donacion, tab_part, tab_pago_part = st.tabs([
    "💰 Pago miembro",
    "📤 Gasto",
    "🎁 Donación",
    "🏕️ Participante",
    "💳 Pago participante",
])

# ── Pago miembro ──────────────────────────────────────────────────
with tab_pago:
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

# ── Gasto ─────────────────────────────────────────────────────────
with tab_gasto:
    with st.form("form_gasto", clear_on_submit=True):
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
                append_gasto(str(date.today()), concepto_g.strip(), monto_g, fuente_g.strip())
                st.success(f"Gasto de ${monto_g:,.0f} registrado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# ── Donación ─────────────────────────────────────────────────────
with tab_donacion:
    with st.form("form_donacion", clear_on_submit=True):
        donante_val = st.text_input("Donante",                   key="donante",   disabled=demo_mode)
        monto_don   = st.number_input("Monto (RD$)", min_value=0, step=100, value=0,
                                      key="monto_don",                            disabled=demo_mode)
        nota_don    = st.text_input("Nota (opcional)",           key="nota_don",  disabled=demo_mode)
        submitted_don = st.form_submit_button("Guardar donación", type="primary",
                                              use_container_width=True, disabled=demo_mode)

    if submitted_don and not demo_mode:
        if not donante_val.strip():
            st.error("El donante no puede estar vacío.")
        elif monto_don <= 0:
            st.error("El monto debe ser mayor a 0.")
        else:
            try:
                append_donacion(str(date.today()), donante_val.strip(), monto_don, nota_don.strip())
                st.success(f"Donación de ${monto_don:,.0f} de '{donante_val.strip()}' registrada.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# ── Participante ──────────────────────────────────────────────────
with tab_part:
    with st.form("form_participante", clear_on_submit=True):
        nombre_part   = st.text_input("Nombre completo",    disabled=demo_mode)
        telefono_part = st.text_input("Teléfono (opcional)", disabled=demo_mode)
        submitted_part = st.form_submit_button("Guardar participante", type="primary",
                                               use_container_width=True, disabled=demo_mode)

    if submitted_part and not demo_mode:
        if not nombre_part.strip():
            st.error("El nombre no puede estar vacío.")
        else:
            try:
                append_participante(nombre_part.strip(), telefono_part.strip())
                st.success(f"Participante '{nombre_part.strip()}' registrado.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# ── Pago participante ─────────────────────────────────────────────
with tab_pago_part:
    if not nombres_part:
        st.info("No hay participantes registrados aún. Regístralos en la pestaña 🏕️ Participante.")
    else:
        with st.form("form_pago_part", clear_on_submit=True):
            part_sel    = st.selectbox("Participante", nombres_part,           disabled=demo_mode)
            concepto_pp = st.selectbox("Concepto",     CONCEPTOS_PARTICIPANTE, disabled=demo_mode)
            monto_pp    = st.number_input("Monto (RD$)", min_value=0, step=100, value=0,
                                          key="monto_pp", disabled=demo_mode)
            nota_pp     = st.text_input("Nota (opcional)", key="nota_pp",      disabled=demo_mode)
            submitted_pp = st.form_submit_button("Guardar pago", type="primary",
                                                 use_container_width=True, disabled=demo_mode)

        if submitted_pp and not demo_mode:
            if monto_pp <= 0:
                st.error("El monto debe ser mayor a 0.")
            else:
                try:
                    append_pago_participante(part_sel, concepto_pp, monto_pp, date.today(), nota_pp)
                    st.success(f"Pago de ${monto_pp:,.0f} registrado para {part_sel}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
