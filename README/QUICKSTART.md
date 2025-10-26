# 🚀 Guía Rápida de Inicio - Yedistribuciones

## Instalación Rápida

### 1. Crear entorno virtual (Recomendado)

```powershell
# En PowerShell (Windows)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

## Ejecución

### Opción A: Iniciar con datos de ejemplo

```powershell
# 1. Inicializar datos de prueba
python init_sample_data.py

# 2. Ejecutar la aplicación
streamlit run main.py
```

### Opción B: Iniciar con base de datos vacía

```powershell
streamlit run main.py
```

## Acceso

La aplicación se abrirá automáticamente en tu navegador en:

**http://localhost:8501**

## Estructura del Menú

1. **📋 Ver Todas las Rutas**: Visualiza todas las rutas registradas
2. **➕ Crear Nueva Ruta**: Formulario para crear rutas
3. **✏️ Gestionar Clientes en Ruta**: Agregar/eliminar/reordenar clientes
4. **✂️ Dividir Ruta**: Divide una ruta en dos
5. **🔗 Fusionar Rutas**: Fusiona dos rutas compatibles
6. **🔍 Buscar Ruta por CEDIS/Día**: Búsqueda filtrada

## Ejemplos de Uso

### Crear una Ruta

1. Menu: "➕ Crear Nueva Ruta"
2. Llenar formulario:
   - Nombre: "Ruta Norte 1"
   - CEDIS: "CEDIS_BOG_01"
   - Día: "LUNES"
3. Click en "✅ Crear Ruta"

### Agregar Clientes a una Ruta

1. Menu: "✏️ Gestionar Clientes en Ruta"
2. Seleccionar la ruta
3. En "➕ Agregar Cliente":
   - ID del Cliente: "CLI_001"
4. Click en "Agregar Cliente"

### Dividir una Ruta

1. Menu: "✂️ Dividir Ruta"
2. Seleccionar ruta con al menos 2 clientes
3. Elegir punto de división (slider)
4. Asignar nombres a rutas A y B
5. Click en "✂️ Dividir Ruta"

### Fusionar Rutas

1. Menu: "🔗 Fusionar Rutas"
2. Seleccionar dos rutas del mismo CEDIS y día
3. Asignar nombre a ruta fusionada
4. Click en "🔗 Fusionar Rutas"

## Testing

### Ejecutar pruebas unitarias

```powershell
pytest tests/domain/test_route_model.py -v
```

### Ejecutar todas las pruebas

```powershell
pytest tests/ -v
```

### Con reporte de cobertura

```powershell
pytest --cov=src tests/
```

## Validación de Tipos

```powershell
mypy src/
```

## Arquitectura

El proyecto implementa **Arquitectura Hexagonal** con:

- **Dominio**: Lógica de negocio pura (`src/domain/`)
- **Aplicación**: Casos de uso (`src/application/`)
- **Infraestructura**: Implementaciones técnicas (`src/infrastructure/`)

Ver `ARQUITECTURA.md` para más detalles.

## Solución de Problemas

### Error: "streamlit no encontrado"

```powershell
pip install streamlit
```

### Error: "No se puede importar módulos"

Asegúrate de estar ejecutando desde el directorio raíz del proyecto.

### Base de datos bloqueada

Cierra todas las instancias de la aplicación y elimina el archivo `yedistribuciones.db` para empezar de cero.

## Datos de Ejemplo

El script `init_sample_data.py` crea:

- 5 rutas de ejemplo
- Múltiples clientes asignados
- Diferentes CEDIS y días

## Stack Tecnológico

- **Python 3.9+**
- **Streamlit**: Framework de UI
- **SQLite**: Base de datos
- **Type Hints**: Tipado estático

## Próximos Pasos

1. ✅ Ejecutar la aplicación
2. ✅ Explorar las funcionalidades
3. ✅ Revisar la arquitectura en `ARQUITECTURA.md`
4. ✅ Ejecutar los tests
5. ✅ Extender con nuevas funcionalidades

## Contacto y Soporte

Este es un proyecto educativo para el curso de Arquitectura de Sistemas.

---

**¡Listo para usar! 🎉**
