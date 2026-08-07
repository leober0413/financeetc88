# Design System — ETC 88
Extraído de identidad visual `@etcprofondo.spm`.

---

## Paleta — Light Theme

| Token | Hex | Uso |
|---|---|---|
| `--color-bg` | `#EAE0C4` | Fondo principal — arena/pergamino cálido |
| `--color-surface` | `#F2EAD3` | Cards, modales, paneles elevados |
| `--color-surface-dim` | `#DDD3B2` | Fondos secundarios, separadores |
| `--color-text-primary` | `#1A1C38` | Headings, body — azul marino casi negro |
| `--color-text-secondary` | `#3C3F5E` | Subtítulos, metadatos |
| `--color-text-muted` | `#6B6E8A` | Captions, placeholders |
| `--color-accent` | `#C49020` | Badges, labels énfasis — dorado ámbar |
| `--color-accent-light` | `#F0C84A` | Hover, highlights sobre accent |
| `--color-accent-bg` | `#F5DFA0` | Fondo de badge/pill accent |
| `--color-border` | `#C8BDA0` | Bordes, divisores |
| `--color-logo` | `#1A1C38` | Icono IXOYC fish — mismo que text-primary |

### Uso en componentes (Light)
- **Badge pill** ("01 EL RETIRO"): bg `#F5DFA0`, text `#8A6210`, border-radius 9999px
- **Label uppercase** ("ENCUENTRO TOTAL CON CRISTO"): color `#C49020`, letter-spacing 0.12em
- **Heading principal**: color `#1A1C38`, serif bold
- **Body**: color `#1A1C38`, sans-serif regular
- **Fecha/meta**: color `#1A1C38`, sans-serif light

---

## Paleta — Dark Theme

| Token | Hex | Uso |
|---|---|---|
| `--color-bg` | `#111328` | Fondo principal — azul marino profundo |
| `--color-surface` | `#1A1C38` | Cards, paneles |
| `--color-surface-dim` | `#0C0E20` | Fondo bajo de superficie |
| `--color-text-primary` | `#EAE0C4` | Headings, body — crema cálido (inverso del bg light) |
| `--color-text-secondary` | `#C8BDA0` | Subtítulos, metadatos |
| `--color-text-muted` | `#8A8AA8` | Captions, placeholders |
| `--color-accent` | `#D4A030` | Badges, labels énfasis — dorado más brillante en oscuro |
| `--color-accent-light` | `#F0C84A` | Hover, highlights |
| `--color-accent-bg` | `#3A2C08` | Fondo de badge/pill en dark |
| `--color-border` | `#2C2E50` | Bordes, divisores |
| `--color-logo` | `#EAE0C4` | Icono IXOYC fish — crema sobre oscuro |

### Uso en componentes (Dark)
- **Badge pill**: bg `#3A2C08`, text `#D4A030`, border `#5A4010`
- **Label uppercase**: color `#D4A030`, letter-spacing 0.12em
- **Heading principal**: color `#EAE0C4`
- **Body**: color `#C8BDA0`

---

## Tipografía

### Heading principal
```
Font: serif display — Playfair Display / EB Garamond / Georgia (fallback)
Size: 32px (mobile 26px)
Weight: 700 (Bold)
Color: --color-text-primary
Line-height: 1.2
Ejemplo: "¿Qué es el ETC 88?"
```

### Badge / pill label
```
Font: sans-serif — Inter / system-ui
Size: 11px
Weight: 500
Case: UPPERCASE
Letter-spacing: 0.08em
Color: #8A6210 (light) / #D4A030 (dark)
Ejemplo: "01  EL RETIRO"
```

### Label énfasis (tracking amplio)
```
Font: sans-serif — Inter / system-ui
Size: 10px
Weight: 600
Case: UPPERCASE
Letter-spacing: 0.16em
Color: --color-accent
Ejemplo: "ENCUENTRO TOTAL CON CRISTO"
```

### Body
```
Font: sans-serif — Inter / system-ui
Size: 16px (mobile 15px)
Weight: 400
Line-height: 1.6
Color: --color-text-primary
Ejemplo: "Tres días para encontrarte contigo, con los demás y con Jesús."
```

### Meta / fecha
```
Font: sans-serif — Inter / system-ui
Size: 13px
Weight: 300–400
Color: --color-text-primary
Letter-spacing: 0.04em
Ejemplo: "4–6 SEP · 2026"
```

---

## Tokens CSS completos

```css
/* ── LIGHT ── */
:root {
  --color-bg:              #EAE0C4;
  --color-surface:         #F2EAD3;
  --color-surface-dim:     #DDD3B2;
  --color-text-primary:    #1A1C38;
  --color-text-secondary:  #3C3F5E;
  --color-text-muted:      #6B6E8A;
  --color-accent:          #C49020;
  --color-accent-light:    #F0C84A;
  --color-accent-bg:       #F5DFA0;
  --color-border:          #C8BDA0;
  --color-logo:            #1A1C38;

  --font-display: 'Playfair Display', 'EB Garamond', Georgia, serif;
  --font-body:    'Inter', system-ui, -apple-system, sans-serif;

  --radius-pill:  9999px;
  --radius-card:  12px;
  --radius-sm:    6px;
}

/* ── DARK ── */
[data-theme="dark"] {
  --color-bg:              #111328;
  --color-surface:         #1A1C38;
  --color-surface-dim:     #0C0E20;
  --color-text-primary:    #EAE0C4;
  --color-text-secondary:  #C8BDA0;
  --color-text-muted:      #8A8AA8;
  --color-accent:          #D4A030;
  --color-accent-light:    #F0C84A;
  --color-accent-bg:       #3A2C08;
  --color-border:          #2C2E50;
  --color-logo:            #EAE0C4;
}
```

---

## Componentes visuales del post

### Badge numerado (ej. "01  EL RETIRO")
```
Shape:    pill (border-radius: 9999px)
Padding:  4px 14px
BG:       --color-accent-bg
Text:     uppercase, 11px, weight 500, --color-accent oscurecido
Gap:      8px entre número y texto
```

### Label sección (ej. "ENCUENTRO TOTAL CON CRISTO")
```
Display:  block, centrado
Font:     sans-serif, 10px, weight 600
Case:     UPPERCASE
Spacing:  letter-spacing 0.16em
Color:    --color-accent
Margin:   24px top
```

### Logo IXOYC (pez)
```
Tipo:     SVG / icono
Color:    --color-logo (monocromo)
Border:   círculo outlined, mismo color
Size:     80–100px
```

### Card de contenido
```
BG:       --color-surface
Radius:   --radius-card (12px)
Padding:  40px 32px (mobile: 32px 20px)
Align:    centro
Shadow:   none (estética plana)
```
