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

_mask_cuota      = pagos["Concepto"].astype(str).str.startswith("Cuota") if not pagos.empty else pd.Series(dtype=bool)
total_cuotas     = pagos.loc[_mask_cuota,  "Monto"].sum() if not pagos.empty else 0
total_tardanzas  = pagos.loc[~_mask_cuota, "Monto"].sum() if not pagos.empty else 0

total_donaciones = donaciones["Monto"].sum() if not donaciones.empty and "Monto" in donaciones.columns else 0
salidas          = gastos["Monto"].sum() if not gastos.empty and "Monto" in gastos.columns else 0
pendiente        = total_esperado - total_cuotas
pct_recaudado    = int(total_cuotas / total_esperado * 100) if total_esperado > 0 else 0

al_dia     = (miembros["Status"] == "PAGO COMPLETO").sum() if "Status" in miembros.columns else 0
pendientes = total_miembros - al_dia

total_part     = len(participantes)
recaudado_part = pagos_part["Monto"].sum() if not pagos_part.empty and "Monto" in pagos_part.columns else 0
esperado_part  = total_part * cuota_part
pct_part       = int(recaudado_part / esperado_part * 100) if esperado_part > 0 else 0
falta_part     = max(esperado_part - recaudado_part, 0)

entradas = total_cuotas + total_tardanzas + total_donaciones + recaudado_part
balance  = entradas - salidas

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

def kpi_section(title, *cards):
    inner = "".join(f'<div>{c}</div>' for c in cards)
    return f"""
<div style="margin-bottom:18px;">
  <div style="color:#64748B;font-size:0.65rem;font-weight:700;letter-spacing:0.1em;
              text-transform:uppercase;margin-bottom:8px;padding-left:2px;">{title}</div>
  <div class="kpi-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
    {inner}
  </div>
</div>"""

st.markdown(f"""
{kpi_section("📊 Estimado",
    kpi_card("Meta del equipo",        f"${total_esperado:,.0f}",  f"{total_miembros} miembros × RD$2,000",                        "#6366F1"),
    kpi_card("Cuotas recaudadas",      f"${total_cuotas:,.0f}",    f"{pct_recaudado}% de la meta",                                 "#10B981"),
    kpi_card("Pendiente cuotas",       f"${pendiente:,.0f}",       "por cobrar en cuotas",                                         "#EF4444" if pendiente > 0 else "#10B981"),
    kpi_card("Esperado participantes", f"${esperado_part:,.0f}" if cuota_part > 0 else "Cuota por definir",
             f"{total_part} participantes × RD${cuota_part:,}" if cuota_part > 0 else f"{total_part} participantes registrados",   "#8B5CF6"),
)}
{kpi_section("💰 Entradas",
    kpi_card("Cuotas",               f"${total_cuotas:,.0f}",    "pagos de cuota miembros",                                      "#10B981"),
    kpi_card("Tardanzas",            f"${total_tardanzas:,.0f}", "multas cobradas en formaciones",                               "#F97316"),
    kpi_card("Donaciones",           f"${total_donaciones:,.0f}","ingresos externos",                                            "#F59E0B"),
    kpi_card("Pagos participantes",  f"${recaudado_part:,.0f}",  f"{pct_part}% del esperado" if cuota_part > 0 else f"{total_part} participantes", "#A78BFA"),
)}
{kpi_section("📤 Salidas & Balance",
    kpi_card("Salidas",         f"${salidas:,.0f}",   "total de gastos",       "#EF4444"),
    kpi_card("Entradas totales",f"${entradas:,.0f}",  "cuotas + tard. + don. + part.", "#06B6D4"),
    kpi_card("Balance",         f"${balance:,.0f}",   "entradas − salidas",    "#10B981" if balance >= 0 else "#EF4444"),
)}
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
# Barras de progreso
# ------------------------------------------------------------------
pct_bar_color  = "#10B981" if pct_recaudado >= 80 else "#F59E0B" if pct_recaudado >= 50 else "#EF4444"
pct_part_color = "#10B981" if pct_part >= 80 else "#F59E0B" if pct_part >= 50 else "#EF4444"

st.markdown(f"""
<div style="display:flex;flex-direction:column;gap:8px;margin-bottom:4px;">
  <div style="background:#1E293B;border-radius:8px;padding:10px 16px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
          <span style="color:#94A3B8;font-size:0.75rem;font-weight:600;">PROGRESO DE RECAUDO — MIEMBROS</span>
          <span style="color:#F1F5F9;font-size:0.75rem;font-weight:700;">
            {pct_recaudado}% · falta ${pendiente:,.0f} · recaudado ${total_cuotas:,.0f}
          </span>
      </div>
      <div style="background:#334155;border-radius:4px;height:10px;">
          <div style="background:{pct_bar_color};width:{min(pct_recaudado,100)}%;
                      height:10px;border-radius:4px;transition:width 0.3s;"></div>
      </div>
  </div>
  <div style="background:#1E293B;border-radius:8px;padding:10px 16px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
          <span style="color:#94A3B8;font-size:0.75rem;font-weight:600;">PROGRESO DE RECAUDO — PARTICIPANTES</span>
          <span style="color:#F1F5F9;font-size:0.75rem;font-weight:700;">
            {f"{pct_part}% · falta ${falta_part:,.0f}" if cuota_part > 0 else f"${recaudado_part:,.0f} recaudado · cuota por definir"}
          </span>
      </div>
      <div style="background:#334155;border-radius:4px;height:10px;">
          <div style="background:{pct_part_color};width:{min(pct_part,100) if cuota_part > 0 else 0}%;
                      height:10px;border-radius:4px;transition:width 0.3s;"></div>
      </div>
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
