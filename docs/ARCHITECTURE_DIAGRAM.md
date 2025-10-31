# 📐 Diagrama de Arquitectura con Google Maps API

## Vista General de la Arquitectura Hexagonal

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ADAPTADORES CONDUCTORES                         │
│                      (Driving Adapters - Entrada)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │            Streamlit UI (streamlit_app.py)                  │      │
│   │                                                              │      │
│   │  • Ver Todas las Rutas                                       │      │
│   │  • Crear Nueva Ruta                                          │      │
│   │  • Gestionar Clientes                                        │      │
│   │  • Dividir Ruta                                              │      │
│   │  • Fusionar Rutas                                            │      │
│   │  • 🆕 Optimizar Ruta (Google Maps)                          │      │
│   │  • 🆕 Ver Métricas de Ruta                                  │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                              ↓ llama                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                      CAPA DE APLICACIÓN (Lógica de Negocio)             │
│                          Application Services                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────────────────────┐  ┌────────────────────────────────┐ │
│   │   RouteService               │  │  RouteOptimizationService 🆕   │ │
│   │   (route_service.py)         │  │  (route_optimization_service)  │ │
│   │                              │  │                                │ │
│   │  • create_route_use_case     │  │  • geocode_clients()           │ │
│   │  • get_all_routes            │  │  • optimize_route_order()      │ │
│   │  • get_route_by_id           │  │  • calculate_route_metrics()   │ │
│   │  • update_route_use_case     │  │  • suggest_route_split()       │ │
│   │  • divide_route_use_case     │  │  • test_optimization_service() │ │
│   │  • merge_routes_use_case     │  │                                │ │
│   │  • add_client_to_route       │  │                                │ │
│   │  • remove_client_from_route  │  │                                │ │
│   └──────────────┬───────────────┘  └───────────┬────────────────────┘ │
│                  │ depende de                    │ depende de           │
│                  ↓ (Puertos)                     ↓ (Puertos)            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    CAPA DE DOMINIO (Núcleo del Sistema)                 │
│              Domain Models + Ports (Abstracciones)                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────────────┐        ┌──────────────────────┐             │
│   │  Models (Entidades)  │        │  Ports (Interfaces)  │             │
│   ├──────────────────────┤        ├──────────────────────┤             │
│   │                      │        │                      │             │
│   │  • Route             │        │  RouteRepositoryPort │             │
│   │    - route_id        │        │  (Persistencia)      │             │
│   │    - name            │        │                      │             │
│   │    - cedis_id        │        │  • save()            │             │
│   │    - day_of_week     │        │  • find_by_id()      │             │
│   │    - clients         │        │  • find_all()        │             │
│   │    - is_active       │        │  • update()          │             │
│   │                      │        │  • delete()          │             │
│   │  Métodos de Negocio: │        │  • begin_transaction()│            │
│   │  • divide_route()    │        │  • commit_transaction()│           │
│   │  • merge_routes()    │        │                      │             │
│   │  • add_client()      │        └──────────────────────┘             │
│   │  • remove_client()   │                                             │
│   │  • validate()        │        ┌──────────────────────────────┐     │
│   └──────────────────────┘        │  RouteOptimizationPort 🆕   │     │
│                                   │  (Optimización)              │     │
│   ┌──────────────────────┐        │                              │     │
│   │  Client              │        │  • geocode_address()         │     │
│   │    - client_id       │        │  • calculate_distance_matrix()│    │
│   │    - name            │        │  • optimize_route()          │     │
│   │    - address         │        │  • get_route_directions()    │     │
│   │    - latitude 🆕     │        │                              │     │
│   │    - longitude 🆕    │        └──────────────────────────────┘     │
│   │                      │                      ↑                       │
│   │  • has_coordinates() │                      │ implementa           │
│   └──────────────────────┘                      │                       │
│                                                 │                       │
└─────────────────────────────────────────────────┼───────────────────────┘
                                                  │
┌─────────────────────────────────────────────────┼───────────────────────┐
│                   CAPA DE INFRAESTRUCTURA       │                       │
│                 (Adaptadores de Salida)         │                       │
├─────────────────────────────────────────────────┼───────────────────────┤
│                                                 │                       │
│   ┌──────────────────────────────┐    ┌────────┴──────────────────┐    │
│   │  SqliteRouteRepository       │    │  GoogleMapsOptimization   │    │
│   │  (sqlite_route_repository)   │    │  Service 🆕               │    │
│   │                              │    │  (google_maps_service)    │    │
│   │  implements                  │    │                           │    │
│   │  RouteRepositoryPort         │    │  implements               │    │
│   │                              │    │  RouteOptimizationPort    │    │
│   │  Tecnología: SQLite          │    │                           │    │
│   │  • Transacciones             │    │  Tecnología: Google Maps  │    │
│   │  • Serialización JSON        │    │  • googlemaps library     │    │
│   │  • Gestión de conexión       │    │  • API key management     │    │
│   └──────────────┬───────────────┘    │  • Error handling         │    │
│                  │                    │  • Fallback logic         │    │
│                  ↓                    └───────────┬───────────────┘    │
│                                                   │                     │
│   ┌──────────────────────────────┐    ┌──────────▼───────────────┐    │
│   │   SQLite Database            │    │  Google Maps APIs        │    │
│   │   yedistribuciones.db        │    │                          │    │
│   │                              │    │  • Directions API        │    │
│   │  Tablas:                     │    │  • Distance Matrix API   │    │
│   │  • routes                    │    │  • Geocoding API         │    │
│   │  • route_events (EventSourcing)│   │                          │    │
│   └──────────────────────────────┘    └──────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                       CONFIGURACIÓN Y DEPENDENCIAS                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │  main.py (Dependency Injection / Assembler)                  │     │
│   │                                                               │     │
│   │  1. Cargar Config (config.py)                                │     │
│   │  2. Crear SqliteRouteRepository                              │     │
│   │  3. Crear GoogleMapsOptimizationService (si API key existe)  │     │
│   │  4. Crear RouteService                                       │     │
│   │  5. Crear RouteOptimizationService                           │     │
│   │  6. Inyectar todo en Streamlit UI                            │     │
│   │  7. Iniciar aplicación                                       │     │
│   └──────────────────────────────────────────────────────────────┘     │
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │  config.py (Configuration Pattern)                           │     │
│   │                                                               │     │
│   │  • GOOGLE_MAPS_API_KEY (de variable de entorno)              │     │
│   │  • CEDIS_LATITUDE, CEDIS_LONGITUDE                           │     │
│   │  • DATABASE_PATH                                             │     │
│   │  • MAX_ROUTE_DISTANCE_KM                                     │     │
│   │  • MAX_ROUTE_DURATION_HOURS                                  │     │
│   │  • is_google_maps_enabled()                                  │     │
│   │  • validate_config()                                         │     │
│   └──────────────────────────────────────────────────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Datos: Optimizar Ruta

```
┌──────────┐
│ Usuario  │
└────┬─────┘
     │
     │ 1. Selecciona "🗺️ Optimizar Ruta"
     │
     ▼
┌─────────────────────────────────┐
│  Streamlit UI                   │
│  (streamlit_app.py)             │
│                                 │
│  optimize_route_view()          │
└────┬────────────────────────────┘
     │
     │ 2. Llama optimize_route_order()
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  RouteOptimizationService                           │
│  (route_optimization_service.py)                    │
│                                                     │
│  optimize_route_order(route_id, cedis, clients)    │
│                                                     │
│  Pasos:                                             │
│  a) Filtrar clientes con coordenadas                │
│  b) Geocodificar clientes sin coordenadas ───┐     │
│  c) Extraer waypoints                        │     │
│  d) Llamar optimizer.optimize_route() ───┐   │     │
└──────────────────────────────────────────┼───┼─────┘
                                           │   │
     ┌─────────────────────────────────────┘   │
     │                                         │
     │ 3. optimize_route()          4. geocode_address()
     │                                         │
     ▼                                         ▼
┌──────────────────────────────────────────────────────────┐
│  GoogleMapsOptimizationService                           │
│  (google_maps_service.py)                                │
│                                                          │
│  implements RouteOptimizationPort                        │
│                                                          │
│  • geocode_address(address) → (lat, lon)                │
│  • optimize_route(origin, waypoints, dest) → Result     │
└────┬─────────────────────────────────┬───────────────────┘
     │                                 │
     │ 5. API Call: geocode()          │ 6. API Call: directions()
     │                                 │
     ▼                                 ▼
┌──────────────────────────────────────────────────────────┐
│  Google Maps APIs (External Service)                     │
│                                                          │
│  • Geocoding API: Dirección → Coordenadas               │
│  • Directions API: Waypoints → Ruta Optimizada          │
└────┬─────────────────────────────────┬───────────────────┘
     │                                 │
     │ 7. Retorna coordenadas          │ 8. Retorna ruta optimizada
     │                                 │
     ▼                                 ▼
┌──────────────────────────────────────────────────────────┐
│  GoogleMapsOptimizationService                           │
│                                                          │
│  Procesa respuestas y crea:                              │
│  RouteOptimizationResult                                 │
│    - optimized_order: [id1, id2, ...]                    │
│    - total_distance_km: 85.3                             │
│    - total_duration_minutes: 247                         │
└────┬─────────────────────────────────────────────────────┘
     │
     │ 9. Retorna RouteOptimizationResult
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│  RouteOptimizationService                               │
│                                                         │
│  Recibe resultado y lo retorna a la UI                 │
└────┬────────────────────────────────────────────────────┘
     │
     │ 10. Retorna result
     │
     ▼
┌─────────────────────────────────┐
│  Streamlit UI                   │
│                                 │
│  Muestra:                       │
│  ✅ Distancia: 85.3 km          │
│  ✅ Tiempo: 247 min             │
│  ✅ Orden optimizado:           │
│     1. Cliente A                │
│     2. Cliente D                │
│     3. Cliente B                │
│     ...                         │
└────┬────────────────────────────┘
     │
     │ 11. Visualiza resultado
     │
     ▼
┌──────────┐
│ Usuario  │
└──────────┘
```

---

## Diagrama de Clases Simplificado

```
┌─────────────────────────────────────────────────────────────┐
│                      «interface»                            │
│                 RouteOptimizationPort                       │
├─────────────────────────────────────────────────────────────┤
│ + geocode_address(address: str): Tuple[float, float] | None│
│ + calculate_distance_matrix(origins, destinations): List[]  │
│ + optimize_route(origin, waypoints, dest): Result          │
│ + get_route_directions(waypoints): Dict                    │
└──────────────────────────┬──────────────────────────────────┘
                           △
                           │ implements
                           │
         ┌─────────────────┴────────────────────────┐
         │                                          │
┌────────┴────────────────────┐   ┌────────────────┴────────────────┐
│ GoogleMapsOptimizationService│   │  FutureMapBoxService 🔮        │
├──────────────────────────────┤   │  (Futuro adaptador alternativo) │
│ - _client: googlemaps.Client │   ├─────────────────────────────────┤
│ - _api_key: str              │   │ - _api_key: str                 │
├──────────────────────────────┤   │ - _base_url: str                │
│ + geocode_address()          │   ├─────────────────────────────────┤
│ + optimize_route()           │   │ + geocode_address()             │
│ + test_connection(): bool    │   │ + optimize_route()              │
└──────────────────────────────┘   └─────────────────────────────────┘
         △                                      △
         │ usa                                  │ usa
         │                                      │
┌────────┴──────────────────────────┐   ┌──────┴──────────────────────┐
│ RouteOptimizationService          │   │  RouteService               │
├───────────────────────────────────┤   ├─────────────────────────────┤
│ - _route_repo: Repository         │   │ - _repository: Repository   │
│ - _optimizer: OptimizationPort    │   ├─────────────────────────────┤
├───────────────────────────────────┤   │ + create_route_use_case()   │
│ + geocode_clients()               │   │ + get_all_routes()          │
│ + optimize_route_order()          │   │ + divide_route_use_case()   │
│ + calculate_route_metrics()       │   │ + merge_routes_use_case()   │
│ + suggest_route_split()           │   └─────────────────────────────┘
└───────────────────────────────────┘
         △                  △
         │ usa              │ usa
         │                  │
┌────────┴──────────────────┴───────┐
│  Streamlit UI                     │
│  (streamlit_app.py)               │
├───────────────────────────────────┤
│ - route_service: RouteService     │
│ - optimization_service: Optional  │
├───────────────────────────────────┤
│ + run_ui()                        │
│ + optimize_route_view()           │
│ + route_metrics_view()            │
└───────────────────────────────────┘
```

---

## Ventajas de esta Arquitectura

### ✅ Bajo Acoplamiento
- UI no conoce Google Maps
- Dominio no depende de infraestructura
- Fácil cambio de proveedor

### ✅ Alta Cohesión
- Cada capa tiene responsabilidades claras
- Lógica de negocio en el dominio
- Coordinación en aplicación

### ✅ Testeabilidad
- Mocks fáciles de los puertos
- Tests unitarios sin API real
- Tests de integración aislados

### ✅ Mantenibilidad
- Cambios localizados
- Código auto-documentado
- Separación de concerns

### ✅ Escalabilidad
- Agregar nuevos adaptadores sin cambiar core
- Múltiples proveedores simultáneos
- Cache strategies desacopladas

---

**Diagramas creados para:** Yedistribuciones v2.0  
**Última actualización:** Enero 2025
