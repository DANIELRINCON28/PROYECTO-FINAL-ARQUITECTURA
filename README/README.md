# 🚚 Yedistribuciones - Sistema de Gestión de Rutas


## Descripción del Proyecto


Sistema de software para optimizar los procesos logísticos y administrativos de Yedistribuciones, implementando el módulo central de **Gestión de Rutas**.


## Arquitectura


Este proyecto implementa una **Arquitectura Hexagonal (Puertos y Adaptadores)** con estricta separación de responsabilidades:



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



### Principios Aplicados


- **SOLID**: Especialmente Inversión de Dependencias (DIP)
  
- **DRY**: Don't Repeat Yourself
  
- **KISS**: Keep It Simple, Stupid
  
- **Separación de Conceptos**: Cada capa con responsabilidad única
  
- **Alta Cohesión y Bajo Acoplamiento**
  

## Estructura del Proyecto



yedistribuciones_project/
├── src/
│   ├── domain/                    # Núcleo de negocio (El Hexágono)
│   │   ├── models/                # Entidades del dominio
│   │   │   ├── route.py          # Modelo Route con lógica de negocio
│   │   │   └── client.py         # Modelo Client
│   │   └── ports/                 # Puertos de salida (interfaces)
│   │       └── route_repository_port.py
│   │
│   ├── application/               # Lógica de aplicación (Casos de Uso)
│   │   ├── services/
│   │   │   └── route_service.py  # Orquestación de casos de uso
│   │   └── dtos.py               # Data Transfer Objects
│   │
│   └── infrastructure/            # Implementaciones tecnológicas
│       ├── persistence/           # Adaptadores de BD (Conducidos)
│       │   └── sqlite_route_repository.py
│       └── ui/                    # Adaptadores de UI (Conductores)
│           └── streamlit_app.py
│
├── tests/                         # Pruebas
├── main.py                        # Punto de entrada y DI
├── requirements.txt               # Dependencias
└── README.md                      # Este archivo



## Stack Tecnológico


- **Lenguaje**: Python 3.9+
  
- **Framework de UI**: Streamlit
  
- **Base de Datos**: SQLite
  
- **Type Hints**: Tipado estático completo
  

## Requisitos Funcionales Implementados


- **RF-RUT-01**: ✅ Crear nueva ruta
  
- **RF-RUT-02**: ✅ Asignar clientes a rutas
  
- **RF-RUT-03**: ✅ Reordenar clientes en rutas
  
- **RF-RUT-04**: ✅ Visualizar todas las rutas
  
- **RF-RUT-06**: ✅ Dividir ruta en dos
  
- **RF-RUT-07**: ✅ Fusionar dos rutas
  

## Requisitos No Funcionales


- **RNF-RUT-01**: ✅ Interfaz simple e intuitiva (Streamlit)
  
- **RNF-RUT-02**: ✅ Respuesta < 2 segundos (índices en BD)
  
- **RNF-RUT-03**: ✅ Integridad transaccional (transacciones SQLite)
  

## Instalación


1. **Clonar o descargar el proyecto**


2. **Crear entorno virtual (recomendado)**


powershell
python -m venv venv
.\venv\Scripts\Activate.ps1


3. **Instalar dependencias**

powershell
pip install -r requirements.txt



## Ejecución


Para iniciar la aplicación:


powershell
streamlit run main.py


La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`


## Uso de la Aplicación


### Crear una Nueva Ruta


1. Ir a **"➕ Crear Nueva Ruta"**
   
2. Completar el formulario:
   - Nombre de la ruta
     
   - CEDIS
     
   - Día de la semana
     
3. Hacer clic en **"✅ Crear Ruta"**


### Gestionar Clientes


1. Ir a **"✏️ Gestionar Clientes en Ruta"**
   
2. Seleccionar una ruta
   
3. Opciones disponibles:
   
   - Agregar cliente
     
   - Eliminar cliente
     
   - Reordenar clientes


### Dividir una Ruta

1. Ir a **"✂️ Dividir Ruta"**
   
2. Seleccionar la ruta a dividir
   
3. Elegir el punto de división

4. Asignar nombres a las nuevas rutas
 
5. Confirmar la división


### Fusionar Rutas


1. Ir a **"🔗 Fusionar Rutas"**
  
2. Seleccionar dos rutas compatibles (mismo CEDIS y día)
  
3. Asignar nombre a la ruta fusionada
  
4. Confirmar la fusión

## Testing


Para ejecutar las pruebas (cuando estén implementadas):


powershell
pytest tests/



Para verificar cobertura:


powershell
pytest --cov=src tests/



## Validación de Tipos


Para validar el tipado estático:


powershell
mypy src/



## Base de Datos


La base de datos SQLite (`yedistribuciones.db`) se crea automáticamente al iniciar la aplicación por primera vez en el directorio raíz del proyecto.


### Esquema

**Tabla `routes`:**
- `id` (TEXT, PRIMARY KEY)
- `name` (TEXT)
- `cedis_id` (TEXT)
- `day_of_week` (TEXT)
- `client_ids` (TEXT, JSON)
- `is_active` (INTEGER, 1/0)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## Arquitectura Hexagonal - Flujo de Dependencias



UI (Streamlit) → RouteService → RouteRepositoryPort ← SqliteRouteRepository
                      ↓
                 Route (Domain)


**Importante**: El dominio NO conoce la infraestructura. La inversión de dependencias se logra mediante el puerto `RouteRepositoryPort`.


## Principio de Inversión de Dependencias (DIP)

python
# ❌ INCORRECTO - Dependencia directa
class RouteService:
    def __init__(self):
        self.repo = SqliteRouteRepository()  # Acoplamiento fuerte

# ✅ CORRECTO - Dependencia invertida
class RouteService:
    def __init__(self, repository: RouteRepositoryPort):
        self._repository = repository  # Depende de abstracción


## Autor

Proyecto desarrollado como parte del curso de Arquitectura de Sistemas.

## Licencia

Proyecto educativo - Uso académico.
#   P R O Y E C T O - F I N A L - A R Q U I T E C T U R A 
 
 


