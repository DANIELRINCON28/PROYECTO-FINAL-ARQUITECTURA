# 🚀 Guía de Instalación y Uso - Optimización Inteligente de Rutas

## 📋 Requisitos Previos

- Python 3.8 o superior
- PostgreSQL instalado y configurado
- API Key de Google Maps (con Distance Matrix API habilitada)

## 🔧 Instalación

### 1. Instalar Dependencias

```powershell
# Navegar al directorio del proyecto
cd C:\Users\jsanc\OneDrive\Documentos\U\ARQUITECTURA\PROYECTO-FINAL-ARQUITECTURA

# Instalar/actualizar dependencias
pip install -r requirements.txt
```

Las nuevas dependencias incluidas son:
- `googlemaps==4.10.0` - Cliente de Google Maps API
- `ortools==9.8.3296` - Google OR-Tools para optimización TSP

### 2. Configurar Variables de Entorno

Crear o actualizar el archivo `.env` en la raíz del proyecto:

```ini
# Google Maps API
GOOGLE_MAPS_API_KEY=tu_api_key_aqui

# CEDIS (Centro de Distribución)
CEDIS_LATITUDE=4.7110
CEDIS_LONGITUDE=-74.0721
CEDIS_ADDRESS=Bogotá, Colombia

# Base de datos PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=RutasDB
DB_USER=postgres
DB_PASSWORD=tu_password
```

### 3. Obtener API Key de Google Maps

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear un nuevo proyecto o seleccionar uno existente
3. Habilitar las APIs:
   - Distance Matrix API
   - Geocoding API (opcional, para geocodificar direcciones)
4. Crear credenciales (API Key)
5. Copiar la API Key al archivo `.env`

**IMPORTANTE**: La API de Google Maps tiene costos. Configure límites de uso en la consola.

## ✅ Verificar Instalación

Ejecutar el script de ejemplo:

```powershell
python scripts\example_optimize_route.py
```

Deberías ver:
```
================================================================================
🚀 DEMOSTRACIÓN: Optimización Inteligente de Rutas (TSP)
================================================================================

1️⃣ Inicializando servicios...
✅ Google Maps Distance Provider configurado
✅ OR-Tools TSP Solver configurado
✅ Servicios creados exitosamente

2️⃣ Verificando disponibilidad de servicios...
   • Google Maps API: ✅
   • OR-Tools TSP Solver: ✅
   • Optimización Inteligente: ✅
```

## 📖 Uso Básico

### Ejemplo Completo

```python
from src.application.factories.service_factory import ServiceFactory
from src.application.dtos import (
    CreateRouteDTO, 
    OptimizeRouteDTO
)
from src.domain.models.client import Client
from config import Config

# 1. Crear servicios
factory = ServiceFactory()
route_service = factory.create_route_service()
optimization_service = factory.create_optimization_service()

# 2. Crear una ruta
route_dto = CreateRouteDTO(
    name="Ruta Norte Bogotá",
    cedis_id="cedis-001",
    day_of_week="LUNES"
)
route = route_service.create_route(route_dto)

# 3. Asignar clientes (asume que los clientes ya existen en BD)
client_ids = ["client-001", "client-002", "client-003", "client-004"]
for client_id in client_ids:
    route_service.assign_client_to_route(route.id, client_id)

# 4. Obtener objetos Client con coordenadas
# (En un caso real, estos vendrían de la base de datos)
clients = [
    Client(
        id="client-001",
        name="Cliente A",
        address="Dirección A",
        latitude=4.7275,
        longitude=-74.0386
    ),
    # ... más clientes
]

# 5. Optimizar la ruta
optimize_dto = OptimizeRouteDTO(
    route_id=route.id,
    cedis_latitude=Config.CEDIS_LATITUDE,
    cedis_longitude=Config.CEDIS_LONGITUDE,
    optimization_strategy="distance"  # "distance", "duration" o "balanced"
)

result = optimization_service.optimize_route_intelligent(optimize_dto, clients)

# 6. Ver resultado
if result.success:
    print(f"✅ Ruta optimizada exitosamente")
    print(f"Orden original: {result.original_client_order}")
    print(f"Orden optimizado: {result.optimized_client_order}")
    print(f"Distancia total: {result.total_distance_km:.2f} km")
    print(f"Duración estimada: {result.total_duration_minutes:.2f} min")
else:
    print(f"❌ Error: {result.message}")
```

## 🎯 Casos de Uso

### Caso 1: Optimizar Ruta Existente

```python
# Obtener ruta existente
route = route_service.get_route_by_id("ruta-123")

# Obtener clientes asignados (con coordenadas)
clients = get_clients_for_route(route.client_ids)

# Optimizar
dto = OptimizeRouteDTO(
    route_id=route.id,
    cedis_latitude=Config.CEDIS_LATITUDE,
    cedis_longitude=Config.CEDIS_LONGITUDE,
    optimization_strategy="distance"
)

result = optimization_service.optimize_route_intelligent(dto, clients)
```

### Caso 2: Comparar Estrategias de Optimización

```python
strategies = ["distance", "duration", "balanced"]
results = {}

for strategy in strategies:
    dto = OptimizeRouteDTO(
        route_id=route.id,
        cedis_latitude=Config.CEDIS_LATITUDE,
        cedis_longitude=Config.CEDIS_LONGITUDE,
        optimization_strategy=strategy
    )
    
    results[strategy] = optimization_service.optimize_route_intelligent(dto, clients)

# Comparar resultados
for strategy, result in results.items():
    print(f"{strategy}: {result.total_distance_km:.2f} km, {result.total_duration_minutes:.2f} min")
```

### Caso 3: Verificar Disponibilidad antes de Optimizar

```python
# Verificar que los servicios estén disponibles
availability = optimization_service.check_optimization_availability()

if availability["intelligent_optimization_available"]:
    result = optimization_service.optimize_route_intelligent(dto, clients)
else:
    print("⚠️ Optimización no disponible")
    if not availability["geo_distance_provider_available"]:
        print("   - Configure GOOGLE_MAPS_API_KEY")
    if not availability["optimization_solver_available"]:
        print("   - Instale ortools: pip install ortools")
```

## 🐛 Solución de Problemas

### Error: "Google Maps Distance service no está disponible"

**Causa**: API Key no configurada o inválida

**Solución**:
1. Verificar que `GOOGLE_MAPS_API_KEY` existe en `.env`
2. Verificar que la API Key es válida en Google Cloud Console
3. Asegurar que Distance Matrix API está habilitada

### Error: "OR-Tools no está disponible"

**Causa**: Biblioteca OR-Tools no instalada

**Solución**:
```powershell
pip install ortools==9.8.3296
```

Si el error persiste, verificar versión de Python:
```powershell
python --version  # Debe ser 3.8 - 3.11
```

### Advertencia: "Usando Nearest Neighbor Solver (subóptimo)"

**Causa**: OR-Tools no está instalado, se usa fallback

**Impacto**: Las rutas optimizadas pueden no ser óptimas pero seguirán siendo mejores que el orden aleatorio

**Solución**: Instalar OR-Tools (ver arriba)

### Error: "Cliente no tiene coordenadas geográficas"

**Causa**: Algunos clientes no tienen latitud/longitud

**Solución**: 
1. Geocodificar las direcciones de los clientes
2. Actualizar la base de datos con las coordenadas
3. Alternativamente, usar el servicio legacy de geocodificación:

```python
# Geocodificar antes de optimizar
geocoded_clients = optimization_service.geocode_clients(client_locations)
```

## 📊 Métricas y Monitoreo

### Logging

El módulo usa Python logging. Para ver logs detallados:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Logs típicos:
```
2024-11-13 10:30:15 - src.infrastructure.services.google_maps_distance_adapter - INFO - Google Maps Distance Adapter inicializado correctamente
2024-11-13 10:30:15 - src.infrastructure.services.ortools_tsp_solver - INFO - OR-Tools TSP Solver inicializado correctamente
2024-11-13 10:30:20 - src.application.services.route_optimization_service - INFO - Iniciando optimización inteligente de ruta ruta-123
2024-11-13 10:30:25 - src.infrastructure.services.ortools_tsp_solver - INFO - TSP resuelto (criterio: distance): 5 puntos, distancia: 45.32 km, duración: 68.50 min
2024-11-13 10:30:26 - src.application.services.route_optimization_service - INFO - Ruta ruta-123 optimizada exitosamente
```

## 🔐 Seguridad

### Proteger API Keys

**NUNCA** commitear el archivo `.env` al repositorio:

```bash
# Verificar que .env está en .gitignore
cat .gitignore | grep .env
```

### Limitar Uso de API

En Google Cloud Console:
1. Ir a APIs & Services > Credentials
2. Seleccionar la API Key
3. Configurar restricciones:
   - Application restrictions: HTTP referrers o IP addresses
   - API restrictions: Limitar a Distance Matrix API

## 📚 Documentación Adicional

- [Documentación Técnica Completa](./docs/ROUTE_OPTIMIZATION_TSP.md)
- [Arquitectura Hexagonal](./docs/HEXAGONAL_ARCHITECTURE.md)
- [API Documentation](./docs/API_DOCUMENTATION.md)

## 🤝 Soporte

Para reportar problemas o sugerencias:
1. Revisar esta guía y la documentación técnica
2. Verificar logs de error
3. Crear un issue en el repositorio con:
   - Descripción del problema
   - Logs relevantes
   - Versiones de dependencias (`pip freeze`)

## 📝 Changelog

### v1.0.0 (2024-11-13)
- ✨ Implementación inicial de optimización inteligente TSP
- ✅ Integración con Google Maps Distance Matrix API
- ✅ Solver OR-Tools con fallback a Nearest Neighbor
- ✅ Arquitectura hexagonal completa
- ✅ DTOs y servicios de aplicación
- ✅ Inyección de dependencias en ServiceFactory
