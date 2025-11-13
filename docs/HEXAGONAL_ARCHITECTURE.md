# 🏛️ Arquitectura Hexagonal - Yedistribuciones

## Índice
1. [Introducción](#introducción)
2. [Principios Fundamentales](#principios-fundamentales)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Capas de la Arquitectura](#capas-de-la-arquitectura)
5. [Puertos y Adaptadores](#puertos-y-adaptadores)
6. [Flujo de Datos](#flujo-de-datos)
7. [Implementación Práctica](#implementación-práctica)
8. [Ventajas y Beneficios](#ventajas-y-beneficios)
9. [Casos de Uso Reales](#casos-de-uso-reales)

---

## 📚 Introducción {#introducción}

### ¿Qué es la Arquitectura Hexagonal?

La **Arquitectura Hexagonal** (también conocida como **Ports & Adapters**) es un patrón arquitectónico propuesto por **Alistair Cockburn** que busca crear aplicaciones débilmente acopladas y altamente mantenibles.

### Objetivo Principal

> **Aislar la lógica de negocio del dominio de los detalles técnicos de infraestructura.**

### Metáfora del Hexágono

```
           Adaptadores de Entrada
                   │
                   ▼
    ┌──────────────────────────────┐
    │                              │
    │    ┌──────────────────┐      │
    │    │                  │      │
◄───┤────│   DOMAIN CORE    │──────┤───►
    │    │  (Lógica de      │      │
    │    │   Negocio)       │      │
    │    └──────────────────┘      │
    │                              │
    └──────────────────────────────┘
                   ▲
                   │
           Adaptadores de Salida
```

El hexágono representa que la aplicación tiene **múltiples caras** (lados) por donde puede interactuar con el exterior.

---

## 🎯 Principios Fundamentales {#principios-fundamentales}

### 1. Separación de Responsabilidades

Cada capa tiene una responsabilidad clara y única:

| Capa | Responsabilidad | ¿Qué NO hace? |
|------|----------------|---------------|
| **Domain** | Lógica de negocio pura | No conoce bases de datos ni frameworks |
| **Application** | Casos de uso y orquestación | No implementa persistencia |
| **Infrastructure** | Detalles técnicos | No contiene lógica de negocio |

### 2. Regla de Dependencias

```
Infrastructure ──► Application ──► Domain
                                    ▲
                              (Nunca depende
                              de nadie más)
```

**Regla de Oro:** Las dependencias siempre apuntan **hacia adentro** (hacia el dominio).

### 3. Inversión de Dependencias (SOLID - DIP)

```python
# ❌ MAL: Dependencia directa
class RouteService:
    def __init__(self):
        self.repository = PostgresRouteRepository()  # Acoplamiento

# ✅ BIEN: Depende de abstracción
class RouteService:
    def __init__(self, repository: RouteRepositoryPort):
        self._repository = repository  # Inyección de dependencias
```

### 4. Testabilidad

Cada capa puede ser testeada independientemente mediante mocks.

---

## 🗂️ Estructura del Proyecto {#estructura-del-proyecto}

### Vista General

```
src/
├── domain/                    # 🟢 NÚCLEO (Lógica de Negocio)
│   ├── models/               # Entidades del dominio
│   │   ├── route.py         # Entidad Route con lógica
│   │   ├── client.py        # Entidad Client
│   │   └── models.py        # Otros modelos
│   │
│   └── ports/               # 🔌 PUERTOS (Interfaces)
│       ├── route_repository_port.py
│       └── route_optimization_port.py
│
├── application/              # 🟡 CASOS DE USO
│   ├── services/
│   │   ├── route_service.py           # Orquestación
│   │   └── route_optimization_service.py
│   │
│   ├── dtos.py              # Data Transfer Objects
│   └── factories/           # Fábricas de servicios
│
└── infrastructure/           # 🔴 DETALLES TÉCNICOS
    ├── persistence/         # 🔌 Adaptadores de BD
    │   ├── postgres_route_repository.py
    │   └── sqlite_route_repository.py
    │
    ├── services/           # 🔌 Adaptadores de servicios externos
    │   └── google_maps_service.py
    │
    └── ui/                 # 🔌 Adaptadores de UI
        ├── flask_app.py    # API REST
        └── streamlit_app.py # UI Web
```

### Mapeo a Capas Hexagonales

```
┌─────────────────────────────────────────────────────────┐
│                    DRIVING ADAPTERS                      │
│              (Adaptadores de Entrada)                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Flask API   │  │  Streamlit   │  │   CLI        │  │
│  │  (REST)      │  │  (Web UI)    │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                 │                  │           │
└─────────┼─────────────────┼──────────────────┼───────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                       │
│                   (Casos de Uso)                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │          RouteService                            │   │
│  │  - create_route()                                │   │
│  │  - assign_client_to_route()                      │   │
│  │  - divide_route_use_case()                       │   │
│  │  - merge_routes_use_case()                       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                          │
│                  (Lógica de Negocio)                     │
│                                                          │
│  ┌──────────────┐           ┌──────────────────┐        │
│  │   Route      │           │    PORTS         │        │
│  │  (Entity)    │           │  (Interfaces)    │        │
│  │              │           │                  │        │
│  │ + add_client()│          │ RouteRepository  │        │
│  │ + remove()   │           │ Port             │        │
│  │ + divide_at()│           │                  │        │
│  └──────────────┘           │ RouteOptimization│        │
│                             │ Port             │        │
│                             └──────────────────┘        │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    DRIVEN ADAPTERS                       │
│               (Adaptadores de Salida)                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  PostgreSQL  │  │  SQLite      │  │ Google Maps  │  │
│  │  Repository  │  │  Repository  │  │   Service    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                 │                  │           │
└─────────┼─────────────────┼──────────────────┼───────────┘
          │                 │                  │
          ▼                 ▼                  ▼
    PostgreSQL DB      SQLite DB        Google Maps API
```

---

## 🎨 Capas de la Arquitectura {#capas-de-la-arquitectura}

### 🟢 1. Domain Layer (Núcleo)

**Ubicación:** `src/domain/`

**Responsabilidad:** Contiene la lógica de negocio pura y las reglas del dominio.

#### Características:
- ✅ **Independiente** de frameworks y tecnologías
- ✅ **No tiene dependencias** externas
- ✅ Contiene **entidades** con comportamiento
- ✅ Define **puertos** (interfaces)

#### Componentes:

**A) Entidades del Dominio**

```python
# src/domain/models/route.py
@dataclass
class Route:
    """
    Entidad Route - Lógica de negocio pura.
    NO depende de frameworks ni bases de datos.
    """
    id: str
    name: str
    cedis_id: str
    day_of_week: str
    client_ids: List[str] = field(default_factory=list)
    is_active: bool = True
    
    def add_client(self, client_id: str) -> None:
        """Lógica de negocio: agregar cliente."""
        if client_id in self.client_ids:
            raise ValueError(f"Cliente {client_id} ya existe en la ruta")
        self.client_ids.append(client_id)
    
    def divide_at(self, split_point: int) -> Tuple['Route', 'Route']:
        """Lógica de negocio: dividir ruta."""
        if split_point <= 0 or split_point >= len(self.client_ids):
            raise ValueError("Punto de división inválido")
        
        clients_a = self.client_ids[:split_point]
        clients_b = self.client_ids[split_point:]
        
        # Retorna tupla de rutas (sin persistir)
        return (clients_a, clients_b)
```

**B) Puertos (Interfaces)**

```python
# src/domain/ports/route_repository_port.py
from abc import ABC, abstractmethod

class RouteRepositoryPort(ABC):
    """
    Puerto: Define el contrato para persistencia.
    NO implementa, solo define qué operaciones se necesitan.
    """
    
    @abstractmethod
    def save(self, route: Route) -> None:
        """Guardar una ruta."""
        pass
    
    @abstractmethod
    def find_by_id(self, route_id: str) -> Optional[Route]:
        """Buscar ruta por ID."""
        pass
    
    @abstractmethod
    def commit_transaction(self) -> None:
        """Confirmar transacción."""
        pass
```

**¿Por qué puertos en el dominio?**
- El dominio **define lo que necesita**
- La infraestructura **implementa cómo hacerlo**
- Inversión de dependencias: Infrastructure depende de Domain

---

### 🟡 2. Application Layer (Casos de Uso)

**Ubicación:** `src/application/`

**Responsabilidad:** Orquesta los casos de uso, coordinando dominio e infraestructura.

#### Características:
- ✅ Coordina entidades del dominio
- ✅ Usa **puertos** (no implementaciones)
- ✅ Transforma datos entre capas (**DTOs**)
- ✅ Maneja transacciones

#### Componentes:

**A) Servicios de Aplicación**

```python
# src/application/services/route_service.py
class RouteService:
    """
    Servicio de aplicación: Orquesta casos de uso.
    Depende SOLO de puertos (abstracciones).
    """
    
    def __init__(self, repository: RouteRepositoryPort) -> None:
        """Inyección de dependencias - Recibe el PUERTO."""
        self._repository = repository  # NO sabe si es Postgres o SQLite
    
    def create_route(self, dto: CreateRouteDTO) -> RouteDTO:
        """
        Caso de Uso: Crear ruta.
        
        Flujo:
        1. Validar datos del DTO
        2. Crear entidad de dominio
        3. Persistir usando el puerto
        4. Confirmar transacción
        5. Retornar DTO de salida
        """
        # 1. Generar ID
        route_id = str(uuid.uuid4())
        
        # 2. Crear entidad (lógica de dominio)
        route = Route(
            id=route_id,
            name=dto.name,
            cedis_id=dto.cedis_id,
            day_of_week=dto.day_of_week.upper(),
            client_ids=[],
            is_active=True
        )
        
        # 3. Persistir (a través del puerto)
        self._repository.save(route)
        
        # 4. Confirmar
        self._repository.commit_transaction()
        
        # 5. Transformar a DTO de salida
        return self._route_to_dto(route)
    
    def divide_route_use_case(
        self, 
        route_id: str, 
        split_point: int, 
        name_a: str, 
        name_b: str
    ) -> Tuple[RouteDTO, RouteDTO]:
        """
        Caso de Uso Complejo: Dividir ruta.
        
        Coordina múltiples operaciones del dominio.
        """
        # 1. Obtener ruta original
        original_route = self._repository.find_by_id(route_id)
        if not original_route:
            raise ValueError(f"Ruta {route_id} no encontrada")
        
        # 2. Lógica de dominio: dividir
        clients_a, clients_b = original_route.divide_at(split_point)
        
        # 3. Crear dos nuevas rutas
        route_a = Route(
            id=str(uuid.uuid4()),
            name=name_a,
            cedis_id=original_route.cedis_id,
            day_of_week=original_route.day_of_week,
            client_ids=clients_a,
            is_active=True
        )
        
        route_b = Route(
            id=str(uuid.uuid4()),
            name=name_b,
            cedis_id=original_route.cedis_id,
            day_of_week=original_route.day_of_week,
            client_ids=clients_b,
            is_active=True
        )
        
        # 4. Persistir ambas
        self._repository.save(route_a)
        self._repository.save(route_b)
        
        # 5. Desactivar original
        original_route.is_active = False
        self._repository.update(original_route)
        
        # 6. Confirmar transacción
        self._repository.commit_transaction()
        
        # 7. Retornar DTOs
        return (self._route_to_dto(route_a), self._route_to_dto(route_b))
```

**B) Data Transfer Objects (DTOs)**

```python
# src/application/dtos.py
@dataclass
class CreateRouteDTO:
    """DTO para entrada: crear ruta."""
    name: str
    cedis_id: str
    day_of_week: str

@dataclass
class RouteDTO:
    """DTO para salida: representación de ruta."""
    id: str
    name: str
    cedis_id: str
    day_of_week: str
    client_ids: List[str]
    client_count: int
    is_active: bool
```

**¿Por qué DTOs?**
- Desacopla la capa de aplicación del dominio
- Evita exponer entidades del dominio a la UI
- Permite transformaciones de datos

---

### 🔴 3. Infrastructure Layer (Detalles Técnicos)

**Ubicación:** `src/infrastructure/`

**Responsabilidad:** Implementa los detalles técnicos (bases de datos, APIs, UI).

#### Características:
- ✅ Implementa los **puertos** definidos en el dominio
- ✅ Contiene **adaptadores** para tecnologías específicas
- ✅ **Depende** del dominio (nunca al revés)

#### Componentes:

**A) Adaptadores de Persistencia (Driven)**

```python
# src/infrastructure/persistence/postgres_route_repository.py
class PostgresRouteRepository(RouteRepositoryPort):
    """
    Adaptador: Implementa RouteRepositoryPort para PostgreSQL.
    Cumple el contrato definido por el dominio.
    """
    
    def __init__(self, connection_params: dict) -> None:
        """Configuración específica de PostgreSQL."""
        self._connection_params = connection_params
        self._conn = None
        self._connect()
    
    def save(self, route: Route) -> None:
        """
        Implementación concreta: guardar en PostgreSQL.
        Traduce entidad de dominio a SQL.
        """
        with self._get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO rutas (
                    identificador_unico, 
                    nombre_descriptivo, 
                    dia_semana, 
                    cedis_id, 
                    activa
                )
                VALUES (%(id)s, %(name)s, %(day)s, %(cedis)s, %(active)s)
            """, {
                'id': route.id,
                'name': route.name,
                'day': self._convert_day_name_to_number(route.day_of_week),
                'cedis': route.cedis_id,
                'active': route.is_active
            })
    
    def find_by_id(self, route_id: str) -> Optional[Route]:
        """
        Implementación concreta: buscar en PostgreSQL.
        Traduce filas SQL a entidad de dominio.
        """
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM rutas 
                WHERE identificador_unico = %s
            """, (route_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Mapear SQL → Domain Entity
            return Route(
                id=row['identificador_unico'],
                name=row['nombre_descriptivo'],
                cedis_id=str(row['cedis_id']),
                day_of_week=self._convert_day_number_to_name(row['dia_semana']),
                client_ids=self._get_client_ids(row['id']),
                is_active=row['activa']
            )
```

**Implementación Alternativa (Intercambiable):**

```python
# src/infrastructure/persistence/sqlite_route_repository.py
class SQLiteRouteRepository(RouteRepositoryPort):
    """
    Adaptador alternativo: Implementa el mismo puerto para SQLite.
    ¡Intercambiable sin cambiar el dominio ni la aplicación!
    """
    
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path)
    
    def save(self, route: Route) -> None:
        """Misma interfaz, implementación diferente."""
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO routes (id, name, cedis_id, day_of_week, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (route.id, route.name, route.cedis_id, route.day_of_week, route.is_active))
```

**B) Adaptadores de Servicios Externos (Driven)**

```python
# src/infrastructure/services/google_maps_service.py
class GoogleMapsOptimizationService(RouteOptimizationPort):
    """
    Adaptador: Conecta con Google Maps API.
    Implementa RouteOptimizationPort.
    """
    
    def __init__(self, api_key: str):
        """Configuración específica de Google Maps."""
        self._client = googlemaps.Client(key=api_key)
    
    def optimize_route(
        self, 
        route_id: str, 
        client_locations: List[ClientLocation],
        origin: Tuple[float, float]
    ) -> OptimizedRouteDTO:
        """
        Implementación: usa Google Maps Directions API.
        Traduce datos del dominio a formato de Google Maps.
        """
        # Preparar waypoints en formato Google Maps
        waypoints = [f"{loc.latitude},{loc.longitude}" for loc in client_locations]
        
        # Llamar API externa
        result = self._client.directions(
            origin=f"{origin[0]},{origin[1]}",
            destination=f"{origin[0]},{origin[1]}",
            waypoints=waypoints,
            optimize_waypoints=True
        )
        
        # Traducir respuesta de Google Maps → DTO del dominio
        optimized_order = result[0]['waypoint_order']
        total_distance = sum(leg['distance']['value'] for leg in result[0]['legs'])
        
        return OptimizedRouteDTO(
            route_id=route_id,
            optimized_order=[client_locations[i].client_id for i in optimized_order],
            total_distance_km=total_distance / 1000,
            # ...
        )
```

**C) Adaptadores de UI (Driving)**

```python
# src/infrastructure/ui/flask_app.py
def create_flask_app(
    route_service: RouteService,
    optimization_service: RouteOptimizationService
) -> Flask:
    """
    Adaptador de entrada: Flask API.
    Traduce HTTP requests → llamadas de servicio.
    """
    app = Flask(__name__)
    
    @app.route('/api/routes', methods=['POST'])
    def create_route_endpoint():
        """
        Endpoint HTTP → Caso de uso.
        """
        # 1. Adaptar HTTP request → DTO
        data = request.get_json()
        dto = CreateRouteDTO(
            name=data['name'],
            cedis_id=data['cedis_id'],
            day_of_week=data['day_of_week']
        )
        
        # 2. Llamar servicio de aplicación
        route_dto = route_service.create_route(dto)
        
        # 3. Adaptar DTO → HTTP response
        return jsonify({
            'success': True,
            'data': {
                'id': route_dto.id,
                'name': route_dto.name,
                # ...
            }
        }), 201
    
    return app
```

---

## 🔌 Puertos y Adaptadores {#puertos-y-adaptadores}

### Concepto de Puertos

> **Puerto**: Interfaz (contrato) que define operaciones necesarias.

**Características:**
- Define **QUÉ** se necesita (no cómo implementarlo)
- Vive en el **dominio**
- Es **abstracto** (ABC en Python)

### Concepto de Adaptadores

> **Adaptador**: Implementación concreta de un puerto.

**Características:**
- Define **CÓMO** implementar el puerto
- Vive en **infraestructura**
- Es **concreto** (clase que hereda del puerto)

### Tipos de Adaptadores

```
┌─────────────────────────────────────────┐
│         DRIVING ADAPTERS                │
│      (Adaptadores Primarios)            │
│   "Quienes usan nuestra aplicación"     │
├─────────────────────────────────────────┤
│  - REST API (Flask)                     │
│  - Web UI (Streamlit)                   │
│  - CLI                                  │
│  - GraphQL API                          │
│  - gRPC                                 │
└───────────────┬─────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │  APPLICATION  │
        └───────┬───────┘
                │
                ▼
┌─────────────────────────────────────────┐
│         DRIVEN ADAPTERS                 │
│      (Adaptadores Secundarios)          │
│  "Quienes son usados por la aplicación" │
├─────────────────────────────────────────┤
│  - PostgreSQL Repository                │
│  - SQLite Repository                    │
│  - Google Maps Service                  │
│  - Email Service                        │
│  - Message Queue                        │
└─────────────────────────────────────────┘
```

### Implementación en el Proyecto

#### Puerto: RouteRepositoryPort

```python
# src/domain/ports/route_repository_port.py

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.route import Route

class RouteRepositoryPort(ABC):
    """
    Puerto (interfaz) para operaciones de persistencia de rutas.
    
    Define el contrato que cualquier implementación de repositorio
    debe cumplir. El dominio define QUÉ necesita, no CÓMO se implementa.
    """
    
    @abstractmethod
    def save(self, route: Route) -> None:
        """Guardar una ruta nueva."""
        pass
    
    @abstractmethod
    def find_by_id(self, route_id: str) -> Optional[Route]:
        """Buscar ruta por ID."""
        pass
    
    @abstractmethod
    def find_all(self, include_inactive: bool = False) -> List[Route]:
        """Obtener todas las rutas."""
        pass
    
    @abstractmethod
    def update(self, route: Route) -> None:
        """Actualizar una ruta existente."""
        pass
    
    @abstractmethod
    def delete(self, route_id: str) -> None:
        """Eliminar una ruta."""
        pass
    
    @abstractmethod
    def commit_transaction(self) -> None:
        """Confirmar transacción actual."""
        pass
    
    @abstractmethod
    def rollback_transaction(self) -> None:
        """Revertir transacción actual."""
        pass
```

#### Adaptador 1: PostgresRouteRepository

```python
# src/infrastructure/persistence/postgres_route_repository.py

class PostgresRouteRepository(RouteRepositoryPort):
    """
    Adaptador concreto para PostgreSQL.
    Implementa el puerto RouteRepositoryPort.
    """
    
    def __init__(self, connection_params: dict) -> None:
        self._connection_params = connection_params
        self._conn = psycopg2.connect(**connection_params)
    
    # Implementa TODOS los métodos del puerto
    def save(self, route: Route) -> None:
        # Lógica específica de PostgreSQL
        ...
    
    def find_by_id(self, route_id: str) -> Optional[Route]:
        # Lógica específica de PostgreSQL
        ...
```

#### Adaptador 2: SQLiteRouteRepository

```python
# src/infrastructure/persistence/sqlite_route_repository.py

class SQLiteRouteRepository(RouteRepositoryPort):
    """
    Adaptador alternativo para SQLite.
    Implementa el MISMO puerto, diferente tecnología.
    """
    
    def __init__(self, db_path: str) -> None:
        self._conn = sqlite3.connect(db_path)
    
    # Implementa TODOS los métodos del puerto
    def save(self, route: Route) -> None:
        # Lógica específica de SQLite
        ...
    
    def find_by_id(self, route_id: str) -> Optional[Route]:
        # Lógica específica de SQLite
        ...
```

### Intercambiabilidad

```python
# main.py

from config import Config

# Decidir qué adaptador usar (configuración)
if Config.DB_TYPE == 'postgres':
    repository = PostgresRouteRepository(connection_params)
elif Config.DB_TYPE == 'sqlite':
    repository = SQLiteRouteRepository(db_path)

# El servicio NO sabe ni le importa cuál es
route_service = RouteService(repository)

# ¡Funciona igual con cualquier adaptador!
route = route_service.create_route(dto)
```

---

## 🔄 Flujo de Datos {#flujo-de-datos}

### Flujo Completo: Crear una Ruta

```
┌──────────────┐
│   Cliente    │  POST /api/routes
│   (Browser)  │  {"name": "Ruta Norte", "cedis_id": "13", "day_of_week": "LUNES"}
└──────┬───────┘
       │
       │ HTTP Request
       ▼
┌─────────────────────────────────────────────────────────┐
│  INFRASTRUCTURE LAYER - Flask Adapter (Driving)          │
│                                                          │
│  @app.route('/api/routes', methods=['POST'])             │
│  def create_route_endpoint():                            │
│      data = request.get_json()                           │
│      dto = CreateRouteDTO(**data)  ◄────────┐           │
│      result = route_service.create_route(dto)│           │
│      return jsonify(result)                  │           │
└──────────────────────────────┬───────────────┘           │
                               │ DTO                       │
                               ▼                           │
┌─────────────────────────────────────────────────────────┐
│  APPLICATION LAYER - RouteService                        │
│                                                          │
│  def create_route(dto: CreateRouteDTO):                  │
│      route_id = uuid.uuid4()                             │
│      route = Route(  ◄────────────────────┐             │
│          id=route_id,                      │             │
│          name=dto.name,      Domain Entity │             │
│          cedis_id=dto.cedis_id,            │             │
│          ...                               │             │
│      )                                     │             │
│      self._repository.save(route) ─────────┼───┐         │
│      self._repository.commit_transaction() │   │         │
│      return self._route_to_dto(route)      │   │         │
└────────────────────────────────────────────┘   │         │
                                                 │         │
                                                 ▼         │
┌─────────────────────────────────────────────────────────┐
│  INFRASTRUCTURE LAYER - PostgresRepository (Driven)      │
│                                                          │
│  def save(route: Route):                                 │
│      cursor.execute("""                                  │
│          INSERT INTO rutas (                             │
│              identificador_unico,                        │
│              nombre_descriptivo,                         │
│              ...                                         │
│          ) VALUES (...)                                  │
│      """, route.__dict__)                                │
│                                                          │
└──────────────────────────────┬───────────────────────────┘
                               │ SQL
                               ▼
                        ┌──────────────┐
                        │  PostgreSQL  │
                        │   Database   │
                        └──────────────┘
```

### Paso a Paso Detallado

**1. Request HTTP entra por Flask** (Driving Adapter)
```python
# infrastructure/ui/flask_app.py
@app.route('/api/routes', methods=['POST'])
def create_route_endpoint():
    data = request.get_json()
    # Traducir HTTP → DTO
    dto = CreateRouteDTO(
        name=data['name'],
        cedis_id=data['cedis_id'],
        day_of_week=data['day_of_week']
    )
```

**2. Flask llama al Servicio de Aplicación**
```python
    # Llamar caso de uso
    result = route_service.create_route(dto)
```

**3. Servicio de Aplicación orquesta**
```python
# application/services/route_service.py
def create_route(self, dto: CreateRouteDTO) -> RouteDTO:
    # Crear entidad de dominio
    route = Route(
        id=str(uuid.uuid4()),
        name=dto.name,
        cedis_id=dto.cedis_id,
        day_of_week=dto.day_of_week,
        client_ids=[],
        is_active=True
    )
```

**4. Validación del Dominio se ejecuta**
```python
# domain/models/route.py
@dataclass
class Route:
    def __post_init__(self):
        # Validaciones de negocio
        if not self.name:
            raise ValueError("Nombre obligatorio")
        if self.day_of_week not in VALID_DAYS:
            raise ValueError("Día inválido")
```

**5. Servicio persiste a través del Puerto**
```python
# application/services/route_service.py
    # Usa el puerto (no sabe si es Postgres o SQLite)
    self._repository.save(route)
    self._repository.commit_transaction()
```

**6. Adaptador traduce a SQL**
```python
# infrastructure/persistence/postgres_route_repository.py
def save(self, route: Route) -> None:
    cursor.execute("""
        INSERT INTO rutas (identificador_unico, nombre_descriptivo, ...)
        VALUES (%(id)s, %(name)s, ...)
    """, {
        'id': route.id,
        'name': route.name,
        # ...
    })
```

**7. Respuesta viaja de vuelta**
```python
# application/services/route_service.py
    return RouteDTO(
        id=route.id,
        name=route.name,
        # ...
    )

# infrastructure/ui/flask_app.py
    return jsonify({'success': True, 'data': result})
```

---

## 💻 Implementación Práctica {#implementación-práctica}

### Ejemplo Completo: Asignar Cliente a Ruta

#### 1. Entidad de Dominio

```python
# src/domain/models/route.py

@dataclass
class Route:
    id: str
    name: str
    cedis_id: str
    day_of_week: str
    client_ids: List[str] = field(default_factory=list)
    is_active: bool = True
    
    def add_client(self, client_id: str) -> None:
        """
        LÓGICA DE NEGOCIO PURA.
        No sabe nada de bases de datos ni HTTP.
        """
        # Regla de negocio: no duplicados
        if client_id in self.client_ids:
            raise ValueError(f"Cliente {client_id} ya existe en la ruta")
        
        # Regla de negocio: límite de clientes
        if len(self.client_ids) >= 50:
            raise ValueError("Ruta no puede tener más de 50 clientes")
        
        self.client_ids.append(client_id)
```

#### 2. Puerto del Dominio

```python
# src/domain/ports/route_repository_port.py

class RouteRepositoryPort(ABC):
    @abstractmethod
    def find_by_id(self, route_id: str) -> Optional[Route]:
        """El dominio define QUÉ necesita."""
        pass
    
    @abstractmethod
    def update(self, route: Route) -> None:
        """El dominio define QUÉ necesita."""
        pass
```

#### 3. Servicio de Aplicación

```python
# src/application/services/route_service.py

class RouteService:
    def __init__(self, repository: RouteRepositoryPort):
        """Inyección del puerto (no implementación)."""
        self._repository = repository
    
    def assign_client_to_route(
        self, 
        route_id: str, 
        client_id: str
    ) -> RouteDTO:
        """
        CASO DE USO: Asignar cliente a ruta.
        Orquesta dominio e infraestructura.
        """
        # 1. Obtener ruta (a través del puerto)
        route = self._repository.find_by_id(route_id)
        if route is None:
            raise ValueError(f"Ruta {route_id} no encontrada")
        
        # 2. Aplicar lógica de negocio (dominio)
        route.add_client(client_id)  # ← DOMINIO PURO
        
        # 3. Persistir cambios (a través del puerto)
        self._repository.update(route)
        self._repository.commit_transaction()
        
        # 4. Retornar DTO
        return RouteDTO(
            id=route.id,
            name=route.name,
            cedis_id=route.cedis_id,
            day_of_week=route.day_of_week,
            client_ids=route.client_ids,
            client_count=len(route.client_ids),
            is_active=route.is_active
        )
```

#### 4. Adaptador PostgreSQL

```python
# src/infrastructure/persistence/postgres_route_repository.py

class PostgresRouteRepository(RouteRepositoryPort):
    def __init__(self, connection_params: dict):
        self._conn = psycopg2.connect(**connection_params)
    
    def find_by_id(self, route_id: str) -> Optional[Route]:
        """IMPLEMENTACIÓN específica de PostgreSQL."""
        cursor = self._conn.cursor()
        
        # Consulta SQL
        cursor.execute("""
            SELECT * FROM rutas 
            WHERE identificador_unico = %s
        """, (route_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Mapear SQL → Entidad de Dominio
        return Route(
            id=row['identificador_unico'],
            name=row['nombre_descriptivo'],
            cedis_id=str(row['cedis_id']),
            day_of_week=self._convert_day(row['dia_semana']),
            client_ids=self._get_client_ids(row['id']),
            is_active=row['activa']
        )
    
    def update(self, route: Route) -> None:
        """IMPLEMENTACIÓN específica de PostgreSQL."""
        cursor = self._conn.cursor()
        
        # Actualizar tabla rutas
        cursor.execute("""
            UPDATE rutas 
            SET nombre_descriptivo = %s, activa = %s
            WHERE identificador_unico = %s
        """, (route.name, route.is_active, route.id))
        
        # Actualizar tabla ruta_clientes
        self._update_route_clients(route)
```

#### 5. Adaptador Flask (API)

```python
# src/infrastructure/ui/flask_app.py

@app.route('/api/routes/<route_id>/clients', methods=['POST'])
def api_add_client(route_id: str):
    """ADAPTADOR: HTTP → Servicio de Aplicación."""
    
    # 1. Adaptar request HTTP → parámetros
    data = request.get_json()
    client_id = data.get('client_id')
    
    if not client_id:
        return jsonify({
            'success': False, 
            'error': 'client_id requerido'
        }), 400
    
    try:
        # 2. Llamar caso de uso
        route_dto = route_service.assign_client_to_route(
            route_id, 
            client_id
        )
        
        # 3. Adaptar DTO → HTTP response
        return jsonify({
            'success': True,
            'message': f'Cliente {client_id} añadido',
            'data': {
                'id': route_dto.id,
                'name': route_dto.name,
                'client_count': route_dto.client_count
            }
        }), 200
        
    except ValueError as e:
        # Manejar errores del dominio
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
```

#### 6. Configuración e Inyección

```python
# main.py (punto de entrada)

from config import Config
from src.infrastructure.persistence.postgres_route_repository import PostgresRouteRepository
from src.application.services.route_service import RouteService
from src.infrastructure.ui.flask_app import create_flask_app

def main():
    # 1. Crear adaptador de BD (infraestructura)
    connection_params = {
        'host': Config.DB_HOST,
        'port': Config.DB_PORT,
        'database': Config.DB_NAME,
        'user': Config.DB_USER,
        'password': Config.DB_PASSWORD
    }
    repository = PostgresRouteRepository(connection_params)
    
    # 2. Crear servicio (aplicación) con inyección de dependencias
    route_service = RouteService(repository)
    
    # 3. Crear adaptador de UI (infraestructura)
    app = create_flask_app(route_service)
    
    # 4. Ejecutar aplicación
    app.run(port=5000)

if __name__ == '__main__':
    main()
```

---

## ✨ Ventajas y Beneficios {#ventajas-y-beneficios}

### 1. Independencia Tecnológica

**Problema sin Hexagonal:**
```python
# ❌ Lógica de negocio acoplada a Flask y PostgreSQL
@app.route('/routes', methods=['POST'])
def create_route():
    name = request.form['name']
    
    # Lógica mezclada con SQL
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO routes ...")
    
    return "OK"
```

**Solución con Hexagonal:**
```python
# ✅ Lógica de negocio independiente
class Route:
    def add_client(self, client_id: str):
        # Reglas de negocio puras
        if client_id in self.client_ids:
            raise ValueError("Duplicado")
```

**Beneficio:** Puedes cambiar Flask por FastAPI, o PostgreSQL por MongoDB sin tocar la lógica de negocio.

### 2. Testabilidad

**Sin Hexagonal:**
```python
# ❌ Difícil de testear (requiere BD real)
def test_create_route():
    # Necesita PostgreSQL corriendo
    response = client.post('/api/routes', ...)
    assert response.status_code == 201
```

**Con Hexagonal:**
```python
# ✅ Fácil de testear con mocks
def test_create_route():
    # Mock del repositorio
    mock_repo = Mock(spec=RouteRepositoryPort)
    service = RouteService(mock_repo)
    
    # Test puro sin BD
    dto = CreateRouteDTO("Ruta 1", "CEDIS_1", "LUNES")
    result = service.create_route(dto)
    
    assert result.name == "Ruta 1"
    mock_repo.save.assert_called_once()
```

### 3. Mantenibilidad

**Estructura Clara:**
- Domain: ¿Qué hace el negocio?
- Application: ¿Qué casos de uso tenemos?
- Infrastructure: ¿Qué tecnologías usamos?

**Cambios Localizados:**
- Cambiar BD: Solo modificas adaptador
- Cambiar API: Solo modificas adaptador de UI
- Cambiar reglas de negocio: Solo modificas dominio

### 4. Escalabilidad

**Agregar Nuevos Adaptadores:**

```python
# Agregar MongoDB sin tocar nada más
class MongoRouteRepository(RouteRepositoryPort):
    def __init__(self, mongo_client):
        self._client = mongo_client
    
    def save(self, route: Route):
        # Implementación MongoDB
        self._client.routes.insert_one(route.__dict__)
    
    # ... otros métodos

# Usar en configuración
if Config.DB_TYPE == 'mongo':
    repository = MongoRouteRepository(mongo_client)
else:
    repository = PostgresRouteRepository(pg_params)

# El resto del código NO CAMBIA
service = RouteService(repository)
```

### 5. Reutilización

**Múltiples Adaptadores de UI:**

```python
# Mismo dominio y aplicación, diferentes UIs

# API REST (Flask)
flask_app = create_flask_app(route_service)

# UI Web (Streamlit)
streamlit_app = create_streamlit_app(route_service)

# CLI
cli_app = create_cli_app(route_service)

# GraphQL
graphql_app = create_graphql_app(route_service)
```

---

## 🎓 Casos de Uso Reales {#casos-de-uso-reales}

### Caso 1: Migración de Base de Datos

**Escenario:** Migrar de SQLite a PostgreSQL

**Sin Hexagonal:**
```
Reescribir toda la aplicación ❌
- 500+ líneas de código SQL embebido
- 2-3 semanas de trabajo
- Alto riesgo de bugs
```

**Con Hexagonal:**
```
1. Crear PostgresRouteRepository ✅
2. Implementar métodos del puerto ✅
3. Cambiar configuración ✅
Total: 1 día de trabajo, bajo riesgo
```

**Código:**
```python
# config.py
DB_TYPE = 'postgres'  # Era 'sqlite'

# main.py (no cambia nada más)
if Config.DB_TYPE == 'postgres':
    repository = PostgresRouteRepository(params)
else:
    repository = SQLiteRouteRepository(db_path)

service = RouteService(repository)  # ← IGUAL
```

### Caso 2: Agregar Optimización con Google Maps

**Escenario:** Integrar Google Maps API para optimizar rutas

**Implementación Hexagonal:**

1. **Definir Puerto:**
```python
# domain/ports/route_optimization_port.py
class RouteOptimizationPort(ABC):
    @abstractmethod
    def optimize_route(self, waypoints: List[Tuple]) -> List[int]:
        pass
```

2. **Crear Adaptador:**
```python
# infrastructure/services/google_maps_service.py
class GoogleMapsOptimizationService(RouteOptimizationPort):
    def __init__(self, api_key: str):
        self._client = googlemaps.Client(api_key)
    
    def optimize_route(self, waypoints: List[Tuple]) -> List[int]:
        # Llamar Google Maps API
        result = self._client.directions(...)
        return result['waypoint_order']
```

3. **Usar en Aplicación:**
```python
# application/services/route_optimization_service.py
class RouteOptimizationService:
    def __init__(self, optimization_port: RouteOptimizationPort):
        self._optimizer = optimization_port
    
    def optimize(self, route_id: str):
        # Usar el puerto (puede ser Google Maps u otro)
        optimized_order = self._optimizer.optimize_route(waypoints)
```

**Beneficio:** El dominio NO conoce Google Maps. Mañana puedes cambiar a Mapbox sin tocar la lógica de negocio.

### Caso 3: Testing Completo

**Test de Dominio (sin dependencias):**
```python
def test_route_add_client():
    # Test puro de lógica de negocio
    route = Route(
        id="1",
        name="Test Route",
        cedis_id="CEDIS_1",
        day_of_week="LUNES",
        client_ids=[]
    )
    
    # Probar regla de negocio
    route.add_client("CLI_001")
    assert len(route.client_ids) == 1
    
    # Probar validación
    with pytest.raises(ValueError):
        route.add_client("CLI_001")  # Duplicado
```

**Test de Aplicación (con mock):**
```python
def test_assign_client_to_route():
    # Mock del repositorio
    mock_repo = Mock(spec=RouteRepositoryPort)
    mock_repo.find_by_id.return_value = Route(
        id="1", name="Test", cedis_id="CEDIS_1", 
        day_of_week="LUNES", client_ids=[]
    )
    
    # Crear servicio con mock
    service = RouteService(mock_repo)
    
    # Ejecutar caso de uso
    result = service.assign_client_to_route("1", "CLI_001")
    
    # Verificar
    assert result.client_count == 1
    mock_repo.update.assert_called_once()
```

**Test de Integración (con BD de test):**
```python
def test_integration_create_route():
    # Usar BD de test (SQLite en memoria)
    test_repo = SQLiteRouteRepository(':memory:')
    service = RouteService(test_repo)
    
    # Test end-to-end
    dto = CreateRouteDTO("Test Route", "CEDIS_1", "LUNES")
    result = service.create_route(dto)
    
    # Verificar persistencia
    found = service.get_route_by_id(result.id)
    assert found.name == "Test Route"
```

---

## 📖 Referencias y Recursos

### Patrones Relacionados

1. **Clean Architecture** (Robert C. Martin)
   - Hexagonal es una implementación de Clean Architecture
   - Mismos principios: capas, dependencias hacia adentro

2. **Onion Architecture** (Jeffrey Palermo)
   - Similar a Hexagonal
   - Énfasis en capas concéntricas

3. **SOLID Principles**
   - **S**ingle Responsibility
   - **O**pen/Closed
   - **L**iskov Substitution
   - **I**nterface Segregation
   - **D**ependency Inversion ← Clave en Hexagonal

### Bibliografía

- **Alistair Cockburn** - "Hexagonal Architecture" (2005)
- **Robert C. Martin** - "Clean Architecture" (2017)
- **Eric Evans** - "Domain-Driven Design" (2003)
- **Vaughn Vernon** - "Implementing Domain-Driven Design" (2013)

---

## 📊 Diagrama de Resumen

```
┌─────────────────────────────────────────────────────────────────┐
│                        HEXAGONAL ARCHITECTURE                    │
│                        Yedistribuciones                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐           ┌──────────────┐                   │
│   │   Flask      │           │  Streamlit   │  DRIVING          │
│   │   (REST)     │           │   (Web UI)   │  ADAPTERS         │
│   └──────┬───────┘           └──────┬───────┘  (Primary)        │
│          │                          │                            │
│          └──────────┬───────────────┘                            │
│                     │                                            │
│                     ▼                                            │
│          ┌─────────────────────┐                                │
│          │  APPLICATION LAYER  │  CASES DE USO                  │
│          │                     │  (Orchestration)               │
│          │  - RouteService     │                                │
│          │  - OptimizationSvc  │                                │
│          └──────────┬──────────┘                                │
│                     │                                            │
│                     ▼                                            │
│          ┌─────────────────────┐                                │
│          │    DOMAIN LAYER     │  LÓGICA DE NEGOCIO             │
│          │                     │  (Business Rules)              │
│          │  ┌──────────────┐   │                                │
│          │  │   Route      │   │  Entities                      │
│          │  │   Client     │   │                                │
│          │  └──────────────┘   │                                │
│          │                     │                                │
│          │  ┌──────────────┐   │                                │
│          │  │    PORTS     │   │  Interfaces                    │
│          │  │ (Interfaces) │   │                                │
│          │  └──────────────┘   │                                │
│          └──────────┬──────────┘                                │
│                     │                                            │
│                     ▼                                            │
│          ┌─────────────────────┐                                │
│          │ INFRASTRUCTURE      │  DETALLES TÉCNICOS             │
│          │                     │  (Implementation)              │
│          └──────────┬──────────┘                                │
│                     │                                            │
│          ┏━━━━━━━━━┻━━━━━━━━━┓                                 │
│          ┃                    ┃                                 │
│    ┌─────▼──────┐      ┌─────▼──────┐  DRIVEN                  │
│    │ PostgreSQL │      │   Google   │  ADAPTERS                 │
│    │ Repository │      │    Maps    │  (Secondary)              │
│    └─────┬──────┘      └─────┬──────┘                          │
│          │                   │                                  │
│          ▼                   ▼                                  │
│    PostgreSQL DB      Google Maps API                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

PRINCIPIOS CLAVE:
✅ Dependencias apuntan hacia adentro (Domain es el centro)
✅ Domain NO conoce Infrastructure
✅ Puertos definen contratos en el Domain
✅ Adaptadores implementan puertos en Infrastructure
✅ Application orquesta usando puertos (no implementaciones)
```

---

## 🎯 Conclusión

La **Arquitectura Hexagonal** implementada en Yedistribuciones proporciona:

1. ✅ **Separación clara** de responsabilidades
2. ✅ **Independencia** tecnológica
3. ✅ **Testabilidad** de alto nivel
4. ✅ **Mantenibilidad** a largo plazo
5. ✅ **Escalabilidad** arquitectónica
6. ✅ **Flexibilidad** para cambios

### Próximos Pasos Recomendados

1. **Ampliar cobertura de tests** usando la arquitectura
2. **Agregar más adaptadores** (MongoDB, Redis, etc.)
3. **Implementar CQRS** sobre la arquitectura hexagonal
4. **Agregar Event Sourcing** para auditoría
5. **Documentar casos de uso** específicos del negocio

---

**Documento creado por:** Equipo de Arquitectura Yedistribuciones  
**Fecha:** Noviembre 2025  
**Versión:** 1.0  
**Basado en:** Hexagonal Architecture (Alistair Cockburn, 2005)
