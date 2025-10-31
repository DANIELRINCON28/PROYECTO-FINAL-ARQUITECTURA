# Documentación de Arquitectura - Yedistribuciones

## 1. Visión General de la Arquitectura

### 1.1 Arquitectura Hexagonal (Puertos y Adaptadores)

El proyecto Yedistribuciones implementa una **Arquitectura Hexagonal** estricta, donde:

- **El Hexágono (Dominio)**: Contiene la lógica de negocio pura, completamente independiente de frameworks y tecnologías.
- **Puertos**: Interfaces abstractas que definen contratos.
  - **Puertos de Entrada**: Casos de uso (en la capa de aplicación)
  - **Puertos de Salida**: Interfaces para persistencia y servicios externos
- **Adaptadores**: Implementaciones tecnológicas concretas.
  - **Adaptadores Conductores (Driving)**: UI, APIs, CLI
  - **Adaptadores Conducidos (Driven)**: Bases de datos, servicios externos

## 2. Capas de la Arquitectura

### 2.1 Capa de Dominio (Domain Layer)

**Ubicación**: `src/domain/`

**Responsabilidad**: Contiene las entidades de negocio y la lógica de negocio pura.

**Reglas Estrictas**:
- ❌ NO puede depender de ninguna otra capa
- ❌ NO puede importar frameworks (Streamlit, SQLite, etc.)
- ✅ Solo contiene lógica de negocio pura
- ✅ Define puertos (interfaces) para servicios externos

**Componentes**:

1. **Models** (`src/domain/models/`)
   - `route.py`: Entidad Route con métodos de negocio
     - `divide_route()`: Lógica de división de rutas
     - `merge_routes()`: Lógica de fusión de rutas
     - `add_client()`, `remove_client()`, `reorder_clients()`
   - `client.py`: Entidad Client

2. **Ports** (`src/domain/ports/`)
   - `route_repository_port.py`: Interfaz abstracta (ABC) para el repositorio
     - Define el contrato que debe cumplir cualquier repositorio

**Ejemplo de Código del Dominio**:

```python
# ✅ CORRECTO - Lógica de negocio pura
def divide_route(self, split_index: int) -> Tuple['Route', 'Route']:
    # Validación de negocio
    if split_index <= 0 or split_index >= len(self.client_ids):
        raise ValueError("Índice inválido")
    
    # Lógica de división
    clients_a = self.client_ids[:split_index]
    clients_b = self.client_ids[split_index:]
    
    # Retornar nuevas instancias (inmutabilidad)
    return route_a, route_b
```

### 2.2 Capa de Aplicación (Application Layer)

**Ubicación**: `src/application/`

**Responsabilidad**: Orquesta los casos de uso del sistema.

**Reglas Estrictas**:
- ✅ Depende del dominio (modelos y puertos)
- ❌ NO depende de la infraestructura
- ✅ Coordina la ejecución de la lógica de negocio
- ✅ Maneja transacciones
- ✅ Convierte entre DTOs y entidades de dominio

**Componentes**:

1. **Services** (`src/application/services/`)
   - `route_service.py`: Implementa los casos de uso
     - `create_route()`: RF-RUT-01
     - `assign_client_to_route()`: RF-RUT-02
     - `reorder_clients_in_route()`: RF-RUT-03
     - `divide_route_use_case()`: RF-RUT-06
     - `merge_routes_use_case()`: RF-RUT-07

2. **DTOs** (`src/application/dtos.py`)
   - Objetos de transferencia de datos para comunicación con la UI

**Ejemplo de Caso de Uso**:

```python
# ✅ CORRECTO - Orquestación de caso de uso
def divide_route_use_case(self, route_id: str, split_point: int, ...):
    try:
        # 1. Iniciar transacción
        self._repository.begin_transaction()
        
        # 2. Recuperar entidad
        route = self._repository.find_by_id(route_id)
        
        # 3. Ejecutar lógica de dominio
        route_a, route_b = route.divide_route(split_point)
        
        # 4. Persistir cambios
        route.deactivate()
        self._repository.update(route)
        self._repository.save(route_a)
        self._repository.save(route_b)
        
        # 5. Confirmar transacción
        self._repository.commit_transaction()
        
        return route_a, route_b
    except Exception as e:
        self._repository.rollback_transaction()
        raise e
```

### 2.3 Capa de Infraestructura (Infrastructure Layer)

**Ubicación**: `src/infrastructure/`

**Responsabilidad**: Implementaciones técnicas concretas.

**Componentes**:

1. **Persistence** (`src/infrastructure/persistence/`)
   - `sqlite_route_repository.py`: Implementa `RouteRepositoryPort`
     - Maneja SQL, conexiones, transacciones
     - Convierte entre filas de BD y entidades de dominio

2. **UI** (`src/infrastructure/ui/`)
   - `streamlit_app.py`: Interfaz de usuario web
     - Recibe el servicio de aplicación por inyección
     - NO accede directamente al repositorio

**Ejemplo de Adaptador de Persistencia**:

```python
# ✅ CORRECTO - Implementación del puerto
class SqliteRouteRepository(RouteRepositoryPort):
    def save(self, route: Route) -> None:
        # SQL específico para SQLite
        client_ids_json = json.dumps(route.client_ids)
        cursor.execute(
            "INSERT INTO routes (...) VALUES (...)",
            (route.id, route.name, ...)
        )
```

## 3. Flujo de Dependencias

### 3.1 Inversión de Dependencias (DIP)

```
┌─────────────────────────────────────────┐
│         CAPA DE UI (Streamlit)          │
│                                         │
│  run_ui(route_service: RouteService)    │
└─────────────────────────────────────────┘
                    │
                    ▼ depende de
┌─────────────────────────────────────────┐
│      CAPA DE APLICACIÓN                 │
│                                         │
│  RouteService(repository: Port) ◄────┐  │
└─────────────────────────────────────────┘
                    │                    │
                    ▼ depende de         │ implementa
┌─────────────────────────────────────────┐
│         CAPA DE DOMINIO                 │
│                                         │
│  RouteRepositoryPort (Interface ABC)    │
│  Route (Entity)                         │
└─────────────────────────────────────────┘
                    ▲
                    │ implementa
┌─────────────────────────────────────────┐
│      CAPA DE INFRAESTRUCTURA            │
│                                         │
│  SqliteRouteRepository implements Port  │
└─────────────────────────────────────────┘
```

### 3.2 Inyección de Dependencias

El archivo `main.py` actúa como el **Ensamblador**:

```python
# 1. Crear adaptador de infraestructura
db_conn = sqlite3.connect("yedistribuciones.db")
route_repo = SqliteRouteRepository(db_conn)

# 2. Inyectar en capa de aplicación
route_service = RouteService(repository=route_repo)

# 3. Inyectar en capa de UI
run_ui(route_service)
```

**Ventajas**:
- ✅ Facilita testing (mock del repositorio)
- ✅ Permite cambiar BD sin modificar lógica de negocio
- ✅ Cumple con el Principio Abierto/Cerrado (OCP)

## 4. Principios SOLID Aplicados

### 4.1 Single Responsibility Principle (SRP)

Cada clase tiene una única responsabilidad:

- `Route`: Lógica de negocio de rutas
- `RouteService`: Orquestación de casos de uso
- `SqliteRouteRepository`: Persistencia en SQLite
- `streamlit_app.py`: Interfaz de usuario

### 4.2 Open/Closed Principle (OCP)

El sistema está **abierto a extensión, cerrado a modificación**:

```python
# Para cambiar de SQLite a PostgreSQL:
# 1. Crear PostgresRouteRepository que implemente RouteRepositoryPort
# 2. En main.py, cambiar la instancia
# 3. NO modificar RouteService ni Route
```

### 4.3 Liskov Substitution Principle (LSP)

Cualquier implementación de `RouteRepositoryPort` puede sustituir a otra:

```python
# Ambas son válidas
route_service = RouteService(SqliteRouteRepository(conn))
route_service = RouteService(PostgresRouteRepository(conn))
route_service = RouteService(MockRouteRepository())  # Para tests
```

### 4.4 Interface Segregation Principle (ISP)

Los puertos definen interfaces específicas y cohesivas, no "gordas".

### 4.5 Dependency Inversion Principle (DIP)

**Clave de la arquitectura hexagonal**:

- ✅ Las capas de alto nivel (Aplicación) NO dependen de bajo nivel (Infraestructura)
- ✅ Ambas dependen de abstracciones (Puertos)

## 5. Patrones de Diseño Utilizados

### 5.1 Repository Pattern

`RouteRepositoryPort` y `SqliteRouteRepository` implementan el patrón Repository para abstraer la persistencia.

### 5.2 Dependency Injection

Todas las dependencias se inyectan por constructor:

```python
def __init__(self, repository: RouteRepositoryPort):
    self._repository = repository
```

### 5.3 Data Transfer Object (DTO)

Los DTOs encapsulan datos para transferencia entre capas:

```python
@dataclass
class CreateRouteDTO:
    name: str
    cedis_id: str
    day_of_week: str
```

### 5.4 Transaction Script

Los métodos de servicio implementan transacciones completas:

```python
begin_transaction()
# operaciones
commit_transaction()
# o rollback_transaction() en caso de error
```

## 6. Garantías de Integridad

### 6.1 Transaccionalidad (RNF-RUT-03)

Las operaciones críticas (dividir, fusionar) usan transacciones:

```python
try:
    self._repository.begin_transaction()
    # múltiples operaciones
    self._repository.commit_transaction()
except:
    self._repository.rollback_transaction()
```

### 6.2 Validaciones

**Nivel de Dominio**:
- Validaciones de negocio en constructores de entidades
- Validaciones en métodos de dominio

**Nivel de Aplicación**:
- Verificación de existencia de entidades
- Coordinación de validaciones

## 7. Testing

### 7.1 Tests Unitarios del Dominio

```python
# tests/domain/test_route_model.py
def test_divide_route():
    route = Route(...)
    route_a, route_b = route.divide_route(2)
    assert len(route_a.client_ids) == 2
```

### 7.2 Tests de Integración

```python
# tests/integration/test_route_service.py
def test_create_and_retrieve_route():
    service = RouteService(mock_repository)
    created = service.create_route(dto)
    retrieved = service.get_route_by_id(created.id)
    assert created.id == retrieved.id
```

## 8. Extensibilidad Futura

### 8.1 Agregar Nueva UI (API REST)

```python
# src/infrastructure/api/fastapi_app.py
@app.post("/routes")
def create_route(dto: CreateRouteDTO):
    return route_service.create_route(dto)
```

### 8.2 Cambiar Base de Datos

```python
# src/infrastructure/persistence/postgres_route_repository.py
class PostgresRouteRepository(RouteRepositoryPort):
    # Implementar métodos del puerto
```

### 8.3 Agregar Nuevos Casos de Uso

Solo modificar `RouteService`, sin tocar dominio ni infraestructura.

## 9. Conclusión

Esta arquitectura garantiza:

- ✅ **Mantenibilidad**: Código organizado y desacoplado
- ✅ **Testabilidad**: Fácil crear mocks y tests unitarios
- ✅ **Flexibilidad**: Cambiar tecnologías sin afectar la lógica de negocio
- ✅ **Escalabilidad**: Fácil agregar nuevas funcionalidades
- ✅ **Cumplimiento de Principios**: SOLID, DRY, KISS, SoC

El proyecto está listo para evolucionar y crecer manteniendo la calidad del código.
