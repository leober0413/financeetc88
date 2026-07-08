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
CONCEPTOS_PARTICIPANTE = [
    "Pago de Participacion", "Inscripcion",
    "Abono 1", "Abono 2", "Abono 3",
    "Pago Completo", "Beca/Descuento",
]


@st.cache_resource
def get_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(creds).open_by_key(st.secrets["sheet_id"])


_SHEETS_EPOCH = pd.Timestamp("1899-12-30")

def _serial_to_date(val):
    """Convert Google Sheets date serial (int) to DD/MM/YYYY string."""
    try:
        n = int(val)
        return (_SHEETS_EPOCH + pd.Timedelta(days=n)).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return val


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
    # Convert date serials in Fecha column
    if "Fecha" in df.columns:
        df["Fecha"] = df["Fecha"].apply(
            lambda v: _serial_to_date(v) if str(v).lstrip("-").isdigit() and v != "" else v
        )
    return df


@st.cache_data(ttl=60)
def load_data():
    sh = get_sheet()
    miembros   = _ws_to_df(sh.worksheet("Miembros"))
    pagos      = _ws_to_df(sh.worksheet("Pagos"))
    gastos     = _ws_to_df(sh.worksheet("Gastos"))
    donaciones = _ws_to_df(sh.worksheet("Donaciones"))

    if not miembros.empty and "Nombre" in miembros.columns:
        miembros = miembros[miembros["Nombre"].astype(str).str.strip() != ""]
    if not pagos.empty and "Miembro" in pagos.columns:
        pagos = pagos[pagos["Miembro"].astype(str).str.strip() != ""]
    if not gastos.empty and "Concepto" in gastos.columns:
        gastos = gastos[gastos["Concepto"].astype(str).str.strip() != ""]
    if not donaciones.empty and "Donante" in donaciones.columns:
        donaciones = donaciones[donaciones["Donante"].astype(str).str.strip() != ""]

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
    if "Monto" in donaciones.columns:
        donaciones["Monto"] = pd.to_numeric(donaciones["Monto"], errors="coerce").fillna(0)

    return miembros, pagos, gastos, donaciones


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
    donaciones = pd.DataFrame([
        {"Fecha": "No especificada", "Donante": "Cuenta de Dayrelins", "Monto": 5000, "Nota": "Merienda formacion 3"},
    ])
    return miembros, pagos, gastos, donaciones


@st.cache_data(ttl=60)
def load_participantes():
    sh = get_sheet()
    participantes = _ws_to_df(sh.worksheet("Participantes"))
    pagos_part    = _ws_to_df(sh.worksheet("Pagos Participantes"))

    if not participantes.empty and "Nombre" in participantes.columns:
        participantes = participantes[participantes["Nombre"].astype(str).str.strip() != ""]
    if not pagos_part.empty and "Participante" in pagos_part.columns:
        pagos_part = pagos_part[pagos_part["Participante"].astype(str).str.strip() != ""]

    if "Activo" in pagos_part.columns:
        pagos_part = pagos_part[pagos_part["Activo"].astype(str).str.upper() != "FALSE"]

    if "Total Aportado" in participantes.columns:
        participantes["Total Aportado"] = pd.to_numeric(participantes["Total Aportado"], errors="coerce").fillna(0)
    if "Monto" in pagos_part.columns:
        pagos_part["Monto"] = pd.to_numeric(pagos_part["Monto"], errors="coerce").fillna(0)

    return participantes, pagos_part


def load_demo_participantes():
    participantes = pd.DataFrame(columns=["Nombre", "Telefono", "Total Aportado", "Status"])
    pagos_part    = pd.DataFrame(columns=["Participante", "Concepto", "Monto", "Fecha", "Nota"])
    return participantes, pagos_part


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


def append_donacion(fecha, donante, monto, nota):
    ws = get_sheet().worksheet("Donaciones")
    headers = ws.row_values(1)
    mapping = {"Fecha": str(fecha), "Donante": donante, "Monto": monto, "Nota": nota}
    ws.append_row([mapping.get(h, "") for h in headers], value_input_option="USER_ENTERED")
    load_data.clear()


def append_participante(nombre, telefono):
    ws = get_sheet().worksheet("Participantes")
    # Find next empty row
    col_a = ws.col_values(1)
    next_row = len(col_a) + 1
    r = next_row
    ws.update(
        values=[[
            nombre,
            telefono,
            f"=IF(A{r}=\"\",\"\",SUMIF('Pagos Participantes'!$A$2:$A$500,A{r},'Pagos Participantes'!$C$2:$C$500))",
            f"=IF(A{r}=\"\",\"\",IF(Resumen!$B$4=0,\"Definir cuota\",IF(C{r}>=Resumen!$B$4,\"PAGO COMPLETO\",\"PENDIENTE\")))",
        ]],
        range_name=f"A{r}:D{r}",
        value_input_option="USER_ENTERED",
    )
    load_participantes.clear()


def append_pago_participante(participante, concepto, monto, fecha, nota):
    ws = get_sheet().worksheet("Pagos Participantes")
    headers = ws.row_values(1)
    mapping = {"Participante": participante, "Concepto": concepto,
               "Monto": monto, "Fecha": str(fecha), "Nota": nota, "Activo": "TRUE"}
    ws.append_row([mapping.get(h, "") for h in headers], value_input_option="USER_ENTERED")
    load_participantes.clear()


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
/* ── Sidebar ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background: #0F172A !important;
}
[data-testid="stSidebar"] {
    border-right: 1px solid #1E293B !important;
}
/* Nav links — activo */
[data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebarNavLink"][aria-current="page"] {
    background: #1E3A5F !important;
    color: #60A5FA !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
/* Nav links — inactivos */
[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNavLink"] {
    color: #94A3B8 !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNavLink"]:hover {
    background: #1E293B !important;
    color: #F1F5F9 !important;
}

/* ── Mobile ── */
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
