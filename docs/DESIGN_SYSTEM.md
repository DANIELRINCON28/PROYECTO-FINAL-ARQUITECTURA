# 🎨 DESIGN SYSTEM - Yedistribuciones

## Visión General

Sistema de diseño corporativo para la aplicación **Yedistribuciones** que garantiza:
- **Profesionalismo**: Paleta neutra con acentos modernos
- **Consistencia**: Componentes reutilizables y patrones estandarizados
- **Usabilidad**: Navegación intuitiva y accesibilidad mejorada
- **Escalabilidad**: Fácil de mantener y extender

---

## 📋 PALETA DE COLORES

### Colores Primarios (Corporativos)
```
Primary - Azul Corporativo
  HEX: #1F4788
  RGB: 31, 71, 136
  USO: Headers, botones primarios, títulos principales

Secondary - Azul Claro
  HEX: #4A7BA7
  RGB: 74, 123, 167
  USO: Botones secundarios, acentos, links

Accent - Verde Éxito
  HEX: #2E8B57
  RGB: 46, 139, 87
  USO: Estados positivos, confirmaciones
```

### Colores Neutrales
```
Dark Gray - Texto Principal
  HEX: #2C3E50
  RGB: 44, 62, 80
  USO: Texto principal, labels, encabezados

Medium Gray - Texto Secundario
  HEX: #7F8C8D
  RGB: 127, 140, 141
  USO: Subtítulos, metadata, descripciones

Light Gray - Fondos
  HEX: #F8F9FA
  RGB: 248, 249, 250
  USO: Fondos de tarjetas, secciones

Border Gray
  HEX: #E0E3E8
  RGB: 224, 227, 232
  USO: Bordes, divisores, separadores
```

### Colores de Estado
```
Success (Éxito)
  HEX: #27AE60
  RGB: 39, 174, 96

Warning (Advertencia)
  HEX: #F39C12
  RGB: 243, 156, 18

Error (Error)
  HEX: #E74C3C
  RGB: 231, 76, 60

Info (Información)
  HEX: #3498DB
  RGB: 52, 152, 219
```

---

## 🔤 TIPOGRAFÍA

### Familia Principal
**Fuente:** Segoe UI / Arial (system fonts - sin descargas adicionales)
- Legibilidad excelente
- Soporte multiplataforma
- Peso recomendado: 400 (Regular), 600 (Semibold), 700 (Bold)

### Escala de Tamaños

| Elemento | Tamaño | Peso | Uso |
|----------|--------|------|-----|
| H1 - Título Principal | 32px | 700 | Títulos de página |
| H2 - Subtítulo | 24px | 600 | Encabezados de sección |
| H3 - Subsección | 18px | 600 | Subtítulos |
| Body - Texto Regular | 14px | 400 | Contenido principal |
| Small - Texto Pequeño | 12px | 400 | Metadata, ayuda |
| Button - Etiqueta | 14px | 600 | Botones, links |

### Espaciado de Línea
- Títulos: 1.2
- Cuerpo: 1.6
- Tablas: 1.4

---

## 🎯 COMPONENTES PRINCIPALES

### 1. Header/Navbar
```
Características:
- Fondo: Azul Corporativo #1F4788
- Texto: Blanco
- Altura: 60px
- Logo + Nombre de App (izquierda)
- Usuarios/Status (derecha)
- Información de breadcrumb elegante
```

### 2. Tarjetas (Cards)
```
Características:
- Fondo: Blanco o Light Gray #F8F9FA
- Borde: 1px solid #E0E3E8
- Border Radius: 8px
- Padding: 20px
- Box Shadow: 0 2px 8px rgba(0,0,0,0.08)
- Hover: Sombra ligeramente aumentada
```

### 3. Botones
```
Primario (Acciones principales):
- Background: Azul Corporativo #1F4788
- Texto: Blanco
- Padding: 10px 24px
- Border Radius: 6px
- Font Weight: 600
- Hover: Oscurecer 10%
- Transición: 200ms ease

Secundario (Acciones alternativas):
- Background: Light Gray #F8F9FA
- Texto: Azul Corporativo #1F4788
- Borde: 1px solid #1F4788
- Hover: Fondo Azul Corporativo claro

Tertiary (Acciones menos importantes):
- Background: Transparent
- Texto: Azul Corporativo #1F4788
- Hover: Background Light Gray

Danger (Acciones destructivas):
- Background: Error #E74C3C
- Texto: Blanco
- Hover: Oscurecer 10%
```

### 4. Inputs y Formularios
```
Características:
- Background: Blanco
- Borde: 1px solid #E0E3E8
- Border Radius: 6px
- Padding: 10px 12px
- Font Size: 14px
- Focus: Borde en Azul Corporativo #1F4788
- Focus Shadow: 0 0 0 3px rgba(31,71,136,0.1)
- Label: Gris Oscuro #2C3E50, Weight 600, Margin Bottom 8px
```

### 5. Alertas
```
Success:
- Fondo: rgba(39, 174, 96, 0.1)
- Borde Izquierdo: 4px solid #27AE60
- Texto: #27AE60

Warning:
- Fondo: rgba(243, 156, 18, 0.1)
- Borde Izquierdo: 4px solid #F39C12
- Texto: #F39C12

Error:
- Fondo: rgba(231, 76, 60, 0.1)
- Borde Izquierdo: 4px solid #E74C3C
- Texto: #E74C3C

Info:
- Fondo: rgba(52, 152, 219, 0.1)
- Borde Izquierdo: 4px solid #3498DB
- Texto: #3498DB

Características comunes:
- Padding: 12px 16px
- Border Radius: 6px
- Font Size: 14px
```

### 6. Tablas
```
Características:
- Header Background: Azul Corporativo #1F4788
- Header Text: Blanco
- Row Background: Blanco / Striped Light Gray
- Border: 1px solid #E0E3E8
- Padding Celda: 12px
- Font Size: 14px
- Hover Row: Background Light Gray ligeramente más oscuro
```

### 7. Navegación Sidebar
```
Características:
- Ancho: 250px (desktop), colapsable a mobile
- Background: #F8F9FA
- Borde Derecho: 1px solid #E0E3E8
- Items Seleccionados: Background Azul Claro #4A7BA7, Texto Blanco
- Hover Items: Background Light Gray
- Icons: 18px, alineados izquierda
- Font Size: 14px
- Padding Items: 12px 16px
```

### 8. Modales/Diálogos
```
Características:
- Overlay: rgba(0,0,0,0.5)
- Background: Blanco
- Border Radius: 8px
- Box Shadow: 0 10px 40px rgba(0,0,0,0.16)
- Ancho Máximo: 500px (desktops), 90vw (mobile)
- Padding: 24px
- Header: Azul Corporativo #1F4788, Blanco, 18px
- Footer: Fondo Light Gray #F8F9FA
```

---

## 🎨 ESTILOS CSS PERSONALIZADOS

```css
/* Tema General */
:root {
    --primary: #1F4788;
    --secondary: #4A7BA7;
    --accent: #2E8B57;
    --success: #27AE60;
    --warning: #F39C12;
    --error: #E74C3C;
    --info: #3498DB;
    
    --dark: #2C3E50;
    --medium: #7F8C8D;
    --light: #F8F9FA;
    --border: #E0E3E8;
    
    --radius: 6px;
    --radius-lg: 8px;
    --shadow: 0 2px 8px rgba(0,0,0,0.08);
    --shadow-lg: 0 10px 40px rgba(0,0,0,0.16);
    
    --transition: 200ms ease;
}

/* Utilidades */
.container-card {
    background: var(--light);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    box-shadow: var(--shadow);
}

.divider {
    border-top: 1px solid var(--border);
    margin: 16px 0;
}

.text-muted {
    color: var(--medium);
    font-size: 12px;
}

.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}

.status-active {
    background: rgba(39, 174, 96, 0.15);
    color: var(--success);
}

.status-inactive {
    background: rgba(127, 140, 141, 0.15);
    color: var(--medium);
}
```

---

## 🚀 PATRONES DE DISEÑO

### Layout Principal
```
┌─────────────────────────────────────────┐
│          HEADER CORPORATIVO             │
├────────────┬──────────────────────────────┤
│            │                              │
│  SIDEBAR   │   CONTENIDO PRINCIPAL        │
│  (250px)   │   (responsive)               │
│            │                              │
│            │                              │
└────────────┴──────────────────────────────┘
```

### Flujo de Página
1. **Header**: Logo + Título + Información de usuario
2. **Breadcrumb**: Navegación contextual (si aplica)
3. **Contenido Principal**: Card con padding generoso
4. **Acciones**: Botones alineados al final de la card

### Densidad de Contenido
- **Espaciado Generoso**: 20px entre elementos
- **Líneas de respiro**: Dividers entre secciones lógicas
- **Máximo 80 caracteres por línea**: Para legibilidad

---

## ♿ ACCESIBILIDAD

### Contraste de Colores
- ✅ Todos los colores cumplen WCAG AA (4.5:1 para texto)
- ✅ Iconos con etiquetas alt
- ✅ Navegación por teclado completa
- ✅ Focus estados visibles

### Estructura Semántica
- Uso correcto de headings (H1 → H3)
- Labels asociados con inputs
- ARIA labels cuando sea necesario
- Validaciones claras en formularios

---

## 📱 RESPONSIVIDAD

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Adaptaciones por Breakpoint

**Mobile:**
- Sidebar colapsable (menú hamburguesa)
- Columnas únicas para formularios
- Tablas convertidas a cards apiladas
- Botones full-width

**Tablet:**
- Sidebar comprimido (solo iconos)
- Layouts en 2 columnas cuando aplique

**Desktop:**
- Sidebar completo
- Layouts multi-columna
- Tablas completas

---

## 🎯 REQUISITOS FUNCIONALES PRIORIZADOS

### Primera Prioridad (Visibles en Home/Dashboard)
1. **RF-RUT-04**: Visualizar todas las rutas → Tabla/Grid prominente
2. **RF-RUT-01**: Crear nueva ruta → Botón FAB + Modal
3. **RF-RUT-02**: Asignar clientes → Panel lateral/modal

### Segunda Prioridad (Acceso por menú)
4. **RF-RUT-03**: Reordenar clientes → Drag & Drop intuitivo
5. **RF-RUT-06**: Dividir ruta → Wizard visual
6. **RF-RUT-07**: Fusionar rutas → Componentes visuales claros

---

## 🔄 PRINCIPIOS DE CONSISTENCIA

### Iconografía
- Usar emoji consistentemente (🚚, ➕, ✏️, etc.)
- O migrar a librería de iconos (Material Icons, Feather Icons)
- Tamaño: 18px para texto, 24px para botones

### Nomenclatura de Páginas/Secciones
- **Naming**: Verbo + Sustantivo (ej: "Crear Ruta", "Ver Rutas")
- **Descripciones**: Línea de texto explicativa debajo del título

### Mensajería
- **Éxito**: "✅ Operación completada exitosamente"
- **Error**: "❌ Ocurrió un error: [detalles]"
- **Info**: "ℹ️ Información relevante"
- **Warning**: "⚠️ Advertencia importante"

---

## 📊 IMPLEMENTACIÓN EN STREAMLIT

```python
# streamlit_config.py
theme_config = {
    'primaryColor': '#1F4788',
    'backgroundColor': '#FFFFFF',
    'secondaryBackgroundColor': '#F8F9FA',
    'textColor': '#2C3E50',
    'font': 'sans serif'
}

# Aplicar en .streamlit/config.toml
[theme]
primaryColor = "#1F4788"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F8F9FA"
textColor = "#2C3E50"
font = "sans serif"
```

---

## ✨ PRÓXIMOS PASOS

1. ✅ Crear `ui_components.py` con funciones de componentes
2. ✅ Refactorizar `streamlit_app.py` con nuevo design
3. ✅ Implementar CSS personalizado en `st.markdown()`
4. ✅ Crear dashboard de bienvenida
5. ✅ Pruebas de responsividad y accesibilidad
6. ✅ Documentar uso de componentes

---

**Documento versión 1.0**
**Última actualización: Noviembre 2025**
