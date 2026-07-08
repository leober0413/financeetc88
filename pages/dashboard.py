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
    miembros, pagos, gastos, donaciones = load_demo_data()
else:
    miembros, pagos, gastos, donaciones = load_data()

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
total_miembros   = len(miembros)
total_esperado   = total_miembros * CUOTA_ESPERADA
total_cuotas     = pagos.loc[pagos["Concepto"].astype(str).str.startswith("Cuota"), "Monto"].sum()
pendiente        = total_esperado - total_cuotas
total_tardanzas  = pagos.loc[~pagos["Concepto"].astype(str).str.startswith("Cuota"), "Monto"].sum()
total_donaciones = donaciones["Monto"].sum() if not donaciones.empty and "Monto" in donaciones.columns else 0
entradas         = total_cuotas + total_tardanzas + total_donaciones
salidas          = gastos["Monto"].sum()
balance          = entradas - salidas

pct_recaudado = int(total_cuotas / total_esperado * 100) if total_esperado > 0 else 0

def kpi_card(label, value, sublabel="\u00a0", accent="#3B82F6"):
    return f"""
    <div style="background:#1E293B;border-radius:12px;padding:16px 18px;
                border-left:5px solid {accent};height:110px;
                display:flex;flex-direction:column;justify-content:space-between;">
        <div style="color:#94A3B8;font-size:0.68rem;font-weight:700;
                    letter-spacing:0.09em;text-transform:uppercase;">
            {label}
        </div>
        <div style="color:#F1F5F9;font-size:1.45rem;font-weight:700;line-height:1.1;">
            {value}
        </div>
        <div style="color:#64748B;font-size:0.68rem;">{sublabel}</div>
    </div>"""

def kpi_grid(*cards):
    inner = "".join(f'<div>{c}</div>' for c in cards)
    return f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
        {inner}
    </div>
    <style>
    @media(max-width:640px){{
        div[data-kpi-grid] > div,
        .kpi-responsive-grid > div {{
            grid-template-columns: repeat(2,1fr) !important;
        }}
    }}
    </style>
    """

cards_html = "".join([
    f'<div>{kpi_card("Total esperado",    f"${total_esperado:,.0f}", f"{total_miembros} miembros × RD$2,000", "#6366F1")}</div>',
    f'<div>{kpi_card("Cuotas recaudadas", f"${total_cuotas:,.0f}",   f"{pct_recaudado}% del total esperado",  "#10B981")}</div>',
    f'<div>{kpi_card("Pendiente",         f"${pendiente:,.0f}",       "por cobrar en cuotas",                  "#EF4444" if pendiente > 0 else "#10B981")}</div>',
    f'<div>{kpi_card("Donaciones",        f"${total_donaciones:,.0f}","ingresos externos",                     "#F59E0B")}</div>',
    f'<div>{kpi_card("Entradas totales",  f"${entradas:,.0f}",        "cuotas + otros + donaciones",           "#06B6D4")}</div>',
    f'<div>{kpi_card("Balance",           f"${balance:,.0f}",         "entradas − salidas",                    "#10B981" if balance >= 0 else "#EF4444")}</div>',
])
st.markdown(f"""
<div class="kpi-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
{cards_html}
</div>
<style>
@media(max-width:640px){{
  .kpi-grid {{ grid-template-columns: repeat(2,1fr) !important; gap:8px !important; }}
  .kpi-grid > div > div {{ height:95px !important; padding:12px 14px !important; }}
  .kpi-grid > div > div > div:nth-child(2) {{ font-size:1.15rem !important; }}
}}
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
pct_bar_color = "#10B981" if pct_recaudado >= 80 else "#F59E0B" if pct_recaudado >= 50 else "#EF4444"
st.markdown(f"""
<div style="background:#1E293B;border-radius:8px;padding:10px 16px;margin-bottom:4px;">
    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="color:#94A3B8;font-size:0.75rem;font-weight:600;">PROGRESO DE RECAUDO</span>
        <span style="color:#F1F5F9;font-size:0.75rem;font-weight:700;">{pct_recaudado}%</span>
    </div>
    <div style="background:#334155;border-radius:4px;height:8px;">
        <div style="background:{pct_bar_color};width:{min(pct_recaudado,100)}%;
                    height:8px;border-radius:4px;transition:width 0.3s;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ------------------------------------------------------------------
# Tabla miembros
# ------------------------------------------------------------------
st.subheader(f"Miembros ({len(miembros_f)} de {total_miembros})")

cols_miembros = [c for c in ["Nombre", "Rol", "Total Aportado", "Status"] if c in miembros_f.columns]
miembros_display = miembros_f[cols_miembros].copy()
if "Status" in miembros_display.columns:
    miembros_display["Status"] = miembros_display["Status"].map(
        lambda v: "✅ Pago completo" if v == "PAGO COMPLETO" else ("⏳ Pendiente" if v == "PENDIENTE" else v)
    )

st.dataframe(
    miembros_display,
    use_container_width=True,
    hide_index=True,
    height=min(36 * len(miembros_display) + 38, 480),
    column_config={
        "Nombre":        st.column_config.TextColumn("Miembro",       width="large"),
        "Rol":           st.column_config.TextColumn("Rol",           width="small"),
        "Total Aportado": st.column_config.ProgressColumn(
            "Aportado", format="$%.0f", min_value=0, max_value=CUOTA_ESPERADA, width="medium"
        ),
        "Status":        st.column_config.TextColumn("Estado",        width="medium"),
    },
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
    pagos_f[cols_pagos],
    use_container_width=True,
    hide_index=True,
    height=min(36 * len(pagos_f) + 38, 400),
    column_config={
        "Miembro":  st.column_config.TextColumn("Miembro",   width="large"),
        "Concepto": st.column_config.TextColumn("Concepto",  width="medium"),
        "Monto":    st.column_config.NumberColumn("Monto",   format="$%.0f", width="small"),
        "Fuente":   st.column_config.TextColumn("Fuente",    width="medium"),
        "Nota":     st.column_config.TextColumn("Nota",      width="medium"),
    },
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
    gastos_f[cols_gastos],
    use_container_width=True,
    hide_index=True,
    height=min(36 * len(gastos_f) + 38, 400),
    column_config={
        "Fecha":    st.column_config.TextColumn("Fecha",    width="small"),
        "Concepto": st.column_config.TextColumn("Concepto", width="large"),
        "Monto":    st.column_config.NumberColumn("Monto",  format="$%.0f", width="small"),
        "Fuente":   st.column_config.TextColumn("Fuente",   width="medium"),
    },
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
# Tabla donaciones
# ------------------------------------------------------------------
st.subheader("Donaciones")
if donaciones.empty:
    st.info("No hay donaciones registradas.")
else:
    cols_don = [c for c in ["Fecha", "Donante", "Monto", "Nota"] if c in donaciones.columns]
    st.dataframe(
        donaciones[cols_don],
        use_container_width=True,
        hide_index=True,
        height=min(36 * len(donaciones) + 38, 300),
        column_config={
            "Fecha":   st.column_config.TextColumn("Fecha",   width="small"),
            "Donante": st.column_config.TextColumn("Donante", width="large"),
            "Monto":   st.column_config.NumberColumn("Monto", format="$%.0f", width="small"),
            "Nota":    st.column_config.TextColumn("Nota",    width="large"),
        },
    )

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
