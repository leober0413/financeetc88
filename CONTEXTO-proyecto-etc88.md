# Contexto del proyecto — Panel de Finanzas ETC 88

## Qué es esto
Dashboard interno de finanzas para el equipo ETC 88, construido con Streamlit, que lee datos en vivo desde un Google Sheet. Es la Fase 2 de un proyecto más grande (dos dashboards: uno interno de finanzas y uno público de transparencia, ambos sobre la misma hoja de Google Sheets como base de datos activa).

## Ubicación local
Carpeta: `~/financeEtc88/`
- `app.py` — la app de Streamlit
- `requirements.txt` — dependencias (streamlit, gspread, google-auth, pandas)
- `venv/` — entorno virtual ya creado y activado
- `.streamlit/secrets.toml` — credenciales de la cuenta de servicio de Google (YA CONFIGURADO Y FUNCIONANDO — no compartir su contenido)

Comando para correr: `source venv/bin/activate && streamlit run app.py`

## Google Sheet (fuente de datos)
- ID del sheet: `1i-Z2I173hSeEAt8WTK8rj24pjQSK4P76r8CCsz6sR1k`
- Compartido con la cuenta de servicio: `financeetc88-dashboard@financeetc88.iam.gserviceaccount.com` (permiso lector)
- Convertido desde un Excel original (`Desarrollo-Registrodepagoetc.xlsx`) que trackeaba cuotas de un equipo/retiro

### Pestañas del Sheet
1. **Tardanzas - Extracurriculares**, **Control de Cuotas**, **Reporte Salidas** — las 3 hojas ORIGINALES, se conservan intactas solo como referencia histórica para que el equipo no se sienta perdido. Ya NO se usan como fuente de datos activa.
2. **Resumen** — KPIs calculados con fórmulas (Total esperado, Cuotas recaudadas, Pendiente, Entradas, Salidas, Balance)
3. **Miembros** — columnas: `Nombre`, `Rol` (dropdown: Director/Asesor/Guia/Cocinero/Musico), `Total Aportado` (fórmula SUMIFS desde Pagos), `Status` (fórmula: PAGO COMPLETO si Total Aportado >= 2000, si no PENDIENTE). 54 miembros. Formato con validación de datos hasta la fila 150 para futuros registros.
4. **Pagos** — columnas: `Miembro`, `Concepto` (dropdown: Cuota 1-4, Formacion 1-4), `Monto`, `Fuente` (dropdown: Control de Cuotas/Tardanzas/Otro), `Nota`. ~41 registros.
5. **Gastos** — columnas: `Fecha`, `Concepto`, `Monto`, `Fuente`. Pre-formateado (moneda) hasta fila 150.
6. **Listas** — pestaña OCULTA que alimenta los dropdowns (columnas Roles, Conceptos, Fuentes). Si Sheets la muestra al abrir el archivo, hay que re-ocultarla manualmente (clic derecho en la pestaña → Ocultar hoja).

### Datos / decisiones tomadas
- Cuota esperada por miembro: RD$2,000 (hardcoded en `app.py` como `CUOTA_ESPERADA`)
- Total esperado actual: RD$108,000 (54 miembros × 2000)
- "Tommy" es una persona distinta de "Tomas Lorenzo" (confirmado por el usuario) — rol: Cocinero
- "Melkin" en la hoja original de Tardanzas se confirmó que es la misma persona que "Merkin Vasquez"
- El Status y Total Aportado en Miembros solo cuentan pagos cuyo Concepto empieza con "Cuota" (no cuenta Formaciones/Tardanzas) — así funcionaba en la hoja original

## Arquitectura de app.py
- `get_client()` — autentica con gspread usando `st.secrets["gcp_service_account"]`, cacheado con `@st.cache_resource`
- `load_data()` — lee las 3 hojas (Miembros, Pagos, Gastos) con `sheet.worksheet(nombre).get_all_records()`, cacheado 60s con `@st.cache_data(ttl=60)`. Filtra filas vacías (nombre/miembro/concepto en blanco) y convierte columnas numéricas con `pd.to_numeric(..., errors="coerce").fillna(0)`
- `load_demo_data()` — datos de muestra hardcoded, se usan si no hay `st.secrets["gcp_service_account"]` configurado (modo demo)
- Filtros por Rol y Status en la barra lateral/columnas superiores
- KPIs con `st.metric`, tabla de miembros con status coloreado (`st.dataframe(...).style.map(...)`), gráfico de barras de progreso por rol, tabla de gastos

## Problema actual
> (completar con el detalle exacto del error/síntoma)

## Próximos pasos pendientes (después de resolver esto)
- Fase 3: Panel Público en Looker Studio (agregados sin nombres individuales — pendiente decisión de directores sobre si mostrar nombres o no)
- Desplegar el panel interno en Streamlit Community Cloud (repo en GitHub, secrets configurados ahí, sin subir `secrets.toml` al repo)
