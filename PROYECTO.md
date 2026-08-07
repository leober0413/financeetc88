# Panel de Finanzas — Equipo ETC 88

Dashboard interno de finanzas. Lee datos en vivo desde Google Sheets. Fase 2 de proyecto mayor.

---

## Stack

| Pieza | Detalle |
|---|---|
| App | Streamlit (`app.py`) |
| Datos | Google Sheets vía gspread |
| Auth GCP | Service account (`secrets.toml`) |
| Python | venv en `~/financeEtc88/venv/` |
| Repo | `github.com/leober0413/financeetc88` (privado) |

**Correr local:**
```bash
source venv/bin/activate && streamlit run app.py
```

**Dependencias (`requirements.txt`):**
```
streamlit
gspread
google-auth
pandas
```

---

## Google Sheet

- **ID:** `1i-Z2I173hSeEAt8WTK8rj24pjQSK4P76r8CCsz6sR1k`
- **Service account:** `financeetc88-dashboard@financeetc88.iam.gserviceaccount.com`
- **Credenciales:** `.streamlit/secrets.toml` (excluido del repo)

### Pestañas activas

| Pestaña | Uso | Columnas |
|---|---|---|
| **Miembros** | 54 miembros | Nombre, Rol, Total Aportado (SUMIFS), Status |
| **Pagos** | ~41 registros | Miembro, Concepto, Monto, Fuente, Nota, Activo |
| **Gastos** | Salidas | Fecha, Concepto, Monto, Fuente, Activo |
| **Listas** | OCULTA — alimenta dropdowns | Roles, Conceptos, Fuentes |

### Pestañas históricas (solo referencia, no se usan)
- Tardanzas - Extracurriculares
- Control de Cuotas
- Reporte Salidas

### Reglas de datos
- `CUOTA_ESPERADA = RD$2,000` (hardcoded)
- `Total esperado = 54 × 2000 = RD$108,000`
- Status PAGO COMPLETO → Total Aportado ≥ 2000
- Solo Conceptos que empiezan con "Cuota" cuentan para Status/Total Aportado (no Formaciones)
- Borrado lógico: columna `Activo = FALSE` en Pagos y Gastos
- "Tommy" ≠ "Tomas Lorenzo" (personas distintas, rol: Cocinero)
- "Melkin" = "Merkin Vasquez" (mismo miembro)

### Valores de dropdowns
- **Rol:** Director, Asesor, Guia, Cocinero, Musico
- **Concepto pago:** Cuota 1, Cuota 2, Cuota 3, Cuota 4, Formacion 1, Formacion 2, Formacion 3, Formacion 4
- **Fuente pago:** Control de Cuotas, Tardanzas, Otro

---

## Arquitectura de app.py

### Constantes
```python
CUOTA_ESPERADA = 2000
CONCEPTOS_PAGO = ["Cuota 1"..."Formacion 4"]
FUENTES_PAGO = ["Control de Cuotas", "Tardanzas", "Otro"]
```

### Funciones de conexión

| Función | Qué hace |
|---|---|
| `get_sheet()` | Autentica con gspread, cachea con `@st.cache_resource` |
| `_ws_to_df(ws)` | Lee worksheet → DataFrame, agrega `_row_num` (fila real en Sheet) |
| `load_data()` | Lee Miembros, Pagos, Gastos. Filtra vacíos y `Activo=FALSE`. Convierte numéricos. Cachea 60s con `@st.cache_data(ttl=60)` |
| `load_demo_data()` | Datos hardcoded de muestra si no hay `secrets.toml` |

### Funciones de escritura

| Función | Qué hace |
|---|---|
| `append_pago(miembro, concepto, monto, fuente, nota)` | Agrega fila a hoja Pagos con `Activo=TRUE`, limpia caché |
| `append_gasto(fecha, concepto, monto, fuente)` | Agrega fila a hoja Gastos con `Activo=TRUE`, limpia caché |
| `soft_delete(worksheet_name, row_num)` | Escribe `FALSE` en columna Activo de fila específica, limpia caché |
| `_col_idx(ws, col_name)` | Devuelve índice (1-based) de columna por nombre |

### Modo demo
```python
demo_mode = "gcp_service_account" not in st.secrets
```
Si `True` → usa `load_demo_data()`, deshabilita escritura, muestra banner de advertencia.

---

## UI — Estructura de pantallas

### Header
```
Panel de Finanzas — Equipo ETC 88          [🔄 Refrescar]
Vista interna. Datos en vivo desde Google Sheets.
```
- Columnas `[5, 1]`
- Botón Refrescar llama `load_data.clear()` + `st.rerun()` (solo si no demo)

### Tabs
```
[📊 Dashboard]  [➕ Registrar]
```

---

### Tab Dashboard

#### Filtros
```
[Filtrar por rol ▾]    [Filtrar por status ▾]
```
- `st.columns(2)` — selectbox con opciones dinámicas desde datos reales
- Filtran `miembros_f` (copia local, no afecta Pagos/Gastos)

#### KPIs — `st.columns(5)`
| Métrica | Cálculo |
|---|---|
| Total esperado | `len(miembros) × 2000` |
| Cuotas recaudadas | Suma Monto donde Concepto startswith "Cuota" |
| Pendiente | Total esperado − Cuotas recaudadas |
| Entradas totales | Cuotas + todo lo que NO es Cuota (Formaciones, etc.) |
| Balance | Entradas totales − Gastos |

#### Tabla Miembros
- Columnas: Nombre, Rol, Total Aportado, Status
- Formato moneda: `${:,.0f}`
- Coloreado por Status con `.style.map()`:
  - PAGO COMPLETO → `#DCEFE2` bg / `#1E4A36` text
  - PENDIENTE → `#FBE9E4` bg / `#A34430` text

#### Tabla Pagos + eliminar
- Columnas: Miembro, Concepto, Monto, Fuente, Nota
- Expander "🗑️ Eliminar pago" (solo modo live):
  - Selectbox con label "Miembro — Concepto — $Monto"
  - Botón llama `soft_delete("Pagos", row_num)`

#### Tabla Gastos + eliminar
- Columnas: Fecha, Concepto, Monto, Fuente
- Expander "🗑️ Eliminar gasto" (solo modo live):
  - Selectbox con label "Concepto — $Monto"
  - Botón llama `soft_delete("Gastos", row_num)`

#### Gráfico por Rol
- `st.bar_chart()` con DataFrame agrupado por Rol
- Columnas graficadas: Esperado vs Recaudado
- Cálculo: `Esperado = count(Miembros) × 2000` por rol

---

### Tab Registrar (solo modo live)

Dos columnas iguales:

**Registrar pago** (`st.form("form_pago")`):
| Campo | Widget |
|---|---|
| Miembro | selectbox (nombres únicos de Miembros) |
| Concepto | selectbox (CONCEPTOS_PAGO) |
| Monto (RD$) | number_input, min=0, step=100 |
| Fuente | selectbox (FUENTES_PAGO) |
| Nota | text_input opcional |
| Submit | "Guardar pago" — type primary |

Validación: monto > 0. Llama `append_pago()`, luego `st.rerun()`.

**Registrar gasto** (`st.form("form_gasto")`):
| Campo | Widget |
|---|---|
| Fecha | date_input (default hoy) |
| Concepto | text_input |
| Monto (RD$) | number_input, min=0, step=100 |
| Fuente | text_input (default "Reporte Salidas") |
| Submit | "Guardar gasto" — type primary |

Validación: concepto no vacío y monto > 0. Llama `append_gasto()`, luego `st.rerun()`.

---

## CSS Mobile (inyectado en app.py)

```css
/* ≤768px: KPIs 2 por fila, tablas con scroll */
@media (max-width: 768px) {
    .main .block-container { padding: 1rem 0.75rem 3rem }
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: 0.5rem }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: calc(45% - 0.25rem) }
    [data-testid="stMetricValue"] > div { font-size: 1.2rem }
    [data-testid="stDataFrame"] > div { overflow-x: auto }
    .stButton > button { width: 100% }
}
/* ≤420px: todo apilado */
@media (max-width: 420px) {
    [data-testid="stHorizontalBlock"] > [data-testid="column"] { min-width: 100% }
}
```

---

## Archivos del repo

```
financeetc88/
├── app.py                    # App principal
├── requirements.txt          # 4 dependencias
├── .gitignore                # Excluye venv/, .streamlit/secrets.toml
├── .streamlit/
│   └── secrets.toml          # NO en repo — credenciales GCP + sheet_id
├── CONTEXTO-proyecto-etc88.md
└── PROYECTO.md               # Este documento
```

---

## Deploy (pendiente)

1. **Streamlit Community Cloud** → `share.streamlit.io`
2. Repo: `leober0413/financeetc88`, branch `main`, file `app.py`
3. Secrets → pegar contenido de `.streamlit/secrets.toml`
4. Viewer auth → Settings → Sharing → **Specific people** → emails del equipo

---

## Fase 3 (pendiente decisión directores)

Panel público en Looker Studio — agregados sin nombres individuales. Misma hoja de Sheets como fuente.
