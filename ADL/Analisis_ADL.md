# Análisis ADL - Yedistribuciones: Sistema de Gestión de Rutas

**Proyecto:** Yedistribuciones - Sistema de Gestión de Rutas  
**Fecha:** 6 de noviembre de 2025  
**Arquitectura Base:** Hexagonal (Ports & Adapters)  
**Autor:** Análisis Estructural y de Comportamiento mediante ADL

---

## Resumen Ejecutivo

Este documento presenta un análisis completo del sistema Yedistribuciones utilizando la notación de **Lenguajes de Descripción de Arquitectura (ADL)**. El análisis se enfoca en la estructura de alto nivel y abstracción de la implementación, identificando componentes computacionales, conectores, configuración topológica, restricciones y propiedades no funcionales.

---

## 1. COMPONENTES (Computational/Storage Units)

Los componentes representan las unidades primarias de cómputo y almacenamiento del sistema. Se identifican según las capas de la arquitectura hexagonal implementada.

### 1.1 Componente: **RouteService** (Servicio de Aplicación)

**Tipo:** Unidad Computacional (Application Service)  
**Responsabilidad:** Orquestación de casos de uso de gestión de rutas

#### Interfaces (Puertos Provistos):
- `createRoute(dto: CreateRouteDTO) -> RouteDTO`
- `assignClientToRoute(route_id: str, client_id: str) -> RouteDTO`
- `removeClientFromRoute(route_id: str, client_id: str) -> RouteDTO`
- `reorderClientsInRoute(route_id: str, ordered_client_ids: List[str]) -> RouteDTO`
- `divideRouteUseCase(...) -> tuple[RouteDTO, RouteDTO]`
- `mergeRoutesUseCase(...) -> RouteDTO`
- `getAllRoutes(include_inactive: bool) -> List[RouteDTO]`
- `findRouteById(route_id: str) -> Optional[RouteDTO]`

#### Interfaces (Puertos Requeridos):
- `RouteRepositoryPort` (puerto de persistencia)

#### Propiedades No Funcionales (PNF):
- **Transaccionalidad:** Alta - Garantiza consistencia ACID en operaciones compuestas (división/fusión)
- **Escalabilidad:** Media - Dependiente del repositorio subyacente
- **Disponibilidad:** Alta - Sin estado interno, permite múltiples instancias
- **Criticidad:** ALTA - Core del sistema de negocio

---

### 1.2 Componente: **RouteOptimizationService** (Servicio de Aplicación)

**Tipo:** Unidad Computacional (Application Service)  
**Responsabilidad:** Orquestación de casos de uso de optimización de rutas

#### Interfaces (Puertos Provistos):
- `geocodeClients(clients: List[ClientLocation]) -> List[ClientLocation]`
- `optimizeRouteOrder(route_id: str, cedis_location: Tuple, client_locations: List) -> RouteOptimizationResult`
- `calculateRouteMetrics(cedis_location: Tuple, client_locations: List) -> Dict[str, float]`
- `suggestRouteDivision(route_id: str, ...) -> Dict`

#### Interfaces (Puertos Requeridos):
- `RouteRepositoryPort` (puerto de persistencia)
- `RouteOptimizationPort` (puerto de optimización externa)

#### Propiedades No Funcionales (PNF):
- **Escalabilidad:** Media - Limitada por API externa (Google Maps)
- **Disponibilidad:** Media - Dependiente de servicio externo
- **Latencia:** Variable - Sujeta a respuesta de API externa
- **Criticidad:** MEDIA - Funcionalidad opcional pero valiosa

---

### 1.3 Componente: **Route** (Entidad de Dominio)

**Tipo:** Unidad Computacional (Domain Model)  
**Responsabilidad:** Lógica de negocio pura de rutas

#### Interfaces (Puertos Provistos):
- `addClient(client_id: str) -> None`
- `removeClient(client_id: str) -> None`
- `reorderClients(ordered_client_ids: List[str]) -> None`
- `divideRoute(split_index: int) -> Tuple[Route, Route]`
- `mergeWith(other_route: Route) -> Route`
- `deactivate() -> None`
- `activate() -> None`

#### Propiedades No Funcionales (PNF):
- **Inmutabilidad:** Media - Operaciones retornan nuevas instancias en divisiones/fusiones
- **Validación:** Alta - Validaciones estrictas de reglas de negocio
- **Independencia:** Alta - Cero dependencias externas
- **Criticidad:** ALTA - Núcleo del modelo de dominio

---

### 1.4 Componente: **Client** (Entidad de Dominio)

**Tipo:** Unidad Computacional (Domain Model)  
**Responsabilidad:** Representación de clientes en el dominio

#### Interfaces (Puertos Provistos):
- `hasCoordinates() -> bool`

#### Propiedades No Funcionales (PNF):
- **Inmutabilidad:** Alta - Dataclass frozen
- **Validación:** Alta - Validaciones en construcción
- **Criticidad:** MEDIA - Entidad auxiliar

---

### 1.5 Componente: **PostgresRouteRepository** (Adaptador de Persistencia)

**Tipo:** Unidad de Almacenamiento (Driven Adapter - Infrastructure)  
**Responsabilidad:** Persistencia de rutas en PostgreSQL

#### Interfaces (Puertos Implementados):
- `RouteRepositoryPort` (implementación completa)
  - `save(route: Route) -> None`
  - `update(route: Route) -> None`
  - `findById(route_id: str) -> Optional[Route]`
  - `getAll() -> List[Route]`
  - `delete(route_id: str) -> None`
  - `beginTransaction() -> None`
  - `commitTransaction() -> None`
  - `rollbackTransaction() -> None`

#### Propiedades No Funcionales (PNF):
- **Persistencia:** Alta - Almacenamiento relacional ACID
- **Transaccionalidad:** Alta - Soporte completo de transacciones
- **Escalabilidad:** Alta - Pool de conexiones configurables (1-10)
- **Disponibilidad:** Alta - Dependiente de PostgreSQL
- **Latencia:** Baja - Operaciones locales de red
- **Criticidad:** ALTA - Punto único de persistencia

---

### 1.6 Componente: **GoogleMapsOptimizationService** (Adaptador de Servicio Externo)

**Tipo:** Unidad Computacional (Driven Adapter - Infrastructure)  
**Responsabilidad:** Integración con Google Maps API para optimización

#### Interfaces (Puertos Implementados):
- `RouteOptimizationPort` (implementación completa)
  - `geocodeAddress(address: str) -> Optional[Tuple[float, float]]`
  - `calculateDistanceMatrix(origins: List, destinations: List) -> List[List[float]]`
  - `optimizeRoute(origin: Tuple, waypoints: List, destination: Optional[Tuple]) -> RouteOptimizationResult`
  - `getRouteDirections(waypoints: List) -> Dict`

#### Propiedades No Funcionales (PNF):
- **Disponibilidad:** Media - Dependiente de servicio externo (Google)
- **Latencia:** Variable - 100-500ms típico, hasta 2s en picos
- **Escalabilidad:** Limitada - Cuotas de API (restricciones de rate-limit)
- **Fiabilidad:** Alta - SLA de Google Maps Platform
- **Criticidad:** MEDIA - Funcionalidad opcional

---

### 1.7 Componente: **StreamlitUI** (Adaptador de Interfaz)

**Tipo:** Unidad Computacional (Driving Adapter - Infrastructure)  
**Responsabilidad:** Interfaz web de usuario

#### Interfaces (Puertos Provistos):
- HTTP endpoints manejados por Streamlit framework
- Vistas:
  - `dashboard_view()`
  - `create_route_view()`
  - `view_all_routes()`
  - `manage_clients_view()`
  - `divide_route_view()`
  - `merge_routes_view()`
  - `optimize_route_view()`
  - `route_metrics_view()`

#### Interfaces (Puertos Requeridos):
- `RouteService`
- `RouteOptimizationService` (opcional)

#### Propiedades No Funcionales (PNF):
- **Usabilidad:** Alta - Diseño corporativo profesional (WCAG AA)
- **Responsividad:** Alta - Layout adaptativo
- **Disponibilidad:** Media - Single instance deployment
- **Latencia:** Baja - Renderizado en cliente
- **Criticidad:** ALTA - Punto de acceso principal

---

### 1.8 Componente: **PostgreSQL Database** (Sistema de Almacenamiento)

**Tipo:** Unidad de Almacenamiento (External System)  
**Responsabilidad:** Persistencia relacional de datos

#### Esquema de Datos:
- **Tablas:** `cedis`, `vendedores`, `clientes`, `rutas`, `rutas_clientes`
- **Relaciones:** 1:N (cedis-rutas), N:M (rutas-clientes)

#### Propiedades No Funcionales (PNF):
- **Persistencia:** Alta - ACID compliant
- **Escalabilidad:** Alta - Pool de conexiones, índices optimizados
- **Disponibilidad:** Alta - Configuración standalone con backups
- **Integridad:** Alta - Constraints, foreign keys, transacciones
- **Criticidad:** CRÍTICA - Almacenamiento primario

---

### 1.9 Componente: **Config** (Configuración del Sistema)

**Tipo:** Unidad Computacional (Configuration Singleton)  
**Responsabilidad:** Gestión centralizada de configuración

#### Interfaces (Puertos Provistos):
- `isGoogleMapsEnabled() -> bool`
- `getCedisLocation() -> Tuple[float, float]`
- `getDatabaseUrl() -> str`
- `getDbConnectionParams() -> dict`
- `validateConfig() -> List[str]`

#### Propiedades No Funcionales (PNF):
- **Centralización:** Alta - Única fuente de verdad
- **Seguridad:** Media - Variables de entorno con dotenv
- **Flexibilidad:** Alta - Configuración por entorno
- **Criticidad:** ALTA - Controla dependencias críticas

---

## 2. CONECTORES (Interactions/Relations)

Los conectores definen los mecanismos de interacción entre componentes.

### 2.1 Conector: **DependencyInjection** (Inyección de Dependencias)

**Tipo:** Procedural Call / Method Invocation  
**Descripción:** Patrón de inyección de dependencias manual a través del constructor

#### Roles:
- **Client:** Componente que requiere dependencias (RouteService, RouteOptimizationService)
- **Injector:** Main.py (ensamblador de la aplicación)
- **Provider:** Implementaciones concretas de puertos

#### Semántica:
- **Protocolo:** Invocación síncrona de métodos
- **Flujo:** Unidireccional (Client → Provider)
- **Acoplamiento:** Bajo - Basado en abstracciones (puertos)

**Glue:** Constructor injection pattern

#### PNF del Conector:
- **Acoplamiento:** Bajo - Interfaces abstractas
- **Testabilidad:** Alta - Fácil mock de dependencias
- **Mantenibilidad:** Alta - Cambio de implementaciones sin afectar clientes

---

### 2.2 Conector: **PostgreSQL-JDBC** (Conexión de Base de Datos)

**Tipo:** Database Connection / psycopg2 Protocol  
**Descripción:** Conexión TCP/IP con protocolo PostgreSQL usando driver psycopg2

#### Roles:
- **Client:** PostgresRouteRepository
- **Server:** PostgreSQL Database

#### Semántica:
- **Protocolo:** PostgreSQL Wire Protocol (TCP/IP)
- **Flujo:** Request/Response síncrono
- **Pool:** 1-10 conexiones concurrentes (configurables)
- **Transaccionalidad:** Soporte ACID completo

**Glue:** psycopg2-binary driver

#### PNF del Conector:
- **Latencia:** Baja (< 10ms en red local)
- **Fiabilidad:** Alta - Reconexión automática
- **Seguridad:** Alta - Autenticación por usuario/password
- **Throughput:** Alto - Pool de conexiones

---

### 2.3 Conector: **Google Maps REST API** (HTTP/REST)

**Tipo:** HTTP REST API Client  
**Descripción:** Cliente HTTP para consumo de Google Maps Platform APIs

#### Roles:
- **Client:** GoogleMapsOptimizationService
- **Server:** Google Maps Platform (APIs: Geocoding, Distance Matrix, Directions)

#### Semántica:
- **Protocolo:** HTTPS/REST (JSON over HTTP)
- **Flujo:** Request/Response síncrono
- **Autenticación:** API Key (query parameter)
- **Rate Limiting:** Cuotas por día/segundo según plan

**Glue:** googlemaps Python client library

#### PNF del Conector:
- **Latencia:** Variable (100ms - 2s)
- **Disponibilidad:** Alta (SLA 99.9% de Google)
- **Escalabilidad:** Limitada por cuotas
- **Seguridad:** Alta - HTTPS, API Key

---

### 2.4 Conector: **Streamlit HTTP Server** (HTTP)

**Tipo:** HTTP Server / WebSocket  
**Descripción:** Servidor web integrado de Streamlit para servir la UI

#### Roles:
- **Server:** Streamlit Framework
- **Client:** Navegador web del usuario

#### Semántica:
- **Protocolo:** HTTP/WebSocket
- **Flujo:** Bidireccional (WebSocket para reactividad)
- **Estado:** Stateful (sesión de usuario)

**Glue:** Streamlit framework

#### PNF del Conector:
- **Latencia:** Baja (< 50ms local)
- **Usabilidad:** Alta - Interfaz reactiva
- **Escalabilidad:** Media - Single-threaded server
- **Seguridad:** Media - Sin autenticación por defecto

---

### 2.5 Conector: **Port-Adapter Boundary** (Interfaz Abstracta)

**Tipo:** Abstract Interface / Boundary  
**Descripción:** Frontera arquitectónica entre capas mediante interfaces

#### Roles:
- **Port (Interface):** RouteRepositoryPort, RouteOptimizationPort
- **Adapter (Implementation):** PostgresRouteRepository, GoogleMapsOptimizationService
- **Consumer:** RouteService, RouteOptimizationService

#### Semántica:
- **Protocolo:** Method invocation through interface
- **Flujo:** Unidireccional (Consumer → Port → Adapter)
- **Binding:** Static (compile-time dependency injection)

**Glue:** Python ABC (Abstract Base Classes)

#### PNF del Conector:
- **Acoplamiento:** Muy bajo - Inversión de dependencias (DIP)
- **Sustituibilidad:** Alta - Cualquier implementación del puerto
- **Testabilidad:** Muy alta - Mocking trivial
- **Evolucionabilidad:** Alta - Cambios localizados

---

### 2.6 Conector: **DTO Data Transfer** (Data Transfer Object)

**Tipo:** Data Serialization / Marshalling  
**Descripción:** Transferencia de datos entre capas usando DTOs

#### Roles:
- **Sender:** Application Services
- **Receiver:** UI Layer / Domain Layer

#### Semántica:
- **Protocolo:** In-memory object passing
- **Serialización:** Python dataclasses
- **Validación:** Type hints + runtime validation

**Glue:** Python dataclasses

#### PNF del Conector:
- **Latencia:** Muy baja (in-memory)
- **Seguridad:** Media - Separación de representaciones
- **Mantenibilidad:** Alta - Contratos explícitos

---

## 3. CONFIGURACIÓN (System Topology/Style)

### 3.1 Estilo Arquitectónico Principal

**Arquitectura Hexagonal (Ports & Adapters)**

La configuración del sistema sigue el patrón de Arquitectura Hexagonal, también conocido como Ports & Adapters, propuesto por Alistair Cockburn.

#### Características del Estilo:
1. **Núcleo de Dominio Central:** Modelos de dominio independientes (Route, Client)
2. **Puertos (Interfaces):** Abstracciones que definen contratos (RouteRepositoryPort, RouteOptimizationPort)
3. **Adaptadores Conductores (Driving):** Inician interacciones (StreamlitUI)
4. **Adaptadores Conducidos (Driven):** Proveen servicios (PostgresRouteRepository, GoogleMapsOptimizationService)
5. **Inversión de Dependencias:** Core depende de abstracciones, no de implementaciones

---

### 3.2 Topología del Sistema (Grafo de Interconexión)

```
┌─────────────────────────────────────────────────────────────────┐
│                      DRIVING ADAPTERS                           │
│                                                                 │
│   ┌──────────────┐                 ┌──────────────┐           │
│   │ StreamlitUI  │                 │  CLI (future)│           │
│   └──────┬───────┘                 └──────┬───────┘           │
│          │                                 │                    │
└──────────┼─────────────────────────────────┼───────────────────┘
           │                                 │
           │ HTTP/Method Calls               │
           ▼                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│                                                                 │
│   ┌────────────────────┐      ┌───────────────────────────┐   │
│   │  RouteService      │◄─────┤RouteOptimizationService   │   │
│   └────────┬───────────┘      └───────────┬───────────────┘   │
│            │                               │                    │
└────────────┼───────────────────────────────┼───────────────────┘
             │                               │
             │ requires                      │ requires
             ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER (CORE)                         │
│                                                                 │
│   ┌──────────────────┐        ┌──────────────────┐            │
│   │«Port»            │        │«Port»            │            │
│   │RouteRepository   │        │RouteOptimization │            │
│   │Port              │        │Port              │            │
│   └────────┬─────────┘        └─────────┬────────┘            │
│            │                             │                     │
│   ┌────────┴─────────┐       ┌──────────┴────────┐            │
│   │  Route (Entity)  │       │  Client (Entity)  │            │
│   └──────────────────┘       └───────────────────┘            │
│                                                                 │
└────────────┬────────────────────────────────┬───────────────────┘
             │ implements                     │ implements
             ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DRIVEN ADAPTERS                               │
│                                                                 │
│   ┌──────────────────────┐      ┌─────────────────────────┐   │
│   │Postgres              │      │GoogleMaps               │   │
│   │RouteRepository       │      │OptimizationService      │   │
│   └─────────┬────────────┘      └────────┬────────────────┘   │
│             │                             │                     │
└─────────────┼─────────────────────────────┼─────────────────────┘
              │                             │
              │ psycopg2                    │ HTTPS/REST
              ▼                             ▼
    ┌──────────────────┐         ┌─────────────────────┐
    │ PostgreSQL DB    │         │ Google Maps API     │
    │ (External)       │         │ (External SaaS)     │
    └──────────────────┘         └─────────────────────┘
```

---

### 3.3 Capas de la Arquitectura

1. **Capa de Presentación (UI):** StreamlitUI
2. **Capa de Aplicación:** RouteService, RouteOptimizationService
3. **Capa de Dominio:** Route, Client, Ports
4. **Capa de Infraestructura:** PostgresRouteRepository, GoogleMapsOptimizationService
5. **Capa de Persistencia:** PostgreSQL Database

---

### 3.4 Flujo de Datos Principal

```
Usuario → StreamlitUI → RouteService → RouteRepositoryPort 
                                      → PostgresRouteRepository 
                                      → PostgreSQL DB
```

**Flujo de Optimización:**
```
Usuario → StreamlitUI → RouteOptimizationService → RouteOptimizationPort
                                                  → GoogleMapsOptimizationService
                                                  → Google Maps API
```

---

## 4. RESTRICCIONES (Constraints)

### 4.1 Restricciones Arquitectónicas

#### R1: Inversión de Dependencias (Arquitectural)
**Descripción:** Las capas internas (Dominio, Aplicación) NO deben depender de capas externas (Infraestructura).  
**Invariante:** `Domain → Application → Infrastructure` (flujo de dependencias invertido mediante puertos)  
**Justificación:** Mantener el core del negocio independiente de tecnologías específicas.  
**Verificación:** Análisis estático de imports - ningún módulo de `domain/` o `application/` debe importar de `infrastructure/`.

---

#### R2: Transaccionalidad en Operaciones Compuestas (Behavioral)
**Descripción:** Las operaciones de división y fusión de rutas DEBEN ejecutarse dentro de una transacción ACID.  
**Invariante:** `BEGIN_TRANSACTION → (divide/merge operations) → COMMIT | ROLLBACK`  
**Justificación:** Garantizar consistencia de datos ante fallos parciales.  
**Verificación:** Todas las operaciones en `RouteService.divideRouteUseCase()` y `mergeRoutesUseCase()` están envueltas en bloques try-catch con rollback.

---

#### R3: Validación de Dominio Obligatoria (Business Rule)
**Descripción:** Todas las entidades de dominio deben validar sus invariantes en el constructor (`__post_init__`).  
**Invariante:** Ninguna entidad de dominio puede existir en estado inválido.  
**Justificación:** Prevenir corrupción de datos en el modelo de negocio.  
**Verificación:** Todas las clases `@dataclass` en `domain/models/` implementan validaciones en `__post_init__`.

---

### 4.2 Restricciones Tecnológicas

#### R4: PostgreSQL como Único Sistema de Persistencia
**Descripción:** El sistema está acoplado a PostgreSQL para persistencia relacional.  
**Impacto:** Cambiar a otro RDBMS requiere modificar `PostgresRouteRepository`.  
**Mitigación:** La abstracción `RouteRepositoryPort` permite crear adaptadores alternativos (ej. `MySQLRouteRepository`).

---

#### R5: Google Maps API Requerida para Optimización
**Descripción:** La funcionalidad de optimización depende de Google Maps Platform.  
**Impacto:** Sin API Key, las características de optimización están deshabilitadas.  
**Mitigación:** Sistema diseñado para operar sin optimización (funcionalidad opcional).

---

### 4.3 Restricciones de Rendimiento

#### R6: Latencia Máxima de UI < 3 segundos
**Descripción:** Las operaciones de UI no deben exceder 3 segundos de latencia percibida.  
**Impacto:** Operaciones de optimización con muchos waypoints pueden violar esta restricción.  
**Mitigación:** Implementar feedback visual (spinners) y limitar número de clientes por ruta.

---

#### R7: Pool de Conexiones Limitado (1-10 conexiones)
**Descripción:** PostgreSQL está configurado con un pool mínimo de 1 y máximo de 10 conexiones.  
**Impacto:** Concurrencia limitada a 10 usuarios simultáneos.  
**Mitigación:** Ajustar `DB_MAX_CONNECTIONS` según carga esperada.

---

### 4.4 Restricciones de Seguridad

#### R8: Credenciales mediante Variables de Entorno
**Descripción:** Todas las credenciales sensibles (DB_PASSWORD, GOOGLE_MAPS_API_KEY) deben almacenarse en variables de entorno.  
**Invariante:** Ningún secreto hardcodeado en código fuente.  
**Verificación:** Uso de `python-dotenv` y `os.getenv()`.

---

#### R9: Sin Autenticación de Usuario Implementada
**Descripción:** La UI de Streamlit no implementa autenticación ni autorización.  
**Impacto:** Cualquier usuario con acceso a la URL puede gestionar rutas.  
**Riesgo:** ALTO en ambientes de producción.  
**Recomendación:** Implementar autenticación antes de deployment productivo.

---

### 4.5 Restricciones de Diseño

#### R10: DTOs Inmutables entre Capas
**Descripción:** Los DTOs utilizados para transferencia entre capas deben ser inmutables (dataclasses frozen o equivalentes).  
**Justificación:** Prevenir mutaciones accidentales que afecten múltiples capas.  
**Estado Actual:** Parcialmente cumplido - DTOs en `application/dtos.py` son mutables.

---

#### R11: Nombres de Días en Español
**Descripción:** Los días de la semana se almacenan en español ('LUNES', 'MARTES', ...).  
**Impacto:** Incompatibilidad con sistemas internacionales.  
**Justificación:** Requisito de negocio (cliente colombiano).

---

## 5. PROPIEDADES NO FUNCIONALES ADICIONALES Y RAZONAMIENTO

### 5.1 Escalabilidad (Scalability)

#### Nivel Actual: **MEDIO**

**Análisis:**
- **Escala Vertical:** Limitada por arquitectura single-threaded de Streamlit
- **Escala Horizontal:** No implementada (sin load balancer, sesiones compartidas)
- **Bottlenecks Identificados:**
  - Conexión única de Streamlit (no multi-proceso)
  - Pool de conexiones PostgreSQL limitado (máx. 10)
  - Rate limits de Google Maps API

**Razonamiento de Decisiones:**
- La arquitectura hexagonal permite reemplazar `StreamlitUI` por un framework escalable (FastAPI + React) sin cambiar el core.
- El uso de puertos permite implementar caché distribuida (Redis) como adaptador adicional.

**Mejoras Sugeridas:**
1. Migrar a arquitectura cliente-servidor separada (API REST)
2. Implementar caché de resultados de optimización
3. Pool de conexiones dinámico con autoescalado

---

### 5.2 Mantenibilidad (Maintainability)

#### Nivel Actual: **ALTO**

**Análisis:**
- **Separación de Concerns:** Excelente - Arquitectura hexagonal bien implementada
- **Acoplamiento:** Bajo - Uso consistente de abstracciones
- **Cohesión:** Alta - Cada componente tiene responsabilidad única
- **Documentación:** Alta - Docstrings completos, diagramas arquitectónicos

**Razonamiento de Decisiones:**
- El patrón Ports & Adapters facilita cambios tecnológicos sin afectar lógica de negocio.
- La capa de aplicación orquesta operaciones complejas manteniendo el dominio limpio.

**Evidencias:**
- Cambio de SQLite a PostgreSQL requirió solo modificar un adaptador
- Adición de Google Maps no afectó código existente (Open/Closed Principle)

---

### 5.3 Testabilidad (Testability)

#### Nivel Actual: **ALTO**

**Análisis:**
- **Inyección de Dependencias:** Implementada - Facilita mocking
- **Puertos Abstractos:** Permite crear test doubles fácilmente
- **Lógica de Dominio Pura:** Sin dependencias externas, 100% testable

**Razonamiento de Decisiones:**
- El uso de abstracciones permite tests unitarios sin infraestructura real.
- Las entidades de dominio pueden testearse de forma aislada.

**Cobertura Actual:**
- Tests de dominio implementados (`tests/domain/test_route_model.py`)
- Tests de integración pendientes

**Mejoras Sugeridas:**
1. Implementar tests de integración para adaptadores
2. Agregar tests de contrato para puertos
3. Configurar CI/CD con cobertura mínima del 80%

---

### 5.4 Seguridad (Security)

#### Nivel Actual: **MEDIO-BAJO**

**Análisis:**
- **Autenticación:** ❌ No implementada
- **Autorización:** ❌ No implementada
- **Encriptación en Tránsito:** ✅ HTTPS para Google Maps, ⚠️ HTTP para Streamlit (configurable)
- **Encriptación en Reposo:** ⚠️ Dependiente de configuración de PostgreSQL
- **Gestión de Secretos:** ✅ Variables de entorno con dotenv

**Vulnerabilidades Identificadas:**
1. **Alta:** Ausencia de autenticación en UI
2. **Media:** Credenciales de DB en variables de entorno (riesgo de exposición)
3. **Baja:** Sin validación de entrada en algunos endpoints de UI

**Razonamiento de Decisiones:**
- La arquitectura hexagonal permite añadir un adaptador de seguridad sin cambiar el core.
- El uso de DTOs previene algunos ataques de inyección.

**Mejoras Recomendadas:**
1. **Crítico:** Implementar autenticación (OAuth2, SAML, o básica)
2. **Alto:** Migrar a vault de secretos (HashiCorp Vault, AWS Secrets Manager)
3. **Medio:** Implementar validación de entrada exhaustiva (Pydantic)
4. **Medio:** Auditoría de operaciones (logging de acciones críticas)

---

### 5.5 Disponibilidad (Availability)

#### Nivel Actual: **MEDIO**

**Análisis:**
- **Uptime Esperado:** ~95% (sin redundancia)
- **SPoF (Single Points of Failure):**
  - Instancia única de Streamlit
  - Servidor único de PostgreSQL
  - Dependencia de Google Maps API (mitigable)

**Razonamiento de Decisiones:**
- La arquitectura permite desplegar múltiples instancias de aplicación con load balancer.
- El repositorio abstracto facilita implementar replicación de DB.

**Estrategias de Mejora:**
1. Configurar PostgreSQL en modo de alta disponibilidad (Primary/Replica)
2. Implementar health checks en aplicación
3. Deployment en contenedores con Kubernetes (auto-healing)
4. Circuit breaker para Google Maps API (graceful degradation)

---

### 5.6 Observabilidad (Observability)

#### Nivel Actual: **BAJO**

**Análisis:**
- **Logging:** Básico - Print statements en consola
- **Métricas:** ❌ No implementadas
- **Tracing:** ❌ No implementado
- **Monitoreo:** ❌ No implementado

**Razonamiento de Decisiones:**
- La arquitectura hexagonal facilita añadir un adaptador de logging/métricas.
- El patrón Repository permite instrumentar operaciones de persistencia.

**Mejoras Sugeridas:**
1. Implementar logging estructurado (JSON) con niveles (DEBUG, INFO, WARN, ERROR)
2. Añadir métricas de negocio (rutas creadas/día, tiempo promedio de optimización)
3. Integrar APM (Application Performance Monitoring) - New Relic, Datadog, o Prometheus
4. Implementar distributed tracing para debugging (Jaeger, Zipkin)

---

### 5.7 Portabilidad (Portability)

#### Nivel Actual: **MEDIO-ALTO**

**Análisis:**
- **Independencia de Plataforma:** Alta - Python multi-plataforma
- **Independencia de DB:** Media - Acoplado a PostgreSQL, pero puerto abstracto
- **Independencia de Cloud:** Alta - Sin servicios cloud específicos
- **Containerización:** ✅ Factible (Dockerfile pendiente)

**Razonamiento de Decisiones:**
- El uso de abstracciones permite migrar entre tecnologías.
- Python + PostgreSQL son ampliamente soportados.

**Evidencias:**
- Migración de SQLite a PostgreSQL exitosa (solo cambio de adaptador)
- Google Maps reemplazable por OpenRouteService u otros

---

### 5.8 Rendimiento (Performance)

#### Nivel Actual: **MEDIO**

**Análisis:**
- **Latencia Promedio:** 100-500ms para operaciones CRUD, 1-3s para optimización
- **Throughput:** Bajo (~10 usuarios concurrentes máximo)
- **Uso de Recursos:** Medio (Python no es el lenguaje más eficiente)

**Cuellos de Botella:**
1. **Google Maps API:** Latencia variable (100ms - 2s)
2. **Streamlit Single-Thread:** Limitación de concurrencia
3. **Consultas SQL:** Sin optimización de índices avanzada

**Optimizaciones Implementadas:**
- Pool de conexiones de DB
- Lazy loading de datos en UI
- Fallback a orden original si API falla

**Mejoras Sugeridas:**
1. Caché de resultados de geocodificación (Redis)
2. Índices compuestos en PostgreSQL (cedis_id + dia_semana)
3. Paginación de resultados en UI
4. Batch processing para operaciones masivas

---

### 5.9 Usabilidad (Usability)

#### Nivel Actual: **ALTO**

**Análisis:**
- **Curva de Aprendizaje:** Baja - UI intuitiva
- **Accesibilidad:** Media - WCAG AA parcial
- **Feedback:** Alto - Mensajes claros de error/éxito
- **Diseño:** Profesional - Paleta corporativa consistente

**Razonamiento de Decisiones:**
- Uso de Design System personalizado mejora consistencia.
- Componentes reutilizables (`ui_components.py`) facilitan UX homogénea.

**Evidencias:**
- Navegación lateral clara con iconos
- Estados visuales diferenciados (activo/inactivo)
- Métricas y KPIs en dashboard

---

### 5.10 Evolucionabilidad (Evolvability)

#### Nivel Actual: **MUY ALTO**

**Análisis:**
- **Facilidad de Extensión:** Alta - Arquitectura abierta (Open/Closed)
- **Impacto de Cambios:** Bajo - Cambios localizados por capas
- **Migración Tecnológica:** Factible - Adaptadores reemplazables

**Razonamiento de Decisiones Arquitectónicas:**

1. **Arquitectura Hexagonal:** Permite evolución independiente de capas
   - Cambio de UI: Solo reemplazar `StreamlitUI`
   - Cambio de DB: Solo crear nuevo adaptador de `RouteRepositoryPort`
   - Cambio de optimizador: Solo crear nuevo adaptador de `RouteOptimizationPort`

2. **Puertos Abstractos:** Facilitan adición de funcionalidades
   - Ejemplo: Añadir caché requiere solo un nuevo adaptador que implemente `RouteRepositoryPort` con decorador

3. **Inyección de Dependencias:** Permite configuración flexible
   - Diferentes configuraciones para dev/test/prod sin cambiar código

**Escenarios de Evolución Anticipados:**
- ✅ **Fácil:** Añadir nuevo proveedor de optimización (OpenRouteService)
- ✅ **Fácil:** Migrar a FastAPI + React manteniendo servicios de aplicación
- ⚠️ **Medio:** Implementar arquitectura multi-tenant (requiere cambios en dominio)
- ⚠️ **Medio:** Migración a microservicios (requiere separar servicios)

---

## 6. DECISIONES ARQUITECTÓNICAS SIGNIFICATIVAS

### DA-01: Adopción de Arquitectura Hexagonal

**Contexto:** Necesidad de un sistema mantenible y extensible para gestión de rutas.

**Decisión:** Implementar patrón Ports & Adapters (Arquitectura Hexagonal).

**Justificación:**
- Independencia de tecnologías de persistencia y UI
- Facilita testing del core de negocio
- Permite migración tecnológica sin afectar lógica de negocio

**Consecuencias:**
- ✅ Código altamente testable
- ✅ Facilidad de cambiar PostgreSQL por otro DB
- ✅ Migración exitosa de SQLite a PostgreSQL
- ⚠️ Mayor complejidad inicial (curva de aprendizaje)
- ⚠️ Más archivos y estructura de carpetas

**Alternativas Consideradas:**
- Arquitectura en Capas Tradicional (descartada por alto acoplamiento)
- CQRS (descartada por over-engineering para caso de uso)

---

### DA-02: PostgreSQL como Sistema de Persistencia

**Contexto:** Necesidad de almacenamiento relacional con transacciones ACID.

**Decisión:** Usar PostgreSQL en lugar de SQLite.

**Justificación:**
- Soporte robusto de transacciones concurrentes
- Escalabilidad superior a SQLite
- Ecosistema maduro y herramientas de administración

**Consecuencias:**
- ✅ Transaccionalidad ACID completa
- ✅ Mejor rendimiento con datos grandes
- ⚠️ Requiere instalación y configuración de servidor
- ⚠️ Mayor complejidad operacional

**Alternativas Consideradas:**
- SQLite (usado inicialmente, migrado por limitaciones de concurrencia)
- MongoDB (descartado por naturaleza relacional de datos de rutas)

---

### DA-03: Google Maps como Proveedor de Optimización

**Contexto:** Necesidad de geocodificación y optimización de rutas.

**Decisión:** Integrar Google Maps Platform APIs.

**Justificación:**
- API madura y confiable (SLA 99.9%)
- Algoritmos de optimización de alta calidad
- Documentación y soporte excelentes

**Consecuencias:**
- ✅ Optimización de rutas de alta calidad
- ✅ Geocodificación precisa
- ⚠️ Costo por uso (requiere presupuesto)
- ⚠️ Dependencia de servicio externo (vendor lock-in parcial)
- ✅ Mitigado con abstracción `RouteOptimizationPort`

**Alternativas Consideradas:**
- OpenRouteService (open-source, considerado como fallback)
- HERE Maps (descartado por menor ecosistema)
- Algoritmos propios (descartado por complejidad)

---

### DA-04: Streamlit como Framework de UI

**Contexto:** Necesidad de interfaz web rápida de desarrollar.

**Decisión:** Usar Streamlit para la UI.

**Justificación:**
- Desarrollo rápido de prototipos
- Python puro (sin HTML/CSS/JS)
- Interactividad sin backend adicional

**Consecuencias:**
- ✅ Time-to-market reducido
- ✅ UI profesional con poco código
- ⚠️ Limitaciones de escalabilidad (single-threaded)
- ⚠️ Customización de UI limitada
- ⚠️ No apto para aplicaciones de alta concurrencia

**Alternativas Consideradas:**
- FastAPI + React (descartado por mayor tiempo de desarrollo)
- Django (descartado por over-engineering)

**Migración Futura:** La arquitectura hexagonal permite reemplazar Streamlit sin cambiar la lógica de negocio.

---

### DA-05: DTOs para Transferencia entre Capas

**Contexto:** Necesidad de desacoplar representaciones de datos entre capas.

**Decisión:** Usar Data Transfer Objects (DTOs) para comunicación UI ↔ Application.

**Justificación:**
- Separar representación de dominio de representación de UI
- Prevenir exposición de entidades de dominio en capa de presentación
- Facilitar versionado de APIs

**Consecuencias:**
- ✅ Desacoplamiento UI/Dominio
- ✅ Contratos explícitos
- ⚠️ Código adicional de mapeo (boilerplate)

**Alternativas Consideradas:**
- Exponer entidades de dominio directamente (descartado por acoplamiento)

---

## 7. MÉTRICAS Y EVALUACIÓN DE CALIDAD

### 7.1 Métricas de Código

| Métrica                        | Valor Estimado | Objetivo | Estado |
|--------------------------------|----------------|----------|--------|
| Líneas de Código (LOC)         | ~3,000         | N/A      | ✅     |
| Complejidad Ciclomática Prom.  | ~5-7           | < 10     | ✅     |
| Acoplamiento (Coupling)        | Bajo           | Bajo     | ✅     |
| Cohesión (Cohesion)            | Alta           | Alta     | ✅     |
| Cobertura de Tests             | ~30%           | > 80%    | ⚠️     |
| Deuda Técnica (horas)          | ~40h           | < 100h   | ✅     |

---

### 7.2 Conformidad con Principios SOLID

| Principio                      | Conformidad | Evidencia                                          |
|--------------------------------|-------------|----------------------------------------------------|
| **S**ingle Responsibility      | ✅ Alta     | Cada servicio/repositorio tiene una responsabilidad|
| **O**pen/Closed                | ✅ Alta     | Extensión mediante nuevos adaptadores              |
| **L**iskov Substitution        | ✅ Alta     | Adaptadores intercambiables sin cambiar clientes   |
| **I**nterface Segregation      | ✅ Media    | Puertos específicos, aunque `RouteService` es amplio|
| **D**ependency Inversion       | ✅ Muy Alta | Dependencias a abstracciones, no implementaciones  |

---

### 7.3 Conformidad con Patrones de Diseño

| Patrón                         | Uso         | Componente                                |
|--------------------------------|-------------|-------------------------------------------|
| Hexagonal Architecture         | ✅ Completo | Estructura global                         |
| Repository Pattern             | ✅ Completo | `RouteRepositoryPort`, `PostgresRouteRepository` |
| Adapter Pattern                | ✅ Completo | `GoogleMapsOptimizationService`, adaptadores |
| Service Layer Pattern          | ✅ Completo | `RouteService`, `RouteOptimizationService` |
| DTO Pattern                    | ✅ Completo | `application/dtos.py`                     |
| Dependency Injection           | ✅ Completo | `main.py` como ensamblador                |
| Singleton (implícito)          | ✅ Parcial  | `Config` class                            |

---

## 8. CONCLUSIONES Y RECOMENDACIONES

### 8.1 Fortalezas de la Arquitectura

1. **Excelente Separación de Concerns:** La arquitectura hexagonal está correctamente implementada, con fronteras claras entre capas.

2. **Alta Testabilidad:** El uso de puertos abstractos facilita enormemente el testing unitario e integración.

3. **Evolucionabilidad Destacable:** El sistema puede evolucionar tecnológicamente sin afectar el core de negocio (evidenciado por la migración SQLite → PostgreSQL).

4. **Código Limpio y Mantenible:** Documentación excelente, nombres descriptivos, y alta cohesión.

5. **Cumplimiento de Principios SOLID:** Especialmente fuerte en Dependency Inversion y Open/Closed.

---

### 8.2 Áreas de Mejora Prioritarias

#### Alta Prioridad:
1. **Seguridad:** Implementar autenticación y autorización (actualmente ausente)
2. **Observabilidad:** Añadir logging estructurado y métricas
3. **Testing:** Incrementar cobertura de tests (actual: 30%, objetivo: 80%)

#### Media Prioridad:
4. **Escalabilidad:** Migrar de Streamlit a arquitectura cliente-servidor separada
5. **Disponibilidad:** Configurar alta disponibilidad de PostgreSQL
6. **Rendimiento:** Implementar caché de resultados de optimización

#### Baja Prioridad:
7. **Internacionalización:** Soportar días de semana en múltiples idiomas
8. **Containerización:** Crear Dockerfile y configuración Kubernetes

---

### 8.3 Adecuación para Producción

**Estado Actual:** ⚠️ **NO APTO PARA PRODUCCIÓN** sin mejoras de seguridad.

**Bloqueadores Críticos:**
- ❌ Ausencia de autenticación
- ❌ Observabilidad insuficiente
- ⚠️ Sin estrategia de alta disponibilidad

**Ruta a Producción Recomendada:**

**Fase 1: Seguridad (2-3 semanas)**
- Implementar autenticación básica (HTTP Basic o OAuth2)
- Migrar secretos a vault seguro
- Habilitar HTTPS en Streamlit

**Fase 2: Observabilidad (1-2 semanas)**
- Logging estructurado (JSON)
- Métricas de aplicación (Prometheus)
- Health checks

**Fase 3: Escalabilidad (4-6 semanas)**
- Migrar a FastAPI + React (opcional)
- Configurar PostgreSQL en alta disponibilidad
- Containerización con Docker/Kubernetes

---

### 8.4 Conformidad ADL

Este análisis ha cubierto los 5 elementos esenciales de la ontología ADL:

✅ **1. COMPONENTES:** 9 componentes identificados con interfaces y PNF detalladas  
✅ **2. CONECTORES:** 6 conectores con roles y semántica especificados  
✅ **3. CONFIGURACIÓN:** Topología y estilo arquitectónico documentados  
✅ **4. RESTRICCIONES:** 11 restricciones críticas enumeradas  
✅ **5. PNF Y RAZONAMIENTO:** 10 propiedades no funcionales analizadas con justificaciones

---

## Anexo A: Glosario de Términos ADL

- **Componente:** Unidad computacional o de almacenamiento con interfaces bien definidas
- **Conector:** Mecanismo de interacción/comunicación entre componentes
- **Puerto (Port):** Interfaz abstracta que define un contrato
- **Adaptador (Adapter):** Implementación concreta de un puerto
- **Estilo Arquitectónico:** Patrón de organización de componentes y conectores
- **PNF (Propiedad No Funcional):** Atributo de calidad del sistema (escalabilidad, seguridad, etc.)
- **Restricción:** Condición o invariante que debe mantenerse en el diseño

---

## Anexo B: Referencias Bibliográficas

1. **Hexagonal Architecture (Ports & Adapters)**  
   Alistair Cockburn, 2005  
   https://alistair.cockburn.us/hexagonal-architecture/

2. **Clean Architecture**  
   Robert C. Martin, 2017  
   ISBN: 978-0134494166

3. **Domain-Driven Design**  
   Eric Evans, 2003  
   ISBN: 978-0321125217

4. **Software Architecture in Practice (4th Ed.)**  
   Len Bass, Paul Clements, Rick Kazman, 2021  
   ISBN: 978-0136886099

---

**Fin del Análisis ADL**  
**Documento generado:** 6 de noviembre de 2025  
**Versión:** 1.0
