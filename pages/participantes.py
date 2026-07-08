import streamlit as st
import pandas as pd
from utils import MOBILE_CSS, load_participantes, load_demo_participantes, soft_delete

st.markdown(MOBILE_CSS, unsafe_allow_html=True)

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
        use_container_width=True,
        hide_index=True,
        height=min(36 * len(part_display) + 38, 400),
        column_config={
            "Nombre":         st.column_config.TextColumn("Participante", width="large"),
            "Telefono":       st.column_config.TextColumn("Teléfono",     width="medium"),
            "Total Aportado": st.column_config.NumberColumn("Aportado",   format="$%.0f", width="small"),
            "Status":         st.column_config.TextColumn("Estado",       width="medium"),
        },
    )

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
        use_container_width=True,
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
        with st.expander("🗑️ Eliminar pago"):
            labels = (
                pagos_part["Participante"].astype(str)
                + " — " + pagos_part["Concepto"].astype(str)
                + " — $" + pagos_part["Monto"].apply(lambda x: f"{x:,.0f}")
            ).tolist()
            row_nums = pagos_part["_row_num"].tolist()
            sel_idx = st.selectbox("Seleccionar pago", range(len(labels)),
                                   format_func=lambda i: labels[i], key="del_pp")
            if st.button("Eliminar pago seleccionado", type="primary", key="btn_del_pp"):
                ok, msg = soft_delete("Pagos Participantes", row_nums[sel_idx])
                if ok:
                    st.success("Pago eliminado.")
                    load_participantes.clear()
                    st.rerun()
                else:
                    st.error(msg)
