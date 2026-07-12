# Contexto del proyecto — Panel de Finanzas ETC 88 (actualizado)

## Qué es esto
Dashboard interno de finanzas para el equipo ETC 88, construido con Streamlit, que lee datos en vivo desde un Google Sheet. Es la Fase 2 de un proyecto más grande (dos dashboards: uno interno de finanzas y uno público de transparencia, ambos sobre la misma hoja de Google Sheets como base de datos activa).

## Ubicación local
Carpeta: `~/financeEtc88/`
- `app.py` — la app de Streamlit (YA FUNCIONANDO, corre localmente sin errores)
- `requirements.txt`
- `venv/`
- `.streamlit/secrets.toml` — credenciales de la cuenta de servicio de Google (configurado y funcionando — NO compartir su contenido)

Comando para correr: `source venv/bin/activate && streamlit run app.py`

## IMPORTANTE: cambio de fuente de datos
El proyecto empezó probándose sobre una **copia** del Google Sheet. Esa etapa ya se superó: ahora se está trabajando directamente sobre la **hoja oficial** del equipo (la que todos usan). La hoja oficial tenía datos reales que la copia no tenía (pagos nuevos, un miembro reemplazado, formaciones nuevas) — todo eso ya se reconstruyó y está reflejado en las pestañas nuevas.

**Pendiente de verificar:** si el `sheet_id` en `secrets.toml` ya apunta al ID de la hoja oficial (no al de la copia de pruebas). Si no, hay que actualizarlo.

## Estructura actual del Google Sheet (hoja oficial)

### Pestañas originales (solo lectura histórica, ya no se editan)
- Tardanzas - Extracurriculares
- Control de Cuotas
- Reporte Salidas

### Pestañas nuevas (fuente de datos activa)
1. **Resumen** — KPIs con fórmulas. Layout de filas (columna A = Indicador, columna B = Valor):
   - B2: Total miembros
   - B3: Cuota individual esperada (2000, fijo)
   - B4: Cuota participante esperada — **quedó en 0, hay que definirla con el equipo** (celda editable, resaltada)
   - B5: Total esperado (equipo)
   - B6: Total cuotas recaudadas
   - B7: Pendiente por cobrar (cuotas equipo)
   - B8: Total tardanzas/formaciones recaudado
   - B9: Total participantes registrados
   - B10: Total esperado participantes
   - B11: Total recaudado participantes
   - B12: Pendiente por cobrar (participantes)
   - B13: Total donaciones
   - B14: Entradas totales (= cuotas + tardanzas + recaudado participantes + donaciones)
   - B15: Salidas (gastos)
   - B16: Balance

2. **Listas** — pestaña OCULTA, alimenta todos los desplegables:
   - Columna A: Roles (Director, Asesor, Guia, Cocinero, Musico)
   - Columna B: Conceptos de cuota/formación (Cuota 1-4, Formacion 1-4)
   - Columna C: Fuentes (Control de Cuotas, Tardanzas, Otro)
   - Columna D: Conceptos de participante (Pago de Participacion, Inscripcion, Abono 1-3, Pago Completo, Beca/Descuento)

3. **Miembros** — Nombre, Rol (dropdown), Total Aportado (fórmula, solo cuenta Concepto="Cuota*"), Status. 54 miembros (incluye "Tommy", que es distinto de "Tomas Lorenzo" — confirmado por el usuario). "Cristopher Jimenez" reemplazó a "Randol Joseph" (confirmado: Randol salió del equipo).

4. **Pagos** — Miembro, Concepto (dropdown), Monto, Fuente (dropdown), Nota. ~47 registros (cuotas + formaciones 1, 2 y 3).

5. **Gastos** — Fecha, Concepto, Monto, Fuente. 1 registro ($2,500 merienda formación 3).

6. **Participantes** — Nombre, Telefono, Total Aportado (fórmula), Status. Tabla NUEVA para asistentes al retiro (distintos de los miembros del equipo). Actualmente vacía — falta que el equipo empiece a registrar participantes.

7. **Pagos Participantes** — Participante (dropdown, source: Participantes!A2:A200), Concepto (dropdown, source: Listas!D2:D8), Monto, Fecha, Nota. Vacía por ahora.

8. **Donaciones** — Fecha, Donante, Monto, Nota. Ya tiene 1 registro: $5,000, Donante "Cuenta de Dayrelins", Nota "Merienda formacion 3" (este dinero antes vivía en una pestaña "Otros Ingresos" que se eliminó — se decidió que todo ingreso no ligado a una cuota individual va aquí, en Donaciones).

### Cambios recientes importantes (por si Claude Code necesita el porqué)
- Se eliminó la pestaña "Otros Ingresos" — todo lo que no es cuota de miembro ni pago de participante ahora se registra en Donaciones.
- Se corrigió un bug de referencia circular en las fórmulas de Resumen (ya resuelto, la versión actual funciona).
- Los desplegables tuvieron un problema de "Input must fall within specified range" al copiar las pestañas al archivo oficial — la validación de datos no se revinculó bien al copiar entre archivos. Se resolvió recreando las validaciones manualmente dentro del archivo oficial (Datos → Validación de datos → seleccionar rango con el ícono de cuadrícula en vez de escribir la fórmula a mano). **Si Claude Code necesita tocar estas hojas por API, tener en cuenta que las validaciones de listas desplegables pueden requerir recrearse si se copian entre spreadsheets.**

## Arquitectura de app.py (estado actual, YA NO actualizado con Participantes/Donaciones)
`app.py` todavía solo lee **Miembros, Pagos y Gastos**. Las tablas de **Participantes, Pagos Participantes y Donaciones son nuevas y el dashboard NO las está mostrando todavía** — esto es probablemente lo próximo a implementar.

- `get_client()` — autentica con gspread usando `st.secrets["gcp_service_account"]`, cacheado con `@st.cache_resource`
- `load_data()` — lee las 3 hojas con `sheet.worksheet(nombre).get_all_records()`, cacheado 60s
- `load_demo_data()` — datos de muestra si no hay secrets configurados
- KPIs con `st.metric`, tabla de miembros con status coloreado, gráfico de progreso por rol, tabla de gastos

## Próximos pasos sugeridos
1. Verificar que `sheet_id` en `secrets.toml` apunte a la hoja oficial, no a la copia
2. Definir con el equipo la "Cuota participante esperada" (Resumen!B4, ahora en 0)
3. Extender `app.py` para leer y mostrar Participantes, Pagos Participantes y Donaciones (nuevas métricas, nueva sección en el dashboard)
4. Actualizar los cálculos de KPIs en `app.py` para que coincidan con la nueva estructura de Resumen (agregar entradas por donaciones y participantes al balance mostrado en la app)
5. Después de esto: Fase 3, Panel Público en Looker Studio (agregados sin nombres individuales — pendiente decisión de directores sobre si mostrar nombres o no)