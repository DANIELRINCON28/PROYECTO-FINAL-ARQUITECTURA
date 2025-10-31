# 🚚 Yedistribuciones - Sistema de Gestión de Rutas

## 📋 Descripción

Sistema profesional de gestión y optimización de rutas de distribución con arquitectura hexagonal, base de datos PostgreSQL y optimización mediante Google Maps.

**Versión:** 2.0 - PostgreSQL Migration  
**Arquitectura:** Hexagonal + SOLID  
**Base de Datos:** PostgreSQL 12+  
**Framework UI:** Streamlit  

---

## ✨ Características Principales

### 🗺️ Gestión de Rutas
- ✅ Crear, editar y eliminar rutas de distribución
- ✅ Asignar clientes a rutas con orden de visita
- ✅ Organizar rutas por día de la semana
- ✅ Gestionar múltiples centros de distribución (CEDIS)
- ✅ Activar/desactivar rutas

### 🎯 Optimización Inteligente
- ✅ Optimización de rutas con Google Maps API
- ✅ Cálculo de distancias y tiempos reales
- ✅ Sugerencias de división de rutas largas
- ✅ Métricas de eficiencia

### 👥 Gestión de Personal
- ✅ Registro de vendedores
- ✅ Asignación de rutas a vendedores
- ✅ Seguimiento de estado de asignaciones
- ✅ Histórico de asignaciones

### 🏢 Gestión de Clientes
- ✅ Registro de clientes con geolocalización
- ✅ Múltiples clientes por ruta
- ✅ Visualización en mapa

### 📊 Base de Datos Profesional
- ✅ PostgreSQL con tablas normalizadas
- ✅ Integridad referencial
- ✅ Índices optimizados
- ✅ Transacciones ACID
- ✅ Backup y recuperación

---

## 🏗️ Arquitectura

### Arquitectura Hexagonal (Ports & Adapters)

```
┌─────────────────────────────────────────┐
│      ADAPTADORES CONDUCTORES            │
│      (Streamlit UI)                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     CAPA DE APLICACIÓN                  │
│     (Servicios de Negocio)              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     CAPA DE DOMINIO                     │
│     (Modelos y Puertos)                 │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     ADAPTADORES CONDUCIDOS              │
│     (PostgreSQL, Google Maps)           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     POSTGRESQL - RutasDB                │
└─────────────────────────────────────────┘
```

### Principios SOLID Aplicados ✅
- **Single Responsibility Principle**
- **Open/Closed Principle**
- **Liskov Substitution Principle**
- **Interface Segregation Principle**
- **Dependency Inversion Principle**

---

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.8 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes Python)

### Instalación en 3 Pasos

#### 1. Instalar Dependencias
```powershell
# Opción A: Instalación automática (Recomendado)
.\install.ps1

# Opción B: Instalación manual
pip install -r requirements.txt
```

#### 2. Configurar Base de Datos
```powershell
# Copiar archivo de configuración
Copy-Item .env.example .env

# Editar .env con tus credenciales
notepad .env

# Inicializar base de datos
python initialize_database.py
```

#### 3. Ejecutar Aplicación
```powershell
python main.py
```

La aplicación se abrirá automáticamente en: `http://localhost:8501`

📚 **Guía Completa:** [QUICKSTART_POSTGRESQL.md](QUICKSTART_POSTGRESQL.md)

---

## 📁 Estructura del Proyecto

```
yedistribuciones_project/
│
├── 🚀 main.py                       # Punto de entrada
├── ⚙️  config.py                     # Configuración
├── 📦 requirements.txt              # Dependencias
│
├── 🗄️  initialize_database.py       # Inicializar BD
├── 🔄 migrate_data.py               # Migrar datos SQLite→PostgreSQL
├── 🛠️  install.ps1                   # Script de instalación
├── 📝 .env.example                  # Plantilla de configuración
│
├── 📖 QUICKSTART_POSTGRESQL.md      # Inicio rápido
├── 📊 RESUMEN_MIGRACION.md          # Resumen de migración
├── 📋 INDICE_MIGRACION.md           # Índice completo
│
├── 📁 src/
│   ├── 📁 domain/                   # Lógica de negocio pura
│   │   ├── 📁 models/
│   │   │   ├── route.py
│   │   │   ├── client.py
│   │   │   └── models.py           # Modelos Django (referencia)
│   │   └── 📁 ports/
│   │       ├── route_repository_port.py
│   │       └── route_optimization_port.py
│   │
│   ├── 📁 application/              # Casos de uso
│   │   └── 📁 services/
│   │       ├── route_service.py
│   │       └── route_optimization_service.py
│   │
│   └── 📁 infrastructure/           # Implementaciones técnicas
│       ├── 📁 persistence/
│       │   ├── postgres_route_repository.py  ← PostgreSQL
│       │   └── sqlite_route_repository.py    (legacy)
│       ├── 📁 services/
│       │   └── google_maps_service.py
│       └── 📁 ui/
│           └── streamlit_app.py
│
└── 📁 README/
    ├── MIGRATION_POSTGRESQL.md              # Guía de migración
    ├── ARCHITECTURE_HEXAGONAL_POSTGRESQL.md # Arquitectura
    ├── DATABASE_SCHEMA.md                   # Esquema de BD
    ├── GOOGLE_MAPS_INTEGRATION.md           # Integración Maps
    └── ...otros documentos
```

---

## 🗄️ Base de Datos

### Tablas Principales

| Tabla | Descripción | Registros |
|-------|-------------|-----------|
| **cedis** | Centros de distribución | ~10 |
| **vendedores** | Personal de ventas | ~50 |
| **clientes** | Clientes con geolocalización | ~1,000 |
| **rutas** | Rutas de distribución | ~100 |
| **rutas_clientes** | Relación rutas-clientes (N:M) | ~2,000 |
| **asignaciones_rutas** | Asignaciones a vendedores | ~10,000 |
| **routes** | Tabla de compatibilidad | ~100 |

### Características de BD
- ✅ Foreign Keys con políticas de eliminación
- ✅ Índices optimizados para consultas frecuentes
- ✅ Triggers para actualización automática
- ✅ Constraints de integridad
- ✅ Tipos de datos avanzados (JSONB)

📊 **Esquema Completo:** [README/DATABASE_SCHEMA.md](README/DATABASE_SCHEMA.md)

---

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` con:

```env
# Base de Datos PostgreSQL (Requerido)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=RutasDB
DB_USER=postgres
DB_PASSWORD=tu_password

# Google Maps API (Opcional - Para optimización)
GOOGLE_MAPS_API_KEY=tu_api_key

# Ubicación CEDIS (Opcional)
CEDIS_LATITUDE=4.7110
CEDIS_LONGITUDE=-74.0721
CEDIS_ADDRESS=Bogotá, Colombia
```

Plantilla completa: [.env.example](.env.example)

---

## 🛠️ Scripts Útiles

### Inicialización
```powershell
# Crear estructura de base de datos
python initialize_database.py

# Verificar configuración
python config.py
```

### Migración (Si vienes de SQLite)
```powershell
# Migrar datos de SQLite a PostgreSQL
python migrate_data.py
```

### Desarrollo
```powershell
# Ejecutar aplicación
python main.py

# Ejecutar con Streamlit directamente
streamlit run src/infrastructure/ui/streamlit_app.py

# Ejecutar tests (si disponibles)
pytest tests/
```

### Base de Datos
```powershell
# Conectar a PostgreSQL
psql -U postgres -d RutasDB

# Ver tablas
psql -U postgres -d RutasDB -c "\dt"

# Backup
pg_dump -U postgres -d RutasDB -f backup.sql

# Restaurar
psql -U postgres -d RutasDB -f backup.sql
```

---

## 📚 Documentación Completa

### Para Empezar
- 🚀 [Inicio Rápido](QUICKSTART_POSTGRESQL.md) - Empieza en 5 minutos
- 📋 [Resumen de Migración](RESUMEN_MIGRACION.md) - Visión general
- 📊 [Índice Completo](INDICE_MIGRACION.md) - Todos los archivos

### Para Desarrolladores
- 🏗️ [Arquitectura Hexagonal](README/ARCHITECTURE_HEXAGONAL_POSTGRESQL.md)
- 🗄️ [Esquema de Base de Datos](README/DATABASE_SCHEMA.md)
- 🗺️ [Integración Google Maps](README/GOOGLE_MAPS_INTEGRATION.md)

### Para Administradores
- 🔄 [Guía de Migración](README/MIGRATION_POSTGRESQL.md)
- ⚙️ [Configuración Avanzada](config.py)

---

## 🔧 Troubleshooting

### Error: "psycopg2 not found"
```powershell
pip install --upgrade psycopg2-binary
```

### Error: "could not connect to server"
```powershell
# Verificar PostgreSQL
Get-Service postgresql*

# Iniciar servicio
Start-Service postgresql-x64-XX
```

### Error: "database does not exist"
```powershell
python initialize_database.py
```

### Error: "authentication failed"
1. Verifica credenciales en `.env`
2. Confirma que PostgreSQL permite conexiones locales
3. Revisa `pg_hba.conf` si es necesario

Más soluciones: [QUICKSTART_POSTGRESQL.md](QUICKSTART_POSTGRESQL.md#solución-de-problemas-comunes)

---

## 🎯 Casos de Uso

### 1. Crear una Nueva Ruta
```python
# En la interfaz Streamlit
1. Ir a "Gestión de Rutas"
2. Click en "Crear Nueva Ruta"
3. Completar formulario
4. Seleccionar clientes
5. Guardar
```

### 2. Optimizar Ruta con Google Maps
```python
# Requiere GOOGLE_MAPS_API_KEY configurada
1. Seleccionar ruta existente
2. Click en "Optimizar Ruta"
3. Revisar sugerencias
4. Aplicar optimización
```

### 3. Asignar Ruta a Vendedor
```python
1. Ir a "Asignaciones"
2. Seleccionar fecha
3. Seleccionar ruta
4. Asignar vendedor
5. Confirmar
```

---

## 🌟 Ventajas de PostgreSQL

| Característica | SQLite | PostgreSQL |
|----------------|--------|------------|
| **Concurrencia** | Limitada | ✅ Multi-usuario |
| **Integridad** | Básica | ✅ Foreign Keys robustos |
| **Escalabilidad** | Pequeña | ✅ Enterprise |
| **Transacciones** | Básicas | ✅ ACID completo |
| **Tipos de datos** | Limitados | ✅ JSONB, Arrays, GIS |
| **Índices** | Básicos | ✅ GIN, GIST, Parciales |
| **Replicación** | No | ✅ Streaming replication |
| **Backup** | Archivo | ✅ Herramientas pro |

---

## 🚧 Roadmap

### Versión Actual (2.0) ✅
- [x] Migración a PostgreSQL
- [x] Arquitectura hexagonal
- [x] Optimización con Google Maps
- [x] Interfaz Streamlit

### Próximas Versiones
- [ ] Pool de conexiones
- [ ] Caché de consultas
- [ ] API REST
- [ ] Aplicación móvil
- [ ] Dashboard analytics
- [ ] Notificaciones en tiempo real

---

## 👥 Contribuir

Este proyecto sigue principios de arquitectura limpia. Para contribuir:

1. Fork del repositorio
2. Crear branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

### Guías de Estilo
- Seguir principios SOLID
- Mantener arquitectura hexagonal
- Documentar cambios
- Incluir tests

---

## 📄 Licencia

Este proyecto es software propietario de Yedistribuciones.

---

## 🆘 Soporte

### Recursos
- 📖 Documentación PostgreSQL: https://www.postgresql.org/docs/
- 📖 psycopg2: https://www.psycopg.org/docs/
- 📖 Streamlit: https://docs.streamlit.io/
- 📖 Google Maps API: https://developers.google.com/maps/documentation

### Contacto
Para soporte técnico, consulta la documentación completa en la carpeta `README/`.

---

## 🎉 Estado del Proyecto

```
✅ Arquitectura:       Hexagonal + SOLID
✅ Base de Datos:      PostgreSQL 12+
✅ Frontend:           Streamlit
✅ Optimización:       Google Maps API
✅ Documentación:      Completa
✅ Scripts:            Automatizados
✅ Estado:             Producción Ready
```

---

**Versión:** 2.0 - PostgreSQL Migration  
**Última Actualización:** Enero 2025  
**Desarrollado con:** ❤️ y Arquitectura Limpia  

🚚 **¡Gestiona tus rutas de distribución de manera profesional!** 📦🗺️
