# Diagramas y Tablas ADL - Yedistribuciones

**Complemento Visual del Análisis ADL**  
**Fecha:** 6 de noviembre de 2025

---

## Tabla Resumen de Componentes ADL

| ID  | Componente | Tipo | Capa | Interfaces Provistos | Interfaces Requeridos | PNF Críticas | Criticidad |
|-----|------------|------|------|---------------------|----------------------|--------------|-----------|
| C1  | RouteService | Computacional | Aplicación | createRoute, divideRoute, mergeRoutes, etc. | RouteRepositoryPort | Transaccionalidad, Disponibilidad | ALTA |
| C2  | RouteOptimizationService | Computacional | Aplicación | optimizeRouteOrder, geocodeClients, calculateMetrics | RouteRepositoryPort, RouteOptimizationPort | Latencia, Disponibilidad | MEDIA |
| C3  | Route | Computacional | Dominio | addClient, removeClient, divideRoute, mergeWith | Ninguno | Validación, Inmutabilidad | ALTA |
| C4  | Client | Computacional | Dominio | hasCoordinates | Ninguno | Inmutabilidad | MEDIA |
| C5  | PostgresRouteRepository | Almacenamiento | Infraestructura | RouteRepositoryPort (impl) | PostgreSQL DB | Transaccionalidad, Persistencia | ALTA |
| C6  | GoogleMapsOptimizationService | Computacional | Infraestructura | RouteOptimizationPort (impl) | Google Maps API | Disponibilidad, Latencia | MEDIA |
| C7  | StreamlitUI | Computacional | Infraestructura | HTTP endpoints, vistas | RouteService, RouteOptimizationService | Usabilidad, Responsividad | ALTA |
| C8  | PostgreSQL Database | Almacenamiento | Externo | SQL queries | Ninguno | Persistencia, Integridad | CRÍTICA |
| C9  | Config | Computacional | Configuración | Métodos de config | Variables de entorno | Seguridad, Centralización | ALTA |

---

## Tabla Resumen de Conectores ADL

| ID  | Conector | Tipo | Componentes Conectados | Protocolo | Flujo | PNF Críticas |
|-----|----------|------|------------------------|-----------|-------|-------------|
| CN1 | DependencyInjection | Procedural Call | Main → Services → Repositories | Method Invocation | Unidireccional | Acoplamiento Bajo, Testabilidad |
| CN2 | PostgreSQL-JDBC | DB Connection | PostgresRouteRepository ↔ PostgreSQL | PostgreSQL Wire (TCP/IP) | Request/Response | Latencia Baja, Fiabilidad |
| CN3 | Google Maps REST API | HTTP REST | GoogleMapsService ↔ Google Maps | HTTPS/REST JSON | Request/Response | Latencia Variable, Disponibilidad |
| CN4 | Streamlit HTTP | HTTP/WebSocket | User Browser ↔ StreamlitUI | HTTP/WS | Bidireccional | Usabilidad, Latencia |
| CN5 | Port-Adapter Boundary | Abstract Interface | Services → Ports → Adapters | Interface Method Call | Unidireccional | Acoplamiento Muy Bajo, Evolucionabilidad |
| CN6 | DTO Data Transfer | Data Serialization | Application ↔ UI/Domain | In-memory objects | In-memory | Latencia Muy Baja, Seguridad |

---

## Diagrama de Componentes y Conectores (Notación ADL)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SISTEMA YEDISTRIBUCIONES                        │
│                     (Sistema de Gestión de Rutas)                       │
└─────────────────────────────────────────────────────────────────────────┘

LEYENDA:
  ┌─────────┐
  │Component│  = Componente Computacional
  └─────────┘
  
  [Storage]  = Componente de Almacenamiento
  
  ───────>   = Conector (flujo de datos/control)
  
  «Port»     = Puerto (interfaz abstracta)


ESTRUCTURA JERÁRQUICA DE COMPONENTES:

┌───────────────────────────────────────────────────────────────────────┐
│ CAPA: DRIVING ADAPTERS (Adaptadores Conductores)                     │
│                                                                       │
│   ┌──────────────────────┐                                           │
│   │ StreamlitUI          │◄────────────── Usuario (Actor Externo)   │
│   │ (C7)                 │                                           │
│   │ -------------------- │                                           │
│   │ Puertos Provistos:   │                                           │
│   │  • dashboard_view()  │                                           │
│   │  • create_route_view()│                                          │
│   │  • optimize_route_view()│                                        │
│   │ Puertos Requeridos:  │                                           │
│   │  • RouteService      │                                           │
│   │  • RouteOptimizationService (opt)│                               │
│   └──────────┬───────────┘                                           │
│              │                                                        │
│              │ CN1: DependencyInjection                              │
│              │ CN6: DTO Transfer                                     │
└──────────────┼────────────────────────────────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────────────────────────────────┐
│ CAPA: APPLICATION LAYER (Capa de Aplicación)                         │
│                                                                       │
│   ┌───────────────────────┐          ┌──────────────────────────┐   │
│   │ RouteService          │          │ RouteOptimizationService │   │
│   │ (C1)                  │          │ (C2)                     │   │
│   │ --------------------- │          │ ----------------------   │   │
│   │ Puertos Provistos:    │          │ Puertos Provistos:       │   │
│   │  • createRoute()      │          │  • optimizeRouteOrder()  │   │
│   │  • divideRoute()      │          │  • geocodeClients()      │   │
│   │  • mergeRoutes()      │          │  • calculateMetrics()    │   │
│   │ Puertos Requeridos:   │          │ Puertos Requeridos:      │   │
│   │  • RouteRepositoryPort│◄─┐       │  • RouteRepositoryPort   │   │
│   └───────────┬───────────┘  │       │  • RouteOptimizationPort │   │
│               │              │       └─────────┬────────────────┘   │
│               │              │                 │                     │
│               │ CN5: Port-Adapter Boundary     │                     │
└───────────────┼──────────────┼─────────────────┼─────────────────────┘
                │              │                 │
                ▼              │                 ▼
┌───────────────────────────────────────────────────────────────────────┐
│ CAPA: DOMAIN LAYER (Núcleo de Dominio)                               │
│                                                                       │
│   ┌─────────────────────────────────────────────────────────┐        │
│   │ «Port» RouteRepositoryPort                              │        │
│   │ (Interface)                                             │        │
│   │ -------------------------------------------------------  │        │
│   │  + save(route: Route)                                   │        │
│   │  + update(route: Route)                                 │        │
│   │  + findById(id: str) -> Optional[Route]                 │        │
│   │  + getAll() -> List[Route]                              │        │
│   │  + delete(id: str)                                      │        │
│   │  + beginTransaction()                                   │        │
│   │  + commitTransaction()                                  │        │
│   │  + rollbackTransaction()                                │        │
│   └─────────────────────────────────────────────────────────┘        │
│                                                                       │
│   ┌─────────────────────────────────────────────────────────┐        │
│   │ «Port» RouteOptimizationPort                            │        │
│   │ (Interface)                                             │        │
│   │ -------------------------------------------------------  │        │
│   │  + geocodeAddress(addr: str) -> Tuple[lat, lon]         │        │
│   │  + optimizeRoute(origin, waypoints) -> Result           │        │
│   │  + calculateDistanceMatrix(...) -> Matrix               │        │
│   └─────────────────────────────────────────────────────────┘        │
│                                                                       │
│   ┌──────────────┐              ┌─────────────┐                      │
│   │ Route        │              │ Client      │                      │
│   │ (C3)         │              │ (C4)        │                      │
│   │ ------------ │              │ ----------- │                      │
│   │ + id: str    │              │ + id: str   │                      │
│   │ + name: str  │              │ + name: str │                      │
│   │ + cedis_id   │              │ + address   │                      │
│   │ + day_of_week│              │ + lat, lon  │                      │
│   │ + client_ids │              │             │                      │
│   │ ------------ │              │ ----------- │                      │
│   │ + addClient()│              │ + hasCoords()│                     │
│   │ + divideRoute()│            │             │                      │
│   │ + mergeWith()│              │             │                      │
│   └──────────────┘              └─────────────┘                      │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                │                                │
                │ CN5: implements                │ CN5: implements
                ▼                                ▼
┌───────────────────────────────────────────────────────────────────────┐
│ CAPA: INFRASTRUCTURE LAYER (Adaptadores Conducidos)                  │
│                                                                       │
│   ┌────────────────────────────┐     ┌──────────────────────────┐   │
│   │ PostgresRouteRepository    │     │ GoogleMapsOptimization   │   │
│   │ (C5)                       │     │ Service (C6)             │   │
│   │ -------------------------- │     │ ----------------------   │   │
│   │ Implementa:                │     │ Implementa:              │   │
│   │  RouteRepositoryPort       │     │  RouteOptimizationPort   │   │
│   │                            │     │                          │   │
│   │ PNF:                       │     │ PNF:                     │   │
│   │  • Transaccionalidad: Alta │     │  • Latencia: Variable    │   │
│   │  • Persistencia: Alta      │     │  • Disponibilidad: Media │   │
│   │  • Pool: 1-10 conexiones   │     │  • Rate Limit: API       │   │
│   └────────────┬───────────────┘     └──────────┬───────────────┘   │
│                │                                 │                   │
│                │ CN2: PostgreSQL-JDBC            │ CN3: HTTPS REST   │
└────────────────┼─────────────────────────────────┼───────────────────┘
                 │                                 │
                 ▼                                 ▼
┌────────────────────────────┐      ┌───────────────────────────┐
│ [PostgreSQL Database]      │      │ [Google Maps Platform]    │
│ (C8 - Sistema Externo)     │      │ (Sistema Externo SaaS)    │
│ -------------------------- │      │ ------------------------- │
│ Tablas:                    │      │ APIs:                     │
│  • cedis                   │      │  • Geocoding API          │
│  • clientes                │      │  • Distance Matrix API    │
│  • rutas                   │      │  • Directions API         │
│  • rutas_clientes          │      │                           │
│  • vendedores              │      │ SLA: 99.9%                │
│                            │      │ Latencia: 100ms - 2s      │
│ PNF:                       │      │                           │
│  • ACID: Completo          │      │                           │
│  • Escalabilidad: Alta     │      │                           │
│  • Criticidad: CRÍTICA     │      │                           │
└────────────────────────────┘      └───────────────────────────┘


┌───────────────────────────────────────────────────────────────────────┐
│ COMPONENTE TRANSVERSAL: Config (C9)                                  │
│                                                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │ Config (Singleton Pattern)                                  │   │
│   │ ------------------------------------------------------------ │   │
│   │ • DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD           │   │
│   │ • GOOGLE_MAPS_API_KEY                                       │   │
│   │ • CEDIS_LATITUDE, CEDIS_LONGITUDE                           │   │
│   │ • MAX_ROUTE_DISTANCE_KM, MAX_ROUTE_DURATION_HOURS           │   │
│   │                                                              │   │
│   │ PNF: Centralización, Seguridad (env vars), Flexibilidad     │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│   Usado por: Todos los componentes de infraestructura                │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Diagrama de Secuencia: Crear Ruta (ADL Behavioral View)

```
Usuario   StreamlitUI   RouteService   RouteRepository   PostgreSQL
  │           │             │                │               │
  │─fill form─►│            │                │               │
  │           │─createRoute(DTO)─►          │               │
  │           │             │                │               │
  │           │             │─generateUUID() │               │
  │           │             │─new Route()────┐               │
  │           │             │                │               │
  │           │             │─save(route)────►               │
  │           │             │                │─INSERT INTO──►│
  │           │             │                │               │───┐
  │           │             │                │               │   │ Transaction
  │           │             │                │               │◄──┘
  │           │             │                │◄──────────────│
  │           │             │─commit()───────►               │
  │           │             │                │─COMMIT────────►│
  │           │             │                │◄──────────────│
  │           │             │◄───────────────│               │
  │           │             │─to_DTO()───────┐               │
  │           │◄──return RouteDTO────────────│               │
  │◄──display─│             │                │               │
  │  success  │             │                │               │

CONECTORES INVOLUCRADOS:
• CN1 (DependencyInjection): StreamlitUI → RouteService
• CN6 (DTO Transfer): RouteService → StreamlitUI (return)
• CN5 (Port-Adapter): RouteService → RouteRepositoryPort → PostgresRepository
• CN2 (PostgreSQL-JDBC): PostgresRepository → PostgreSQL

RESTRICCIONES APLICADAS:
• R2: Transaccionalidad en operaciones (COMMIT/ROLLBACK)
• R3: Validación de dominio en Route.__post_init__
• R8: Credenciales desde variables de entorno
```

---

## Diagrama de Secuencia: Optimizar Ruta (ADL Behavioral View)

```
Usuario  StreamlitUI  RouteOptService  RouteRepo  GoogleMapsService  GoogleAPI
  │         │              │              │             │               │
  │─select route─►         │              │             │               │
  │         │─optimizeRouteOrder()───►    │             │               │
  │         │              │─findById()───►             │               │
  │         │              │              │─SELECT──►PostgreSQL         │
  │         │              │◄─Route────────             │               │
  │         │              │                             │               │
  │         │              │─geocodeClients()───────────►               │
  │         │              │                             │─geocode()────►│
  │         │              │                             │               │───┐
  │         │              │                             │               │   │ External
  │         │              │                             │               │   │ API Call
  │         │              │                             │               │◄──┘
  │         │              │                             │◄─coordinates─│
  │         │              │                             │               │
  │         │              │─optimizeRoute()────────────►               │
  │         │              │                             │─directions()─►│
  │         │              │                             │ (waypoint_   │
  │         │              │                             │  optimize=T) │
  │         │              │                             │◄─optimized──│
  │         │              │                             │   order      │
  │         │              │◄─RouteOptimizationResult────│               │
  │         │◄─display optimized route────│             │               │
  │◄─visual─│              │              │             │               │
  │  map    │              │              │             │               │

CONECTORES INVOLUCRADOS:
• CN1: StreamlitUI → RouteOptimizationService
• CN5: RouteOptService → RouteOptimizationPort → GoogleMapsService
• CN3: GoogleMapsService → Google Maps API (HTTPS REST)

RESTRICCIONES APLICADAS:
• R5: Google Maps API requerida (funcionalidad opcional)
• R6: Latencia máxima < 3 segundos (puede violarse con muchos waypoints)

PNF OBSERVADAS:
• Latencia: Variable (100ms - 2s por API externa)
• Disponibilidad: Dependiente de Google Maps SLA
• Fiabilidad: Alta (SLA 99.9%)
```

---

## Diagrama de Secuencia: Dividir Ruta (ADL Behavioral View)

```
Usuario  StreamlitUI  RouteService   RouteRepo   Route(Domain)  PostgreSQL
  │         │             │              │             │            │
  │─select route + split point─►         │             │            │
  │         │─divideRouteUseCase()───►   │             │            │
  │         │             │─beginTransaction()─►       │            │
  │         │             │              │─BEGIN───────────────────►│
  │         │             │              │◄────────────────────────│
  │         │             │─findById()───►             │            │
  │         │             │              │─SELECT──────────────────►│
  │         │             │◄─originalRoute─────────────────────────│
  │         │             │                             │            │
  │         │             │─divideRoute(index)─────────►│           │
  │         │             │                             │─validate──┐
  │         │             │                             │◄──────────┘
  │         │             │                             │─split─────┐
  │         │             │                             │  logic    │
  │         │             │                             │◄──────────┘
  │         │             │◄─(routeA, routeB)───────────│           │
  │         │             │                             │            │
  │         │             │─deactivate(original)───►Route.deactivate()
  │         │             │─update(original)───►        │            │
  │         │             │              │─UPDATE activa=false──────►│
  │         │             │─save(routeA)─►             │            │
  │         │             │              │─INSERT──────────────────►│
  │         │             │─save(routeB)─►             │            │
  │         │             │              │─INSERT──────────────────►│
  │         │             │─commitTransaction()─►      │            │
  │         │             │              │─COMMIT──────────────────►│
  │         │             │              │◄────────────────────────│
  │         │◄─(dtoA, dtoB)──────────────│             │            │
  │◄─display both routes──│              │             │            │

RESTRICCIONES APLICADAS (CRÍTICAS):
• R2: Transaccionalidad garantizada (BEGIN → operaciones → COMMIT/ROLLBACK)
• R3: Validación en Route.divideRoute() (índice válido, lista no vacía)
• R1: Inversión de dependencias (RouteService → RouteRepositoryPort)

PNF OBSERVADAS:
• Transaccionalidad: ALTA (ACID completo)
• Consistencia: ALTA (rollback automático en caso de error)
• Integridad: ALTA (soft delete de ruta original)

CONECTORES:
• CN1: DependencyInjection
• CN5: Port-Adapter Boundary
• CN2: PostgreSQL-JDBC con soporte transaccional
```

---

## Matriz de Trazabilidad: Restricciones vs Componentes

| Restricción | C1<br>RouteService | C2<br>OptService | C3<br>Route | C5<br>PostgresRepo | C6<br>GoogleMaps | C7<br>StreamlitUI | C8<br>PostgreSQL | C9<br>Config |
|-------------|:------------------:|:----------------:|:-----------:|:------------------:|:----------------:|:-----------------:|:----------------:|:------------:|
| **R1: Inversión de Dependencias** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ➖ | ➖ |
| **R2: Transaccionalidad** | ✅ | ➖ | ➖ | ✅ | ➖ | ➖ | ✅ | ➖ |
| **R3: Validación de Dominio** | ➖ | ➖ | ✅ | ➖ | ➖ | ➖ | ➖ | ➖ |
| **R4: PostgreSQL Único** | ➖ | ➖ | ➖ | ✅ | ➖ | ➖ | ✅ | ✅ |
| **R5: Google Maps Requerida** | ➖ | ✅ | ➖ | ➖ | ✅ | ⚠️ | ➖ | ✅ |
| **R6: Latencia UI < 3s** | ⚠️ | ⚠️ | ➖ | ⚠️ | ⚠️ | ✅ | ➖ | ➖ |
| **R7: Pool Conexiones 1-10** | ➖ | ➖ | ➖ | ✅ | ➖ | ➖ | ✅ | ✅ |
| **R8: Credenciales en .env** | ➖ | ➖ | ➖ | ⚠️ | ⚠️ | ➖ | ➖ | ✅ |
| **R9: Sin Autenticación** | ➖ | ➖ | ➖ | ➖ | ➖ | ❌ | ➖ | ➖ |
| **R10: DTOs Inmutables** | ⚠️ | ⚠️ | ➖ | ➖ | ➖ | ⚠️ | ➖ | ➖ |
| **R11: Días en Español** | ➖ | ➖ | ✅ | ✅ | ➖ | ✅ | ✅ | ➖ |

**Leyenda:**
- ✅ = Restricción aplicada y cumplida
- ⚠️ = Restricción aplicada parcialmente o con limitaciones
- ❌ = Restricción NO cumplida (violación)
- ➖ = Restricción no aplicable a este componente

---

## Matriz de Propiedades No Funcionales por Componente

| PNF | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 |
|-----|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Escalabilidad** | 🟢 | 🟡 | 🟢 | 🟢 | 🟢 | 🟡 | 🔴 | 🟢 | 🟢 |
| **Disponibilidad** | 🟢 | 🟡 | 🟢 | 🟢 | 🟢 | 🟡 | 🟡 | 🟢 | 🟢 |
| **Latencia** | 🟢 | 🟡 | 🟢 | 🟢 | 🟢 | 🔴 | 🟢 | 🟢 | 🟢 |
| **Transaccionalidad** | 🟢 | ➖ | ➖ | ➖ | 🟢 | ➖ | ➖ | 🟢 | ➖ |
| **Seguridad** | 🟢 | 🟢 | 🟢 | 🟢 | 🟡 | 🟡 | 🔴 | 🟢 | 🟡 |
| **Testabilidad** | 🟢 | 🟢 | 🟢 | 🟢 | 🟡 | 🟡 | 🟡 | ➖ | 🟢 |
| **Mantenibilidad** | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟡 | ➖ | 🟢 |
| **Evolucionabilidad** | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟡 | ➖ | 🟢 |
| **Usabilidad** | ➖ | ➖ | ➖ | ➖ | ➖ | ➖ | 🟢 | ➖ | ➖ |
| **Criticidad** | 🔴 | 🟡 | 🔴 | 🟡 | 🔴 | 🟡 | 🔴 | 🔴 | 🔴 |

**Leyenda:**
- 🟢 = Alta/Buena
- 🟡 = Media/Aceptable
- 🔴 = Baja/Crítica
- ➖ = No aplicable

---

## Mapa de Decisiones Arquitectónicas (ADRs)

```
┌────────────────────────────────────────────────────────────────────┐
│                     DECISIONES ARQUITECTÓNICAS                     │
│                         (ADR Overview)                             │
└────────────────────────────────────────────────────────────────────┘

DA-01: Arquitectura Hexagonal
  ├─ Contexto: Necesidad de desacoplamiento
  ├─ Decisión: Ports & Adapters
  ├─ Impacto: ✅ Alta testabilidad, ✅ Evolucionabilidad
  └─ Trade-off: ⚠️ Mayor complejidad inicial

        │
        ▼

DA-02: PostgreSQL como RDBMS
  ├─ Contexto: Necesidad de ACID y concurrencia
  ├─ Decisión: PostgreSQL (migración desde SQLite)
  ├─ Impacto: ✅ Transaccionalidad, ✅ Escalabilidad
  └─ Trade-off: ⚠️ Requiere servidor dedicado

        │
        ▼

DA-03: Google Maps API
  ├─ Contexto: Optimización de rutas
  ├─ Decisión: Google Maps Platform
  ├─ Impacto: ✅ Algoritmos de alta calidad
  └─ Trade-off: ⚠️ Costo por uso, ⚠️ Vendor lock-in parcial
               ✅ Mitigado con RouteOptimizationPort (abstracción)

        │
        ▼

DA-04: Streamlit como UI
  ├─ Contexto: Time-to-market rápido
  ├─ Decisión: Streamlit (Python-only)
  ├─ Impacto: ✅ Desarrollo rápido, ✅ UI profesional
  └─ Trade-off: ⚠️ Limitaciones de escalabilidad
               ✅ Mitigable con migración futura (Hexagonal permite cambio)

        │
        ▼

DA-05: DTOs para Transferencia
  ├─ Contexto: Desacoplamiento UI/Dominio
  ├─ Decisión: Data Transfer Objects
  ├─ Impacto: ✅ Contratos explícitos, ✅ Versionado de API
  └─ Trade-off: ⚠️ Código de mapeo adicional

```

---

## Grafo de Dependencias (ADL Configuration)

```
Notación:
  A ──> B  : A depende de B
  A ━━> B  : A implementa la interfaz B
  A ···> B : A usa ocasionalmente B (opcional)


                        ┌──────────────┐
                        │   Usuario    │
                        │   (Actor)    │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ StreamlitUI  │
                        │     (C7)     │
                        └──────┬───────┘
                               │
                ┌──────────────┼──────────────┐
                │                             │
                ▼                             ▼
         ┌──────────────┐            ┌────────────────┐
         │ RouteService │            │RouteOptService │
         │     (C1)     │            │      (C2)      │
         └──────┬───────┘            └────────┬───────┘
                │                             │
                │                   ┌─────────┴─────────┐
                │                   │                   │
                ▼                   ▼                   ▼
    ┌────────────────────┐  ┌────────────────┐  ┌─────────────────┐
    │«RouteRepository    │  │«RouteRepository│  │«RouteOptimization│
    │     Port»          │  │     Port»      │  │     Port»        │
    │   (Interface)      │  │   (Interface)  │  │   (Interface)    │
    └─────────┬──────────┘  └────────┬───────┘  └──────┬───────────┘
              │                      │                  │
              │ implements           │ implements       │ implements
              │                      │                  │
              ▼                      ▼                  ▼
    ┌─────────────────┐    ┌─────────────────┐   ┌──────────────────┐
    │ PostgresRoute   │    │ PostgresRoute   │   │ GoogleMaps       │
    │ Repository (C5) │    │ Repository (C5) │   │ Service (C6)     │
    └────────┬────────┘    └────────┬────────┘   └────────┬─────────┘
             │                      │                      │
             ▼                      ▼                      ▼
    ┌─────────────────┐    ┌─────────────────┐   ┌──────────────────┐
    │  PostgreSQL DB  │    │  PostgreSQL DB  │   │ Google Maps API  │
    │      (C8)       │    │      (C8)       │   │   (External)     │
    └─────────────────┘    └─────────────────┘   └──────────────────┘


DOMINIO (usado por Application Layer):
    ┌────────────┐          ┌────────────┐
    │   Route    │          │   Client   │
    │    (C3)    │          │    (C4)    │
    └────────────┘          └────────────┘
         ▲                        ▲
         │                        │
         │ usa                    │ usa
         │                        │
    ┌────┴──────────┐    ┌────────┴─────┐
    │ RouteService  │    │RouteOptService│
    │     (C1)      │    │      (C2)     │
    └───────────────┘    └───────────────┘


CONFIGURACIÓN (usado por todos):
    ┌──────────────────┐
    │      Config      │
    │       (C9)       │
    │  (Singleton)     │
    └────────┬─────────┘
             │
             │ provee configuración a
             │
    ┌────────┼──────────────────┬──────────────────┐
    │        │                  │                  │
    ▼        ▼                  ▼                  ▼
  (C5)     (C6)               (C7)              (C8)
PostgresRepo GoogleMaps    StreamlitUI      PostgreSQL
```

---

## Conclusiones Visuales

### Fortalezas Arquitectónicas (Resumen Visual)

```
┌─────────────────────────────────────────────────────────────┐
│  FORTALEZAS DE LA ARQUITECTURA                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🟢 Separación de Concerns         ████████████ 100%       │
│  🟢 Inversión de Dependencias      ████████████  98%       │
│  🟢 Testabilidad                   ██████████    85%       │
│  🟢 Evolucionabilidad              ███████████   95%       │
│  🟢 Mantenibilidad                 ███████████   90%       │
│  🟡 Escalabilidad                  ██████        60%       │
│  🟡 Seguridad                      ████          45%       │
│  🔴 Observabilidad                 ██            25%       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Áreas de Mejora Prioritarias (Roadmap Visual)

```
FASE 1: SEGURIDAD (Crítico - 2-3 semanas)
┌──────────────────────────────────────────┐
│ ❌ Implementar autenticación             │
│ ⚠️  Migrar secretos a vault              │
│ ⚠️  Habilitar HTTPS                      │
└──────────────────────────────────────────┘

FASE 2: OBSERVABILIDAD (Alto - 1-2 semanas)
┌──────────────────────────────────────────┐
│ 📊 Logging estructurado (JSON)           │
│ 📈 Métricas de aplicación (Prometheus)   │
│ 🔍 Health checks                         │
└──────────────────────────────────────────┘

FASE 3: ESCALABILIDAD (Medio - 4-6 semanas)
┌──────────────────────────────────────────┐
│ 🚀 Migrar a FastAPI + React (opcional)   │
│ 🗄️  PostgreSQL HA (Primary/Replica)      │
│ 🐳 Containerización (Docker/K8s)         │
└──────────────────────────────────────────┘
```

---

**Fin del Documento de Diagramas y Tablas ADL**  
**Versión:** 1.0  
**Fecha:** 6 de noviembre de 2025
