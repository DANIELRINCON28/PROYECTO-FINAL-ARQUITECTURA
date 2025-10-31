# Arquitectura Hexagonal - Migración PostgreSQL

## 🏛️ Vista de Arquitectura Completa

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                         ADAPTADORES CONDUCTORES                       ┃
┃                          (Driving Adapters)                          ┃
┃                                                                       ┃
┃  ┌─────────────────────┐       ┌──────────────────────┐            ┃
┃  │   Streamlit UI      │       │   CLI Interface      │            ┃
┃  │  (Puerto HTTP)      │       │   (Puerto Console)   │            ┃
┃  └──────────┬──────────┘       └──────────┬───────────┘            ┃
┗━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━┛
               │                             │
               └──────────────┬──────────────┘
                              │
                              │ API Calls
                              ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                       CAPA DE APLICACIÓN                             ┃
┃                     (Application Layer)                              ┃
┃                                                                       ┃
┃  ┌───────────────────────────────────────────────────────────────┐  ┃
┃  │                    RouteService                                │  ┃
┃  │  • createRoute()                                               │  ┃
┃  │  • updateRoute()                                               │  ┃
┃  │  • deleteRoute()                                               │  ┃
┃  │  • listRoutes()                                                │  ┃
┃  │  • divideRoute()                                               │  ┃
┃  │  • mergeRoutes()                                               │  ┃
┃  └───────────────────────────────────────────────────────────────┘  ┃
┃                                                                       ┃
┃  ┌───────────────────────────────────────────────────────────────┐  ┃
┃  │            RouteOptimizationService                            │  ┃
┃  │  • optimizeRoute()                                             │  ┃
┃  │  • calculateRouteMetrics()                                     │  ┃
┃  │  • suggestRouteDivision()                                      │  ┃
┃  └───────────────────────────────────────────────────────────────┘  ┃
┃                                                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                              │
                              │ Usa interfaces abstractas
                              ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                         CAPA DE DOMINIO                              ┃
┃                        (Domain Layer)                                ┃
┃                                                                       ┃
┃  ┌─────────────────────────────────────────────────────────────┐    ┃
┃  │                   MODELOS DE DOMINIO                         │    ┃
┃  │                                                              │    ┃
┃  │  ┌────────────┐  ┌────────────┐  ┌────────────┐           │    ┃
┃  │  │   Route    │  │   Client   │  │   Cedis    │           │    ┃
┃  │  ├────────────┤  ├────────────┤  ├────────────┤           │    ┃
┃  │  │ id         │  │ id         │  │ id         │           │    ┃
┃  │  │ name       │  │ name       │  │ nombre     │           │    ┃
┃  │  │ cedis_id   │  │ address    │  │ ciudad     │           │    ┃
┃  │  │ day_of_week│  │ latitude   │  │ ...        │           │    ┃
┃  │  │ client_ids │  │ longitude  │  │            │           │    ┃
┃  │  │ ...        │  │ ...        │  │            │           │    ┃
┃  │  └────────────┘  └────────────┘  └────────────┘           │    ┃
┃  │                                                              │    ┃
┃  │  + Lógica de negocio pura                                   │    ┃
┃  │  + Sin dependencias externas                                │    ┃
┃  │  + Validaciones de dominio                                  │    ┃
┃  └─────────────────────────────────────────────────────────────┘    ┃
┃                                                                       ┃
┃  ┌─────────────────────────────────────────────────────────────┐    ┃
┃  │                   PUERTOS (INTERFACES)                       │    ┃
┃  │                                                              │    ┃
┃  │  ┌──────────────────────────────────────────────────┐       │    ┃
┃  │  │ RouteRepositoryPort (Output Port)               │       │    ┃
┃  │  ├──────────────────────────────────────────────────┤       │    ┃
┃  │  │ + save(route: Route)                            │       │    ┃
┃  │  │ + update(route: Route)                          │       │    ┃
┃  │  │ + find_by_id(id: str) -> Route                  │       │    ┃
┃  │  │ + get_all() -> List[Route]                      │       │    ┃
┃  │  │ + delete(id: str)                               │       │    ┃
┃  │  │ + begin_transaction()                           │       │    ┃
┃  │  │ + commit_transaction()                          │       │    ┃
┃  │  │ + rollback_transaction()                        │       │    ┃
┃  │  └──────────────────────────────────────────────────┘       │    ┃
┃  │                                                              │    ┃
┃  │  ┌──────────────────────────────────────────────────┐       │    ┃
┃  │  │ RouteOptimizationPort (Output Port)             │       │    ┃
┃  │  ├──────────────────────────────────────────────────┤       │    ┃
┃  │  │ + optimize_route(clients) -> OrderedClients     │       │    ┃
┃  │  │ + calculate_distance(origin, dest) -> float     │       │    ┃
┃  │  │ + calculate_duration(origin, dest) -> float     │       │    ┃
┃  │  └──────────────────────────────────────────────────┘       │    ┃
┃  └─────────────────────────────────────────────────────────────┘    ┃
┃                                                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                              │
                              │ Implementan
                              ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    ADAPTADORES CONDUCIDOS                            ┃
┃                     (Driven Adapters)                                ┃
┃                   CAPA DE INFRAESTRUCTURA                            ┃
┃                                                                       ┃
┃  ┌────────────────────────────────────────────────────────────┐     ┃
┃  │            ADAPTADORES DE PERSISTENCIA                     │     ┃
┃  │                                                             │     ┃
┃  │  ┌──────────────────────────────────────────────┐          │     ┃
┃  │  │  PostgresRouteRepository ✨ NUEVO            │          │     ┃
┃  │  │  implements RouteRepositoryPort              │          │     ┃
┃  │  ├──────────────────────────────────────────────┤          │     ┃
┃  │  │  - _connection_params: dict                  │          │     ┃
┃  │  │  - _conn: psycopg2.connection                │          │     ┃
┃  │  │  - _in_transaction: bool                     │          │     ┃
┃  │  │                                               │          │     ┃
┃  │  │  + save(route)                                │          │     ┃
┃  │  │  + update(route)                              │          │     ┃
┃  │  │  + find_by_id(id)                             │          │     ┃
┃  │  │  + get_all()                                  │          │     ┃
┃  │  │  + delete(id)                                 │          │     ┃
┃  │  │  + begin_transaction()                        │          │     ┃
┃  │  │  + commit_transaction()                       │          │     ┃
┃  │  │  + rollback_transaction()                     │          │     ┃
┃  │  │  - _row_to_route(row)                         │          │     ┃
┃  │  └──────────────────────────────────────────────┘          │     ┃
┃  │                                                             │     ┃
┃  │  ┌──────────────────────────────────────────────┐          │     ┃
┃  │  │  SqliteRouteRepository (Legacy)              │          │     ┃
┃  │  │  implements RouteRepositoryPort              │          │     ┃
┃  │  │  (Mantenido para compatibilidad)             │          │     ┃
┃  │  └──────────────────────────────────────────────┘          │     ┃
┃  └────────────────────────────────────────────────────────────┘     ┃
┃                                                                       ┃
┃  ┌────────────────────────────────────────────────────────────┐     ┃
┃  │           ADAPTADORES DE SERVICIOS EXTERNOS                │     ┃
┃  │                                                             │     ┃
┃  │  ┌──────────────────────────────────────────────┐          │     ┃
┃  │  │  GoogleMapsOptimizationService               │          │     ┃
┃  │  │  implements RouteOptimizationPort            │          │     ┃
┃  │  ├──────────────────────────────────────────────┤          │     ┃
┃  │  │  - _client: googlemaps.Client                │          │     ┃
┃  │  │  + optimize_route(clients)                   │          │     ┃
┃  │  │  + calculate_distance(...)                   │          │     ┃
┃  │  │  + calculate_duration(...)                   │          │     ┃
┃  │  └──────────────────────────────────────────────┘          │     ┃
┃  └────────────────────────────────────────────────────────────┘     ┃
┃                                                                       ┃
┃  ┌────────────────────────────────────────────────────────────┐     ┃
┃  │                  BASE DE DATOS                              │     ┃
┃  │                                                             │     ┃
┃  │          ┌───────────────────────────┐                      │     ┃
┃  │          │   PostgreSQL - RutasDB    │                      │     ┃
┃  │          ├───────────────────────────┤                      │     ┃
┃  │          │  Tables:                  │                      │     ┃
┃  │          │  • cedis                  │                      │     ┃
┃  │          │  • vendedores             │                      │     ┃
┃  │          │  • clientes               │                      │     ┃
┃  │          │  • rutas                  │                      │     ┃
┃  │          │  • rutas_clientes         │                      │     ┃
┃  │          │  • asignaciones_rutas     │                      │     ┃
┃  │          │  • routes (compatibilidad)│                      │     ┃
┃  │          └───────────────────────────┘                      │     ┃
┃  └────────────────────────────────────────────────────────────┘     ┃
┃                                                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## 🔄 Flujo de Datos

### Ejemplo: Crear una nueva ruta

```
1. Usuario interactúa con UI (Streamlit)
        ↓
2. UI llama a RouteService.createRoute(route_data)
        ↓
3. RouteService:
   - Valida los datos
   - Crea entidad Route (dominio)
   - Llama a RouteRepository.save(route)
        ↓
4. PostgresRouteRepository:
   - Convierte Route a formato SQL
   - Ejecuta INSERT en PostgreSQL
   - Maneja transacción
        ↓
5. PostgreSQL:
   - Valida constraints
   - Ejecuta triggers
   - Persiste datos
        ↓
6. Respuesta fluye de vuelta:
   PostgreSQL → Repository → Service → UI → Usuario
```

## 🎯 Principios Aplicados

### 1. **Separation of Concerns**
- ✅ Cada capa tiene responsabilidad única
- ✅ Dominio independiente de infraestructura
- ✅ UI separada de lógica de negocio

### 2. **Dependency Inversion (DIP)**
```
❌ MAL:
RouteService → PostgresRouteRepository
(Dependencia directa de implementación concreta)

✅ BIEN:
RouteService → RouteRepositoryPort ← PostgresRouteRepository
(Dependencia de abstracción)
```

### 3. **Single Responsibility (SRP)**
- `Route`: Solo lógica de ruta
- `RouteService`: Solo casos de uso de rutas
- `PostgresRouteRepository`: Solo persistencia en PostgreSQL
- `Config`: Solo configuración

### 4. **Open/Closed (OCP)**
```python
# Extensible sin modificar código existente
class NewMemoryRepository(RouteRepositoryPort):
    """Nueva implementación in-memory"""
    # No requiere cambios en RouteService
```

### 5. **Liskov Substitution (LSP)**
```python
# Cualquier implementación de RouteRepositoryPort
# puede reemplazar a otra sin romper el sistema
repo: RouteRepositoryPort = PostgresRouteRepository(params)
# O
repo: RouteRepositoryPort = SqliteRouteRepository(conn)
# O
repo: RouteRepositoryPort = MongoRouteRepository(client)
```

## 📦 Inyección de Dependencias

```python
# main.py - El único lugar con acoplamiento
def main():
    # Configurar adaptadores
    db_params = Config.get_db_connection_params()
    route_repo = PostgresRouteRepository(db_params)
    
    # Inyectar en servicios
    route_service = RouteService(repository=route_repo)
    
    # Inyectar en UI
    run_ui(route_service, optimization_service)
```

## 🔌 Puertos e Interfaces

### Puerto de Salida (Output Port)
```python
class RouteRepositoryPort(ABC):
    """
    Abstracción que define el contrato
    NO depende de tecnología específica
    """
    @abstractmethod
    def save(self, route: Route) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, route_id: str) -> Optional[Route]:
        pass
```

### Adaptador Conducido (Driven Adapter)
```python
class PostgresRouteRepository(RouteRepositoryPort):
    """
    Implementación concreta
    Depende del puerto (abstracción)
    """
    def save(self, route: Route) -> None:
        # Implementación específica de PostgreSQL
        cursor.execute("INSERT INTO routes ...")
```

## 🛡️ Ventajas de esta Arquitectura

### 1. **Testabilidad**
```python
# Fácil crear mocks para testing
class MockRouteRepository(RouteRepositoryPort):
    def __init__(self):
        self.routes = {}
    
    def save(self, route: Route) -> None:
        self.routes[route.id] = route

# Test sin base de datos real
def test_create_route():
    mock_repo = MockRouteRepository()
    service = RouteService(repository=mock_repo)
    service.create_route(...)
    assert len(mock_repo.routes) == 1
```

### 2. **Mantenibilidad**
- Cambios en BD no afectan dominio
- Nuevas features se agregan sin modificar existentes
- Cada componente tiene responsabilidad clara

### 3. **Flexibilidad**
```python
# Fácil cambiar de PostgreSQL a MongoDB
mongo_repo = MongoRouteRepository(client)
service = RouteService(repository=mongo_repo)
# ¡Sin cambios en RouteService!
```

### 4. **Escalabilidad**
- Fácil agregar caché
- Fácil agregar logging
- Fácil agregar métricas
- Todo mediante decoradores o wrappers

## 🚀 Extensiones Futuras

### Pool de Conexiones
```python
from psycopg2 import pool

class PostgresRouteRepository:
    _connection_pool = None
    
    @classmethod
    def initialize_pool(cls, minconn=1, maxconn=10):
        cls._connection_pool = pool.SimpleConnectionPool(
            minconn, maxconn, **Config.get_db_connection_params()
        )
```

### Caché
```python
class CachedRouteRepository(RouteRepositoryPort):
    def __init__(self, repository: RouteRepositoryPort):
        self._repository = repository
        self._cache = {}
    
    def find_by_id(self, route_id: str):
        if route_id in self._cache:
            return self._cache[route_id]
        route = self._repository.find_by_id(route_id)
        self._cache[route_id] = route
        return route
```

### Logging
```python
class LoggingRouteRepository(RouteRepositoryPort):
    def __init__(self, repository: RouteRepositoryPort):
        self._repository = repository
        self._logger = logging.getLogger(__name__)
    
    def save(self, route: Route):
        self._logger.info(f"Saving route {route.id}")
        result = self._repository.save(route)
        self._logger.info(f"Route {route.id} saved successfully")
        return result
```

---

**Documentación completa**: README/MIGRATION_POSTGRESQL.md
