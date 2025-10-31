# 🚚 Yedistribuciones v2.0 - Sistema de Gestión de Rutas con Optimización

Sistema profesional de gestión de rutas de distribución implementado con **Arquitectura Hexagonal** y **Google Maps API** para optimización en tiempo real.

---

## 🎯 Novedades en v2.0

### ✨ Características Nuevas

- **🗺️ Optimización de Rutas con Google Maps**
  - Geocodificación automática de direcciones
  - Cálculo de ruta óptima minimizando distancia y tiempo
  - Basado en datos reales de tráfico

- **📊 Métricas y Analíticas**
  - Distancia total del recorrido (km)
  - Tiempo estimado (minutos)
  - Sugerencias inteligentes de división de rutas

- **🏗️ Arquitectura Mejorada**
  - Puerto de optimización (abstracción)
  - Adaptador de Google Maps (implementación)
  - Inyección de dependencias mejorada
  - Configuración centralizada

---

## 📦 Requisitos del Sistema

- **Python:** 3.9 o superior
- **Sistema Operativo:** Windows, Linux o macOS
- **Dependencias:**
  - streamlit==1.31.0
  - googlemaps==4.10.0
  - folium==0.15.1
  - streamlit-folium==0.15.1
- **(Opcional) Google Maps API Key** para optimización de rutas

---

## 🚀 Instalación Rápida

### 1. Clonar/Descargar el Proyecto

```powershell
cd "C:\Users\ASUS\Desktop\2025-2\ARQUITECTURA\Final_arquitectura"
cd yedistribuciones_project
```

### 2. Crear y Activar Entorno Virtual

```powershell
# Crear entorno virtual
python -m venv venv

# Activar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activar (Windows CMD)
.\venv\Scripts\activate.bat

# Activar (Linux/Mac)
source venv/bin/activate
```

### 3. Instalar Dependencias

```powershell
pip install -r requirements.txt
```

### 4. (Opcional) Configurar Google Maps API

#### Obtener API Key:
1. Ir a: https://console.cloud.google.com/
2. Crear proyecto "Yedistribuciones"
3. Habilitar APIs:
   - ✅ Directions API
   - ✅ Distance Matrix API
   - ✅ Geocoding API
4. Crear credenciales → Clave de API
5. Copiar la API key

#### Configurar API Key:

```powershell
# Windows PowerShell
$env:GOOGLE_MAPS_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXX"

# Windows CMD
set GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXX

# Linux/Mac
export GOOGLE_MAPS_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXX"
```

#### Verificar Configuración:

```powershell
python config.py
```

### 5. Poblar Base de Datos (Primera Vez)

```powershell
python init_sample_data.py
```

### 6. Ejecutar Aplicación

```powershell
streamlit run main.py
```

La aplicación estará disponible en: **http://localhost:8501**

---

## 📱 Funcionalidades

### Funcionalidades Básicas (Sin API Key)

1. **📋 Ver Todas las Rutas**
   - Lista completa de rutas activas e inactivas
   - Información: CEDIS, día, número de clientes

2. **➕ Crear Nueva Ruta**
   - Nombre, CEDIS ID, día de la semana
   - Lista de clientes a incluir

3. **✏️ Gestionar Clientes en Ruta**
   - Agregar clientes a ruta existente
   - Remover clientes de ruta

4. **✂️ Dividir Ruta**
   - Dividir ruta en dos sub-rutas
   - Especificar punto de división
   - Las rutas originales se marcan como inactivas

5. **🔗 Fusionar Rutas**
   - Combinar dos rutas en una sola
   - Eliminación de duplicados automática
   - Las rutas originales se marcan como inactivas

6. **🔍 Buscar Ruta por CEDIS/Día**
   - Filtrar rutas por CEDIS y día de la semana

### Funcionalidades Avanzadas (Con API Key de Google Maps)

7. **🗺️ Optimizar Ruta**
   - Geocodificación automática de direcciones
   - Cálculo de orden óptimo de visita
   - Muestra distancia total y tiempo estimado
   - **Nota:** No modifica la ruta en BD (solo sugerencia)

8. **📊 Ver Métricas de Ruta**
   - Distancia total real (km)
   - Tiempo estimado (minutos)
   - Número de clientes con coordenadas
   - **Análisis de eficiencia:**
     - Compara con límites configurados
     - Sugiere división si es necesario
     - Indica punto óptimo de división

---

## 📁 Estructura del Proyecto

```
yedistribuciones_project/
│
├── config.py                          # Configuración centralizada
├── main.py                            # Punto de entrada + Inyección de dependencias
├── init_sample_data.py                # Script para poblar base de datos
├── requirements.txt                   # Dependencias del proyecto
├── yedistribuciones.db                # Base de datos SQLite (auto-generada)
│
├── src/                               # Código fuente
│   ├── __init__.py
│   │
│   ├── domain/                        # ⬡ CAPA DE DOMINIO
│   │   ├── __init__.py
│   │   ├── models/                    # Entidades de negocio
│   │   │   ├── route.py               # Entidad Route
│   │   │   └── client.py              # Entidad Client
│   │   └── ports/                     # Interfaces (abstracciones)
│   │       ├── route_repository_port.py
│   │       └── route_optimization_port.py
│   │
│   ├── application/                   # ⬡ CAPA DE APLICACIÓN
│   │   ├── __init__.py
│   │   ├── dtos.py                    # Data Transfer Objects
│   │   └── services/                  # Casos de uso
│   │       ├── route_service.py
│   │       └── route_optimization_service.py
│   │
│   └── infrastructure/                # ⬡ CAPA DE INFRAESTRUCTURA
│       ├── __init__.py
│       ├── persistence/               # Adaptadores de persistencia
│       │   └── sqlite_route_repository.py
│       ├── services/                  # Adaptadores de servicios externos
│       │   └── google_maps_service.py
│       └── ui/                        # Adaptadores de interfaz
│           └── streamlit_app.py
│
├── tests/                             # Tests unitarios e integración
│   ├── domain/
│   └── ...
│
└── README/                            # Documentación completa
    ├── README.md                      # Este archivo
    ├── ARQUITECTURA.md                # Explicación de arquitectura hexagonal
    ├── GOOGLE_MAPS_INTEGRATION.md    # Guía completa de Google Maps
    ├── ARCHITECTURE_DIAGRAM.md        # Diagramas visuales
    ├── INTEGRATION_SUMMARY.md         # Resumen de integración
    ├── QUICKSTART.md                  # Guía rápida
    └── PROYECTO_COMPLETADO.md         # Checklist del proyecto
```

---

## 🏗️ Arquitectura

### Arquitectura Hexagonal (Puertos y Adaptadores)

```
┌─────────────────────────────────────────┐
│     ADAPTADORES CONDUCTORES             │
│  (Driving Adapters - Input/UI)          │
│                                         │
│  • Streamlit UI                         │
│  • REST API (futuro)                    │
│  • CLI (futuro)                         │
└──────────────┬──────────────────────────┘
               │
               ↓ usa
┌──────────────────────────────────────────┐
│      CAPA DE APLICACIÓN                  │
│   (Application Services / Use Cases)     │
│                                          │
│  • RouteService                          │
│  • RouteOptimizationService              │
└──────────────┬───────────────────────────┘
               │
               ↓ depende de (puertos)
┌──────────────────────────────────────────┐
│         CAPA DE DOMINIO                  │
│     (Business Logic - Core)              │
│                                          │
│  Modelos:                                │
│  • Route (entidad)                       │
│  • Client (entidad)                      │
│                                          │
│  Puertos (interfaces):                   │
│  • RouteRepositoryPort                   │
│  • RouteOptimizationPort                 │
└──────────────┬───────────────────────────┘
               │
               ↑ implementa
┌──────────────────────────────────────────┐
│    ADAPTADORES CONDUCIDOS                │
│  (Driven Adapters - Output)              │
│                                          │
│  Persistencia:                           │
│  • SqliteRouteRepository                 │
│  • (futuro) PostgresRepository           │
│                                          │
│  Servicios Externos:                     │
│  • GoogleMapsOptimizationService         │
│  • (futuro) MapBoxService                │
└──────────────────────────────────────────┘
```

**Ventajas:**
- ✅ **Independencia de frameworks:** Dominio no conoce Streamlit, SQLite o Google Maps
- ✅ **Testeabilidad:** Fácil crear mocks de puertos
- ✅ **Mantenibilidad:** Cambios localizados, bajo acoplamiento
- ✅ **Flexibilidad:** Cambiar tecnologías sin tocar el core

---

## 🎨 Patrones de Diseño Implementados

### 1. Port/Adapter Pattern
- **Puertos:** Interfaces en capa de dominio
- **Adaptadores:** Implementaciones en infraestructura
- Ejemplo: `RouteOptimizationPort` ← `GoogleMapsOptimizationService`

### 2. Dependency Injection
- Inyección desde `main.py`
- No hay `new` en capas internas
- Facilita testing con mocks

### 3. Service Layer Pattern
- Servicios de aplicación coordinan operaciones
- Lógica de negocio en el dominio
- Lógica de coordinación en aplicación

### 4. Repository Pattern
- Abstracción de persistencia
- `RouteRepositoryPort` ← `SqliteRouteRepository`

### 5. DTO (Data Transfer Object)
- `CreateRouteDTO`, `RouteDTO`, `ClientDTO`
- Desacopla UI de entidades de dominio

---

## ⚙️ Configuración Avanzada

### Variables de Entorno

```env
# Google Maps API
GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXX

# Ubicación del CEDIS
CEDIS_LATITUDE=4.7110
CEDIS_LONGITUDE=-74.0721
CEDIS_ADDRESS=Bogotá, Colombia

# Base de datos
DATABASE_PATH=yedistribuciones.db

# Límites de ruta (para análisis)
MAX_ROUTE_DISTANCE_KM=100.0
MAX_ROUTE_DURATION_HOURS=8.0
```

### Archivo .env (Opcional)

Crear archivo `.env` en la raíz:

```env
GOOGLE_MAPS_API_KEY=tu_api_key_aqui
CEDIS_LATITUDE=4.7110
CEDIS_LONGITUDE=-74.0721
```

Luego instalar `python-dotenv`:

```powershell
pip install python-dotenv
```

Y descomentar en `config.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 🧪 Testing

### Ejecutar Tests

```powershell
# Tests unitarios
pytest tests/

# Tests con coverage
pytest --cov=src tests/

# Test específico
pytest tests/domain/test_route_model.py
```

### Ejemplo de Test con Mock

```python
from unittest.mock import Mock
from src.application.services.route_optimization_service import RouteOptimizationService

def test_optimize_route_order():
    # Mock del puerto
    mock_optimizer = Mock(spec=RouteOptimizationPort)
    mock_optimizer.optimize_route.return_value = RouteOptimizationResult(...)
    
    # Servicio con mock inyectado
    service = RouteOptimizationService(
        route_repository=mock_repo,
        optimization_service=mock_optimizer
    )
    
    result = service.optimize_route_order(...)
    assert result.total_distance_km > 0
```

---

## 💰 Costos de Google Maps API

### Precios (2024)

| API | Precio/1000 llamadas | Crédito gratuito mensual |
|-----|----------------------|---------------------------|
| Directions API | $5.00 | $200 (~40,000 llamadas) |
| Distance Matrix API | $5.00 | $200 (~40,000 llamadas) |
| Geocoding API | $5.00 | $200 (~40,000 llamadas) |

### Estimación para Yedistribuciones

**100 rutas/día:**
- Geocoding: 500 direcciones × 30 días = 15,000 llamadas/mes
- Optimization: 100 rutas × 30 días = 3,000 llamadas/mes
- **Total: ~18,000 llamadas/mes** → **GRATIS** (dentro de $200)

---

## 🐛 Troubleshooting

### Problema: Módulo no encontrado

```powershell
# Solución: Reinstalar dependencias
pip install -r requirements.txt
```

### Problema: Base de datos bloqueada

```powershell
# Solución: Cerrar aplicación y eliminar BD
rm yedistribuciones.db
python init_sample_data.py
```

### Problema: API key no configurada

```powershell
# Verificar configuración
python config.py

# Configurar API key
$env:GOOGLE_MAPS_API_KEY="tu_api_key"
```

### Problema: "REQUEST_DENIED" en Google Maps

**Solución:**
1. Verificar APIs habilitadas en Google Cloud Console
2. Revisar restricciones de la API key
3. Regenerar API key si es necesario

---

## 📚 Documentación Completa

| Documento | Descripción |
|-----------|-------------|
| **README.md** | Este archivo: guía general |
| **ARQUITECTURA.md** | Explicación detallada de arquitectura hexagonal |
| **GOOGLE_MAPS_INTEGRATION.md** | Guía completa de Google Maps API |
| **ARCHITECTURE_DIAGRAM.md** | Diagramas visuales de arquitectura |
| **INTEGRATION_SUMMARY.md** | Resumen ejecutivo de integración |
| **QUICKSTART.md** | Guía de inicio rápido |
| **PROYECTO_COMPLETADO.md** | Checklist de requisitos completados |

---

## 🔮 Roadmap (Futuras Mejoras)

### Versión 2.1
- [ ] Persistencia de coordenadas en BD
- [ ] Caché de resultados de optimización
- [ ] Visualización de mapas con Folium

### Versión 2.2
- [ ] Exportar rutas a PDF con mapas
- [ ] API REST para integraciones
- [ ] Dashboard de métricas

### Versión 3.0
- [ ] Optimización multi-vehículo (OR-Tools)
- [ ] Modo offline con OpenStreetMap
- [ ] App móvil para conductores

---

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abrir Pull Request

### Lineamientos de Código

- Seguir **Arquitectura Hexagonal**
- Aplicar **SOLID principles**
- Agregar **type hints** en Python
- Escribir **docstrings** en funciones
- Crear **tests** para nueva funcionalidad

---

## 📄 Licencia

Este proyecto es desarrollado con fines académicos para el curso de Arquitectura de Software.

---

## 👥 Autores

**Yedistribuciones Development Team**

---

## 📞 Soporte

Para dudas o problemas:
1. Revisar documentación en carpeta `README/`
2. Ejecutar `python config.py` para verificar configuración
3. Consultar troubleshooting en este documento

---

## 🎓 Referencias

- [Hexagonal Architecture - Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)

---

**Versión:** 2.0  
**Última actualización:** Enero 2025  
**Estado:** ✅ Producción
