# Guía Rápida de Referencia ADL - Yedistribuciones

**Documento de Consulta Rápida**  
**Fecha:** 6 de noviembre de 2025

---

## 📋 Índice de Documentación ADL

Este proyecto contiene los siguientes documentos de análisis ADL:

1. **`Analisis_ADL.md`** - Análisis completo y detallado (documento principal)
2. **`Diagramas_ADL.md`** - Diagramas visuales y tablas de referencia
3. **`Referencia_Rapida_ADL.md`** - Esta guía de consulta rápida

---

## 🎯 Componentes Principales (Quick Reference)

### Core del Sistema

| Componente | Capa | Responsabilidad | Criticidad |
|------------|------|----------------|------------|
| **Route** | Dominio | Lógica de negocio de rutas | 🔴 ALTA |
| **RouteService** | Aplicación | Casos de uso de gestión | 🔴 ALTA |
| **PostgresRouteRepository** | Infraestructura | Persistencia en PostgreSQL | 🔴 ALTA |
| **StreamlitUI** | Infraestructura | Interfaz de usuario web | 🔴 ALTA |

### Componentes Opcionales

| Componente | Capa | Responsabilidad | Criticidad |
|------------|------|----------------|------------|
| **RouteOptimizationService** | Aplicación | Optimización de rutas | 🟡 MEDIA |
| **GoogleMapsOptimizationService** | Infraestructura | Integración con Google Maps | 🟡 MEDIA |

---

## 🔌 Puertos (Interfaces Abstractas)

### RouteRepositoryPort
```python
# Puerto de salida (Output Port) para persistencia
+ save(route: Route) -> None
+ update(route: Route) -> None
+ findById(route_id: str) -> Optional[Route]
+ getAll() -> List[Route]
+ delete(route_id: str) -> None
+ beginTransaction() -> None
+ commitTransaction() -> None
+ rollbackTransaction() -> None
```

**Implementado por:** `PostgresRouteRepository`

---

### RouteOptimizationPort
```python
# Puerto de salida (Output Port) para optimización
+ geocodeAddress(address: str) -> Optional[Tuple[float, float]]
+ optimizeRoute(origin, waypoints, destination) -> RouteOptimizationResult
+ calculateDistanceMatrix(origins, destinations) -> List[List[float]]
```

**Implementado por:** `GoogleMapsOptimizationService`

---

## 🔗 Conectores Clave

| Conector | Tipo | Latencia | Fiabilidad |
|----------|------|----------|------------|
| **PostgreSQL-JDBC** | DB Connection | < 10ms | 🟢 Alta |
| **Google Maps REST** | HTTP/REST | 100ms - 2s | 🟢 Alta (SLA 99.9%) |
| **Streamlit HTTP** | HTTP/WebSocket | < 50ms | 🟡 Media |
| **Port-Adapter Boundary** | Abstract Interface | In-memory | 🟢 Muy Alta |

---

## 🏗️ Estilo Arquitectónico

**Arquitectura Hexagonal (Ports & Adapters)**

```
┌─────────────────────────────────────┐
│      DRIVING ADAPTERS               │
│      (UI, CLI, API)                 │
└───────────┬─────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│      APPLICATION LAYER              │
│      (Use Cases)                    │
└───────────┬─────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│      DOMAIN LAYER (CORE)            │
│      (Business Logic)               │
│      + Ports (Interfaces)           │
└───────────┬─────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│      DRIVEN ADAPTERS                │
│      (DB, External APIs)            │
└─────────────────────────────────────┘
```

**Principio Clave:** Las dependencias apuntan hacia adentro (hacia el dominio).

---

## ⚠️ Restricciones Críticas (Top 5)

### R1: Inversión de Dependencias
- ✅ **Estado:** Cumplida
- **Descripción:** Core no depende de infraestructura
- **Verificación:** Análisis de imports - dominio/aplicación no importan de infrastructure/

### R2: Transaccionalidad
- ✅ **Estado:** Cumplida
- **Descripción:** Operaciones compuestas en transacciones ACID
- **Aplica a:** `divideRouteUseCase()`, `mergeRoutesUseCase()`

### R3: Validación de Dominio
- ✅ **Estado:** Cumplida
- **Descripción:** Todas las entidades validan en `__post_init__`
- **Aplica a:** `Route`, `Client`

### R8: Credenciales en Variables de Entorno
- ✅ **Estado:** Cumplida
- **Descripción:** Sin secretos hardcodeados
- **Implementación:** `python-dotenv` + `Config` class

### R9: Sin Autenticación
- ❌ **Estado:** NO cumplida (vulnerabilidad)
- **Descripción:** UI sin autenticación/autorización
- **Riesgo:** ALTO en producción
- **Recomendación:** **Implementar antes de deployment**

---

## 📊 Propiedades No Funcionales (Resumen)

| PNF | Nivel | Comentario |
|-----|-------|------------|
| **Escalabilidad** | 🟡 MEDIO | Limitada por Streamlit single-thread |
| **Disponibilidad** | 🟡 MEDIO | Sin redundancia (SPoF: Streamlit, PostgreSQL) |
| **Seguridad** | 🔴 BAJO | ❌ Sin autenticación |
| **Mantenibilidad** | 🟢 ALTO | Excelente separación de concerns |
| **Testabilidad** | 🟢 ALTO | Puertos facilitan mocking |
| **Evolucionabilidad** | 🟢 MUY ALTO | Arquitectura hexagonal permite cambios |
| **Usabilidad** | 🟢 ALTO | UI intuitiva y profesional |
| **Observabilidad** | 🔴 BAJO | Sin logging estructurado ni métricas |
| **Rendimiento** | 🟡 MEDIO | Latencia aceptable, throughput limitado |

---

## 🛠️ Decisiones Arquitectónicas (ADRs)

### DA-01: Arquitectura Hexagonal
- **Por qué:** Desacoplamiento, testabilidad, evolución
- **Trade-off:** Mayor complejidad inicial
- **Resultado:** ✅ Migración SQLite→PostgreSQL exitosa

### DA-02: PostgreSQL
- **Por qué:** ACID, concurrencia, escalabilidad
- **Trade-off:** Requiere servidor dedicado
- **Resultado:** ✅ Transaccionalidad robusta

### DA-03: Google Maps API
- **Por qué:** Optimización de alta calidad
- **Trade-off:** Costo por uso, vendor lock-in
- **Mitigación:** ✅ Abstracción con `RouteOptimizationPort`

### DA-04: Streamlit
- **Por qué:** Time-to-market rápido
- **Trade-off:** Limitaciones de escalabilidad
- **Mitigación futura:** Migración a FastAPI+React (hexagonal lo facilita)

### DA-05: DTOs
- **Por qué:** Desacoplamiento UI/Dominio
- **Trade-off:** Código de mapeo adicional
- **Resultado:** ✅ Contratos explícitos

---

## 🚨 Bloqueadores para Producción

### Críticos (DEBE resolverse)
1. ❌ **Autenticación:** Implementar sistema de autenticación/autorización
2. ⚠️ **Secretos:** Migrar a vault seguro (HashiCorp Vault, AWS Secrets Manager)
3. ⚠️ **Logging:** Implementar logging estructurado (JSON) con niveles

### Altos (DEBERÍA resolverse)
4. ⚠️ **Alta Disponibilidad:** Configurar PostgreSQL Primary/Replica
5. ⚠️ **Monitoreo:** Añadir health checks y métricas (Prometheus)
6. ⚠️ **HTTPS:** Habilitar HTTPS en Streamlit

### Medios (PUEDE resolverse)
7. ⚠️ **Escalabilidad:** Migrar de Streamlit a arquitectura cliente-servidor
8. ⚠️ **Caché:** Implementar caché de geocodificación (Redis)
9. ⚠️ **Tests:** Incrementar cobertura de 30% a 80%

---

## 📈 Métricas de Calidad

### Conformidad SOLID
- **S**ingle Responsibility: ✅ 95%
- **O**pen/Closed: ✅ 90%
- **L**iskov Substitution: ✅ 95%
- **I**nterface Segregation: 🟡 75%
- **D**ependency Inversion: ✅ 98%

### Métricas de Código
- **Líneas de Código:** ~3,000
- **Complejidad Ciclomática:** 5-7 (objetivo: < 10) ✅
- **Cobertura de Tests:** 30% (objetivo: > 80%) ⚠️
- **Acoplamiento:** Bajo ✅
- **Cohesión:** Alta ✅

---

## 🎓 Patrones de Diseño Aplicados

| Patrón | Componente | Estado |
|--------|------------|--------|
| **Hexagonal Architecture** | Estructura global | ✅ Completo |
| **Repository Pattern** | `RouteRepositoryPort` | ✅ Completo |
| **Adapter Pattern** | `GoogleMapsService`, `PostgresRepo` | ✅ Completo |
| **Service Layer** | `RouteService`, `RouteOptService` | ✅ Completo |
| **DTO Pattern** | `application/dtos.py` | ✅ Completo |
| **Dependency Injection** | `main.py` | ✅ Completo |
| **Singleton** (implícito) | `Config` | ✅ Parcial |

---

## 🔄 Flujos de Operaciones Clave

### Crear Ruta
```
Usuario → StreamlitUI → RouteService → Route (validación) 
       → RouteRepositoryPort → PostgresRepository → PostgreSQL
```
**Tiempo:** ~100ms  
**Transaccional:** ✅ Sí

---

### Optimizar Ruta
```
Usuario → StreamlitUI → RouteOptimizationService 
       → RouteOptimizationPort → GoogleMapsService → Google Maps API
```
**Tiempo:** 1-3s (depende de Google)  
**Transaccional:** ➖ No aplica  
**Opcional:** ✅ Sistema funciona sin optimización

---

### Dividir Ruta
```
Usuario → StreamlitUI → RouteService.divideRouteUseCase()
       → BEGIN TRANSACTION
       → Route.divideRoute() (lógica de dominio)
       → PostgresRepository: deactivate(original), save(routeA), save(routeB)
       → COMMIT TRANSACTION
```
**Tiempo:** ~200ms  
**Transaccional:** ✅ ACID completo  
**Rollback:** ✅ Automático en caso de error

---

## 🧪 Estrategia de Testing

### Tests Unitarios (Recomendado)
- **Dominio:** `Route`, `Client` (sin dependencias)
- **Servicios:** `RouteService`, `RouteOptService` (mock de puertos)
- **Cobertura objetivo:** > 80%

### Tests de Integración (Recomendado)
- **Repositorio:** `PostgresRouteRepository` (con DB de test)
- **Adaptadores:** `GoogleMapsService` (con API key de test)

### Tests de Contrato (Opcional)
- Verificar que adaptadores cumplen contratos de puertos

---

## 🌐 Variables de Entorno Requeridas

```bash
# Base de Datos PostgreSQL (REQUERIDO)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=RutasDB
DB_USER=postgres
DB_PASSWORD=tu_password

# Google Maps API (OPCIONAL - para optimización)
GOOGLE_MAPS_API_KEY=tu_api_key_aqui

# Configuración CEDIS (OPCIONAL - valores por defecto disponibles)
CEDIS_LATITUDE=4.7110
CEDIS_LONGITUDE=-74.0721
CEDIS_ADDRESS="Bogotá, Colombia"

# Límites de Ruta (OPCIONAL)
MAX_ROUTE_DISTANCE_KM=100.0
MAX_ROUTE_DURATION_HOURS=8.0

# Pool de Conexiones (OPCIONAL)
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=10
```

---

## 📚 Comandos Útiles

### Inicializar Base de Datos
```powershell
python scripts/initialize_database.py
```

### Poblar Datos de Ejemplo
```powershell
python scripts/init_sample_data.py
```

### Ejecutar Aplicación
```powershell
streamlit run main.py
```

### Ejecutar Tests
```powershell
pytest tests/ --cov=src --cov-report=html
```

---

## 🔍 Dónde Encontrar...

### Modelos de Dominio
- `src/domain/models/route.py` - Entidad Route
- `src/domain/models/client.py` - Entidad Client

### Puertos (Interfaces)
- `src/domain/ports/route_repository_port.py` - Puerto de persistencia
- `src/domain/ports/route_optimization_port.py` - Puerto de optimización

### Servicios de Aplicación
- `src/application/services/route_service.py` - Casos de uso de rutas
- `src/application/services/route_optimization_service.py` - Casos de optimización

### Adaptadores (Implementaciones)
- `src/infrastructure/persistence/postgres_route_repository.py` - Adaptador PostgreSQL
- `src/infrastructure/services/google_maps_service.py` - Adaptador Google Maps
- `src/infrastructure/ui/streamlit_app.py` - Adaptador UI

### DTOs
- `src/application/dtos.py` - Todos los DTOs

### Configuración
- `config.py` - Configuración centralizada
- `.env` - Variables de entorno (no versionado)

---

## 💡 Preguntas Frecuentes (FAQ)

### ¿Por qué Arquitectura Hexagonal?
Para desacoplar el core de negocio de tecnologías específicas, facilitando testing y evolución.

### ¿Puedo cambiar PostgreSQL por otro DB?
Sí, solo necesitas crear un nuevo adaptador que implemente `RouteRepositoryPort`.

### ¿Puedo reemplazar Google Maps por otro proveedor?
Sí, crea un nuevo adaptador que implemente `RouteOptimizationPort` (ej. OpenRouteService).

### ¿Por qué Streamlit si no escala?
Por time-to-market. La arquitectura hexagonal permite migrar a FastAPI+React sin cambiar el core.

### ¿El sistema funciona sin Google Maps API?
Sí, la optimización es opcional. El sistema de gestión de rutas funciona completamente sin ella.

### ¿Cómo ejecuto tests?
```powershell
pytest tests/ -v
```

### ¿Está listo para producción?
❌ NO sin implementar autenticación, logging estructurado y alta disponibilidad.

---

## 🚀 Roadmap de Mejoras

### Fase 1: Seguridad (2-3 semanas) - CRÍTICO
- [ ] Implementar autenticación (OAuth2 o HTTP Basic)
- [ ] Migrar secretos a vault
- [ ] Habilitar HTTPS

### Fase 2: Observabilidad (1-2 semanas) - ALTO
- [ ] Logging estructurado (JSON)
- [ ] Métricas con Prometheus
- [ ] Health checks

### Fase 3: Escalabilidad (4-6 semanas) - MEDIO
- [ ] Migrar a FastAPI + React (opcional)
- [ ] PostgreSQL HA (Primary/Replica)
- [ ] Containerización (Docker/K8s)

### Fase 4: Optimizaciones (2-3 semanas) - BAJO
- [ ] Caché de geocodificación (Redis)
- [ ] Índices compuestos en DB
- [ ] Incrementar cobertura de tests (80%)

---

## 📞 Contacto y Soporte

Para preguntas sobre la arquitectura ADL o el proyecto:
- Consultar documentación completa: `ADL/Analisis_ADL.md`
- Revisar diagramas: `ADL/Diagramas_ADL.md`
- Documentación técnica: `docs/`

---

## 📝 Checklist de Revisión ADL

### ✅ Completado
- [x] Identificación de componentes (9 componentes)
- [x] Definición de interfaces (puertos provistos/requeridos)
- [x] Identificación de conectores (6 conectores)
- [x] Especificación de topología (grafo de interconexión)
- [x] Definición de estilo arquitectónico (Hexagonal)
- [x] Enumeración de restricciones (11 restricciones)
- [x] Análisis de PNF (10 propiedades)
- [x] Documentación de decisiones arquitectónicas (5 ADRs)
- [x] Diagramas visuales (componentes, secuencia, dependencias)
- [x] Métricas de calidad

### ⚠️ Recomendaciones Pendientes
- [ ] Implementar autenticación (bloqueador de producción)
- [ ] Añadir logging estructurado
- [ ] Configurar alta disponibilidad
- [ ] Incrementar cobertura de tests

---

**Fin de Guía Rápida de Referencia ADL**  
**Versión:** 1.0  
**Fecha:** 6 de noviembre de 2025

**Para análisis detallado, consultar:** `Analisis_ADL.md`
