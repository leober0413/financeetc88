import streamlit as st
import pandas as pd
from utils import MOBILE_CSS, load_presupuesto

st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Carga de datos
# ------------------------------------------------------------------
try:
    resumen, cocina_items, musica_items, dir_items, guia_items = load_presupuesto()
except Exception as e:
    st.error(f"Error cargando presupuesto DAC: {e}")
    st.stop()

# ------------------------------------------------------------------
# Encabezado
# ------------------------------------------------------------------
col_title, col_refresh = st.columns([5, 1])
col_title.title("Presupuesto — ETC 88")
col_title.caption("Datos en vivo desde hoja DAC")
if col_refresh.button("🔄 Refrescar", use_container_width=True):
    load_presupuesto.clear()
    st.rerun()

# ------------------------------------------------------------------
# Helpers UI
# ------------------------------------------------------------------
def kpi_card(label, value, sublabel="\u00a0", accent="#3B82F6"):
    return f"""
    <div style="background:#1E293B;border-radius:12px;padding:16px 18px;
                border-left:5px solid {accent};height:110px;
                display:flex;flex-direction:column;justify-content:space-between;">
        <div style="color:#94A3B8;font-size:0.68rem;font-weight:700;
                    letter-spacing:0.09em;text-transform:uppercase;">{label}</div>
        <div style="color:#F1F5F9;font-size:1.45rem;font-weight:700;line-height:1.1;">{value}</div>
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

def progress_bar(label, recaudado, total, color=None):
    pct = int(recaudado / total * 100) if total > 0 else 0
    c = color or ("#10B981" if pct >= 80 else "#F59E0B" if pct >= 50 else "#EF4444")
    ahorro = total - recaudado
    return f"""
<div style="background:#1E293B;border-radius:8px;padding:10px 16px;margin-bottom:8px;">
    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="color:#94A3B8;font-size:0.75rem;font-weight:600;">{label.upper()}</span>
        <span style="color:#F1F5F9;font-size:0.75rem;font-weight:700;">
          {pct}% · real ${recaudado:,.0f} vs ${total:,.0f} presupuestado
          {f" · ahorro ${ahorro:,.0f}" if ahorro > 0 else ""}
        </span>
    </div>
    <div style="background:#334155;border-radius:4px;height:8px;">
        <div style="background:{c};width:{min(pct,100)}%;height:8px;border-radius:4px;transition:width 0.3s;"></div>
    </div>
</div>"""

# ------------------------------------------------------------------
# Totales del resumen general
# ------------------------------------------------------------------
gran_total    = resumen.get("GRAN TOTAL", {})
total_ppto    = gran_total.get("total", 0)
total_real    = gran_total.get("real", 0)
ahorro_total  = total_ppto - total_real

cats = {
    "PPTO Directores": {"label": "Directores", "accent": "#6366F1"},
    "PPTO Cocina":     {"label": "Cocina",      "accent": "#F59E0B"},
    "PPTO Musica":     {"label": "Música",      "accent": "#8B5CF6"},
    "PPTO Guias":      {"label": "Guías",       "accent": "#0EA5E9"},
}

# ------------------------------------------------------------------
# Sección resumen general
# ------------------------------------------------------------------
st.html(kpi_section("📊 Resumen General",
    kpi_card("Gran total presupuestado", f"${total_ppto:,.0f}",  "costo total planificado",  "#6366F1"),
    kpi_card("Costo real",               f"${total_real:,.0f}",  "con donaciones aplicadas", "#10B981"),
    kpi_card("Ahorro por donaciones",    f"${ahorro_total:,.0f}","diferencia ppto vs real",  "#F59E0B"),
))

# ------------------------------------------------------------------
# KPIs por categoría
# ------------------------------------------------------------------
cat_cards = []
for key, meta in cats.items():
    d = resumen.get(key, {"total": 0, "real": 0})
    pct = int(d["real"] / d["total"] * 100) if d["total"] > 0 else 0
    cat_cards.append(kpi_card(
        meta["label"],
        f"${d['real']:,.0f}",
        f"de ${d['total']:,.0f} · {pct}% del ppto",
        meta["accent"],
    ))

st.html(kpi_section("💰 Por Categoría", *cat_cards))

# ------------------------------------------------------------------
# Barras de progreso por categoría
# ------------------------------------------------------------------
for key, meta in cats.items():
    d = resumen.get(key, {"total": 0, "real": 0})
    st.html(progress_bar(meta["label"], d["real"], d["total"], meta["accent"]))
st.html(progress_bar("Gran Total", total_real, total_ppto, "#06B6D4"))

st.divider()

# ------------------------------------------------------------------
# Detalle por categoría
# ------------------------------------------------------------------
st.subheader("Detalle por categoría")

tab_dir, tab_cocina, tab_musica, tab_guias = st.tabs(
    ["🎯 Directores", "🍳 Cocina", "🎵 Música", "📚 Guías"]
)

with tab_dir:
    d = resumen.get("PPTO Directores", {"total": 0, "real": 0})
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuestado", f"${d['total']:,.0f}")
    c2.metric("Costo real", f"${d['real']:,.0f}")
    c3.metric("Ahorro / Donado", f"${d['total'] - d['real']:,.0f}")
    if dir_items:
        df = pd.DataFrame(dir_items)
        df = df[df["Total"] > 0]
        donados = (df["Estado"] == "🎁").sum()
        st.caption(f"{donados} ítems donados")
        st.dataframe(
            df,
            hide_index=True,
            width="stretch",
            height=min(36 * len(df) + 38, 450),
            column_config={
                "Material": st.column_config.TextColumn("Material", width="large"),
                "Total":    st.column_config.NumberColumn("Total RD$", format="$%.0f", width="small"),
                "Estado":   st.column_config.TextColumn("Estado", width="small"),
                "Nota":     st.column_config.TextColumn("Nota", width="large"),
            },
        )

with tab_cocina:
    d = resumen.get("PPTO Cocina", {"total": 0, "real": 0})
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuestado", f"${d['total']:,.0f}")
    c2.metric("Costo real", f"${d['real']:,.0f}")
    c3.metric("Ahorro / Donado", f"${d['total'] - d['real']:,.0f}")
    if cocina_items:
        df = pd.DataFrame(cocina_items)
        df = df[df["Total"] > 0]
        verificados = (df["Verificado"] == "✅").sum()
        donados = (df["Estado"] == "🎁").sum()
        st.caption(f"{verificados} de {len(df)} ítems verificados · {donados} donados")
        st.dataframe(
            df,
            hide_index=True,
            width="stretch",
            height=min(36 * len(df) + 38, 450),
            column_config={
                "Artículo":   st.column_config.TextColumn("Artículo", width="large"),
                "Total":      st.column_config.NumberColumn("Total RD$", format="$%.0f", width="small"),
                "Estado":     st.column_config.TextColumn("Estado", width="small"),
                "Verificado": st.column_config.TextColumn("Verif.", width="small"),
            },
        )

with tab_musica:
    d = resumen.get("PPTO Musica", {"total": 0, "real": 0})
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuestado", f"${d['total']:,.0f}")
    c2.metric("Costo real", f"${d['real']:,.0f}")
    c3.metric("Ahorro / Donado", f"${d['total'] - d['real']:,.0f}")
    if musica_items:
        df = pd.DataFrame(musica_items)
        donados = (df["Estado"] == "🎁").sum()
        st.caption(f"{donados} ítems donados")
        st.dataframe(
            df,
            hide_index=True,
            width="stretch",
            height=min(36 * len(df) + 38, 300),
            column_config={
                "Descripción": st.column_config.TextColumn("Descripción", width="large"),
                "Cantidad":    st.column_config.TextColumn("Cant.", width="small"),
                "Total":       st.column_config.NumberColumn("Total RD$", format="$%.0f", width="small"),
                "Estado":      st.column_config.TextColumn("Estado", width="small"),
            },
        )

with tab_guias:
    d = resumen.get("PPTO Guias", {"total": 0, "real": 0})
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuestado", f"${d['total']:,.0f}")
    c2.metric("Costo real", f"${d['real']:,.0f}")
    c3.metric("Ahorro / Donado", f"${d['total'] - d['real']:,.0f}")
    if guia_items:
        df = pd.DataFrame(guia_items)
        df = df[df["Total"] > 0]
        donados = (df["Estado"] == "🎁").sum()
        st.caption(f"{donados} ítems donados")
        st.dataframe(
            df,
            hide_index=True,
            width="stretch",
            height=min(36 * len(df) + 38, 450),
            column_config={
                "Material": st.column_config.TextColumn("Material", width="large"),
                "Total":    st.column_config.NumberColumn("Total RD$", format="$%.0f", width="small"),
                "Estado":   st.column_config.TextColumn("Estado", width="small"),
                "Nota":     st.column_config.TextColumn("Nota", width="large"),
            },
        )
