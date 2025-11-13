# 📡 Documentación de API - Yedistribuciones

## Información General

- **Base URL**: `http://localhost:5000`
- **Formato**: JSON
- **Autenticación**: No requerida (desarrollo)
- **Versión**: 1.0

## Tabla de Contenidos

1. [Rutas (Routes)](#rutas)
   - [Listar todas las rutas](#get-routes)
   - [Obtener ruta por ID](#get-route-by-id)
   - [Crear nueva ruta](#create-route)
   - [Asignar cliente a ruta](#add-client)
   - [Eliminar cliente de ruta](#remove-client)
   - [Reordenar clientes](#reorder-clients)
   - [Dividir ruta](#divide-route)
   - [Fusionar rutas](#merge-routes)
   - [Optimizar ruta](#optimize-route)

2. [Clientes (Clients)](#clientes)
   - [Listar clientes disponibles](#get-clients)

3. [Modelos de Datos](#modelos)
4. [Códigos de Estado](#codigos)
5. [Ejemplos de Uso](#ejemplos)
6. [Arquitectura e Integración](#arquitectura)

---

## 🚦 Rutas (Routes) {#rutas}

### 📋 Listar todas las rutas {#get-routes}

Obtiene todas las rutas activas del sistema.

**Endpoint**
```http
GET /api/routes
```

**Respuesta Exitosa** (200 OK)
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Ruta Norte - Lunes",
      "cedis_id": "13",
      "day_of_week": "LUNES",
      "client_count": 12,
      "is_active": true
    },
    {
      "id": "650e8400-e29b-41d4-a716-446655440001",
      "name": "Ruta Sur - Martes",
      "cedis_id": "14",
      "day_of_week": "MARTES",
      "client_count": 8,
      "is_active": true
    }
  ]
}
```

**Ejemplo cURL**
```bash
curl -X GET http://localhost:5000/api/routes
```

**Ejemplo Python**
```python
import requests

response = requests.get('http://localhost:5000/api/routes')
data = response.json()

for route in data['data']:
    print(f"{route['name']}: {route['client_count']} clientes")
```

**Flujo en la Arquitectura**
```
Cliente HTTP → Flask Adapter → RouteService → Repository → PostgreSQL
                                     ↓
                                   DTO ← Route Entity
```

---

### 🔍 Obtener ruta por ID {#get-route-by-id}

Obtiene los detalles completos de una ruta específica.

**Endpoint**
```http
GET /api/routes/{route_id}
```

**Parámetros de URL**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| route_id | string (UUID) | ID único de la ruta |

**Respuesta Exitosa** (200 OK)
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Ruta Norte - Lunes",
    "cedis_id": "13",
    "day_of_week": "LUNES",
    "client_ids": [
      "CLI_001",
      "CLI_002",
      "CLI_003"
    ],
    "client_count": 3,
    "is_active": true
  }
}
```

**Respuesta de Error** (404 Not Found)
```json
{
  "success": false,
  "error": "Ruta no encontrada"
}
```

**Ejemplo cURL**
```bash
curl -X GET http://localhost:5000/api/routes/550e8400-e29b-41d4-a716-446655440000
```

**Ejemplo JavaScript (Fetch)**
```javascript
fetch(`http://localhost:5000/api/routes/${routeId}`)
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('Ruta:', data.data);
    } else {
      console.error('Error:', data.error);
    }
  });
```

---

### ➕ Crear nueva ruta {#create-route}

Crea una nueva ruta en el sistema.

**Endpoint**
```http
POST /routes/create
```

**Nota**: Este endpoint usa form-data (no JSON) y redirige a la vista web.

**Parámetros de Formulario**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| name | string | Sí | Nombre de la ruta |
| cedis_id | string | Sí | ID del CEDIS |
| day_of_week | string | Sí | Día de la semana (LUNES, MARTES, etc.) |

**Ejemplo cURL**
```bash
curl -X POST http://localhost:5000/routes/create \
  -F "name=Ruta Oeste - Miércoles" \
  -F "cedis_id=15" \
  -F "day_of_week=MIERCOLES"
```

**Flujo en la Arquitectura**
```
HTTP POST → Flask Adapter → CreateRouteDTO
                ↓
         RouteService.create_route()
                ↓
         RouteBuilder.create_simple()  (Builder Pattern)
                ↓
         Repository.save()
                ↓
         PostgreSQL
```

---

### 👥 Asignar cliente a ruta {#add-client}

Añade un cliente a una ruta existente.

**Endpoint**
```http
POST /api/routes/{route_id}/clients
```

**Parámetros de URL**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| route_id | string (UUID) | ID de la ruta |

**Body (JSON)**
```json
{
  "client_id": "CLI_001"
}
```

**Respuesta Exitosa** (200 OK)
```json
{
  "success": true,
  "message": "Cliente CLI_001 añadido a la ruta",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Ruta Norte - Lunes",
    "client_count": 13
  }
}
```

**Respuesta de Error** (400 Bad Request)
```json
{
  "success": false,
  "error": "client_id requerido"
}
```

**Ejemplo Python**
```python
import requests

route_id = "550e8400-e29b-41d4-a716-446655440000"
payload = {"client_id": "CLI_001"}

response = requests.post(
    f'http://localhost:5000/api/routes/{route_id}/clients',
    json=payload
)

result = response.json()
print(result['message'])
```

**Flujo en la Arquitectura**
```
HTTP POST → Flask Adapter → RouteService.assign_client_to_route()
                                  ↓
                           Repository.find_by_id()
                                  ↓
                           Route.add_client()  (Domain Logic)
                                  ↓
                           Repository.update()
                                  ↓
                           Transaction Commit
```

---

### ➖ Eliminar cliente de ruta {#remove-client}

Elimina un cliente de una ruta.

**Endpoint**
```http
DELETE /api/routes/{route_id}/clients/{client_id}
```

**Parámetros de URL**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| route_id | string (UUID) | ID de la ruta |
| client_id | string | ID del cliente |

**Respuesta Exitosa** (200 OK)
```json
{
  "success": true,
  "message": "Cliente CLI_001 eliminado de la ruta",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Ruta Norte - Lunes",
    "client_count": 12
  }
}
```

**Ejemplo cURL**
```bash
curl -X DELETE http://localhost:5000/api/routes/550e8400-e29b-41d4-a716-446655440000/clients/CLI_001
```

**Ejemplo JavaScript (Axios)**
```javascript
axios.delete(`/api/routes/${routeId}/clients/${clientId}`)
  .then(response => {
    if (response.data.success) {
      alert(response.data.message);
      // Actualizar UI
    }
  })
  .catch(error => console.error(error));
```

---

### 🔄 Reordenar clientes {#reorder-clients}

Cambia el orden de los clientes en una ruta.

**Endpoint**
```http
POST /api/routes/{route_id}/reorder
```

**Parámetros de URL**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| route_id | string (UUID) | ID de la ruta |

**Body (JSON)**
```json
{
  "client_ids": ["CLI_003", "CLI_001", "CLI_002"]
}
```

**Respuesta Exitosa** (200 OK)
```json
{
  "success": true,
  "message": "Clientes reordenados exitosamente",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Ruta Norte - Lunes",
    "client_ids": ["CLI_003", "CLI_001", "CLI_002"]
  }
}
```

**Ejemplo Python**
```python
import requests

route_id = "550e8400-e29b-41d4-a716-446655440000"
new_order = ["CLI_003", "CLI_001", "CLI_002"]

response = requests.post(
    f'http://localhost:5000/api/routes/{route_id}/reorder',
    json={"client_ids": new_order}
)
```

---

### ✂️ Dividir ruta {#divide-route}

Divide una ruta en dos rutas nuevas.

**Endpoint**
```http
POST /api/routes/divide
```

**Body (JSON)**
```json
{
  "route_id": "550e8400-e29b-41d4-a716-446655440000",
  "split_point": 5,
  "name_a": "Ruta Norte A",
  "name_b": "Ruta Norte B"
}
```

**Parámetros**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| route_id | string | ID de la ruta a dividir |
| split_point | integer | Índice donde dividir (primeros N clientes en A) |
| name_a | string | Nombre para la primera ruta |
| name_b | string | Nombre para la segunda ruta |

**Respuesta Exitosa** (200 OK)
```json
{
  "success": true,
  "message": "Ruta dividida exitosamente",
  "data": {
    "route_a": {
      "id": "750e8400-e29b-41d4-a716-446655440000",
      "name": "Ruta Norte A",
      "client_count": 5
    },
    "route_b": {
      "id": "850e8400-e29b-41d4-a716-446655440001",
      "name": "Ruta Norte B",
      "client_count": 7
    }
  }
}
```

**Ejemplo Python**
```python
import requests

payload = {
    "route_id": "550e8400-e29b-41d4-a716-446655440000",
    "split_point": 5,
    "name_a": "Ruta Norte A",
    "name_b": "Ruta Norte B"
}

response = requests.post(
    'http://localhost:5000/api/routes/divide',
    json=payload
)

result = response.json()
print(f"Ruta A: {result['data']['route_a']['client_count']} clientes")
print(f"Ruta B: {result['data']['route_b']['client_count']} clientes")
```

**Flujo en la Arquitectura**
```
HTTP POST → Flask Adapter → RouteService.divide_route_use_case()
                                  ↓
                           Repository.find_by_id()
                                  ↓
                           Route.divide_at()  (Domain Logic)
                                  ↓
                    (2x) RouteBuilder.build()  (Builder Pattern)
                                  ↓
                    (2x) Repository.save()
                                  ↓
                           Transaction Commit
```

---

### 🔗 Fusionar rutas {#merge-routes}

Fusiona dos rutas en una sola.

**Endpoint**
```http
POST /api/routes/merge
```

**Body (JSON)**
```json
{
  "route_a_id": "550e8400-e29b-41d4-a716-446655440000",
  "route_b_id": "650e8400-e29b-41d4-a716-446655440001",
  "new_name": "Ruta Fusionada Norte-Sur"
}
```

**Respuesta Exitosa** (200 OK)
```json
{
  "success": true,
  "message": "Rutas fusionadas exitosamente",
  "data": {
    "id": "950e8400-e29b-41d4-a716-446655440002",
    "name": "Ruta Fusionada Norte-Sur",
    "client_count": 20
  }
}
```

**Ejemplo cURL**
```bash
curl -X POST http://localhost:5000/api/routes/merge \
  -H "Content-Type: application/json" \
  -d '{
    "route_a_id": "550e8400-e29b-41d4-a716-446655440000",
    "route_b_id": "650e8400-e29b-41d4-a716-446655440001",
    "new_name": "Ruta Fusionada"
  }'
```

---

### 🎯 Optimizar ruta {#optimize-route}

Optimiza el orden de clientes en una ruta para minimizar distancia.

**Endpoint**
```http
POST /api/routes/{route_id}/optimize
```

**Parámetros de URL**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| route_id | string (UUID) | ID de la ruta |

**Body (JSON)**
```json
{
  "clients": [
    {
      "id": "CLI_001",
      "address": "Calle 123 #45-67",
      "latitude": 4.6097,
      "longitude": -74.0817
    },
    {
      "id": "CLI_002",
      "address": "Avenida 45 #12-34",
      "latitude": 4.6487,
      "longitude": -74.0578
    }
  ],
  "origin": {
    "latitude": 4.7110,
    "longitude": -74.0721
  }
}
```

**Respuesta Exitosa** (200 OK)
```json
{
  "success": true,
  "message": "Ruta optimizada exitosamente",
  "data": {
    "original_distance_km": 45.3,
    "optimized_distance_km": 38.7,
    "distance_saved_km": 6.6,
    "time_saved_minutes": 18,
    "optimized_order": ["CLI_002", "CLI_001", "CLI_003"]
  }
}
```

**Respuesta de Error** (503 Service Unavailable)
```json
{
  "success": false,
  "error": "Optimización no disponible"
}
```

**Nota**: Requiere Google Maps API Key configurada.

**Flujo en la Arquitectura - Strategy Pattern**
```
HTTP POST → Flask Adapter → RouteOptimizationService
                                  ↓
                         OptimizationContext
                                  ↓
                  ┌───────────────┴────────────────┐
                  │                                │
         GoogleMapsStrategy          NearestNeighborStrategy
         (si API disponible)              (fallback)
                  │                                │
                  └────────────┬───────────────────┘
                               ↓
                      OptimizationResult
                               ↓
                      Repository.update()
```

---

## 👥 Clientes (Clients) {#clientes}

### 📋 Listar clientes disponibles {#get-clients}

Obtiene todos los clientes disponibles para asignar a rutas.

**Endpoint**
```http
GET /api/clients
```

**Respuesta Exitosa** (200 OK)
```json
{
  "success": true,
  "data": [
    {
      "id": "CLI_001",
      "name": "Tienda El Éxito",
      "address": "Calle 123 #45-67, Bogotá",
      "phone": "3001234567"
    },
    {
      "id": "CLI_002",
      "name": "Supermercado La Fortuna",
      "address": "Avenida 45 #12-34, Bogotá",
      "phone": "3009876543"
    }
  ]
}
```

**Ejemplo Python**
```python
import requests

response = requests.get('http://localhost:5000/api/clients')
clients = response.json()['data']

# Crear dropdown
for client in clients:
    print(f"<option value='{client['id']}'>{client['name']}</option>")
```

---

## 📊 Modelos de Datos {#modelos}

### Route (Ruta)

```typescript
interface Route {
  id: string;              // UUID único
  name: string;            // Nombre descriptivo
  cedis_id: string;        // ID del CEDIS de origen
  day_of_week: string;     // LUNES, MARTES, etc.
  client_ids: string[];    // Array de IDs de clientes (orden de visita)
  client_count: number;    // Cantidad de clientes
  is_active: boolean;      // Estado de la ruta
}
```

### Client (Cliente)

```typescript
interface Client {
  id: string;              // ID único
  name: string;            // Nombre del cliente
  address: string;         // Dirección completa
  phone: string;           // Teléfono de contacto
}
```

### OptimizationResult

```typescript
interface OptimizationResult {
  original_distance_km: number;      // Distancia antes
  optimized_distance_km: number;     // Distancia después
  distance_saved_km: number;         // Ahorro en km
  time_saved_minutes: number;        // Ahorro en minutos
  optimized_order: string[];         // Nuevo orden de clientes
}
```

### ErrorResponse

```typescript
interface ErrorResponse {
  success: false;
  error: string;           // Mensaje de error
}
```

---

## 🚦 Códigos de Estado HTTP {#codigos}

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Operación exitosa |
| 400 | Bad Request | Parámetros inválidos o faltantes |
| 404 | Not Found | Ruta o recurso no encontrado |
| 500 | Internal Server Error | Error del servidor |
| 503 | Service Unavailable | Servicio (como optimización) no disponible |

---

## 💡 Ejemplos de Uso Completos {#ejemplos}

### Ejemplo 1: Crear y configurar una ruta completa

```python
import requests

BASE_URL = "http://localhost:5000"

# 1. Crear ruta
form_data = {
    "name": "Ruta Centro - Jueves",
    "cedis_id": "13",
    "day_of_week": "JUEVES"
}
response = requests.post(f"{BASE_URL}/routes/create", data=form_data)

# Obtener el ID de la ruta creada (desde redirección)
route_id = "..."  # Obtenido de la respuesta

# 2. Obtener clientes disponibles
response = requests.get(f"{BASE_URL}/api/clients")
clients = response.json()['data']

# 3. Asignar primeros 5 clientes
for client in clients[:5]:
    requests.post(
        f"{BASE_URL}/api/routes/{route_id}/clients",
        json={"client_id": client['id']}
    )
    print(f"✅ Cliente {client['name']} asignado")

# 4. Optimizar ruta
clients_data = [
    {
        "id": c['id'],
        "address": c['address'],
        "latitude": 4.60,  # Coordenadas reales
        "longitude": -74.08
    }
    for c in clients[:5]
]

optimization_payload = {
    "clients": clients_data,
    "origin": {"latitude": 4.7110, "longitude": -74.0721}
}

response = requests.post(
    f"{BASE_URL}/api/routes/{route_id}/optimize",
    json=optimization_payload
)

if response.status_code == 200:
    result = response.json()['data']
    print(f"💾 Ahorro: {result['distance_saved_km']} km")
    print(f"⏱️ Tiempo ahorrado: {result['time_saved_minutes']} min")
```

### Ejemplo 2: Gestión de rutas con errores

```javascript
async function manageRoute(routeId) {
  try {
    // Obtener ruta
    const response = await fetch(`/api/routes/${routeId}`);
    if (!response.ok) {
      throw new Error('Ruta no encontrada');
    }
    
    const routeData = await response.json();
    console.log('Ruta:', routeData.data);
    
    // Agregar cliente
    const addResponse = await fetch(`/api/routes/${routeId}/clients`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({client_id: 'CLI_NEW'})
    });
    
    if (!addResponse.ok) {
      const error = await addResponse.json();
      console.error('Error:', error.error);
    }
    
  } catch (error) {
    console.error('Error de red:', error);
  }
}
```

---

## 🏗️ Arquitectura e Integración {#arquitectura}

### Flujo General de Request

```
┌─────────────┐
│   Cliente   │  (Browser, App, Script)
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────────────────┐
│         Flask Application               │
│  (Infrastructure Layer - UI Adapter)    │
│                                         │
│  @app.route('/api/routes')              │
│  def api_get_routes():                  │
│      service = get_route_service()      │
│      routes = service.get_all_routes()  │
│      return jsonify(...)                │
└──────┬──────────────────────────────────┘
       │ DTO
       ▼
┌─────────────────────────────────────────┐
│         Application Layer               │
│         (RouteService)                  │
│                                         │
│  - Casos de uso                         │
│  - Orquestación                         │
│  - Validaciones de negocio              │
└──────┬──────────────────────────────────┘
       │ Domain Models
       ▼
┌─────────────────────────────────────────┐
│         Domain Layer                    │
│                                         │
│  Route Entity (Lógica de negocio)       │
│  - add_client()                         │
│  - remove_client()                      │
│  - divide_at()                          │
└──────┬──────────────────────────────────┘
       │ Through Port
       ▼
┌─────────────────────────────────────────┐
│    Infrastructure Layer                 │
│    (PostgresRouteRepository)            │
│                                         │
│  - Persistencia                         │
│  - Queries SQL                          │
│  - Transacciones                        │
└──────┬──────────────────────────────────┘
       │ SQL
       ▼
┌─────────────────────────────────────────┐
│          PostgreSQL Database            │
│                                         │
│  Tablas: rutas, clientes,               │
│          ruta_clientes, cedis           │
└─────────────────────────────────────────┘
```

### Patrones de Diseño en la API

#### 1. **Adapter Pattern** - Flask como Driving Adapter
```python
# Flask adapta HTTP → Llamadas de servicio
@app.route('/api/routes/<route_id>/clients', methods=['POST'])
def api_add_client(route_id: str):
    # Adaptar request HTTP a parámetros del dominio
    data = request.get_json()
    client_id = data.get('client_id')
    
    # Llamar al servicio (capa de aplicación)
    route = service.assign_client_to_route(route_id, client_id)
    
    # Adaptar respuesta del dominio a HTTP JSON
    return jsonify({...})
```

#### 2. **Dependency Injection** - Servicios inyectados
```python
# Servicios inyectados al crear la app
app = create_flask_app(route_service, optimization_service)

# Disponibles en toda la aplicación
service = app.config['ROUTE_SERVICE']
```

#### 3. **Factory Pattern** - Creación de la app
```python
from src.application.factories import FlaskServiceFactory

# Factory crea y configura todo
factory = FlaskServiceFactory()
app = factory.create_flask_app()
```

#### 4. **Strategy Pattern** - Optimización
```python
# Diferentes estrategias de optimización
@app.route('/api/routes/<route_id>/optimize', methods=['POST'])
def api_optimize_route(route_id: str):
    # OptimizationService usa Strategy Pattern
    # Puede usar GoogleMapsStrategy, NearestNeighborStrategy, etc.
    result = opt_service.optimize_route(...)
```

### Principios SOLID en la API

✅ **Single Responsibility**: Cada endpoint tiene una única responsabilidad  
✅ **Open/Closed**: Fácil agregar nuevos endpoints sin modificar existentes  
✅ **Liskov Substitution**: Servicios intercambiables vía interfaces  
✅ **Interface Segregation**: Contratos específicos (Ports)  
✅ **Dependency Inversion**: Flask depende de abstracciones, no implementaciones

---

## 🔐 Consideraciones de Seguridad

**Desarrollo Actual**:
- ❌ Sin autenticación
- ❌ Sin rate limiting
- ❌ Sin validación CSRF

**Recomendaciones para Producción**:
1. Implementar autenticación JWT o OAuth2
2. Agregar rate limiting (Flask-Limiter)
3. Validar y sanitizar todos los inputs
4. Usar HTTPS
5. Implementar CORS apropiado
6. Agregar logging de auditoría

---

## 📚 Recursos Adicionales

- **Código Fuente**: `src/infrastructure/ui/flask_app.py`
- **Servicios**: `src/application/services/`
- **Modelos**: `src/domain/models/`
- **Documentación Patrones**: `docs/DESIGN_PATTERNS.md`
- **Arquitectura**: `docs/ARCHITECTURE_HEXAGONAL_POSTGRESQL.md`

---

## 📝 Notas de Versión

**v1.0** (Noviembre 2025)
- ✅ API REST completa
- ✅ CRUD de rutas
- ✅ Optimización de rutas
- ✅ División y fusión de rutas
- ✅ Gestión de clientes

---

**Mantenido por**: Equipo Yedistribuciones  
**Última actualización**: Noviembre 2025  
**Soporte**: Consultar documentación técnica en `docs/`
