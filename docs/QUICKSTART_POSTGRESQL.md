# 🚀 Guía de Inicio Rápido - PostgreSQL Migration

## ⚡ Instalación Rápida (5 minutos)

### Prerrequisitos
- ✅ Python 3.8 o superior
- ✅ PostgreSQL 12 o superior
- ✅ pip

### Paso 1: Clonar/Descargar el Proyecto
```powershell
cd C:\Users\ASUS\Desktop\2025-2\ARQUITECTURA\Final_arquitectura\yedistribuciones_project
```

### Paso 2: Instalar Dependencias
```powershell
# Opción A: Script automático (Recomendado)
.\install.ps1

# Opción B: Manual
pip install -r requirements.txt
```

### Paso 3: Configurar Variables de Entorno
```powershell
# Copiar archivo de ejemplo
Copy-Item .env.example .env

# Editar .env con tus credenciales
notepad .env
```

**Configuración mínima en .env:**
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=RutasDB
DB_USER=postgres
DB_PASSWORD=tu_password_aqui
```

### Paso 4: Inicializar Base de Datos
```powershell
python initialize_database.py
```

### Paso 5: (Opcional) Migrar Datos de SQLite
```powershell
# Solo si tienes datos previos en SQLite
python migrate_data.py
```

### Paso 6: ¡Ejecutar la Aplicación!
```powershell
python main.py
```

La aplicación abrirá automáticamente en tu navegador: `http://localhost:8501`

---

## 🔧 Solución de Problemas Comunes

### ❌ Error: "psycopg2 not found"
```powershell
pip install --upgrade psycopg2-binary
```

### ❌ Error: "could not connect to server"
```powershell
# Verificar estado de PostgreSQL
Get-Service postgresql*

# Iniciar servicio
Start-Service postgresql-x64-XX
```

### ❌ Error: "database does not exist"
```powershell
# Ejecutar script de inicialización
python initialize_database.py
```

### ❌ Error: "authentication failed"
1. Verifica usuario y contraseña en `.env`
2. Revisa que PostgreSQL permita conexiones locales
3. Edita `pg_hba.conf` si es necesario

---

## 📊 Verificación de Instalación

### Verificar PostgreSQL
```powershell
psql -U postgres -c "SELECT version();"
```

### Verificar Base de Datos
```powershell
psql -U postgres -d RutasDB -c "\dt"
```

### Verificar Conexión desde Python
```powershell
python -c "from config import Config; import psycopg2; conn = psycopg2.connect(**Config.get_db_connection_params()); print('✅ Conexión exitosa'); conn.close()"
```

---

## 📂 Estructura del Proyecto

```
yedistribuciones_project/
├── 📄 main.py                      ← Punto de entrada
├── 📄 config.py                    ← Configuración
├── 📄 initialize_database.py       ← Inicializar BD
├── 📄 migrate_data.py              ← Migrar de SQLite
├── 📄 requirements.txt             ← Dependencias
├── 📄 .env.example                 ← Plantilla de config
├── 📄 install.ps1                  ← Script de instalación
│
├── 📁 src/
│   ├── 📁 domain/                  ← Lógica de negocio
│   │   ├── 📁 models/
│   │   │   ├── route.py
│   │   │   ├── client.py
│   │   │   └── models.py          ← Modelos Django (referencia)
│   │   └── 📁 ports/
│   │       └── route_repository_port.py
│   │
│   ├── 📁 application/             ← Casos de uso
│   │   └── 📁 services/
│   │       ├── route_service.py
│   │       └── route_optimization_service.py
│   │
│   └── 📁 infrastructure/          ← Implementaciones técnicas
│       ├── 📁 persistence/
│       │   ├── postgres_route_repository.py  ✨ NUEVO
│       │   └── sqlite_route_repository.py    (legacy)
│       ├── 📁 services/
│       │   └── google_maps_service.py
│       └── 📁 ui/
│           └── streamlit_app.py
│
└── 📁 README/                      ← Documentación
    ├── MIGRATION_POSTGRESQL.md     ← Guía completa
    └── ARCHITECTURE_HEXAGONAL_POSTGRESQL.md
```

---

## 🎯 Características Principales

### ✅ Migración Completada
- PostgreSQL como base de datos principal
- Arquitectura hexagonal mantenida
- Principios SOLID aplicados
- Tablas según modelo Django

### ✅ Compatibilidad
- Tabla `routes` para sistema actual
- Tablas Django para futuras integraciones
- Mantiene SQLite como opción legacy

### ✅ Optimizaciones
- Índices en consultas frecuentes
- Transacciones ACID
- Context managers para seguridad
- Preparado para pool de conexiones

---

## 🌟 Próximos Pasos

1. **Explorar la aplicación**
   - Crear rutas
   - Asignar clientes
   - Optimizar con Google Maps (si configurado)

2. **Cargar datos de ejemplo**
   ```powershell
   python init_sample_data.py
   ```

3. **Personalizar**
   - Ajustar límites de rutas en `.env`
   - Configurar Google Maps API
   - Personalizar coordenadas CEDIS

4. **Producción**
   - Configurar backup automático
   - Implementar pool de conexiones
   - Configurar replicación (si necesario)

---

## 📚 Documentación Completa

- **Migración**: `README/MIGRATION_POSTGRESQL.md`
- **Arquitectura**: `README/ARCHITECTURE_HEXAGONAL_POSTGRESQL.md`
- **API Google Maps**: `README/GOOGLE_MAPS_INTEGRATION.md`

---

## 🆘 Soporte

### Recursos
- Documentación PostgreSQL: https://www.postgresql.org/docs/
- psycopg2: https://www.psycopg.org/docs/
- Streamlit: https://docs.streamlit.io/

### Comandos Útiles

```powershell
# Ver logs de PostgreSQL
Get-Content "C:\Program Files\PostgreSQL\XX\data\log\*.log" -Tail 50

# Backup de base de datos
pg_dump -U postgres -d RutasDB -f backup.sql

# Restaurar backup
psql -U postgres -d RutasDB -f backup.sql

# Conectar a PostgreSQL
psql -U postgres -d RutasDB

# Ver configuración actual
python config.py
```

---

## ✨ ¡Listo para Usar!

Si todos los pasos se completaron exitosamente, tu sistema está listo para:

- ✅ Gestionar rutas de distribución
- ✅ Optimizar con Google Maps
- ✅ Escalar con PostgreSQL
- ✅ Mantener arquitectura limpia

**¡Disfruta tu sistema de gestión de rutas!** 🚚📦🗺️
