import streamlit as st
import pandas as pd
from utils import MOBILE_CSS, CONCEPTOS_PARTICIPANTE, load_participantes, load_demo_participantes, soft_delete, update_row

st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Dialogs de confirmación
# ------------------------------------------------------------------
@st.dialog("Editar participante")
def _dlg_edit_part(row, row_num):
    st.caption(str(row.get("Nombre", "")))
    e_nombre   = st.text_input("Nombre",   value=str(row.get("Nombre", "")))
    e_telefono = st.text_input("Teléfono", value=str(row.get("Telefono", "")))
    c1, c2 = st.columns(2)
    if c1.button("Guardar", type="primary", use_container_width=True):
        update_row("Participantes", row_num, {"Nombre": e_nombre, "Telefono": e_telefono})
        load_participantes.clear()
        st.rerun()
    if c2.button("Cancelar", use_container_width=True):
        st.rerun()

@st.dialog("Confirmar eliminación")
def _dlg_del_part(label, row_num):
    st.warning(f"¿Eliminar participante **{label}**?", icon="⚠️")
    c1, c2 = st.columns(2)
    if c1.button("Sí, eliminar", type="primary", use_container_width=True):
        ok, msg = soft_delete("Participantes", row_num)
        if ok:
            load_participantes.clear()
            st.rerun()
        else:
            st.error(msg)
    if c2.button("Cancelar", use_container_width=True):
        st.rerun()

@st.dialog("Editar pago de participante")
def _dlg_edit_pp(row, row_num, nombres_pp):
    st.caption(f"{row.get('Participante','')} — {row.get('Concepto','')} — ${row['Monto']:,.0f}")
    e_part = st.selectbox("Participante", nombres_pp,
                          index=nombres_pp.index(row["Participante"]) if row["Participante"] in nombres_pp else 0)
    e_conc = st.selectbox("Concepto", CONCEPTOS_PARTICIPANTE,
                          index=CONCEPTOS_PARTICIPANTE.index(row["Concepto"]) if row["Concepto"] in CONCEPTOS_PARTICIPANTE else 0)
    e_monto = st.number_input("Monto (RD$)", value=float(row["Monto"]), min_value=0.0, step=100.0)
    e_nota  = st.text_input("Nota", value=str(row.get("Nota", "")))
    c1, c2 = st.columns(2)
    if c1.button("Guardar", type="primary", use_container_width=True):
        update_row("Pagos Participantes", row_num, {"Participante": e_part, "Concepto": e_conc, "Monto": e_monto, "Nota": e_nota})
        load_participantes.clear()
        st.rerun()
    if c2.button("Cancelar", use_container_width=True):
        st.rerun()

@st.dialog("Confirmar eliminación")
def _dlg_del_pp(label, row_num):
    st.warning(f"¿Eliminar pago **{label}**?", icon="⚠️")
    c1, c2 = st.columns(2)
    if c1.button("Sí, eliminar", type="primary", use_container_width=True):
        ok, msg = soft_delete("Pagos Participantes", row_num)
        if ok:
            load_participantes.clear()
            st.rerun()
        else:
            st.error(msg)
    if c2.button("Cancelar", use_container_width=True):
        st.rerun()

# ------------------------------------------------------------------
# Carga de datos
# ------------------------------------------------------------------
demo_mode = "gcp_service_account" not in st.secrets

if demo_mode:
    st.warning(
        "Mostrando datos de demostración — no hay credenciales configuradas (`st.secrets`).",
        icon="⚠️",
    )
    participantes, pagos_part = load_demo_participantes()
else:
    participantes, pagos_part = load_participantes()

# ------------------------------------------------------------------
# Encabezado
# ------------------------------------------------------------------
col_title, col_refresh = st.columns([5, 1])
col_title.title("Participantes — ETC 88")
col_title.caption("Retiro · Registro de asistentes y pagos")
if not demo_mode and col_refresh.button("🔄 Refrescar", use_container_width=True):
    load_participantes.clear()
    st.rerun()

# ------------------------------------------------------------------
# KPIs
# ------------------------------------------------------------------
total_part     = len(participantes)
total_recaudado = pagos_part["Monto"].sum() if not pagos_part.empty and "Monto" in pagos_part.columns else 0
pagos_completos = participantes[participantes["Status"] == "PAGO COMPLETO"].shape[0] if "Status" in participantes.columns else 0
pendientes      = total_part - pagos_completos

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total participantes", total_part)
k2.metric("Pago completo",       pagos_completos)
k3.metric("Pendientes",          pendientes)
k4.metric("Total recaudado",     f"${total_recaudado:,.0f}")

st.divider()

# ------------------------------------------------------------------
# Tabla participantes
# ------------------------------------------------------------------
st.subheader(f"Participantes ({total_part})")

if participantes.empty:
    st.info("No hay participantes registrados aún.")
else:
    cols_p = [c for c in ["Nombre", "Telefono", "Total Aportado", "Status"] if c in participantes.columns]
    part_display = participantes[cols_p].copy()
    if "Status" in part_display.columns:
        part_display["Status"] = part_display["Status"].map(
            lambda v: "✅ Pago completo" if v == "PAGO COMPLETO" else ("⏳ Pendiente" if v == "PENDIENTE" else v)
        )
    st.dataframe(
        part_display,
        width='stretch',
        hide_index=True,
        height=min(36 * len(part_display) + 38, 400),
        column_config={
            "Nombre":         st.column_config.TextColumn("Participante", width="large"),
            "Telefono":       st.column_config.TextColumn("Teléfono",     width="medium"),
            "Total Aportado": st.column_config.NumberColumn("Aportado",   format="$%.0f", width="small"),
            "Status":         st.column_config.TextColumn("Estado",       width="medium"),
        },
    )

    if not demo_mode and "_row_num" in participantes.columns:
        labels_p   = participantes["Nombre"].astype(str).tolist()
        row_nums_p = participantes["_row_num"].tolist()

        with st.expander("✏️ Editar participante"):
            sel_ep = st.selectbox("Seleccionar participante", range(len(labels_p)),
                                  format_func=lambda i: labels_p[i], key="edit_part")
            if st.button("Abrir editor", key="btn_open_edit_part", use_container_width=True):
                _dlg_edit_part(participantes.iloc[sel_ep], row_nums_p[sel_ep])

        with st.expander("🗑️ Eliminar participante"):
            sel_p = st.selectbox("Seleccionar participante", range(len(labels_p)),
                                 format_func=lambda i: labels_p[i], key="del_part")
            if st.button("Eliminar participante", type="primary", key="btn_del_part", use_container_width=True):
                _dlg_del_part(labels_p[sel_p], row_nums_p[sel_p])

st.divider()

# ------------------------------------------------------------------
# Tabla pagos participantes
# ------------------------------------------------------------------
st.subheader("Pagos de participantes")

if pagos_part.empty:
    st.info("No hay pagos de participantes registrados aún.")
else:
    pf1, pf2 = st.columns(2)
    parts_disp    = ["Todos"] + sorted(pagos_part["Participante"].dropna().unique().tolist()) if "Participante" in pagos_part.columns else ["Todos"]
    conceptos_disp = ["Todos"] + sorted(pagos_part["Concepto"].dropna().unique().tolist()) if "Concepto" in pagos_part.columns else ["Todos"]

    part_sel    = pf1.selectbox("Participante", parts_disp,     key="pp_part")
    concepto_sel = pf2.selectbox("Concepto",    conceptos_disp, key="pp_concepto")

    pagos_f = pagos_part.copy()
    if part_sel    != "Todos":
        pagos_f = pagos_f[pagos_f["Participante"] == part_sel]
    if concepto_sel != "Todos":
        pagos_f = pagos_f[pagos_f["Concepto"] == concepto_sel]

    st.caption(f"{len(pagos_f)} de {len(pagos_part)} pagos")

    cols_pp = [c for c in ["Participante", "Concepto", "Monto", "Fecha", "Nota"] if c in pagos_f.columns]
    st.dataframe(
        pagos_f[cols_pp],
        width='stretch',
        hide_index=True,
        height=min(36 * len(pagos_f) + 38, 400),
        column_config={
            "Participante": st.column_config.TextColumn("Participante", width="large"),
            "Concepto":     st.column_config.TextColumn("Concepto",     width="medium"),
            "Monto":        st.column_config.NumberColumn("Monto",      format="$%.0f", width="small"),
            "Fecha":        st.column_config.TextColumn("Fecha",        width="small"),
            "Nota":         st.column_config.TextColumn("Nota",         width="medium"),
        },
    )

    if not demo_mode and "_row_num" in pagos_part.columns:
        labels_pp   = (
            pagos_part["Participante"].astype(str)
            + " — " + pagos_part["Concepto"].astype(str)
            + " — $" + pagos_part["Monto"].apply(lambda x: f"{x:,.0f}")
        ).tolist()
        row_nums_pp = pagos_part["_row_num"].tolist()
        nombres_pp  = sorted(pagos_part["Participante"].dropna().unique().tolist())

        with st.expander("✏️ Editar pago"):
            sel_epp = st.selectbox("Seleccionar pago", range(len(labels_pp)),
                                   format_func=lambda i: labels_pp[i], key="edit_pp")
            if st.button("Abrir editor", key="btn_open_edit_pp", use_container_width=True):
                _dlg_edit_pp(pagos_part.iloc[sel_epp], row_nums_pp[sel_epp], nombres_pp)

        with st.expander("🗑️ Eliminar pago"):
            sel_idx = st.selectbox("Seleccionar pago", range(len(labels_pp)),
                                   format_func=lambda i: labels_pp[i], key="del_pp")
            if st.button("Eliminar pago seleccionado", type="primary", key="btn_del_pp", use_container_width=True):
                _dlg_del_pp(labels_pp[sel_idx], row_nums_pp[sel_idx])
