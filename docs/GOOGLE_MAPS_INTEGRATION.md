# 🗺️ Integración de Google Maps API

## Descripción General

Este documento describe la integración de Google Maps API en Yedistribuciones para optimización de rutas, manteniendo la **Arquitectura Hexagonal** y aplicando patrones de diseño.

---

## 📁 Estructura del Proyecto (Actualizada)

```
yedistribuciones_project/
│
├── config.py                          # 🆕 Configuración centralizada
├── main.py                            # 🔄 Actualizado con inyección de optimización
├── requirements.txt                   # 🔄 Actualizado con nuevas dependencias
│
├── src/
│   ├── domain/                        # CAPA DE DOMINIO (sin cambios)
│   │   ├── models/
│   │   │   ├── route.py
│   │   │   └── client.py             # 🔄 Actualizado con lat/lon
│   │   └── ports/
│   │       ├── route_repository_port.py
│   │       └── route_optimization_port.py  # 🆕 PUERTO de optimización
│   │
│   ├── application/                   # CAPA DE APLICACIÓN
│   │   ├── services/
│   │   │   ├── route_service.py
│   │   │   └── route_optimization_service.py  # 🆕 Servicio de aplicación
│   │   └── dtos.py
│   │
│   └── infrastructure/                # CAPA DE INFRAESTRUCTURA
│       ├── persistence/
│       │   └── sqlite_route_repository.py
│       ├── services/
│       │   └── google_maps_service.py        # 🆕 ADAPTADOR de Google Maps
│       └── ui/
│           └── streamlit_app.py      # 🔄 Actualizado con vistas de optimización
│
└── README/
    ├── ARQUITECTURA.md
    ├── GOOGLE_MAPS_INTEGRATION.md    # 🆕 Este documento
    └── ...
```

---

## 🏗️ Arquitectura Hexagonal Aplicada

### Principios Seguidos

1. **Dependency Inversion Principle (DIP)**: El dominio NO depende de Google Maps
2. **Adapter Pattern**: Google Maps es un adaptador intercambiable
3. **Port Pattern**: Abstracción para cualquier servicio de optimización
4. **Separation of Concerns**: Cada capa tiene responsabilidades claras

### Flujo de Dependencias

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DOMINIO                          │
│  (Reglas de negocio puras, sin dependencias externas)       │
│                                                              │
│  ┌────────────────────────────────────────────┐             │
│  │   RouteOptimizationPort (Abstracción)      │             │
│  │   - geocode_address()                      │             │
│  │   - calculate_distance_matrix()            │             │
│  │   - optimize_route()                       │             │
│  │   - get_route_directions()                 │             │
│  └────────────────────────────────────────────┘             │
└───────────────────────┬─────────────────────────────────────┘
                        │ depende de (↑)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                 CAPA DE APLICACIÓN                          │
│  (Casos de uso, orquestación)                               │
│                                                              │
│  ┌────────────────────────────────────────────┐             │
│  │   RouteOptimizationService                 │             │
│  │   - geocode_clients()                      │             │
│  │   - optimize_route_order()                 │             │
│  │   - calculate_route_metrics()              │             │
│  │   - suggest_route_split()                  │             │
│  └────────────────────────────────────────────┘             │
└───────────────────────┬─────────────────────────────────────┘
                        │ implementa (↓)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│              CAPA DE INFRAESTRUCTURA                        │
│  (Adaptadores para tecnologías específicas)                 │
│                                                              │
│  ┌────────────────────────────────────────────┐             │
│  │   GoogleMapsOptimizationService            │             │
│  │   implements RouteOptimizationPort         │             │
│  │                                            │             │
│  │   + Usa googlemaps library                 │             │
│  │   + Maneja API key                         │             │
│  │   + Convierte formatos                     │             │
│  └────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

**Ventaja**: Si mañana queremos usar OpenRouteService, Mapbox u otro proveedor, solo creamos un nuevo adaptador sin tocar dominio ni aplicación.

---

## 🔧 Configuración

### 1. Instalar Dependencias

```powershell
cd yedistribuciones_project
.\venv\Scripts\python.exe -m pip install googlemaps folium streamlit-folium
```

### 2. Obtener API Key de Google Maps

#### Paso a paso:

1. **Ir a Google Cloud Console**
   - URL: https://console.cloud.google.com/

2. **Crear o seleccionar un proyecto**
   - Haz clic en el selector de proyectos (arriba)
   - Clic en "Nuevo Proyecto"
   - Nombre: `Yedistribuciones`

3. **Habilitar APIs necesarias**
   - Ve a "APIs y servicios" → "Biblioteca"
   - Busca y habilita:
     - ✅ **Directions API** (para rutas punto a punto)
     - ✅ **Distance Matrix API** (para matriz de distancias)
     - ✅ **Geocoding API** (para convertir direcciones a coordenadas)

4. **Crear credenciales**
   - Ve a "APIs y servicios" → "Credenciales"
   - Clic en "+ CREAR CREDENCIALES" → "Clave de API"
   - Copia la API key generada

5. **(Recomendado) Restringir la API key**
   - Clic en la API key creada
   - En "Restricciones de aplicación": Selecciona "Direcciones IP"
   - Agrega tu IP o restricción deseada
   - En "Restricciones de API": Selecciona las 3 APIs habilitadas

### 3. Configurar la API Key

#### Opción 1: Variable de Entorno (Recomendado)

**Windows PowerShell:**
```powershell
$env:GOOGLE_MAPS_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

**Windows CMD:**
```cmd
set GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Linux/Mac:**
```bash
export GOOGLE_MAPS_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

#### Opción 2: Archivo .env

1. Crear archivo `.env` en la raíz:
```env
GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CEDIS_LATITUDE=4.7110
CEDIS_LONGITUDE=-74.0721
CEDIS_ADDRESS=Bogotá, Colombia
```

2. Instalar python-dotenv:
```powershell
pip install python-dotenv
```

3. Cargar en `config.py` (agregar al inicio):
```python
from dotenv import load_dotenv
load_dotenv()
```

### 4. Configurar Ubicación del CEDIS

```powershell
$env:CEDIS_LATITUDE="4.7110"
$env:CEDIS_LONGITUDE="-74.0721"
$env:CEDIS_ADDRESS="Calle 123 # 45-67, Bogotá"
```

### 5. Verificar Configuración

```powershell
python config.py
```

**Salida esperada:**
```
============================================================
CONFIGURACIÓN ACTUAL DE YEDISTRIBUCIONES
============================================================
Google Maps API: ✅ Configurada
CEDIS: Bogotá, Colombia
  Latitud: 4.711
  Longitud: -74.0721
Base de datos: yedistribuciones.db
Límite distancia: 100.0 km
Límite duración: 8.0 horas
============================================================
```

---

## 🚀 Uso de la Aplicación

### Ejecutar la Aplicación

```powershell
cd yedistribuciones_project
.\venv\Scripts\streamlit.exe run main.py
```

### Nuevas Funcionalidades

#### 1. 🗺️ Optimizar Ruta

**Ubicación:** Menú principal → "🗺️ Optimizar Ruta"

**Funcionalidad:**
- Selecciona una ruta existente
- El sistema geocodifica automáticamente las direcciones
- Usa Google Maps para calcular el orden óptimo
- Minimiza distancia y tiempo de recorrido
- Muestra:
  - Distancia total (km)
  - Tiempo estimado (minutos)
  - Orden optimizado de visita

**Nota:** Esta función NO modifica la ruta en la base de datos, solo muestra una sugerencia.

#### 2. 📊 Ver Métricas de Ruta

**Ubicación:** Menú principal → "📊 Ver Métricas de Ruta"

**Funcionalidad:**
- Calcula métricas reales usando Google Maps:
  - Distancia total del recorrido
  - Tiempo estimado
  - Número de clientes geocodificados
  
- **Análisis de Eficiencia:**
  - Compara con límites configurados
  - Sugiere división si es necesario
  - Indica punto óptimo de división

**Ejemplo de salida:**
```
📈 Métricas Actuales
  Distancia Total: 85.3 km
  Tiempo Estimado: 287 min
  Clientes con Coordenadas: 15

💡 Análisis de Eficiencia
  ✅ La ruta está dentro de los límites recomendados
```

---

## 🧩 Patrones de Diseño Implementados

### 1. Port/Adapter Pattern (Hexagonal Architecture)

**Puerto (Abstracción):**
```python
# src/domain/ports/route_optimization_port.py

class RouteOptimizationPort(ABC):
    @abstractmethod
    def optimize_route(
        self,
        origin: Tuple[float, float],
        waypoints: List[Tuple[float, float]],
        destination: Tuple[float, float]
    ) -> RouteOptimizationResult:
        pass
```

**Adaptador (Implementación):**
```python
# src/infrastructure/services/google_maps_service.py

class GoogleMapsOptimizationService(RouteOptimizationPort):
    def __init__(self, api_key: str):
        self._client = googlemaps.Client(key=api_key)
    
    def optimize_route(self, origin, waypoints, destination):
        # Implementación específica de Google Maps
        directions = self._client.directions(...)
        return RouteOptimizationResult(...)
```

**Beneficios:**
- ✅ Dominio independiente de Google Maps
- ✅ Fácil cambio a otro proveedor (Mapbox, HERE, etc.)
- ✅ Testeable con mocks

### 2. Dependency Injection

**Inyección en main.py:**
```python
# Crear adaptador
google_maps_adapter = GoogleMapsOptimizationService(api_key=Config.GOOGLE_MAPS_API_KEY)

# Inyectar en servicio de aplicación
optimization_service = RouteOptimizationService(
    route_repository=route_repo,
    optimization_service=google_maps_adapter  # Inyección de dependencia
)

# Inyectar en UI
run_ui(route_service, optimization_service)
```

**Beneficios:**
- ✅ Bajo acoplamiento
- ✅ Alta testeabilidad
- ✅ Flexibilidad para cambiar implementaciones

### 3. Service Layer Pattern

**RouteOptimizationService** coordina múltiples operaciones:
```python
def optimize_route_order(self, route_id, cedis_location, client_locations):
    # 1. Filtrar clientes con coordenadas
    clients_with_coords = [c for c in client_locations if c.latitude]
    
    # 2. Extraer coordenadas
    waypoints = [(c.latitude, c.longitude) for c in clients_with_coords]
    
    # 3. Llamar al servicio de optimización (puerto)
    result = self._optimizer.optimize_route(origin, waypoints, destination)
    
    return result
```

**Beneficios:**
- ✅ Lógica de coordinación separada del dominio
- ✅ Reutilizable desde múltiples adaptadores
- ✅ Fácil de testear

### 4. Configuration Pattern

**Config centralizado:**
```python
class Config:
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', None)
    CEDIS_LATITUDE = float(os.getenv('CEDIS_LATITUDE', '4.7110'))
    
    @classmethod
    def is_google_maps_enabled(cls) -> bool:
        return cls.GOOGLE_MAPS_API_KEY is not None
```

**Beneficios:**
- ✅ Única fuente de verdad
- ✅ Fácil cambio entre ambientes
- ✅ Validación centralizada

---

## 🧪 Testing

### Test de Configuración

```python
# test_config.py
def test_config_validation():
    warnings = Config.validate_config()
    assert isinstance(warnings, list)

def test_google_maps_enabled():
    # Simular API key configurada
    Config.GOOGLE_MAPS_API_KEY = "test_key"
    assert Config.is_google_maps_enabled() == True
```

### Test del Puerto (con Mock)

```python
# test_route_optimization_service.py
from unittest.mock import Mock

def test_optimize_route_order():
    # Mock del puerto
    mock_optimizer = Mock(spec=RouteOptimizationPort)
    mock_optimizer.optimize_route.return_value = RouteOptimizationResult(
        optimized_order=[1, 2, 3],
        total_distance_km=50.0,
        total_duration_minutes=120.0
    )
    
    # Servicio con mock inyectado
    service = RouteOptimizationService(
        route_repository=mock_repo,
        optimization_service=mock_optimizer
    )
    
    result = service.optimize_route_order(...)
    
    assert result.total_distance_km == 50.0
    mock_optimizer.optimize_route.assert_called_once()
```

### Test del Adaptador (Integración)

```python
# test_google_maps_service.py
def test_google_maps_geocode():
    service = GoogleMapsOptimizationService(api_key="test_key")
    coords = service.geocode_address("Bogotá, Colombia")
    
    assert coords is not None
    assert -90 <= coords[0] <= 90  # Latitud válida
    assert -180 <= coords[1] <= 180  # Longitud válida
```

---

## 📊 Diagrama de Secuencia: Optimizar Ruta

```
Usuario → Streamlit UI → RouteOptimizationService → GoogleMapsAdapter → Google Maps API

1. Usuario selecciona ruta
   ↓
2. UI llama optimization_service.optimize_route_order()
   ↓
3. Servicio geocodifica clientes sin coordenadas
   ├→ Llama optimizer.geocode_address() para cada cliente
   └→ GoogleMapsAdapter usa googlemaps.geocode()
   ↓
4. Servicio extrae waypoints
   ↓
5. Servicio llama optimizer.optimize_route()
   ├→ GoogleMapsAdapter usa googlemaps.directions()
   └→ Procesa respuesta y extrae orden optimizado
   ↓
6. Servicio retorna RouteOptimizationResult
   ↓
7. UI muestra distancia, tiempo y orden
```

---

## 🔒 Seguridad

### Mejores Prácticas

1. **Nunca subir API keys a Git**
   ```gitignore
   # .gitignore
   .env
   config_local.py
   ```

2. **Usar variables de entorno**
   - Evita hardcodear API keys
   - Diferentes keys por ambiente (dev/prod)

3. **Restringir API key en Google Cloud**
   - Restricción por IP
   - Restricción por API específica
   - Cuotas y límites

4. **Rotación de keys**
   - Cambiar API keys periódicamente
   - Usar diferentes keys por servicio

### Manejo de Errores

```python
# google_maps_service.py
def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
    try:
        result = self._client.geocode(address)
        # ... procesamiento
    except googlemaps.exceptions.ApiError as e:
        print(f"Error de API de Google Maps: {str(e)}")
        return None
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return None
```

---

## 💰 Costos de Google Maps API

### Precios (Enero 2024)

| API | Precio por 1000 llamadas | Crédito gratuito mensual |
|-----|--------------------------|--------------------------|
| Directions API | $5.00 | $200 (≈ 40,000 llamadas) |
| Distance Matrix API | $5.00 | $200 (≈ 40,000 llamadas) |
| Geocoding API | $5.00 | $200 (≈ 40,000 llamadas) |

### Estimación de Uso

Para Yedistribuciones con **100 rutas/día**:
- Geocoding: 500 clientes/día × 30 días = **15,000 llamadas/mes**
- Optimization: 100 rutas/día × 30 días = **3,000 llamadas/mes**
- **Total: ~18,000 llamadas/mes** → **GRATIS** (dentro del crédito de $200)

### Optimización de Costos

1. **Cachear geocodificación**
   - Guardar coordenadas en base de datos
   - No volver a geocodificar la misma dirección

2. **Batch requests**
   - Usar Distance Matrix para múltiples puntos
   - Reducir número de llamadas

3. **Fallback sin API**
   - Funcionalidad básica sin optimización
   - Degradación elegante

---

## 🐛 Troubleshooting

### Error: "googlemaps module not found"

**Solución:**
```powershell
.\venv\Scripts\python.exe -m pip install googlemaps
```

### Error: "API key not configured"

**Solución:**
```powershell
$env:GOOGLE_MAPS_API_KEY="tu_api_key_aqui"
python config.py  # Verificar
```

### Error: "REQUEST_DENIED"

**Causas:**
- API no habilitada en Google Cloud
- API key inválida
- Restricciones de IP/API

**Solución:**
1. Verificar APIs habilitadas en Google Cloud Console
2. Revisar restricciones de la API key
3. Regenerar API key si es necesario

### Error: "OVER_QUERY_LIMIT"

**Causas:**
- Excediste el límite gratuito
- Demasiadas llamadas simultáneas

**Solución:**
1. Habilitar facturación en Google Cloud
2. Implementar rate limiting
3. Cachear resultados

---

## 📚 Referencias

- [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- [Directions API](https://developers.google.com/maps/documentation/directions)
- [Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix)
- [Geocoding API](https://developers.google.com/maps/documentation/geocoding)
- [googlemaps Python Client](https://github.com/googlemaps/google-maps-services-python)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

---

## 🎯 Próximos Pasos (Futuras Mejoras)

1. **Cachear Geocodificación**
   - Guardar lat/lon en base de datos
   - Evitar llamadas repetidas

2. **Visualización de Mapas**
   - Usar Folium para mostrar rutas
   - Marcadores interactivos

3. **Reportes PDF**
   - Exportar rutas optimizadas
   - Incluir mapas

4. **Optimización Multi-Vehículo**
   - Usar Google OR-Tools
   - Asignar múltiples rutas simultáneamente

5. **Modo Offline**
   - OpenStreetMap como fallback
   - OSRM para routing local

---

**Autor:** Yedistribuciones Development Team  
**Última actualización:** Enero 2025  
**Versión:** 2.0
