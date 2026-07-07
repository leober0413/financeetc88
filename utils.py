import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CUOTA_ESPERADA = 2000
CONCEPTOS_PAGO = [
    "Cuota 1", "Cuota 2", "Cuota 3", "Cuota 4",
    "Formacion 1", "Formacion 2", "Formacion 3", "Formacion 4",
]
FUENTES_PAGO = ["Control de Cuotas", "Tardanzas", "Otro"]


@st.cache_resource
def get_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(creds).open_by_key(st.secrets["sheet_id"])


def _ws_to_df(ws):
    vals = ws.get_all_values(value_render_option="UNFORMATTED_VALUE")
    if not vals:
        return pd.DataFrame()
    if len(vals) < 2:
        return pd.DataFrame(columns=vals[0])
    headers = vals[0]
    rows = vals[1:]
    df = pd.DataFrame(rows, columns=headers)
    df["_row_num"] = range(2, len(rows) + 2)
    return df


@st.cache_data(ttl=60)
def load_data():
    sh = get_sheet()
    miembros = _ws_to_df(sh.worksheet("Miembros"))
    pagos    = _ws_to_df(sh.worksheet("Pagos"))
    gastos   = _ws_to_df(sh.worksheet("Gastos"))

    if not miembros.empty and "Nombre" in miembros.columns:
        miembros = miembros[miembros["Nombre"].astype(str).str.strip() != ""]
    if not pagos.empty and "Miembro" in pagos.columns:
        pagos = pagos[pagos["Miembro"].astype(str).str.strip() != ""]
    if not gastos.empty and "Concepto" in gastos.columns:
        gastos = gastos[gastos["Concepto"].astype(str).str.strip() != ""]

    if "Activo" in pagos.columns:
        pagos = pagos[pagos["Activo"].astype(str).str.upper() != "FALSE"]
    if "Activo" in gastos.columns:
        gastos = gastos[gastos["Activo"].astype(str).str.upper() != "FALSE"]

    if "Total Aportado" in miembros.columns:
        miembros["Total Aportado"] = pd.to_numeric(miembros["Total Aportado"], errors="coerce").fillna(0)
    if "Monto" in pagos.columns:
        pagos["Monto"] = pd.to_numeric(pagos["Monto"], errors="coerce").fillna(0)
    if "Monto" in gastos.columns:
        gastos["Monto"] = pd.to_numeric(gastos["Monto"], errors="coerce").fillna(0)

    return miembros, pagos, gastos


def load_demo_data():
    miembros = pd.DataFrame([
        {"Nombre": "Juan Manuel De La Cruz", "Rol": "Director", "Total Aportado": 2000, "Status": "PAGO COMPLETO"},
        {"Nombre": "Jean Carlos De La Cruz", "Rol": "Director", "Total Aportado": 0,    "Status": "PENDIENTE"},
        {"Nombre": "Laura Fernandez",        "Rol": "Asesor",   "Total Aportado": 1000, "Status": "PENDIENTE"},
        {"Nombre": "Fernando Cordero",       "Rol": "Guia",     "Total Aportado": 2000, "Status": "PAGO COMPLETO"},
        {"Nombre": "Paloma Mendez",          "Rol": "Cocinero", "Total Aportado": 500,  "Status": "PENDIENTE"},
        {"Nombre": "Tommy",                  "Rol": "Cocinero", "Total Aportado": 0,    "Status": "PENDIENTE"},
    ])
    pagos = pd.DataFrame([
        {"Miembro": "Juan Manuel De La Cruz", "Concepto": "Cuota 1",     "Monto": 2000, "Fuente": "Control de Cuotas", "Nota": ""},
        {"Miembro": "Fernando Cordero",       "Concepto": "Cuota 1",     "Monto": 2000, "Fuente": "Control de Cuotas", "Nota": ""},
        {"Miembro": "Laura Fernandez",        "Concepto": "Cuota 1",     "Monto": 1000, "Fuente": "Control de Cuotas", "Nota": ""},
        {"Miembro": "Paloma Mendez",          "Concepto": "Cuota 1",     "Monto": 500,  "Fuente": "Control de Cuotas", "Nota": ""},
        {"Miembro": "Tommy",                  "Concepto": "Formacion 1", "Monto": 100,  "Fuente": "Tardanzas",         "Nota": ""},
    ])
    gastos = pd.DataFrame([
        {"Fecha": "No especificada", "Concepto": "Merienda formacion 3", "Monto": 2500, "Fuente": "Reporte Salidas"},
    ])
    return miembros, pagos, gastos


def _col_idx(ws, col_name):
    headers = ws.row_values(1)
    return headers.index(col_name) + 1 if col_name in headers else None


def append_pago(miembro, concepto, monto, fuente, nota):
    ws = get_sheet().worksheet("Pagos")
    headers = ws.row_values(1)
    mapping = {"Miembro": miembro, "Concepto": concepto, "Monto": monto,
               "Fuente": fuente, "Nota": nota, "Activo": "TRUE"}
    ws.append_row([mapping.get(h, "") for h in headers], value_input_option="USER_ENTERED")
    load_data.clear()


def append_gasto(fecha, concepto, monto, fuente):
    ws = get_sheet().worksheet("Gastos")
    headers = ws.row_values(1)
    mapping = {"Fecha": str(fecha), "Concepto": concepto,
               "Monto": monto, "Fuente": fuente, "Activo": "TRUE"}
    ws.append_row([mapping.get(h, "") for h in headers], value_input_option="USER_ENTERED")
    load_data.clear()


def soft_delete(worksheet_name, row_num):
    ws = get_sheet().worksheet(worksheet_name)
    idx = _col_idx(ws, "Activo")
    if idx is None:
        return False, "Columna 'Activo' no existe. Agrégala al Sheet primero."
    ws.update_cell(row_num, idx, "FALSE")
    load_data.clear()
    return True, ""


MOBILE_CSS = """
<style>
@media (max-width: 768px) {
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 0.5rem !important; }
  [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: calc(45% - 0.25rem) !important; flex: 1 1 calc(45% - 0.25rem) !important; }
  [data-testid="stMetricValue"] > div { font-size: 1.1rem !important; }
  [data-testid="stDataFrame"] > div { overflow-x: auto !important; }
  .stButton > button { width: 100% !important; }
}
@media (max-width: 420px) {
  [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
}
</style>
"""
