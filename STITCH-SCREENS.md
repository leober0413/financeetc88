# Stitch — Panel de Finanzas ETC 88
**Proyecto ID:** `10078308099094505993`
**Design System:** ETC 88 Unified Ledger (`assets/b861859db8094b329c8c607fa4338f19`)

---

## Design System — ETC 88 Unified Ledger

### Paleta
| Token | Hex |
|---|---|
| Background | `#F8F9FA` |
| Surface | `#FFFFFF` |
| Border | `#E2E8F0` |
| Text primary | `#191C1D` |
| Text secondary | `#424754` |
| Positive (text) | `#276749` |
| Positive (bg) | `#DCEFE2` |
| Negative (text) | `#A34430` |
| Negative (bg) | `#FBE9E4` |
| Accent | `#3B82F6` |
| Accent hover | `#2563EB` |
| Chart Esperado | `#CBD5E0` |
| Chart Recaudado | `#48BB78` |

### Tipografía — Inter
| Uso | Tamaño | Peso |
|---|---|---|
| Título página | 24px (mobile 20px) | 700 |
| Sección heading | 18px | 600 |
| KPI valor | 28px | 700 |
| KPI label | 12px, uppercase, 0.05em | 600 |
| Table header | 12px, uppercase | 600 |
| Body | 14px | 400 |
| Label sm | 12px | 500 |

### Espaciado
| Token | Valor |
|---|---|
| Page padding | 24px |
| Card padding | 16px |
| Section gap | 24px |
| Element gap sm | 8px |
| Element gap md | 16px |
| Grid gutter | 24px |

### Componentes clave
- **KPI Cards** — white surface, 1px border `#E2E8F0`, 4px radius, 16px padding. Label arriba (secondary, uppercase), valor abajo (bold, semantic color).
- **Badges de Status** — pill (9999px radius). PAGO COMPLETO: `#DCEFE2` bg / `#276749` text. PENDIENTE: `#FBE9E4` bg / `#A34430` text.
- **Botón primario** — `#3B82F6` bg, blanco, full-width en forms.
- **Botón outline** — borde `#E2E8F0`, texto azul. Usado en Refrescar.
- **Tablas** — headers 12px uppercase, rows 48px min-height, 1px dividers.
- **Inputs/Dropdowns** — 1px border, 14px text, focus: 2px blue border.
- **Bar chart** — agrupado, Esperado (gris) + Recaudado (verde) por Rol.
- **Expanders** — colapsados por defecto para acciones destructivas (eliminar).

---

## Pantallas Generadas

### GRUPO 1: Dashboard (tab "📊 Dashboard" activo)

Estructura común a todas las variantes Dashboard:

```
┌─────────────────────────────────────────────┐
│ Panel de Finanzas — Equipo ETC 88  [🔄 Ref] │
│ Vista interna. Datos en vivo...              │
├─────────────────────────────────────────────┤
│ [📊 Dashboard ──]  [➕ Registrar]           │
├─────────────────────────────────────────────┤
│ [Filtrar por rol ▾]  [Filtrar por status ▾] │
├─────────────────────────────────────────────┤
│ ┌──────────┐┌────────────┐┌─────────┐       │
│ │TOTAL ESP.││CUOTAS RECAU││PENDIENTE│ ...   │
│ │RD$108,000││  RD$64,000 ││RD$44,000│       │
│ └──────────┘└────────────┘└─────────┘       │
├─────────────────────────────────────────────┤
│ Miembros (54 de 54)                         │
│ Nombre | Rol | Total Aportado | Status      │
│ Juan Manuel... Director  RD$2,000 [✓PAGO]  │
│ Jean Carlos... Director  RD$0     [PEND.]  │
│ Laura Fernandez Asesor   RD$1,000 [PEND.]  │
├─────────────────────────────────────────────┤
│ Pagos registrados                           │
│ Miembro | Concepto | Monto | Fuente | Nota  │
│ ▶ 🗑️ Eliminar pago                          │
├─────────────────────────────────────────────┤
│ Gastos registrados                          │
│ Fecha | Concepto | Monto | Fuente           │
│ ▶ 🗑️ Eliminar gasto                         │
├─────────────────────────────────────────────┤
│ Progreso de recaudo por rol                 │
│ [Gráfico barras agrupadas: Esp. vs Recaud.] │
│  Director  Asesor  Guia  Cocinero           │
└─────────────────────────────────────────────┘
```

#### Variantes Dashboard disponibles en Stitch

| # | Título | Tema | ID pantalla | Dimensiones |
|---|---|---|---|---|
| 1 | Panel de Finanzas — ETC 88 | Default (generado aparte) | `c53b6c719f7647b4a2a6e841e92162c2` | 2560×2232 |
| 2 | Dashboard — Panel de Finanzas | Principal (design system) | `220e36ec98e244b68e5a8cba7cf9ab03` | 2560×2048 |
| 3 | Dashboard — Panel de Finanzas | Variante | `6a3c08e88e3c4e988b495c2ce99d6225` | 2560×2176 |
| 4 | Finance Overview Dashboard | Variante | `1fa6e386818848428731487ee7d3cd6b` | 2560×2048 |
| 5 | Dashboard — Panel de Finanzas | Variante | `915ec861fad543b880936c56936e80b3` | 2560×2048 |
| 6 | Dashboard — Panel de Finanzas | Variante | `b274b9b7032149fea995596934ffcaec` | 2560×2048 |
| 7 | Dashboard — Pesto Light | Tema verde/crema claro | `31d2f1154012432f9f1ce4bf17fc78dc` | 2560×2176 |
| 8 | Dashboard — Modern Wiki | Tema wiki moderno claro | `282bb15f8c9b4ebfbd8e77f053fb72ac` | 2560×2176 |
| 9 | Dashboard — Cream & Yellow Wiki | Tema crema/amarillo | `b38f98fee60b480fac0e9d807db89bcd` | 2560×2176 |
| 10 | Dashboard — Pesto Dark | Tema verde oscuro | `920b40f102f1436c9cf0cd71314768a1` | 2560×2226 |
| 11 | Dashboard — Modern Wiki Dark | Tema wiki oscuro | `c5a4518366b74e11a37d730834c31cb1` | 2560×2226 |
| 12 | Dashboard — Deep Blue Wiki Dark | Tema azul profundo oscuro | `f394b0a6f1514448a5cb41c118bca92d` | 2560×2226 |
| 13 | Dashboard — Cream Wiki Dark | Tema crema oscuro | `c9b5e40b986442d6992704ac534656a4` | 2560×2234 |
| 14 | Dashboard — Panel de Finanzas | Variante | `33056cbca28840c29310a34bd84db62b` | 2560×2048 |

---

### GRUPO 2: Registrar (tab "➕ Registrar" activo)

Estructura común a todas las variantes Registrar:

```
┌─────────────────────────────────────────────┐
│ Panel de Finanzas — Equipo ETC 88  [🔄 Ref] │
├─────────────────────────────────────────────┤
│ [📊 Dashboard]  [➕ Registrar ──]           │
├──────────────────────┬──────────────────────┤
│ Registrar pago       │ Registrar gasto      │
│                      │                      │
│ Miembro       [▾]    │ Fecha      [📅]      │
│ Concepto      [▾]    │ Concepto   [______]  │
│ Monto (RD$)   [___]  │ Monto(RD$) [______]  │
│ Fuente        [▾]    │ Fuente     [______]  │
│ Nota (opc.)   [___]  │                      │
│                      │                      │
│ [Guardar pago ─────] │ [Guardar gasto ────] │
└──────────────────────┴──────────────────────┘
```

**Campos — Registrar pago:**
- Miembro: dropdown con 54 nombres
- Concepto: dropdown — Cuota 1, Cuota 2, Cuota 3, Cuota 4, Formacion 1, Formacion 2, Formacion 3, Formacion 4
- Monto (RD$): number input, step 100
- Fuente: dropdown — Control de Cuotas, Tardanzas, Otro
- Nota: text input opcional
- Submit: "Guardar pago" — azul, full-width

**Campos — Registrar gasto:**
- Fecha: date picker (default hoy)
- Concepto: text input
- Monto (RD$): number input, step 100
- Fuente: text input (default "Reporte Salidas")
- Submit: "Guardar gasto" — azul, full-width

#### Variantes Registrar disponibles en Stitch

| # | Título | Tema | ID pantalla | Dimensiones |
|---|---|---|---|---|
| 1 | Registrar — Panel de Finanzas | Principal (design system) | `f355fdb76a6d4c35992aeec302623598` | 2560×2282 |
| 2 | Registrar — Pesto Light | Tema verde claro | `18eaa46cfc0d45aaa67cf22669bac6b0` | 2560×2314 |
| 3 | Registrar — Cream Wiki | Tema crema/wiki | `465038145d954a4880d351e477b6aac6` | 2560×2314 |
| 4 | Registrar — Pesto Dark | Tema verde oscuro | `aad01740f2354fa0ac9764eb48a12068` | 2560×2252 |
| 5 | Registrar — Modern Wiki | Tema wiki moderno | `bf5abeffdd8449fa8869ddc665eb792d` | 2560×2314 |

---

## Comportamiento Mobile (≤768px)

- Header: título full-width, botón Refrescar debajo
- KPI cards: wrap 2 por fila (5to card full-width)
- Filtros: apilados verticalmente
- Tablas: scroll horizontal
- Formularios: columnas apiladas
- Gráfico: scroll horizontal

CSS inyectado en `app.py`:
- Breakpoint 768px: `flex-wrap: wrap`, columnas min 45%
- Breakpoint 420px: columnas 100% (apiladas)

---

## Archivos clave del repo

| Archivo | Función |
|---|---|
| `app.py` | App principal Streamlit |
| `requirements.txt` | `streamlit`, `gspread`, `google-auth`, `pandas` |
| `.gitignore` | Excluye `venv/`, `.streamlit/secrets.toml` |
| `.streamlit/secrets.toml` | Credenciales GCP + Sheet ID (NO en repo) |

**GitHub:** `github.com/leober0413/financeetc88` (privado)

---

## Próximos pasos

- [ ] Deploy en Streamlit Community Cloud
- [ ] Configurar viewer auth (Settings → Sharing → Specific people)
- [ ] Agregar emails del equipo ETC 88
- [ ] Decidir tema visual final entre las variantes Stitch
