import streamlit as st
import pandas as pd
from datetime import date
try:
    from utils import MOBILE_CSS, load_fondo, append_fondo, soft_delete
except Exception as _e:
    import traceback
    st.error(f"Import error: {_e}")
    st.code(traceback.format_exc())
    st.stop()

st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Carga
# ------------------------------------------------------------------
try:
    df = load_fondo()
except Exception as e:
    st.error(f"Error cargando Profondo: {e}")
    st.stop()

# ------------------------------------------------------------------
# Encabezado
# ------------------------------------------------------------------
col_title, col_refresh = st.columns([5, 1])
col_title.title("Profondo")
col_title.caption("Entradas y salidas del fondo")
if col_refresh.button("🔄 Refrescar", use_container_width=True):
    load_fondo.clear()
    st.rerun()

# ------------------------------------------------------------------
# KPIs
# ------------------------------------------------------------------
entradas = df.loc[df["Tipo"] == "Entrada", "Monto"].sum() if not df.empty else 0
salidas  = df.loc[df["Tipo"] == "Salida",  "Monto"].sum() if not df.empty else 0
balance  = entradas - salidas

def kpi_card(label, value, accent="#3B82F6"):
    return f"""
    <div style="background:#1E293B;border-radius:12px;padding:16px 18px;
                border-left:5px solid {accent};height:90px;
                display:flex;flex-direction:column;justify-content:space-between;">
        <div style="color:#94A3B8;font-size:0.68rem;font-weight:700;
                    letter-spacing:0.09em;text-transform:uppercase;">{label}</div>
        <div style="color:#F1F5F9;font-size:1.45rem;font-weight:700;line-height:1.1;">{value}</div>
    </div>"""

st.html(f"""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:20px;">
  <div>{kpi_card("Entradas", f"${entradas:,.0f}", "#10B981")}</div>
  <div>{kpi_card("Salidas",  f"${salidas:,.0f}",  "#EF4444")}</div>
  <div>{kpi_card("Balance",  f"${balance:,.0f}",  "#10B981" if balance >= 0 else "#EF4444")}</div>
</div>
""")

st.divider()

# ------------------------------------------------------------------
# Registrar entrada/salida
# ------------------------------------------------------------------
with st.expander("➕ Registrar movimiento", expanded=False):
    with st.form("form_fondo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        fecha   = c1.date_input("Fecha", value=date.today())
        tipo    = c2.selectbox("Tipo", ["Entrada", "Salida"])
        concepto = st.text_input("Concepto")
        c3, c4 = st.columns(2)
        monto   = c3.number_input("Monto (RD$)", min_value=0.0, step=100.0)
        nota    = c4.text_input("Nota (opcional)")
        submitted = st.form_submit_button("Guardar", use_container_width=True, type="primary")
        if submitted:
            if not concepto.strip():
                st.error("Concepto requerido.")
            elif monto <= 0:
                st.error("Monto debe ser mayor a 0.")
            else:
                append_fondo(fecha.strftime("%d/%m/%Y"), tipo, concepto.strip(), monto, nota.strip())
                st.success("Movimiento registrado.")
                st.rerun()

# ------------------------------------------------------------------
# Tabla
# ------------------------------------------------------------------
st.subheader("Movimientos")

if df.empty:
    st.info("Sin movimientos registrados.")
else:
    display_cols = [c for c in ["Fecha", "Tipo", "Concepto", "Monto", "Nota"] if c in df.columns]
    st.dataframe(
        df[display_cols],
        hide_index=True,
        use_container_width=True,
        height=min(36 * len(df) + 38, 500),
        column_config={
            "Monto": st.column_config.NumberColumn("Monto RD$", format="$%.0f"),
            "Tipo":  st.column_config.TextColumn("Tipo"),
        },
    )

    # ------------------------------------------------------------------
    # Eliminar
    # ------------------------------------------------------------------
    with st.expander("🗑️ Eliminar movimiento"):
        opciones = [
            f"Fila {row['_row_num']} — {row.get('Fecha','')} — {row.get('Concepto','')} — ${row.get('Monto',0):,.0f}"
            for _, row in df.iterrows()
        ]
        sel = st.selectbox("Seleccionar", opciones)
        if st.button("Eliminar", type="primary"):
            fila = int(sel.split("—")[0].replace("Fila", "").strip())
            ok, err = soft_delete("Profondo", fila)
            if ok:
                load_fondo.clear()
                st.success("Eliminado.")
                st.rerun()
            else:
                st.error(err)
