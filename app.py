import streamlit as st
from utils import (
    CUOTA_ESPERADA, MOBILE_CSS,
    load_data, load_demo_data, soft_delete,
)

st.set_page_config(page_title="ETC 88 · Dashboard", layout="wide")
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

# ------------------------------------------------------------------
# Tabla gastos + eliminar
# ------------------------------------------------------------------
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
st.bar_chart(resumen_rol.set_index("Rol")[["Esperado", "Recaudado"]])

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
