import streamlit as st
from utils import (
    CUOTA_ESPERADA, MOBILE_CSS,
    load_data, load_demo_data, soft_delete,
)

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
    miembros, pagos, gastos = load_demo_data()
else:
    miembros, pagos, gastos = load_data()

# ------------------------------------------------------------------
# Encabezado
# ------------------------------------------------------------------
col_title, col_refresh = st.columns([5, 1])
col_title.title("Panel de Finanzas — ETC 88")
col_title.caption(
    "Vista interna. Datos en vivo desde Google Sheets." if not demo_mode
    else "Vista interna — modo demo."
)
if not demo_mode and col_refresh.button("🔄 Refrescar", use_container_width=True):
    load_data.clear()
    st.rerun()

# ------------------------------------------------------------------
# Filtros
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# KPIs
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# Tabla miembros
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# Tabla pagos + eliminar
# ------------------------------------------------------------------
st.subheader("Pagos registrados")

pf1, pf2, pf3 = st.columns(3)
miembros_disp  = ["Todos"] + sorted(pagos["Miembro"].dropna().unique().tolist()) if "Miembro" in pagos.columns else ["Todos"]
conceptos_disp = ["Todos"] + sorted(pagos["Concepto"].dropna().unique().tolist()) if "Concepto" in pagos.columns else ["Todos"]
fuentes_disp   = ["Todos"] + sorted(pagos["Fuente"].dropna().unique().tolist()) if "Fuente" in pagos.columns else ["Todos"]

miembro_sel  = pf1.selectbox("Miembro",  miembros_disp,  key="pago_miembro")
concepto_sel = pf2.selectbox("Concepto", conceptos_disp, key="pago_concepto")
fuente_sel   = pf3.selectbox("Fuente",   fuentes_disp,   key="pago_fuente")

pagos_f = pagos.copy()
if miembro_sel  != "Todos":
    pagos_f = pagos_f[pagos_f["Miembro"]  == miembro_sel]
if concepto_sel != "Todos":
    pagos_f = pagos_f[pagos_f["Concepto"] == concepto_sel]
if fuente_sel   != "Todos":
    pagos_f = pagos_f[pagos_f["Fuente"]   == fuente_sel]

st.caption(f"{len(pagos_f)} de {len(pagos)} pagos")

cols_pagos = [c for c in ["Miembro", "Concepto", "Monto", "Fuente", "Nota"] if c in pagos_f.columns]
st.dataframe(
    pagos_f[cols_pagos].style.format({"Monto": "${:,.0f}"}),
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

# ------------------------------------------------------------------
# Tabla gastos + eliminar
# ------------------------------------------------------------------
st.subheader("Gastos registrados")

gf1, gf2, gf3, gf4 = st.columns(4)
conceptos_g_disp = ["Todos"] + sorted(gastos["Concepto"].dropna().unique().tolist()) if "Concepto" in gastos.columns else ["Todos"]
fuentes_g_disp   = ["Todos"] + sorted(gastos["Fuente"].dropna().unique().tolist()) if "Fuente" in gastos.columns else ["Todos"]

concepto_g_sel = gf1.selectbox("Concepto", conceptos_g_disp, key="gasto_concepto")
fuente_g_sel   = gf2.selectbox("Fuente",   fuentes_g_disp,   key="gasto_fuente")

import pandas as pd
if "Fecha" in gastos.columns:
    fechas_validas = pd.to_datetime(gastos["Fecha"], dayfirst=True, errors="coerce").dropna()
    fecha_min = fechas_validas.min().date() if not fechas_validas.empty else None
    fecha_max = fechas_validas.max().date() if not fechas_validas.empty else None
else:
    fecha_min = fecha_max = None

fecha_desde = gf3.date_input("Desde", value=fecha_min, key="gasto_desde") if fecha_min else None
fecha_hasta = gf4.date_input("Hasta", value=fecha_max, key="gasto_hasta") if fecha_max else None

gastos_f = gastos.copy()
if concepto_g_sel != "Todos":
    gastos_f = gastos_f[gastos_f["Concepto"] == concepto_g_sel]
if fuente_g_sel   != "Todos":
    gastos_f = gastos_f[gastos_f["Fuente"]   == fuente_g_sel]
if fecha_desde and fecha_hasta and "Fecha" in gastos_f.columns:
    fechas_parsed = pd.to_datetime(gastos_f["Fecha"], dayfirst=True, errors="coerce")
    gastos_f = gastos_f[(fechas_parsed.dt.date >= fecha_desde) & (fechas_parsed.dt.date <= fecha_hasta)]

st.caption(f"{len(gastos_f)} de {len(gastos)} gastos")

cols_gastos = [c for c in ["Fecha", "Concepto", "Monto", "Fuente"] if c in gastos_f.columns]
st.dataframe(
    gastos_f[cols_gastos].style.format({"Monto": "${:,.0f}"}),
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

# ------------------------------------------------------------------
# Gráfico por rol
# ------------------------------------------------------------------
st.subheader("Progreso de recaudo por rol")
resumen_rol = (
    miembros.groupby("Rol")
    .agg(Miembros=("Nombre", "count"), Recaudado=("Total Aportado", "sum"))
    .reset_index()
)
resumen_rol["Esperado"]    = resumen_rol["Miembros"] * CUOTA_ESPERADA
resumen_rol["% Recaudado"] = (resumen_rol["Recaudado"] / resumen_rol["Esperado"] * 100).round(1)
import altair as alt
chart_data = resumen_rol.melt(id_vars="Rol", value_vars=["Esperado", "Recaudado"], var_name="Tipo", value_name="Monto")
st.altair_chart(
    alt.Chart(chart_data).mark_bar().encode(
        x=alt.X("Rol:N", title=None),
        y=alt.Y("Monto:Q", title="RD$"),
        color=alt.Color("Tipo:N", scale=alt.Scale(domain=["Esperado", "Recaudado"], range=["#E53E3E", "#38A169"])),
        xOffset="Tipo:N",
        tooltip=["Rol", "Tipo", alt.Tooltip("Monto:Q", format="$,.0f")],
    ).properties(height=350),
    use_container_width=True,
)

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
