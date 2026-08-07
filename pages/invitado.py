import streamlit as st
import pandas as pd
import altair as alt
from utils import CUOTA_ESPERADA, MOBILE_CSS, load_data, load_demo_data, load_participantes, load_demo_participantes, load_cuota_participante

st.markdown(MOBILE_CSS, unsafe_allow_html=True)

demo_mode = "gcp_service_account" not in st.secrets

if demo_mode:
    miembros, pagos, gastos, donaciones = load_demo_data()
    participantes, pagos_part = load_demo_participantes()
    cuota_part = 0
else:
    miembros, pagos, gastos, donaciones = load_data()
    participantes, pagos_part = load_participantes()
    cuota_part = load_cuota_participante()

# ------------------------------------------------------------------
# Encabezado
# ------------------------------------------------------------------
st.title("ETC 88 — Progreso de Recaudo")
st.caption("Vista pública · datos en vivo")

# ------------------------------------------------------------------
# Cálculos
# ------------------------------------------------------------------
total_miembros   = len(miembros)
total_esperado   = total_miembros * CUOTA_ESPERADA
total_cuotas     = pagos.loc[pagos["Concepto"].astype(str).str.startswith("Cuota"), "Monto"].sum() if not pagos.empty else 0
total_tardanzas  = pagos.loc[~pagos["Concepto"].astype(str).str.startswith("Cuota"), "Monto"].sum() if not pagos.empty else 0
total_donaciones = donaciones["Monto"].sum() if not donaciones.empty and "Monto" in donaciones.columns else 0
entradas         = total_cuotas + total_tardanzas + total_donaciones
salidas          = gastos["Monto"].sum() if not gastos.empty and "Monto" in gastos.columns else 0
balance          = entradas - salidas
pct_recaudado    = int(total_cuotas / total_esperado * 100) if total_esperado > 0 else 0

al_dia    = (miembros["Status"] == "PAGO COMPLETO").sum() if "Status" in miembros.columns else 0
pendientes = total_miembros - al_dia

total_part          = len(participantes)
recaudado_part      = pagos_part["Monto"].sum() if not pagos_part.empty and "Monto" in pagos_part.columns else 0
esperado_part       = total_part * cuota_part
pct_part            = int(recaudado_part / esperado_part * 100) if esperado_part > 0 else 0
esperado_part_label = f"${esperado_part:,.0f} ({total_part} × RD${cuota_part:,})" if cuota_part > 0 else f"{total_part} participantes · cuota por definir"

# ------------------------------------------------------------------
# KPIs
# ------------------------------------------------------------------
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

cards_html = "".join([
    f'<div>{kpi_card("Meta del equipo",         f"${total_esperado:,.0f}",    f"{total_miembros} miembros × RD$2,000", "#6366F1")}</div>',
    f'<div>{kpi_card("Cuotas recaudadas",       f"${total_cuotas:,.0f}",      f"{pct_recaudado}% de la meta",          "#10B981")}</div>',
    f'<div>{kpi_card("Donaciones",              f"${total_donaciones:,.0f}",  "ingresos externos",                     "#F59E0B")}</div>',
    f'<div>{kpi_card("Entradas totales",        f"${entradas:,.0f}",          "cuotas + otros + donaciones",           "#06B6D4")}</div>',
    f'<div>{kpi_card("Gastos",                  f"${salidas:,.0f}",           "salidas registradas",                   "#EF4444")}</div>',
    f'<div>{kpi_card("Balance",                 f"${balance:,.0f}",           "entradas − gastos",                     "#10B981" if balance >= 0 else "#EF4444")}</div>',
    f'<div>{kpi_card("Esperado participantes",  esperado_part_label if cuota_part == 0 else f"${esperado_part:,.0f}", esperado_part_label if cuota_part > 0 else "\u00a0", "#8B5CF6")}</div>',
    f'<div>{kpi_card("Recaudado participantes", f"${recaudado_part:,.0f}",    f"{pct_part}% del esperado" if cuota_part > 0 else f"{total_part} participantes", "#A78BFA")}</div>',
])

st.markdown(f"""
<div class="kpi-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
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

# ------------------------------------------------------------------
# Barra de progreso
# ------------------------------------------------------------------
pct_bar_color = "#10B981" if pct_recaudado >= 80 else "#F59E0B" if pct_recaudado >= 50 else "#EF4444"
st.markdown(f"""
<div style="background:#1E293B;border-radius:8px;padding:10px 16px;margin-bottom:4px;">
    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="color:#94A3B8;font-size:0.75rem;font-weight:600;">PROGRESO DE RECAUDO</span>
        <span style="color:#F1F5F9;font-size:0.75rem;font-weight:700;">{pct_recaudado}%</span>
    </div>
    <div style="background:#334155;border-radius:4px;height:10px;">
        <div style="background:{pct_bar_color};width:{min(pct_recaudado,100)}%;
                    height:10px;border-radius:4px;transition:width 0.3s;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Miembros al día vs pendientes
# ------------------------------------------------------------------
st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
c1.metric("Miembros al día ✅", al_dia, delta=None)
c2.metric("Pendientes ⏳", pendientes, delta=None)

st.divider()

# ------------------------------------------------------------------
# Gráfico por rol
# ------------------------------------------------------------------
st.subheader("Recaudo por rol")

if not miembros.empty and "Rol" in miembros.columns and "Total Aportado" in miembros.columns:
    resumen_rol = (
        miembros.groupby("Rol")
        .agg(Miembros=("Nombre", "count"), Recaudado=("Total Aportado", "sum"))
        .reset_index()
    )
    resumen_rol["Esperado"] = resumen_rol["Miembros"] * CUOTA_ESPERADA
    chart_data = resumen_rol.melt(
        id_vars="Rol",
        value_vars=["Esperado", "Recaudado"],
        var_name="Tipo",
        value_name="Monto",
    )
    st.altair_chart(
        alt.Chart(chart_data).mark_bar().encode(
            x=alt.X("Rol:N", title=None),
            y=alt.Y("Monto:Q", title="RD$"),
            color=alt.Color(
                "Tipo:N",
                scale=alt.Scale(domain=["Esperado", "Recaudado"], range=["#E53E3E", "#38A169"]),
            ),
            xOffset="Tipo:N",
            tooltip=["Rol", "Tipo", alt.Tooltip("Monto:Q", format="$,.0f")],
        ).properties(height=320),
        width="stretch",
    )
else:
    st.info("Sin datos de roles disponibles.")
