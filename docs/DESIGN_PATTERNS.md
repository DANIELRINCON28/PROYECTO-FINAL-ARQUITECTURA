# 🎨 Patrones de Diseño Implementados

## Tabla de Contenidos
1. [Singleton - Conexión a Base de Datos](#singleton)
2. [Builder - Construcción de Rutas](#builder)
3. [Factory - Creación de Servicios](#factory)
4. [Strategy - Algoritmos de Optimización](#strategy)
5. [Repository - Persistencia de Datos](#repository)
6. [Adapter - Adaptadores de Infraestructura](#adapter)
7. [Dependency Injection - Inversión de Dependencias](#dependency-injection)

---

## 🔐 1. Singleton - Conexión a Base de Datos {#singleton}

### Propósito
Garantizar que solo exista una única instancia de la conexión a la base de datos en toda la aplicación, optimizando recursos y evitando múltiples conexiones innecesarias.

### Ubicación
```
src/infrastructure/database/database_connection.py
```

### Diagrama UML
```
┌─────────────────────────────────┐
│    DatabaseConnection           │
├─────────────────────────────────┤
│ - _instance: DatabaseConnection │
│ - _lock: Lock                   │
│ - _connection: Connection       │
├─────────────────────────────────┤
│ + get_instance()                │
│ + get_connection()              │
│ + get_cursor()                  │
│ + commit()                      │
│ + rollback()                    │
└─────────────────────────────────┘
```

### Implementación Clave
```python
class DatabaseConnection:
    _instance: Optional['DatabaseConnection'] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls, connection_params: Optional[Dict[str, Any]] = None):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    instance = super().__new__(cls)
                    cls._instance = instance
        return cls._instance
```

### Uso
```python
from src.infrastructure.database import DatabaseConnection
from config import Config

# Primera llamada: crea la instancia
params = {
    'host': Config.DB_HOST,
    'port': Config.DB_PORT,
    'database': Config.DB_NAME,
    'user': Config.DB_USER,
    'password': Config.DB_PASSWORD
}
db = DatabaseConnection.get_instance(params)

# Segunda llamada: retorna la misma instancia
db2 = DatabaseConnection.get_instance()
assert db is db2  # True - misma instancia

# Uso con context manager
with db.get_cursor() as cursor:
    cursor.execute("SELECT * FROM rutas")
    results = cursor.fetchall()
```

### Ventajas
- ✅ Control de acceso único a la base de datos
- ✅ Reutilización de la conexión existente
- ✅ Gestión centralizada de la conexión
- ✅ Reducción del overhead de múltiples conexiones
- ✅ Thread-safe con Double-Checked Locking

### Consideraciones
- ⚠️ Puede dificultar el testing (usar `reset_instance()` para tests)
- ⚠️ Acoplamiento global en toda la aplicación

---

## 🏗️ 2. Builder - Construcción de Rutas {#builder}

### Propósito
Facilitar la construcción compleja de objetos Route paso a paso, permitiendo crear rutas con diferentes configuraciones de manera fluida y legible.

### Ubicación
```
src/domain/builders/route_builder.py
```

### Diagrama UML
```
┌─────────────────────┐
│   RouteBuilder      │
├─────────────────────┤
│ - _id               │
│ - _name             │
│ - _cedis_id         │
│ - _day_of_week      │
│ - _client_ids       │
│ - _is_active        │
├─────────────────────┤
│ + with_id()         │
│ + with_auto_id()    │
│ + with_name()       │
│ + with_cedis()      │
│ + with_day()        │
│ + with_client()     │
│ + with_clients()    │
│ + build()           │
└─────────────────────┘
        │
        │ builds
        ▼
┌─────────────────────┐
│      Route          │
└─────────────────────┘
```

### Implementación Clave
```python
class RouteBuilder:
    def with_name(self, name: str) -> 'RouteBuilder':
        if not name or not name.strip():
            raise ValueError("El nombre no puede estar vacío")
        self._name = name.strip()
        return self
    
    def build(self) -> Route:
        # Validar campos obligatorios
        if self._id is None:
            raise ValueError("Debe especificar un ID")
        
        # Construir el objeto Route
        route = Route(
            id=self._id,
            name=self._name,
            cedis_id=self._cedis_id,
            day_of_week=self._day_of_week,
            client_ids=self._client_ids.copy(),
            is_active=self._is_active
        )
        
        self._reset()
        return route
```

### Uso
```python
from src.domain.builders import RouteBuilder

# Construcción fluida
route = (RouteBuilder()
    .with_auto_id()
    .with_name("Ruta Norte")
    .with_cedis("CEDIS_BOGOTA")
    .with_day("LUNES")
    .with_clients(["CLI_001", "CLI_002", "CLI_003"])
    .with_active_status(True)
    .build())

# Método de conveniencia
route2 = RouteBuilder.create_simple("Ruta Sur", "CEDIS_MEDELLIN", "MARTES")

# Con Director
director = RouteDirector(RouteBuilder())
route3 = director.construct_weekly_route("Ruta Semanal", "CEDIS_CALI", "MIÉRCOLES")
```

### Ventajas
- ✅ Construcción paso a paso de objetos complejos
- ✅ Código más legible y mantenible
- ✅ Validación incremental durante la construcción
- ✅ Separación de la lógica de construcción
- ✅ Métodos fluidos (method chaining)

### Patrones Relacionados
- **Director**: Conoce recetas específicas para construir rutas comunes

---

## 🏭 3. Factory - Creación de Servicios {#factory}

### Propósito
Proporcionar una interfaz centralizada para crear instancias de servicios con sus dependencias correctamente configuradas, facilitando la inyección de dependencias y el testing.

### Ubicación
```
src/application/factories/service_factory.py
```

### Diagrama UML
```
┌──────────────────────┐
│   ServiceFactory     │
├──────────────────────┤
│ - _db_connection     │
│ - _repository        │
│ - _optimization      │
├──────────────────────┤
│ + create_route_      │
│   service()          │
│ + create_           │
│   optimization_     │
│   service()         │
│ + create_all_       │
│   services()        │
└──────────────────────┘
        │
        │ creates
        ▼
┌──────────────────────┐
│   RouteService       │
└──────────────────────┘
```

### Implementación Clave
```python
class ServiceFactory:
    def create_route_service(self) -> RouteService:
        repository = self._create_repository()
        return RouteService(repository)
    
    def create_optimization_service(self) -> Optional[RouteOptimizationService]:
        optimization_port = self._create_optimization_service()
        repository = self._create_repository()
        
        if optimization_port:
            return RouteOptimizationService(repository, optimization_port)
        return None
```

### Uso
```python
from src.application.factories import ServiceFactory

# Crear factory
factory = ServiceFactory.create_default()

# Crear servicios individuales
route_service = factory.create_route_service()
opt_service = factory.create_optimization_service()

# Crear todos los servicios
route_service, opt_service = factory.create_all_services()

# Para Flask
from src.application.factories import FlaskServiceFactory
FlaskServiceFactory.create_and_run()

# Para testing con mocks
from unittest.mock import Mock
mock_repo = Mock(spec=RouteRepositoryPort)
factory = ServiceFactory.create_for_testing(repository=mock_repo)
```

### Ventajas
- ✅ Centralización de la creación de objetos complejos
- ✅ Facilita el cambio de implementaciones
- ✅ Simplifica la configuración de dependencias
- ✅ Mejora la testabilidad mediante mocks
- ✅ Oculta la complejidad de construcción

### Variantes Implementadas
- **ServiceFactory**: Factory general
- **FlaskServiceFactory**: Factory especializada para Flask

---

## 🎯 4. Strategy - Algoritmos de Optimización {#strategy}

### Propósito
Definir una familia de algoritmos de optimización de rutas, encapsular cada uno de ellos y hacerlos intercambiables. Strategy permite que el algoritmo varíe independientemente de los clientes que lo usan.

### Ubicación
```
src/domain/strategies/optimization_strategy.py
```

### Diagrama UML
```
┌────────────────────────────────┐
│ RouteOptimizationStrategy      │
│        <<interface>>            │
├────────────────────────────────┤
│ + optimize()                   │
│ + get_name()                   │
│ + is_available()               │
└────────────────────────────────┘
            △
            │ implements
    ┌───────┼───────┬────────┐
    │       │       │        │
┌───┴───┐ ┌─┴─────┐ ┌──┴────┐ ┌────────┐
│Nearest│ │Google │ │2-Opt  │ │Custom  │
│Neighbor│ │Maps   │ │       │ │Strategy│
└───────┘ └───────┘ └───────┘ └────────┘

┌────────────────────────────────┐
│   OptimizationContext          │
├────────────────────────────────┤
│ - strategy: Strategy           │
├────────────────────────────────┤
│ + set_strategy()               │
│ + optimize()                   │
└────────────────────────────────┘
```

### Estrategias Implementadas

#### 1. Nearest Neighbor Strategy (Vecino Más Cercano)
```python
class NearestNeighborStrategy(RouteOptimizationStrategy):
    """Algoritmo Greedy - Rápido pero no óptimo"""
    
    def optimize(self, route, client_locations, origin):
        # Selecciona siempre el cliente más cercano no visitado
        # O(n²) complejidad temporal
        pass
```

**Características:**
- ⚡ Rápido: O(n²)
- 🎯 Precisión: Buena (no óptima)
- 💰 Costo: Gratis
- 📊 Uso: Rutas pequeñas/medianas

#### 2. Google Maps Strategy
```python
class GoogleMapsStrategy(RouteOptimizationStrategy):
    """Optimización usando Google Maps API"""
    
    def optimize(self, route, client_locations, origin):
        # Usa waypoint optimization de Google Maps
        # Considera tráfico real y distancias reales
        pass
```

**Características:**
- ⚡ Velocidad: Depende de API
- 🎯 Precisión: Excelente (óptima)
- 💰 Costo: Requiere API key ($)
- 📊 Uso: Producción, precisión crítica

#### 3. 2-Opt Strategy
```python
class TwoOptStrategy(RouteOptimizationStrategy):
    """Optimización local mediante intercambios"""
    
    def optimize(self, route, client_locations, origin):
        # Mejora iterativa intercambiando aristas
        # O(n² × iteraciones)
        pass
```

**Características:**
- ⚡ Velocidad: Media
- 🎯 Precisión: Muy buena (óptimo local)
- 💰 Costo: Gratis
- 📊 Uso: Balance precisión/velocidad

### Uso
```python
from src.domain.strategies import (
    NearestNeighborStrategy,
    GoogleMapsStrategy,
    TwoOptStrategy,
    OptimizationContext
)

# Crear estrategia
strategy = NearestNeighborStrategy()

# Usar con contexto
context = OptimizationContext(strategy)
result = context.optimize(route, client_locations, origin)

# Cambiar estrategia dinámicamente
context.set_strategy(TwoOptStrategy(max_iterations=500))
result2 = context.optimize(route, client_locations, origin)

# Con Google Maps
maps_service = GoogleMapsService(api_key)
context.set_strategy(GoogleMapsStrategy(maps_service))
result3 = context.optimize(route, client_locations, origin)

# Resultado
print(f"Orden optimizado: {result.optimized_order}")
print(f"Distancia: {result.total_distance_km} km")
print(f"Duración: {result.total_duration_minutes} min")
print(f"Algoritmo: {result.algorithm_used}")
```

### Ventajas
- ✅ Algoritmos intercambiables en runtime
- ✅ Fácil agregar nuevos algoritmos
- ✅ Separación de la lógica de optimización
- ✅ Facilita testing de diferentes estrategias
- ✅ Permite comparación de algoritmos

---

## 📚 5. Repository - Persistencia de Datos {#repository}

### Propósito
Encapsular la lógica de acceso a datos y proporcionar una interfaz de colección de objetos del dominio, abstrayendo la tecnología de persistencia.

### Ubicación
```
src/domain/ports/route_repository_port.py (Interface)
src/infrastructure/persistence/postgres_route_repository.py (Implementation)
```

### Diagrama UML
```
┌─────────────────────────────┐
│  RouteRepositoryPort        │
│      <<interface>>          │
├─────────────────────────────┤
│ + save(route)               │
│ + find_by_id(id)            │
│ + find_all()                │
│ + update(route)             │
│ + delete(id)                │
│ + find_by_cedis(cedis_id)   │
└─────────────────────────────┘
            △
            │ implements
    ┌───────┴────────┐
    │                │
┌───┴─────────┐ ┌───┴──────────┐
│PostgresRoute│ │SQLiteRoute   │
│Repository   │ │Repository    │
└─────────────┘ └──────────────┘
```

### Implementación Clave
```python
from abc import ABC, abstractmethod

class RouteRepositoryPort(ABC):
    """Puerto (interfaz) para el repositorio de rutas"""
    
    @abstractmethod
    def save(self, route: Route) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, route_id: str) -> Optional[Route]:
        pass

class PostgresRouteRepository(RouteRepositoryPort):
    """Implementación concreta con PostgreSQL"""
    
    def save(self, route: Route) -> None:
        with self._get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO rutas (identificador_unico, nombre_descriptivo, ...)
                VALUES (%(id)s, %(name)s, ...)
            """, {...})
```

### Uso
```python
from src.infrastructure.persistence import PostgresRouteRepository

# Crear repositorio
repo = PostgresRouteRepository(connection_params)

# Operaciones CRUD
route = RouteBuilder.create_simple("Ruta 1", "CEDIS_1", "LUNES")
repo.save(route)

# Buscar
found_route = repo.find_by_id(route.id)

# Actualizar
found_route.add_client("CLI_001")
repo.update(found_route)

# Eliminar
repo.delete(route.id)
```

### Ventajas
- ✅ Abstracción de la persistencia
- ✅ Fácil cambiar de BD (PostgreSQL ↔ SQLite)
- ✅ Facilita testing con mocks
- ✅ Separa dominio de infraestructura
- ✅ Interfaz tipo colección

---

## 🔌 6. Adapter - Adaptadores de Infraestructura {#adapter}

### Propósito
Convertir la interfaz de una clase en otra interfaz que los clientes esperan. Permite que clases con interfaces incompatibles trabajen juntas.

### Ubicación
```
src/infrastructure/ui/flask_app.py (UI Adapter)
src/infrastructure/services/google_maps_service.py (Service Adapter)
```

### Diagrama UML
```
┌──────────────────┐
│  Application     │
│    Service       │
└────────┬─────────┘
         │ uses
         ▼
┌──────────────────┐
│   Port           │
│  <<interface>>   │
└────────┬─────────┘
         △
         │ implements
         │
┌────────┴─────────┐
│   Adapter        │
│                  │
├──────────────────┤
│ External Service │
└──────────────────┘
```

### Ejemplos Implementados

#### 1. Flask UI Adapter
```python
# Adaptador de entrada (Driving Adapter)
def create_flask_app(route_service, optimization_service):
    """Adapta HTTP requests a llamadas de servicio"""
    
    @app.route('/api/routes', methods=['POST'])
    def create_route():
        # Adaptar request HTTP a DTO
        dto = CreateRouteDTO(**request.json)
        
        # Llamar al servicio
        result = route_service.create_route(dto)
        
        # Adaptar respuesta a JSON
        return jsonify(result.__dict__)
```

#### 2. Google Maps Service Adapter
```python
# Adaptador de salida (Driven Adapter)
class GoogleMapsService(RouteOptimizationPort):
    """Adapta Google Maps API a nuestro puerto"""
    
    def optimize_route(self, origin, waypoints):
        # Adaptar datos a formato Google Maps
        gmaps_request = self._adapt_to_gmaps_format(origin, waypoints)
        
        # Llamar API externa
        response = self._gmaps_client.directions(...)
        
        # Adaptar respuesta a nuestro formato
        return self._adapt_from_gmaps_format(response)
```

### Ventajas
- ✅ Integración con APIs externas
- ✅ Mantiene el dominio limpio
- ✅ Fácil cambiar proveedores externos
- ✅ Facilita testing con mocks

---

## 💉 7. Dependency Injection - Inversión de Dependencias {#dependency-injection}

### Propósito
Invertir el control de las dependencias, inyectándolas desde fuera en lugar de crearlas internamente. Cumple con el principio SOLID de Inversión de Dependencias.

### Implementación en el Sistema
```python
# ❌ MAL: Dependencia directa
class RouteService:
    def __init__(self):
        self.repository = PostgresRouteRepository()  # Acoplamiento fuerte

# ✅ BIEN: Inyección de dependencias
class RouteService:
    def __init__(self, repository: RouteRepositoryPort):
        self._repository = repository  # Depende de abstracción

# Uso
repo = PostgresRouteRepository(params)
service = RouteService(repo)  # Inyección por constructor
```

### Ventajas
- ✅ Bajo acoplamiento
- ✅ Alta testabilidad
- ✅ Flexibilidad para cambiar implementaciones
- ✅ Cumple SOLID (DIP)

---

## 📊 Resumen de Patrones por Capa

### Domain Layer
- ✅ **Builder**: Construcción de rutas
- ✅ **Strategy**: Algoritmos de optimización
- ✅ **Entity**: Modelo Route con lógica de negocio

### Application Layer
- ✅ **Factory**: Creación de servicios
- ✅ **DTO**: Transfer objects
- ✅ **Service**: Casos de uso

### Infrastructure Layer
- ✅ **Singleton**: Conexión a BD
- ✅ **Repository**: Persistencia
- ✅ **Adapter**: UI y servicios externos

---

## 🎓 Beneficios Generales

1. **Mantenibilidad**: Código organizado y fácil de entender
2. **Escalabilidad**: Fácil agregar nuevas funcionalidades
3. **Testabilidad**: Componentes aislados y mockeables
4. **Reusabilidad**: Componentes reutilizables
5. **Flexibilidad**: Fácil cambiar implementaciones
6. **SOLID**: Cumple principios de diseño

---

## 📖 Referencias

- **Gang of Four (GoF)**: Design Patterns - Elements of Reusable Object-Oriented Software
- **Martin Fowler**: Patterns of Enterprise Application Architecture
- **Clean Architecture**: Robert C. Martin
- **Domain-Driven Design**: Eric Evans

---

**Autor**: Sistema Yedistribuciones  
**Fecha**: Noviembre 2025  
**Versión**: 1.0
