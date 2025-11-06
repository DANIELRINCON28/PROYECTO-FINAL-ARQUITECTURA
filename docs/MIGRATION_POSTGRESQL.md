# Migración a PostgreSQL - Yedistribuciones

## 📋 Descripción

Este documento describe la migración completa del sistema de gestión de rutas de SQLite a PostgreSQL, manteniendo la arquitectura hexagonal y los principios SOLID.

## 🏗️ Arquitectura

La arquitectura hexagonal se mantiene intacta:

```
┌─────────────────────────────────────────────────────────┐
│                  CAPA DE APLICACIÓN                     │
│              (Casos de Uso / Servicios)                 │
│  • RouteService                                         │
│  • RouteOptimizationService                            │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼────────┐ ┌─────▼──────────┐
│  PUERTO DE     │ │  PUERTO DE     │
│   ENTRADA      │ │   SALIDA       │
│                │ │                │
│ • Streamlit UI │ │ • Repository   │
└────────────────┘ └────────┬───────┘
                            │
                   ┌────────▼────────┐
                   │ INFRAESTRUCTURA │
                   │                 │
                   │ PostgreSQL      │
                   │ Repository      │
                   └─────────────────┘
```

## 🗃️ Estructura de Directorios

```
yedistribuciones_project/
├── config.py                          # Configuración centralizada
├── main.py                            # Punto de entrada con DI
├── initialize_database.py             # Script de inicialización de BD
├── migrate_data.py                    # Script de migración de datos
├── requirements.txt                   # Dependencias (actualizado)
├── .env.example                       # Plantilla de variables de entorno
├── src/
│   ├── domain/                        # CAPA DE DOMINIO
│   │   ├── models/
│   │   │   ├── route.py              # Entidad Route
│   │   │   ├── client.py             # Entidad Client
│   │   │   └── models.py             # Modelos Django (referencia)
│   │   └── ports/
│   │       └── route_repository_port.py  # Puerto de salida (abstracción)
│   ├── application/                   # CAPA DE APLICACIÓN
│   │   └── services/
│   │       ├── route_service.py      # Lógica de negocio
│   │       └── route_optimization_service.py
│   └── infrastructure/                # CAPA DE INFRAESTRUCTURA
│       ├── persistence/
│       │   ├── postgres_route_repository.py  # ✨ NUEVO
│       │   └── sqlite_route_repository.py    # Legacy (mantener)
│       ├── services/
│       │   └── google_maps_service.py
│       └── ui/
│           └── streamlit_app.py
```

## 🆕 Cambios Realizados

### 1. **Configuración (`config.py`)**
   - ✅ Agregadas variables de configuración PostgreSQL
   - ✅ Método `get_database_url()` para DSN de PostgreSQL
   - ✅ Método `get_db_connection_params()` para parámetros de conexión
   - ✅ Validación de configuración actualizada

### 2. **Dependencias (`requirements.txt`)**
   - ✅ Agregado `psycopg2-binary==2.9.9` (driver PostgreSQL)
   - ✅ Agregado `python-dotenv==1.0.0` (gestión de variables de entorno)

### 3. **Nuevo Repositorio PostgreSQL**
   - ✅ Archivo: `src/infrastructure/persistence/postgres_route_repository.py`
   - ✅ Implementa `RouteRepositoryPort`
   - ✅ Usa psycopg2 con conexiones parametrizadas
   - ✅ Manejo de transacciones ACID
   - ✅ Context managers para seguridad
   - ✅ Preparado para pool de conexiones

### 4. **Script de Inicialización (`initialize_database.py`)**
   - ✅ Crea la base de datos `RutasDB` si no existe
   - ✅ Crea todas las tablas según el modelo Django
   - ✅ Tablas principales:
     - `cedis` - Centros de distribución
     - `vendedores` - Vendedores
     - `clientes` - Clientes con coordenadas
     - `rutas` - Rutas con relaciones
     - `rutas_clientes` - Relación N:M
     - `asignaciones_rutas` - Asignaciones a vendedores
     - `routes` - Tabla de compatibilidad
   - ✅ Índices optimizados para consultas frecuentes
   - ✅ Triggers para actualización automática de timestamps
   - ✅ Constraints y validaciones a nivel de BD

### 5. **Script de Migración (`migrate_data.py`)**
   - ✅ Migra datos de SQLite a PostgreSQL
   - ✅ Manejo de errores robusto
   - ✅ Estadísticas de migración
   - ✅ Verificación post-migración

### 6. **Punto de Entrada (`main.py`)**
   - ✅ Actualizado para usar PostgreSQL por defecto
   - ✅ Carga automática de variables de entorno
   - ✅ Manejo de errores de conexión mejorado
   - ✅ Mensajes de ayuda para troubleshooting

## 🚀 Instalación y Configuración

### Paso 1: Instalar Dependencias

```powershell
pip install -r requirements.txt
```

### Paso 2: Instalar PostgreSQL

Si no tienes PostgreSQL instalado:

**Windows:**
```powershell
# Descargar desde: https://www.postgresql.org/download/windows/
# O usar Chocolatey:
choco install postgresql
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

### Paso 3: Configurar Variables de Entorno

Copia el archivo de ejemplo:
```powershell
Copy-Item .env.example .env
```

Edita `.env` con tus valores:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=RutasDB
DB_USER=postgres
DB_PASSWORD=tu_password_segura
```

### Paso 4: Inicializar Base de Datos

```powershell
python initialize_database.py
```

Este script:
- ✅ Crea la base de datos `RutasDB`
- ✅ Crea todas las tablas con sus relaciones
- ✅ Crea índices para optimización
- ✅ Configura triggers y funciones

### Paso 5: Migrar Datos (Opcional)

Si tienes datos en SQLite:

```powershell
python migrate_data.py
```

### Paso 6: Ejecutar la Aplicación

```powershell
python main.py
```

O directamente con Streamlit:
```powershell
streamlit run src/infrastructure/ui/streamlit_app.py
```

## 🔧 Verificación de la Instalación

### Verificar Conexión PostgreSQL

```powershell
# Conectar con psql
psql -U postgres -d RutasDB

# Ver tablas
\dt

# Ver datos de rutas
SELECT * FROM routes LIMIT 5;

# Salir
\q
```

### Verificar Estructura

```sql
-- Ver todas las tablas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Ver índices
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public';

-- Contar registros
SELECT 
    'routes' as tabla, COUNT(*) as registros FROM routes
UNION ALL
SELECT 'cedis', COUNT(*) FROM cedis
UNION ALL
SELECT 'clientes', COUNT(*) FROM clientes;
```

## 📊 Modelo de Datos

### Diagrama E-R

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│  CEDIS   │       │    RUTAS     │       │ CLIENTES │
├──────────┤       ├──────────────┤       ├──────────┤
│ id (PK)  │───┐   │ id (PK)      │   ┌───│ id (PK)  │
│ nombre   │   └──>│ cedis_id(FK) │   │   │ nombre   │
│ ciudad   │       │ nombre       │   │   │ direccion│
└──────────┘       │ dia_semana   │   │   │ latitud  │
                   │ activa       │   │   │ longitud │
                   └──────┬───────┘   │   └──────────┘
                          │           │
                   ┌──────▼───────────▼──┐
                   │  RUTAS_CLIENTES     │
                   ├─────────────────────┤
                   │ id (PK)             │
                   │ ruta_id (FK)        │
                   │ cliente_id (FK)     │
                   │ orden_visita        │
                   └─────────────────────┘
```

## 🔒 Principios SOLID Aplicados

### Single Responsibility Principle (SRP)
- ✅ `PostgresRouteRepository`: Solo maneja persistencia
- ✅ `RouteService`: Solo lógica de negocio
- ✅ `initialize_database.py`: Solo inicialización

### Open/Closed Principle (OCP)
- ✅ Extensible sin modificar el código existente
- ✅ Se puede agregar nuevo repositorio sin cambiar servicios

### Liskov Substitution Principle (LSP)
- ✅ `PostgresRouteRepository` es completamente intercambiable con `SqliteRouteRepository`
- ✅ Ambos implementan `RouteRepositoryPort`

### Interface Segregation Principle (ISP)
- ✅ `RouteRepositoryPort` define solo métodos necesarios
- ✅ No hay métodos innecesarios en la interfaz

### Dependency Inversion Principle (DIP)
- ✅ Servicios dependen de `RouteRepositoryPort` (abstracción)
- ✅ No dependen de implementaciones concretas
- ✅ Inyección de dependencias en `main.py`

## 🛡️ Ventajas de PostgreSQL

### Sobre SQLite:
1. **Concurrencia**: Múltiples conexiones simultáneas
2. **Integridad**: Constraints y foreign keys robustos
3. **Rendimiento**: Índices avanzados y optimización de consultas
4. **Escalabilidad**: Preparado para millones de registros
5. **Transacciones**: ACID completo
6. **Tipos de datos**: JSON nativo, arrays, etc.
7. **Seguridad**: Control de acceso granular
8. **Backup**: Herramientas profesionales de respaldo

## 🐛 Troubleshooting

### Error: "could not connect to server"

```powershell
# Verificar que PostgreSQL esté corriendo
Get-Service postgresql*

# Iniciar servicio si está detenido
Start-Service postgresql-x64-XX
```

### Error: "database does not exist"

```powershell
# Ejecutar script de inicialización
python initialize_database.py
```

### Error: "authentication failed"

```powershell
# Verificar credenciales en .env
# Revisar pg_hba.conf para configuración de autenticación
```

### Error: "psycopg2 not found"

```powershell
# Reinstalar dependencias
pip install --force-reinstall psycopg2-binary
```

## 📚 Referencias

- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **psycopg2 Documentation**: https://www.psycopg.org/docs/
- **Arquitectura Hexagonal**: https://alistair.cockburn.us/hexagonal-architecture/
- **Principios SOLID**: https://en.wikipedia.org/wiki/SOLID

## 🎯 Próximos Pasos

1. ✅ Migración completada
2. ⏭️ Pruebas de integración
3. ⏭️ Optimización de consultas
4. ⏭️ Implementar pool de conexiones
5. ⏭️ Agregar caché de consultas
6. ⏭️ Configurar replicación (producción)

## 👨‍💻 Mantenimiento

### Backup de Base de Datos

```powershell
# Backup completo
pg_dump -U postgres -d RutasDB -f backup_$(Get-Date -Format "yyyyMMdd").sql

# Restaurar backup
psql -U postgres -d RutasDB -f backup_20250130.sql
```

### Vacío y Análisis

```sql
-- Optimizar tablas
VACUUM ANALYZE routes;
VACUUM ANALYZE rutas;
VACUUM ANALYZE clientes;
```

---

**Autor**: Equipo de Desarrollo Yedistribuciones  
**Fecha**: Enero 2025  
**Versión**: 2.0 - PostgreSQL Migration
