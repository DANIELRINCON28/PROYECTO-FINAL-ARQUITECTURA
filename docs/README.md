🚚 Yedistribuciones - Sistema de Gestión de Rutas
📘 Descripción del Proyecto

Sistema de software para optimizar los procesos logísticos y administrativos de Yedistribuciones, implementando el módulo central de Gestión de Rutas.

🧩 Arquitectura

El proyecto implementa una Arquitectura Hexagonal (Puertos y Adaptadores) con estricta separación de responsabilidades.

┌─────────────────────────────────────────────────────────┐
│                  ADAPTADORES CONDUCTORES                │
│                  (Driving Adapters)                     │
│                                                         │
│              ┌──────────────────────┐                   │
│              │   Streamlit UI       │                   │
│              └──────────────────────┘                   │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  CAPA DE APLICACIÓN                     │
│                  (Application Layer)                    │
│                                                         │
│              ┌──────────────────────┐                   │
│              │   RouteService       │                   │
│              │   (Casos de Uso)     │                   │
│              └──────────────────────┘                   │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  CAPA DE DOMINIO                        │
│                  (Domain Layer - El Hexágono)           │
│                                                         │
│     ┌────────────────┐      ┌────────────────────┐     │
│     │  Route Model   │      │  RouteRepository   │     │
│     │  Client Model  │      │  Port (Interface)  │     │
│     └────────────────┘      └────────────────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  ADAPTADORES CONDUCIDOS                 │
│                  (Driven Adapters)                      │
│                                                         │
│              ┌──────────────────────┐                   │
│              │ SQLite Repository    │                   │
│              └──────────────────────┘                   │
└─────────────────────────────────────────────────────────┘

⚙️ Principios Aplicados

SOLID – Inversión de Dependencias (DIP)

DRY – Don't Repeat Yourself

KISS – Keep It Simple, Stupid

Separación de Conceptos – Cada capa tiene una única responsabilidad

Alta Cohesión y Bajo Acoplamiento

🧱 Estructura del Proyecto
yedistribuciones_project/
├── src/
│   ├── domain/                    # Núcleo de negocio (El Hexágono)
│   │   ├── models/
│   │   │   ├── route.py           # Modelo Route con lógica de negocio
│   │   │   └── client.py          # Modelo Client
│   │   └── ports/
│   │       └── route_repository_port.py
│   │
│   ├── application/               # Casos de Uso
│   │   ├── services/
│   │   │   └── route_service.py
│   │   └── dtos.py
│   │
│   └── infrastructure/
│       ├── persistence/
│       │   └── sqlite_route_repository.py
│       └── ui/
│           └── streamlit_app.py
│
├── tests/
├── main.py
├── requirements.txt
└── README.md

🧰 Stack Tecnológico

Lenguaje: Python 3.9+

Framework UI: Streamlit

Base de Datos: SQLite

Tipado: Type Hints (mypy compatible)

✅ Requisitos Funcionales Implementados
Código	Descripción	Estado
RF-RUT-01	Crear nueva ruta	✅
RF-RUT-02	Asignar clientes a rutas	✅
RF-RUT-03	Reordenar clientes en rutas	✅
RF-RUT-04	Visualizar todas las rutas	✅
RF-RUT-06	Dividir ruta en dos	✅
RF-RUT-07	Fusionar dos rutas	✅
⚡ Requisitos No Funcionales

RNF-RUT-01: ✅ Interfaz simple e intuitiva (Streamlit)

RNF-RUT-02: ✅ Tiempo de respuesta < 2 segundos (índices en BD)

RNF-RUT-03: ✅ Integridad transaccional (transacciones SQLite)

🛠️ Instalación
1. Clonar el repositorio
git clone https://github.com/<usuario>/yedistribuciones.git
cd yedistribuciones

2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

3. Instalar dependencias
pip install -r requirements.txt

▶️ Ejecución

Iniciar la aplicación:

streamlit run main.py


Abrirá automáticamente http://localhost:8501.

🧭 Uso de la Aplicación
➕ Crear Nueva Ruta

Ir a "Crear Nueva Ruta"

Completar el formulario:

Nombre de la ruta

CEDIS

Día de la semana

Clic en "Crear Ruta"

✏️ Gestionar Clientes

Ir a "Gestionar Clientes en Ruta"

Seleccionar una ruta

Acciones: agregar, eliminar o reordenar clientes

✂️ Dividir Ruta

Seleccionar ruta

Elegir punto de división

Asignar nombres y confirmar

🔗 Fusionar Rutas

Seleccionar dos rutas compatibles

Asignar nombre y confirmar

🧪 Testing

Ejecutar pruebas:

pytest tests/


Con cobertura:

pytest --cov=src tests/

🧾 Validación de Tipos
mypy src/

💾 Base de Datos

El archivo yedistribuciones.db se crea automáticamente al iniciar la app.

Esquema
Campo	Tipo	Descripción
id	TEXT	Primary Key
name	TEXT	Nombre de la ruta
cedis_id	TEXT	Identificador del CEDIS
day_of_week	TEXT	Día asignado
client_ids	TEXT (JSON)	Clientes asociados
is_active	INTEGER	1 = activa
created_at	TIMESTAMP	Creación
updated_at	TIMESTAMP	Actualización
🧭 Flujo de Dependencias
UI (Streamlit) → RouteService → RouteRepositoryPort ← SqliteRouteRepository
                      ↓
                 Route (Domain)


El dominio no conoce la infraestructura. La inversión de dependencias se logra mediante RouteRepositoryPort.

🔄 Ejemplo de DIP (Dependency Inversion Principle)
# ❌ INCORRECTO - Dependencia directa
class RouteService:
    def __init__(self):
        self.repo = SqliteRouteRepository()  # Acoplamiento fuerte

# ✅ CORRECTO - Dependencia invertida
class RouteService:
    def __init__(self, repository: RouteRepositoryPort):
        self._repository = repository  # Depende de abstracción

👨‍💻 Autor

Proyecto desarrollado como parte del curso de Arquitectura de Sistemas.

📄 Licencia

Proyecto educativo - Uso académico.
