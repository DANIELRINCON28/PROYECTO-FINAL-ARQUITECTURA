# 📘 GUÍA DE USO - Nueva Interfaz Profesional

## 🎨 Bienvenida a la Nueva UI/UX de Yedistribuciones

Se ha realizado un rediseño completo de la interfaz gráfica con enfoque **corporativo, profesional y accesible**.

---

## ✨ Cambios Principales

### 1. **Diseño Corporativo**
- ✅ Paleta de colores neutra (Azul corporativo #1F4788)
- ✅ Tipografía profesional (Segoe UI / Arial)
- ✅ Espaciado generoso y respirable
- ✅ Componentes consistentes

### 2. **Navegación Mejorada**
- ✅ Barra lateral (sidebar) profesional
- ✅ Menú principal organizado por funcionalidad
- ✅ Estado del sistema visible en tiempo real
- ✅ Dashboard ejecutivo como página de inicio

### 3. **Componentes Reutilizables**
- ✅ Cards profesionales
- ✅ Alertas con estilos mejorados
- ✅ Botones consistentes
- ✅ Formularios optimizados
- ✅ Tablas con mejor legibilidad

### 4. **Experiencia de Usuario**
- ✅ Mensajes de error/éxito clarificadores
- ✅ Instrucciones contextuales
- ✅ Confirmaciones para operaciones críticas
- ✅ Validaciones intuitivas

---

## 🚀 Requisitos Funcionales Priorizados

### Prioridad 1 (Visibles en Dashboard)

#### **RF-RUT-04**: Visualizar todas las rutas ⭐⭐⭐
- **Ubicación**: Menú → "📋 Ver Todas las Rutas"
- **Mejoras**:
  - Tabla clara con información esencial
  - Filtros para rutas activas e inactivas
  - Estadísticas en tarjetas
  - Gestión rápida de estado
  - Vista de detalles expandible

#### **RF-RUT-01**: Crear nueva ruta ⭐⭐⭐
- **Ubicación**: Menú → "➕ Crear Nueva Ruta" | Dashboard → Botón rápido
- **Mejoras**:
  - Formulario limpio y bien organizado
  - Validación en tiempo real
  - Confirmación de éxito con ID de ruta
  - Instrucciones contextuales

#### **RF-RUT-02**: Asignar clientes a rutas ⭐⭐⭐
- **Ubicación**: Menú → "✏️ Gestionar Clientes"
- **Mejoras**:
  - Interfaz con tabs (Agregar, Eliminar, Reordenar)
  - Visualización clara de clientes actuales
  - Feedback inmediato de operaciones

### Prioridad 2 (Acceso por Menú)

#### **RF-RUT-03**: Reordenar clientes en rutas ⭐⭐
- **Ubicación**: "✏️ Gestionar Clientes" → Tab "🔄 Reordenar"
- **Mejoras**:
  - Editor de texto intuitivo
  - Instrucciones claras
  - Validaciones

#### **RF-RUT-06**: Dividir ruta en dos ⭐⭐
- **Ubicación**: Menú → "✂️ Dividir Ruta"
- **Mejoras**:
  - Slider visual para seleccionar punto de división
  - Vista previa de la división
  - Campos para nombres de nuevas rutas
  - Confirmación clara

#### **RF-RUT-07**: Fusionar dos rutas ⭐⭐
- **Ubicación**: Menú → "🔗 Fusionar Rutas"
- **Mejoras**:
  - Selectores lado a lado
  - Vista previa de la fusión
  - Campo para nombre de ruta fusionada
  - Información clara

---

## 🎯 Archivos Modificados

### 1. **`src/infrastructure/ui/ui_components.py`** (NUEVO)
Librería completa de componentes reutilizables con:
- Funciones para headers, sections, cards
- Alertas (success, warning, error, info)
- Cajas de información contextuales
- Métodos de utilidad
- Inyección de CSS personalizado

**Funciones principales**:
```python
init_ui()                           # Inicializar la UI
render_header(title, subtitle)      # Encabezado de página
render_section_header(title)        # Encabezado de sección
alert(message, type)                # Alertas
success_box(title, desc)            # Caja de éxito
warning_box(title, desc)            # Caja de advertencia
error_box(title, desc)              # Caja de error
info_box(title, desc)               # Caja de información
```

### 2. **`src/infrastructure/ui/streamlit_app.py`** (REFACTORIZADO)
Interfaz principal completamente redesñada con:
- Dashboard ejecutivo
- Sidebar profesional
- Vistas mejoradas para cada función
- Componentes reutilizables

**Estructura de vistas**:
```
run_ui() → Punto de entrada
├── dashboard_view()           # Dashboard ejecutivo (NUEVA)
├── view_all_routes()          # RF-RUT-04 mejorada
├── create_route_view()        # RF-RUT-01 mejorada
├── manage_clients_view()      # RF-RUT-02 + RF-RUT-03 mejorada
├── divide_route_view()        # RF-RUT-06 mejorada
├── merge_routes_view()        # RF-RUT-07 mejorada
├── search_route_view()        # Búsqueda mejorada
├── optimize_route_view()      # Optimización mejorada
└── route_metrics_view()       # Métricas mejoradas
```

### 3. **`docs/DESIGN_SYSTEM.md`** (NUEVO)
Documento exhaustivo con:
- Paleta de colores
- Tipografía
- Componentes
- Estilos CSS
- Principios de diseño
- Patrones de navegación

---

## 🎨 Paleta de Colores

| Uso | Hex | RGB | Aplicación |
|-----|-----|-----|-----------|
| Primary | #1F4788 | 31, 71, 136 | Headers, botones principales |
| Secondary | #4A7BA7 | 74, 123, 167 | Botones secundarios |
| Success | #27AE60 | 39, 174, 96 | Operaciones exitosas |
| Warning | #F39C12 | 243, 156, 18 | Advertencias |
| Error | #E74C3C | 231, 76, 60 | Errores |
| Info | #3498DB | 52, 152, 219 | Información |
| Light BG | #F8F9FA | 248, 249, 250 | Fondos |
| Dark Text | #2C3E50 | 44, 62, 80 | Texto principal |

---

## 📱 Responsividad

La interfaz se adapta automáticamente a diferentes tamaños de pantalla:

| Dispositivo | Ancho | Comportamiento |
|-------------|-------|-----------------|
| Mobile | < 768px | Sidebar colapsable, single-column layout |
| Tablet | 768-1024px | Sidebar comprimido, 2-column layout |
| Desktop | > 1024px | Sidebar completo, multi-column layout |

---

## ⚡ Mejoras de Performance

- ✅ Componentes CSS en línea (sin carga de archivos externos)
- ✅ Reutilización de funciones
- ✅ Estructura modular
- ✅ Carga eficiente de datos

---

## ♿ Accesibilidad

### Conformidad WCAG AA
- ✅ Contraste de colores: 4.5:1 (mínimo requerido)
- ✅ Navegación por teclado completa
- ✅ Labels asociados con inputs
- ✅ Estados de foco visibles
- ✅ Estructura semántica correcta

### Semántica
- ✅ Headings estructurados (H1 → H3)
- ✅ Uso correcto de etiquetas
- ✅ Alt text en iconos
- ✅ Inputs con labels explícitos

---

## 🔄 Flujo de Trabajo

### Flujo Típico de Operación

```
1. INICIO
   ↓
2. DASHBOARD
   - Ver resumen de rutas
   - Ver KPIs principales
   - Acciones rápidas
   ↓
3. CREAR / GESTIONAR RUTAS
   - Crear nueva ruta (RF-RUT-01)
   - Asignar clientes (RF-RUT-02)
   - Reordenar clientes (RF-RUT-03)
   ↓
4. OPTIMIZACIÓN (Opcional)
   - Dividir rutas grandes (RF-RUT-06)
   - Fusionar rutas pequeñas (RF-RUT-07)
   - Optimizar orden (Opcional)
   ↓
5. ANÁLISIS
   - Ver todas las rutas (RF-RUT-04)
   - Buscar específicas
   - Revisar métricas
```

---

## 💡 Tips de Uso

### Mejores Prácticas

1. **Dashboard como Punto de Inicio**
   - Siempre comienza aquí para ver el estado general
   - Accede a acciones rápidas desde aquí

2. **Usar Tabs para Gestión de Clientes**
   - Tab "Agregar" para nuevos clientes
   - Tab "Eliminar" para remover clientes
   - Tab "Reordenar" para cambiar orden

3. **Validar Divisiones de Rutas**
   - Usa el slider para visualizar la división
   - Asigna nombres descriptivos

4. **Confirmar Fusiones**
   - Revisa la vista previa antes de fusionar
   - Verifica que sea la operación correcta

5. **Buscar Rutas**
   - Usa búsqueda para localizar rutas rápidamente
   - Filtra por CEDIS y día

---

## 🐛 Troubleshooting

### Problema: Sidebar no se muestra
**Solución**: Actualiza la página (F5) o reinicia Streamlit

### Problema: Colores no se aplican
**Solución**: Limpia cache del navegador (Ctrl+Shift+Del)

### Problema: Formularios no responden
**Solución**: Verifica que no haya errores en la consola del navegador

---

## 📈 Próximas Mejoras Planeadas

- [ ] Integración de Google Maps para visualización
- [ ] Gráficos y dashboards avanzados
- [ ] Exportación de reportes (PDF/Excel)
- [ ] Notificaciones en tiempo real
- [ ] Dark mode
- [ ] Multiidioma

---

## 📞 Soporte

Para reportar problemas o sugerencias:
1. Revisa los logs en la consola de Streamlit
2. Verifica que todos los campos obligatorios estén completos
3. Intenta recargar la página
4. Contacta al equipo de desarrollo

---

**Versión**: 2.0 (Rediseño Corporativo)
**Última actualización**: Noviembre 2025
**Status**: ✅ Producción

---

## 📚 Documentación Relacionada

- `docs/DESIGN_SYSTEM.md` - Sistema de diseño completo
- `docs/PROYECTO_COMPLETADO.md` - Visión general del proyecto
- `README.md` - Instrucciones de instalación
- `src/infrastructure/ui/ui_components.py` - Referencia de componentes
