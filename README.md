# 🚚 Yedistribuciones - Sistema de Gestión de Rutas

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Architecture](https://img.shields.io/badge/architecture-hexagonal-purple.svg)

Sistema empresarial de gestión y optimización de rutas de distribución, diseñado con **Arquitectura Hexagonal** y principios **SOLID**.

---

## 📋 Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Características Principales](#-características-principales)
3. [Arquitectura del Sistema](#-arquitectura-del-sistema)
4. [Estructura del Proyecto](#-estructura-del-proyecto)
5. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
6. [Instalación](#-instalación)
7. [Configuración](#-configuración)
8. [Uso](#-uso)
9. [API REST](#-api-rest)
10. [Patrones de Diseño](#-patrones-de-diseño)
11. [Testing](#-testing)
12. [Documentación Adicional](#-documentación-adicional)
13. [Contribución](#-contribución)
14. [Licencia](#-licencia)

---

## 🎯 Descripción General

**Yedistribuciones** es una solución empresarial para la gestión integral de rutas de distribución, permitiendo a empresas de logística optimizar sus operaciones de entrega mediante:

- **Gestión centralizada** de rutas por CEDIS (Centros de Distribución)
- **Optimización inteligente** de rutas usando algoritmos avanzados
- **Asignación flexible** de clientes a rutas
- **Operaciones avanzadas** como división y fusión de rutas
- **Integración con Google Maps** para optimización en tiempo real
- **Interfaz web moderna** y API REST

### Caso de Uso Principal

Empresas de distribución que necesitan:
- Planificar rutas semanales por día y CEDIS
- Optimizar el orden de visitas a clientes
- Gestionar cambios dinámicos en las rutas
- Visualizar y analizar métricas de distribución

---

## ✨ Características Principales

### 🗺️ Gestión de Rutas

- ✅ **Crear rutas** por CEDIS y día de la semana
- ✅ **Asignar/desasignar clientes** a rutas
- ✅ **Reordenar clientes** manualmente o automáticamente
- ✅ **Dividir rutas** cuando exceden capacidad
- ✅ **Fusionar rutas** para optimizar recursos
- ✅ **Eliminar rutas** con confirmación de seguridad
- ✅ **Filtrar rutas** por CEDIS y día

### 🎯 Optimización Inteligente

- 🚀 **Algoritmo Nearest Neighbor** (Greedy) - Rápido y eficiente
- 🌐 **Google Maps Optimization** - Considerando tráfico real
- 🔄 **2-Opt Algorithm** - Balance entre precisión y velocidad
- 📊 **Métricas de optimización** - Ahorro de distancia y tiempo

### 👥 Gestión de Clientes

- 📋 Listado de clientes disponibles
- 🔍 Búsqueda y filtrado de clientes
- 📍 Geocodificación de direcciones
- 📞 Información de contacto completa

### 📊 Dashboard y Reportes

- 📈 Estadísticas generales del sistema
- 📉 Distribución de rutas por CEDIS
- 🎨 Visualizaciones interactivas
- 📱 Diseño responsivo (móvil/tablet/desktop)

---

## 🏛️ Arquitectura del Sistema

### Arquitectura Hexagonal (Ports & Adapters)

El sistema implementa **Arquitectura Hexagonal** para lograr:

```
┌─────────────────────────────────────────────────────────┐
│                   DRIVING ADAPTERS                       │
│              (Adaptadores de Entrada)                    │
│                                                          │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│   │  Flask   │  │Streamlit │  │   CLI    │             │
│   │   API    │  │    UI    │  │          │             │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘             │
└────────┼─────────────┼─────────────┼────────────────────┘
         │             │             │
         ▼             ▼             ▼
┌─────────────────────────────────────────────────────────┐
│               APPLICATION LAYER                          │
│            (Casos de Uso y DTOs)                         │
│                                                          │
│  ┌──────────────────────────────────────┐               │
│  │     RouteService                     │               │
│  │     RouteOptimizationService         │               │
│  └──────────────────────────────────────┘               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  DOMAIN LAYER                            │
│            (Lógica de Negocio Pura)                      │
│                                                          │
│  ┌─────────┐        ┌──────────────┐                    │
│  │  Route  │        │    PORTS     │                    │
│  │ (Entity)│        │ (Interfaces) │                    │
│  └─────────┘        └──────────────┘                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  DRIVEN ADAPTERS                         │
│              (Adaptadores de Salida)                     │
│                                                          │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│   │PostgreSQL│  │  SQLite  │  │  Google  │             │
│   │Repository│  │Repository│  │   Maps   │             │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘             │
└────────┼─────────────┼─────────────┼────────────────────┘
         │             │             │
         ▼             ▼             ▼
    PostgreSQL     SQLite DB    Google Maps API
```

### Principios SOLID Aplicados

| Principio | Implementación |
|-----------|----------------|
| **S**ingle Responsibility | Cada clase tiene una única responsabilidad |
| **O**pen/Closed | Extensible mediante puertos sin modificar código |
| **L**iskov Substitution | Adaptadores intercambiables (PostgreSQL ↔ SQLite) |
| **I**nterface Segregation | Puertos específicos por funcionalidad |
| **D**ependency Inversion | Dependencias hacia abstracciones (puertos) |

📖 **Documentación completa:** [`docs/HEXAGONAL_ARCHITECTURE.md`](docs/HEXAGONAL_ARCHITECTURE.md)

---

## 📁 Estructura del Proyecto

```
PROYECTO-FINAL-ARQUITECTURA/
│
├── 📄 main.py                          # Punto de entrada principal
├── 📄 main_flask.py                    # Punto de entrada Flask
├── 📄 config.py                        # Configuración centralizada
├── 📄 requirements.txt                 # Dependencias Python
├── 📄 .env                            # Variables de entorno (no versionado)
│
├── 📂 src/                            # Código fuente principal
│   │
│   ├── 📂 domain/                     # 🟢 CAPA DE DOMINIO
│   │   ├── 📂 models/                # Entidades del dominio
│   │   │   ├── route.py              # Entidad Route (lógica de negocio)
│   │   │   ├── client.py             # Entidad Client
│   │   │   └── models.py             # Otros modelos
│   │   │
│   │   ├── 📂 ports/                 # Interfaces (contratos)
│   │   │   ├── route_repository_port.py      # Puerto de persistencia
│   │   │   └── route_optimization_port.py    # Puerto de optimización
│   │   │
│   │   ├── 📂 builders/              # Patrón Builder
│   │   │   └── route_builder.py     # Constructor de rutas
│   │   │
│   │   └── 📂 strategies/            # Patrón Strategy
│   │       └── optimization_strategy.py  # Estrategias de optimización
│   │
│   ├── 📂 application/               # 🟡 CAPA DE APLICACIÓN
│   │   ├── 📂 services/              # Servicios (casos de uso)
│   │   │   ├── route_service.py             # Servicio de rutas
│   │   │   └── route_optimization_service.py # Servicio de optimización
│   │   │
│   │   ├── 📂 factories/             # Patrón Factory
│   │   │   └── service_factory.py   # Fábrica de servicios
│   │   │
│   │   └── dtos.py                   # Data Transfer Objects
│   │
│   └── 📂 infrastructure/            # 🔴 CAPA DE INFRAESTRUCTURA
│       │
│       ├── 📂 database/              # Gestión de BD
│       │   └── database_connection.py  # Singleton de conexión
│       │
│       ├── 📂 persistence/           # Adaptadores de persistencia
│       │   ├── postgres_route_repository.py  # Implementación PostgreSQL
│       │   └── sqlite_route_repository.py    # Implementación SQLite
│       │
│       ├── 📂 services/              # Adaptadores de servicios externos
│       │   └── google_maps_service.py  # Integración Google Maps
│       │
│       └── 📂 ui/                    # Adaptadores de UI
│           ├── flask_app.py          # API REST con Flask
│           ├── streamlit_app.py      # UI Web con Streamlit
│           ├── ui_components.py      # Componentes reutilizables
│           │
│           ├── 📂 templates/         # Plantillas HTML
│           │   ├── base.html
│           │   ├── dashboard.html
│           │   ├── routes_list.html
│           │   ├── route_detail.html
│           │   ├── create_route.html
│           │   ├── divide_route.html
│           │   ├── merge_routes.html
│           │   ├── optimize_route.html
│           │   └── manage_clients.html
│           │
│           └── 📂 static/            # Archivos estáticos
│               ├── css/
│               │   └── style.css
│               └── js/
│                   └── main.js
│
├── 📂 scripts/                       # Scripts de utilidad
│   ├── initialize_database.py        # Inicializar esquema de BD
│   ├── init_sample_data.py           # Datos de prueba
│   ├── reset_and_populate_db.py      # Resetear y poblar BD
│   ├── migrate_data.py               # Migración de datos
│   └── clean_and_populate_database.py
│
├── 📂 tests/                         # Pruebas unitarias
│   ├── domain/
│   │   └── test_route_model.py
│   └── __init__.py
│
├── 📂 docs/                          # Documentación técnica
│   ├── HEXAGONAL_ARCHITECTURE.md    # Documentación de arquitectura
│   ├── DESIGN_PATTERNS.md            # Patrones de diseño implementados
│   ├── API_DOCUMENTATION.md          # Documentación de API REST
│   ├── ARCHITECTURE_DIAGRAM.md       # Diagramas de arquitectura
│   ├── DATABASE_SCHEMA.md            # Esquema de base de datos
│   ├── QUICKSTART.md                 # Guía de inicio rápido
│   └── ...                           # Más documentación
│
└── 📂 ADL/                           # Architecture Decision Log
    ├── INDICE_ADL.md                 # Índice de decisiones
    └── ...                           # Decisiones arquitectónicas
```

### Convenciones de Colores por Capa

- 🟢 **Verde** - Domain Layer (Lógica de Negocio Pura)
- 🟡 **Amarillo** - Application Layer (Casos de Uso)
- 🔴 **Rojo** - Infrastructure Layer (Detalles Técnicos)

---

## 🛠️ Tecnologías Utilizadas

### Backend

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Python** | 3.8+ | Lenguaje principal |
| **Flask** | 2.3+ | Framework web para API REST |
| **PostgreSQL** | 14+ | Base de datos principal |
| **SQLite** | 3.x | Base de datos alternativa |
| **psycopg2** | 2.9+ | Driver PostgreSQL |
| **googlemaps** | 4.10+ | Integración Google Maps API |
| **python-dotenv** | 1.0+ | Gestión de variables de entorno |

### Frontend

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Bootstrap** | 5.3+ | Framework CSS |
| **Font Awesome** | 6.4+ | Iconografía |
| **Chart.js** | 4.0+ | Gráficos y visualizaciones |
| **JavaScript (Vanilla)** | ES6+ | Interactividad |

### Herramientas de Desarrollo

- **Git** - Control de versiones
- **VS Code** - Editor recomendado
- **Postman** - Testing de API
- **DBeaver** - Gestión de BD

---

## 🚀 Instalación

### Prerrequisitos

```bash
# Python 3.8 o superior
python --version

# PostgreSQL 14 o superior
psql --version

# pip actualizado
pip install --upgrade pip
```

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/DANIELRINCON28/PROYECTO-FINAL-ARQUITECTURA.git
cd PROYECTO-FINAL-ARQUITECTURA
```

### Paso 2: Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Base de Datos

#### Opción A: PostgreSQL (Recomendado para Producción)

```bash
# Crear base de datos
createdb RutasDB

# O desde psql
psql -U postgres
CREATE DATABASE RutasDB;
\q
```

#### Opción B: SQLite (Para Desarrollo)

```bash
# No requiere configuración previa
# Se crea automáticamente al ejecutar
```

### Paso 5: Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Base de Datos
DB_TYPE=postgres              # 'postgres' o 'sqlite'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=RutasDB
DB_USER=postgres
DB_PASSWORD=tu_contraseña

# Google Maps API (Opcional)
GOOGLE_MAPS_API_KEY=tu_api_key_aqui

# Configuración del CEDIS
CEDIS_LATITUDE=4.7110
CEDIS_LONGITUDE=-74.0721
CEDIS_ADDRESS=Bogotá, Colombia

# Flask
FLASK_PORT=5000
DEBUG=True
```

### Paso 6: Inicializar Base de Datos

```bash
# Crear esquema y datos de ejemplo
python scripts/reset_and_populate_db.py
```

### Paso 7: Ejecutar la Aplicación

```bash
# Opción 1: Flask (API + Web UI)
python main_flask.py

# Opción 2: Main principal
python main.py

# Opción 3: Solo Streamlit
python -m streamlit run src/infrastructure/ui/streamlit_app.py
```

### Paso 8: Acceder a la Aplicación

- **Web UI:** http://localhost:5000
- **API REST:** http://localhost:5000/api
- **Streamlit:** http://localhost:8501 (si se ejecuta)

---

## ⚙️ Configuración

### Configuración de PostgreSQL

```python
# config.py
class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'RutasDB')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
```

### Configuración de Google Maps

1. Obtener API Key desde [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar APIs:
   - Directions API
   - Geocoding API
   - Distance Matrix API
3. Agregar la key al archivo `.env`

```env
GOOGLE_MAPS_API_KEY=AIzaSy...
```

### Configuración de CEDIS

Configurar las coordenadas del centro de distribución:

```env
CEDIS_LATITUDE=4.7110
CEDIS_LONGITUDE=-74.0721
CEDIS_ADDRESS=Bogotá, Colombia
```

---

## 💻 Uso

### Interfaz Web

#### 1. Dashboard Principal

![Dashboard](docs/images/dashboard.png)

- Visualiza estadísticas generales
- Distribución de rutas por CEDIS
- Rutas recientes

#### 2. Gestión de Rutas

**Crear Nueva Ruta:**
```
1. Click en "➕ Crear Ruta"
2. Ingresar nombre, CEDIS y día
3. Guardar
```

**Asignar Clientes:**
```
1. Abrir detalle de ruta
2. Click en "➕ Añadir Clientes"
3. Seleccionar clientes
4. Confirmar
```

**Optimizar Ruta:**
```
1. Abrir detalle de ruta con clientes
2. Click en "🎯 Optimizar Ruta"
3. Revisar resultado de optimización
4. Aplicar cambios
```

**Dividir Ruta:**
```
1. Abrir ruta con múltiples clientes
2. Click en "✂️ Dividir Ruta"
3. Seleccionar punto de división
4. Ingresar nombres para ambas rutas
5. Confirmar
```

### API REST

#### Autenticación

Actualmente no requiere autenticación (desarrollo).

#### Endpoints Principales

```bash
# Listar todas las rutas
GET /api/routes

# Obtener ruta específica
GET /api/routes/{route_id}

# Crear ruta
POST /routes/create
Content-Type: application/x-www-form-urlencoded
Body: name=Ruta Norte&cedis_id=13&day_of_week=LUNES

# Asignar cliente a ruta
POST /api/routes/{route_id}/clients
Content-Type: application/json
Body: {"client_id": "CLI_001"}

# Eliminar cliente de ruta
DELETE /api/routes/{route_id}/clients/{client_id}

# Optimizar ruta
POST /api/routes/{route_id}/optimize
Content-Type: application/json
Body: {
  "clients": [...],
  "origin": {"latitude": 4.71, "longitude": -74.07}
}

# Dividir ruta
POST /api/routes/divide
Content-Type: application/json
Body: {
  "route_id": "...",
  "split_point": 5,
  "name_a": "Ruta A",
  "name_b": "Ruta B"
}

# Eliminar ruta
DELETE /api/routes/{route_id}
```

📖 **Documentación completa de API:** [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md)

### Ejemplos con cURL

```bash
# Obtener todas las rutas
curl -X GET http://localhost:5000/api/routes

# Crear cliente en ruta
curl -X POST http://localhost:5000/api/routes/550e8400-e29b-41d4-a716-446655440000/clients \
  -H "Content-Type: application/json" \
  -d '{"client_id": "CLI_001"}'

# Eliminar ruta
curl -X DELETE http://localhost:5000/api/routes/550e8400-e29b-41d4-a716-446655440000
```

### Ejemplos con Python

```python
import requests

BASE_URL = "http://localhost:5000"

# Obtener todas las rutas
response = requests.get(f"{BASE_URL}/api/routes")
routes = response.json()['data']

for route in routes:
    print(f"{route['name']}: {route['client_count']} clientes")

# Asignar cliente
route_id = "550e8400-e29b-41d4-a716-446655440000"
client_id = "CLI_001"

response = requests.post(
    f"{BASE_URL}/api/routes/{route_id}/clients",
    json={"client_id": client_id}
)

if response.json()['success']:
    print("✅ Cliente asignado exitosamente")
```

---

## 🎨 Patrones de Diseño

El proyecto implementa múltiples patrones de diseño:

### Patrones Implementados

| Patrón | Ubicación | Propósito |
|--------|-----------|-----------|
| **Hexagonal Architecture** | Estructura completa | Arquitectura base |
| **Repository Pattern** | `domain/ports/` | Abstracción de persistencia |
| **Adapter Pattern** | `infrastructure/` | Integración con tecnologías |
| **Strategy Pattern** | `domain/strategies/` | Algoritmos de optimización |
| **Factory Pattern** | `application/factories/` | Creación de servicios |
| **Builder Pattern** | `domain/builders/` | Construcción de entidades |
| **Singleton Pattern** | `infrastructure/database/` | Conexión única a BD |
| **DTO Pattern** | `application/dtos.py` | Transferencia de datos |
| **Service Layer** | `application/services/` | Casos de uso |
| **Dependency Injection** | Manual en constructores | Inversión de dependencias |

📖 **Documentación completa:** [`docs/DESIGN_PATTERNS.md`](docs/DESIGN_PATTERNS.md)

---

## 🧪 Testing

### Estructura de Tests

```
tests/
├── domain/
│   └── test_route_model.py          # Tests de entidades
├── application/
│   └── test_route_service.py        # Tests de servicios
└── infrastructure/
    └── test_postgres_repository.py  # Tests de adaptadores
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Solo tests de dominio
pytest tests/domain/

# Con output detallado
pytest -v -s
```

### Ejemplo de Test

```python
def test_route_add_client():
    """Test de lógica de dominio pura."""
    route = Route(
        id="1",
        name="Test Route",
        cedis_id="CEDIS_1",
        day_of_week="LUNES",
        client_ids=[]
    )
    
    # Agregar cliente
    route.add_client("CLI_001")
    assert len(route.client_ids) == 1
    
    # Validar no duplicados
    with pytest.raises(ValueError):
        route.add_client("CLI_001")
```

---

## 📚 Documentación Adicional

### Documentos Principales

| Documento | Descripción |
|-----------|-------------|
| [`HEXAGONAL_ARCHITECTURE.md`](docs/HEXAGONAL_ARCHITECTURE.md) | Arquitectura hexagonal completa |
| [`DESIGN_PATTERNS.md`](docs/DESIGN_PATTERNS.md) | Patrones de diseño implementados |
| [`API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) | Documentación completa de API REST |
| [`DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) | Esquema de base de datos |
| [`QUICKSTART.md`](docs/QUICKSTART.md) | Guía de inicio rápido |

### ADL (Architecture Decision Log)

Registro de decisiones arquitectónicas importantes:

- [`ADL/INDICE_ADL.md`](ADL/INDICE_ADL.md) - Índice de decisiones
- [`ADL/Analisis_ADL.md`](ADL/Analisis_ADL.md) - Análisis de decisiones

---

## 🤝 Contribución

### Guía de Contribución

1. **Fork** el repositorio
2. **Crea** una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre** un Pull Request

### Estándares de Código

- Seguir **PEP 8** para Python
- Documentar funciones con **docstrings**
- Escribir **tests** para nuevas funcionalidades
- Mantener la **arquitectura hexagonal**
- Respetar los **principios SOLID**

### Reporte de Bugs

Usa el template de issues de GitHub e incluye:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Screenshots si aplica
- Versión de Python y dependencias

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [`LICENSE`](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2025 Yedistribuciones

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👥 Autores

- **Daniel Rincón** - [@DANIELRINCON28](https://github.com/DANIELRINCON28)
- **Equipo Yedistribuciones**

---

## 🙏 Agradecimientos

- **Alistair Cockburn** - Por el patrón Hexagonal Architecture
- **Robert C. Martin** - Por Clean Architecture y SOLID
- **Eric Evans** - Por Domain-Driven Design
- Comunidad de Python y Flask
- Contributors del proyecto

---

## 📞 Soporte

- **Issues:** [GitHub Issues](https://github.com/DANIELRINCON28/PROYECTO-FINAL-ARQUITECTURA/issues)
- **Documentación:** [`docs/`](docs/)
- **Email:** soporte@yedistribuciones.com

---

## 🔄 Changelog

### Version 1.0.0 (Noviembre 2025)

#### Añadido
- ✅ Sistema completo de gestión de rutas
- ✅ Arquitectura hexagonal
- ✅ Integración con PostgreSQL
- ✅ API REST completa
- ✅ Optimización con Google Maps
- ✅ División y fusión de rutas
- ✅ Eliminación de rutas con confirmación
- ✅ Dashboard con métricas
- ✅ Diseño responsivo

#### Patrones Implementados
- ✅ Repository Pattern
- ✅ Adapter Pattern
- ✅ Strategy Pattern
- ✅ Factory Pattern
- ✅ Builder Pattern
- ✅ Singleton Pattern

---

## 🎓 Recursos de Aprendizaje

### Tutoriales

1. [Inicio Rápido](docs/QUICKSTART.md)
2. [Arquitectura Hexagonal](docs/HEXAGONAL_ARCHITECTURE.md)
3. [Patrones de Diseño](docs/DESIGN_PATTERNS.md)
4. [API REST](docs/API_DOCUMENTATION.md)

### Videos

- 🎥 [Introducción a Arquitectura Hexagonal](#)
- 🎥 [Demo del Sistema](#)
- 🎥 [Configuración Paso a Paso](#)

---

## 📊 Estadísticas del Proyecto

```
📁 Archivos: 80+
💻 Líneas de Código: 10,000+
📝 Líneas de Documentación: 5,000+
🧪 Tests: 25+
⭐ GitHub Stars: [Actualizar]
🍴 Forks: [Actualizar]
```

---

## 🗺️ Roadmap

### Version 1.1 (Próxima)

- [ ] Autenticación y autorización (JWT)
- [ ] Sistema de roles y permisos
- [ ] Exportación de reportes (PDF, Excel)
- [ ] Notificaciones en tiempo real
- [ ] Integración con Waze
- [ ] App móvil (React Native)

### Version 2.0 (Futuro)

- [ ] Machine Learning para predicción de rutas
- [ ] Integración con ERP
- [ ] Sistema de tracking GPS en tiempo real
- [ ] Análisis predictivo de demanda
- [ ] Microservicios

---

<div align="center">

**⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub ⭐**

Hecho con ❤️ por el equipo de Yedistribuciones

[🏠 Website](#) • [📧 Email](mailto:info@yedistribuciones.com) • [💼 LinkedIn](#) • [🐦 Twitter](#)

</div>

---

**© 2025 Yedistribuciones. Todos los derechos reservados.**
