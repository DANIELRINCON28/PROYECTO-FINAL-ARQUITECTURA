# Módulo de Optimización Inteligente de Rutas (TSP)

## 📋 Descripción General

Este módulo implementa el **ordenamiento inteligente de rutas** utilizando el problema del viajante (TSP - Traveling Salesman Problem) para minimizar la distancia total recorrida desde el CEDIS al visitar todos los clientes asignados a una ruta.

## 🏗️ Arquitectura

La implementación sigue estrictamente la **Arquitectura Hexagonal (Ports & Adapters)**:

```
┌─────────────────────────────────────────────────────────┐
│                   CAPA DE APLICACIÓN                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │   RouteOptimizationService                        │  │
│  │   - optimize_route_intelligent()                  │  │
│  │   - check_optimization_availability()             │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           │ Usa
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    CAPA DE DOMINIO                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  PUERTOS (Interfaces Abstractas)                 │   │
│  │  • GeoDistanceProviderPort                       │   │
│  │  • RouteOptimizationSolverPort                   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           │ Implementado por
                           ▼
┌─────────────────────────────────────────────────────────┐
│                CAPA DE INFRAESTRUCTURA                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ADAPTADORES (Implementaciones Concretas)        │   │
│  │  • GoogleMapsDistanceAdapter                     │   │
│  │  • ORToolsTSPSolver                              │   │
│  │  • NearestNeighborTSPSolver (Fallback)           │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 📦 Componentes Implementados

### 1. Puertos (Domain Layer)

#### `GeoDistanceProviderPort`
**Ubicación:** `src/domain/ports/geo_distance_provider_port.py`

Interfaz abstracta para calcular distancias entre coordenadas geográficas.

```python
class GeoDistanceProviderPort(ABC):
    @abstractmethod
    def calculate_distance(origin: GeoCoordinate, destination: GeoCoordinate) -> DistanceResult
    
    @abstractmethod
    def calculate_distance_matrix(origins: List[GeoCoordinate], destinations: List[GeoCoordinate]) -> List[List[DistanceResult]]
    
    @abstractmethod
    def is_available() -> bool
```

**Value Objects:**
- `GeoCoordinate`: Representa una coordenada geográfica (latitud, longitud)
- `DistanceResult`: Resultado con distancia (km) y duración (minutos)

#### `RouteOptimizationSolverPort`
**Ubicación:** `src/domain/ports/route_optimization_solver_port.py`

Interfaz abstracta para resolver problemas de optimización TSP.

```python
class RouteOptimizationSolverPort(ABC):
    @abstractmethod
    def solve_tsp(distance_matrix: List[List[float]], start_index: int) -> OptimizationResult
    
    @abstractmethod
    def solve_tsp_with_duration(distance_matrix, duration_matrix, start_index, optimize_by) -> OptimizationResult
    
    @abstractmethod
    def is_available() -> bool
```

**Value Object:**
- `OptimizationResult`: Resultado con índices ordenados, distancia total y duración total

### 2. Servicio de Aplicación

#### `RouteOptimizationService`
**Ubicación:** `src/application/services/route_optimization_service.py`

Servicio que orquesta la optimización de rutas.

**Método Principal:**
```python
def optimize_route_intelligent(dto: OptimizeRouteDTO, clients: List[Client]) -> OptimizedRouteResultDTO
```

**Proceso:**
1. Obtiene la ruta del repositorio
2. Valida que todos los clientes tienen coordenadas
3. Construye lista de coordenadas [CEDIS, Cliente1, Cliente2, ...]
4. Calcula matriz de distancias usando `GeoDistanceProviderPort`
5. Resuelve TSP usando `RouteOptimizationSolverPort`
6. Mapea índices optimizados a IDs de clientes
7. Actualiza el orden en la entidad Route
8. Persiste cambios
9. Retorna resultado

### 3. Adaptadores (Infrastructure Layer)

#### `GoogleMapsDistanceAdapter`
**Ubicación:** `src/infrastructure/services/google_maps_distance_adapter.py`

Implementación concreta que usa **Google Maps Distance Matrix API**.

**Características:**
- Calcula distancias reales por carretera
- Considera tráfico y condiciones de ruta
- Fallback a distancia euclidiana (Haversine) si no hay ruta disponible
- Requiere API Key de Google Maps

**Configuración:**
```python
# .env
GOOGLE_MAPS_API_KEY=tu_api_key_aqui
```

#### `ORToolsTSPSolver`
**Ubicación:** `src/infrastructure/services/ortools_tsp_solver.py`

Implementación que usa **Google OR-Tools** para resolver TSP de forma óptima.

**Características:**
- Algoritmo de optimización avanzado
- Búsqueda local guiada (Guided Local Search)
- Soluciones cercanas al óptimo
- Límite de tiempo configurable (30 segundos)

**Estrategias de optimización:**
- `distance`: Minimiza distancia total
- `duration`: Minimiza tiempo total
- `balanced`: Balance 60% distancia, 40% tiempo

#### `NearestNeighborTSPSolver`
**Ubicación:** `src/infrastructure/services/ortools_tsp_solver.py`

Implementación de **fallback** sin dependencias externas.

**Características:**
- Algoritmo Nearest Neighbor (vecino más cercano)
- Soluciones subóptimas pero rápidas
- No requiere instalación de OR-Tools
- Siempre disponible

## 🚀 Uso

### Instalación de Dependencias

```powershell
# Instalar nuevas dependencias
pip install googlemaps==4.10.0
pip install ortools==9.8.3296
```

### Ejemplo de Uso

```python
from src.application.factories.service_factory import ServiceFactory
from src.application.dtos import OptimizeRouteDTO
from src.domain.models.client import Client

# 1. Crear factory y obtener servicio
factory = ServiceFactory()
optimization_service = factory.create_optimization_service()

# 2. Verificar disponibilidad
availability = optimization_service.check_optimization_availability()
print(availability)
# {
#   "geo_distance_provider_available": True,
#   "optimization_solver_available": True,
#   "intelligent_optimization_available": True
# }

# 3. Preparar datos
dto = OptimizeRouteDTO(
    route_id="ruta-123",
    cedis_latitude=4.7110,
    cedis_longitude=-74.0721,
    optimization_strategy="distance"  # "distance", "duration" o "balanced"
)

clients = [
    Client(id="c1", name="Cliente 1", address="...", latitude=4.72, longitude=-74.08),
    Client(id="c2", name="Cliente 2", address="...", latitude=4.68, longitude=-74.05),
    # ... más clientes
]

# 4. Ejecutar optimización
result = optimization_service.optimize_route_intelligent(dto, clients)

# 5. Revisar resultado
print(f"Éxito: {result.success}")
print(f"Orden original: {result.original_client_order}")
print(f"Orden optimizado: {result.optimized_client_order}")
print(f"Distancia total: {result.total_distance_km:.2f} km")
print(f"Duración total: {result.total_duration_minutes:.2f} min")
```

## 📊 DTOs

### `OptimizeRouteDTO`
```python
@dataclass
class OptimizeRouteDTO:
    route_id: str
    cedis_latitude: float
    cedis_longitude: float
    optimization_strategy: str = "distance"  # "distance", "duration", "balanced"
```

### `OptimizedRouteResultDTO`
```python
@dataclass
class OptimizedRouteResultDTO:
    route_id: str
    original_client_order: List[str]
    optimized_client_order: List[str]
    total_distance_km: float
    total_duration_minutes: float
    distance_saved_km: float
    success: bool
    message: str
```

## 🔧 Configuración

### Variables de Entorno (.env)

```ini
# Google Maps API Key (obligatorio para optimización)
GOOGLE_MAPS_API_KEY=AIzaSy...

# Coordenadas del CEDIS
CEDIS_LATITUDE=4.7110
CEDIS_LONGITUDE=-74.0721
CEDIS_ADDRESS=Bogotá, Colombia
```

## ⚠️ Manejo de Errores

El servicio implementa múltiples niveles de tolerancia a fallos:

1. **API Key no configurada**: El geo distance provider no estará disponible
2. **OR-Tools no instalado**: Se usa Nearest Neighbor Solver automáticamente
3. **Fallo en cálculo de distancias**: Se retorna error detallado sin actualizar la ruta
4. **Clientes sin coordenadas**: Se lanza excepción descriptiva
5. **Matriz de distancias inválida**: El solver lanza excepción clara

## 🧪 Testing

### Mock de Puertos

```python
from unittest.mock import Mock
from src.application.factories.service_factory import ServiceFactory

# Crear mocks
mock_geo_provider = Mock(spec=GeoDistanceProviderPort)
mock_tsp_solver = Mock(spec=RouteOptimizationSolverPort)

# Configurar comportamiento
mock_geo_provider.is_available.return_value = True
mock_geo_provider.calculate_distance_matrix.return_value = [[...]]

mock_tsp_solver.is_available.return_value = True
mock_tsp_solver.solve_tsp_with_duration.return_value = OptimizationResult(...)

# Inyectar mocks
service = RouteOptimizationService(
    route_repository=mock_repo,
    optimization_service=None,
    geo_distance_provider=mock_geo_provider,
    optimization_solver=mock_tsp_solver
)
```

## 📈 Ventajas de la Arquitectura

1. **Desacoplamiento**: El dominio no conoce detalles de Google Maps u OR-Tools
2. **Testabilidad**: Los puertos se pueden mockear fácilmente
3. **Flexibilidad**: Se pueden cambiar adaptadores sin tocar el dominio
4. **Fallback automático**: Si OR-Tools no está disponible, usa Nearest Neighbor
5. **Múltiples proveedores**: Se puede agregar OpenStreetMap, Mapbox, etc. sin cambiar el core

## 🔄 Flujo de Datos

```
Usuario → UI → DTO → RouteOptimizationService
                           │
                           ├─→ RouteRepository (obtener ruta)
                           │
                           ├─→ GeoDistanceProviderPort (calcular distancias)
                           │       └─→ GoogleMapsDistanceAdapter
                           │              └─→ Google Maps API
                           │
                           ├─→ RouteOptimizationSolverPort (resolver TSP)
                           │       └─→ ORToolsTSPSolver
                           │              └─→ Google OR-Tools
                           │
                           └─→ RouteRepository (actualizar ruta)
```

## 📝 Próximos Pasos

1. **Integración UI**: Agregar botón "Optimizar Ruta" en Flask/Streamlit
2. **Visualización**: Mostrar mapa con ruta antes/después de optimizar
3. **Métricas**: Mostrar ahorro de distancia y tiempo
4. **Cache**: Cachear matrices de distancias para evitar llamadas repetidas
5. **Límites API**: Manejar límites de Google Maps (25x25 puntos por request)

## 🐛 Troubleshooting

### OR-Tools no se instala
```powershell
# Versión específica de Python requerida (3.8-3.11)
python --version

# Reinstalar con pip actualizado
python -m pip install --upgrade pip
pip install ortools
```

### Google Maps retorna error
```python
# Verificar API Key
from src.infrastructure.services.google_maps_distance_adapter import GoogleMapsDistanceAdapter
adapter = GoogleMapsDistanceAdapter("tu_api_key")
print(adapter.is_available())  # Debe ser True
```

### Solución subóptima
- Si usa Nearest Neighbor: Instalar OR-Tools
- Si usa OR-Tools: Aumentar tiempo límite en el solver
- Considerar usar estrategia "balanced" en lugar de "distance"

## 📚 Referencias

- [Google OR-Tools Documentation](https://developers.google.com/optimization)
- [Google Maps Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix)
- [Traveling Salesman Problem (TSP)](https://en.wikipedia.org/wiki/Travelling_salesman_problem)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
