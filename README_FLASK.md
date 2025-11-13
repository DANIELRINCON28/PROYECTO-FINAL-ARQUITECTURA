# 🚚 Yedistribuciones - Sistema de Gestión de Rutas (Flask)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-orange.svg)](docs/ARQUITECTURA.md)

Sistema profesional de gestión y optimización de rutas de distribución para Yedistribuciones, implementado con **Arquitectura Hexagonal (Ports & Adapters)** y **Flask**.

## 🎯 Características Principales

- ✅ **Gestión completa de rutas** de distribución
- ✅ **Optimización inteligente** con Google Maps API
- ✅ **Arquitectura Hexagonal** limpia y desacoplada
- ✅ **API REST** para integraciones
- ✅ **Interfaz web profesional** con Flask y Bootstrap 5
- ✅ **Base de datos PostgreSQL** robusta y escalable
- ✅ **Design System corporativo** consistente

## 🚀 Inicio Rápido

### Prerrequisitos

```bash
- Python 3.11 o superior
- PostgreSQL 15 o superior
- pip (gestor de paquetes de Python)
```

### Instalación

1. **Clonar el repositorio**
```powershell
git clone <repository-url>
cd PROYECTO-FINAL-ARQUITECTURA
```

2. **Crear entorno virtual**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. **Instalar dependencias**
```powershell
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Crear archivo `.env` en la raíz del proyecto:
```env
# Base de datos PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=RutasDB
DB_USER=postgres
DB_PASSWORD=tu_password

# Google Maps API (opcional - para optimización)
GOOGLE_MAPS_API_KEY=tu_api_key_aqui

# Flask Configuration
FLASK_PORT=5000
DEBUG=True
SECRET_KEY=yedistribuciones-secret-key-change-in-production
```

5. **Inicializar base de datos**
```powershell
python scripts/initialize_database.py
```

6. **Ejecutar aplicación**
```powershell
python main_flask.py
```

7. **Abrir navegador**
```
http://localhost:5000
```

## 📁 Estructura del Proyecto

```
PROYECTO-FINAL-ARQUITECTURA/
│
├── src/                                    # Código fuente
│   ├── domain/                            # 🎯 Capa de Dominio
│   │   ├── models/                        # Entidades del negocio
│   │   │   ├── route.py                   # Entidad Route
│   │   │   └── client.py                  # Entidad Client
│   │   └── ports/                         # Puertos (Interfaces)
│   │       ├── route_repository_port.py   # Puerto de persistencia
│   │       └── route_optimization_port.py # Puerto de optimización
│   │
│   ├── application/                       # 🔧 Capa de Aplicación
│   │   ├── dtos.py                        # Data Transfer Objects
│   │   └── services/                      # Servicios de aplicación
│   │       ├── route_service.py           # Casos de uso de rutas
│   │       └── route_optimization_service.py
│   │
│   └── infrastructure/                    # 🔌 Capa de Infraestructura
│       ├── persistence/                   # Adaptadores de persistencia
│       │   └── postgres_route_repository.py
│       ├── services/                      # Adaptadores de servicios
│       │   └── google_maps_service.py
│       └── ui/                            # 🌐 Adaptador de UI (Flask)
│           ├── flask_app.py               # ⭐ Aplicación Flask
│           ├── templates/                 # Plantillas HTML
│           │   ├── base.html
│           │   ├── dashboard.html
│           │   ├── routes_list.html
│           │   └── ...
│           └── static/                    # Recursos estáticos
│               ├── css/style.css
│               └── js/main.js
│
├── scripts/                               # Scripts de utilidad
│   ├── initialize_database.py             # Inicializar BD
│   └── init_sample_data.py               # Datos de prueba
│
├── tests/                                 # Tests unitarios
│   └── domain/
│       └── test_route_model.py
│
├── docs/                                  # Documentación
│   ├── ARQUITECTURA.md
│   ├── MIGRACION_FLASK.md                # 📘 Guía de migración
│   └── ...
│
├── main_flask.py                          # ⭐ Punto de entrada Flask
├── config.py                              # Configuración centralizada
├── requirements.txt                       # Dependencias Python
└── README.md                              # Este archivo
```

## 🏗️ Arquitectura Hexagonal

```
┌──────────────────────────────────────────────────────────┐
│                   DRIVING ADAPTERS                        │
│                  (Infrastructure/UI)                      │
├──────────────────────────────────────────────────────────┤
│  Flask App                                               │
│  ├── Web UI (Templates HTML + CSS + JS)                 │
│  └── REST API (JSON endpoints)                          │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                        │
│                 (Use Cases / Services)                    │
├──────────────────────────────────────────────────────────┤
│  RouteService                                            │
│  RouteOptimizationService                               │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                           │
│                  (Business Logic)                         │
├──────────────────────────────────────────────────────────┤
│  Entities: Route, Client                                 │
│  Ports: RouteRepositoryPort, OptimizationPort           │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│                   DRIVEN ADAPTERS                         │
│             (Infrastructure/Implementations)              │
├──────────────────────────────────────────────────────────┤
│  PostgresRouteRepository                                 │
│  GoogleMapsOptimizationService                          │
└──────────────────────────────────────────────────────────┘
```

**Principios aplicados:**
- ✅ Dependency Inversion Principle (DIP)
- ✅ Single Responsibility Principle (SRP)
- ✅ Open/Closed Principle (OCP)
- ✅ Inyección de Dependencias
- ✅ Separación de responsabilidades por capas

## 🔌 API REST

La aplicación incluye una API REST completa:

### Endpoints de Rutas

```http
GET    /api/routes                          # Obtener todas las rutas
GET    /api/routes/<route_id>               # Obtener ruta específica
POST   /api/routes/<route_id>/clients       # Añadir cliente a ruta
DELETE /api/routes/<route_id>/clients/<id>  # Eliminar cliente
POST   /api/routes/<route_id>/reorder       # Reordenar clientes
POST   /api/routes/divide                   # Dividir ruta
POST   /api/routes/merge                    # Fusionar rutas
POST   /api/routes/<route_id>/optimize      # Optimizar ruta
```

### Ejemplo de Respuesta

```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Ruta Norte Bogotá",
    "cedis_id": "CEDIS_BOGOTA",
    "day_of_week": "LUNES",
    "client_count": 15,
    "is_active": true
  }
}
```

## 🎨 Interfaz de Usuario

### Vistas Disponibles

| Ruta | Descripción | Casos de Uso |
|------|-------------|--------------|
| `/` | Dashboard ejecutivo | KPIs, estadísticas, gráficos |
| `/routes` | Lista de rutas | RF-RUT-04 |
| `/routes/create` | Crear nueva ruta | RF-RUT-01 |
| `/routes/<id>` | Detalle de ruta | RF-RUT-05 |
| `/routes/<id>/clients` | Gestionar clientes | RF-RUT-02, RF-RUT-08 |
| `/routes/divide` | Dividir ruta | RF-RUT-06 |
| `/routes/merge` | Fusionar rutas | RF-RUT-07 |
| `/routes/<id>/optimize` | Optimizar ruta | RF-OPT-01 |

### Tecnologías Frontend

- **Bootstrap 5.3**: Framework CSS responsivo
- **Font Awesome 6.4**: Iconografía
- **Chart.js 4.4**: Gráficos y visualizaciones
- **jQuery 3.7**: Manipulación DOM y AJAX
- **Jinja2**: Motor de templates

## 📊 Casos de Uso Implementados

### Gestión de Rutas
- ✅ **RF-RUT-01**: Crear nueva ruta
- ✅ **RF-RUT-02**: Asignar cliente a ruta
- ✅ **RF-RUT-03**: Reordenar clientes en ruta
- ✅ **RF-RUT-04**: Visualizar todas las rutas
- ✅ **RF-RUT-05**: Ver detalle de ruta específica
- ✅ **RF-RUT-06**: Dividir ruta en dos
- ✅ **RF-RUT-07**: Fusionar dos rutas
- ✅ **RF-RUT-08**: Eliminar cliente de ruta

### Optimización (Google Maps)
- ✅ **RF-OPT-01**: Optimizar orden de visita
- ✅ **RF-OPT-02**: Calcular distancias y tiempos
- ✅ **RF-OPT-03**: Visualizar métricas de ahorro

## 🧪 Testing

Ejecutar tests unitarios:

```powershell
# Todos los tests
pytest tests/ -v

# Tests de dominio
pytest tests/domain/ -v

# Con coverage
pytest --cov=src tests/
```

## 🚀 Despliegue

### Desarrollo Local

```powershell
python main_flask.py
```

### Producción con Gunicorn (Linux)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "src.infrastructure.ui.flask_app:create_flask_app()"
```

### Docker (Próximamente)

```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main_flask.py"]
```

## 📚 Documentación

- 📘 [Arquitectura Hexagonal](docs/ARQUITECTURA.md)
- 📘 [Migración de Streamlit a Flask](docs/MIGRACION_FLASK.md)
- 📘 [Esquema de Base de Datos](docs/DATABASE_SCHEMA.md)
- 📘 [Guía de Inicio Rápido](docs/QUICKSTART.md)

## 🔧 Configuración Avanzada

### Google Maps API

Para habilitar la optimización de rutas:

1. Obtener API Key de [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar APIs:
   - Directions API
   - Distance Matrix API
   - Geocoding API
3. Agregar key en `.env`:
```env
GOOGLE_MAPS_API_KEY=tu_api_key_aqui
```

### Base de Datos

PostgreSQL es requerido. Configuración en `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=RutasDB
DB_USER=postgres
DB_PASSWORD=tu_password
```

## 🤝 Contribuciones

Este proyecto sigue la arquitectura hexagonal. Al contribuir:

1. **Dominio**: Lógica de negocio pura, sin dependencias externas
2. **Aplicación**: Casos de uso, orquestación
3. **Infraestructura**: Implementaciones concretas de puertos

## 📄 Licencia

Este proyecto es parte del curso de Arquitectura de Software.

## 👥 Equipo

- **Desarrollo**: Equipo Yedistribuciones
- **Arquitectura**: Hexagonal (Ports & Adapters)
- **Framework**: Flask 3.0.0

## 📞 Soporte

Para dudas o problemas:
1. Revisar documentación en `/docs`
2. Consultar issues en el repositorio
3. Contactar al equipo de desarrollo

---

## 🎉 ¡Gracias por usar Yedistribuciones!

**Sistema de Gestión de Rutas con Arquitectura Hexagonal**

*Desarrollado con 💙 usando Flask y buenas prácticas de arquitectura de software*
