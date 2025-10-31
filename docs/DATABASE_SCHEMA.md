# 🗄️ DIAGRAMA DE BASE DE DATOS - RutasDB

## Esquema Completo de PostgreSQL

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        BASE DE DATOS: RutasDB                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─────────────────────────────────────────────────────────────────────────┐
│                         TABLA: cedis                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ 🔑 id                    SERIAL PRIMARY KEY                            │
│ 📝 nombre                VARCHAR(100) NOT NULL                         │
│ 📍 ciudad                VARCHAR(100) NOT NULL                         │
│ 📅 fecha_creacion        TIMESTAMP WITH TIME ZONE DEFAULT NOW()       │
│                                                                         │
│ 🔒 CONSTRAINT: UNIQUE(nombre, ciudad)                                  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ 1:N
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                         TABLA: rutas                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ 🔑 id                         SERIAL PRIMARY KEY                       │
│ 🏷️  identificador_unico       VARCHAR(50) NOT NULL UNIQUE              │
│ 📝 nombre_descriptivo         VARCHAR(150) NOT NULL                    │
│ 📆 dia_semana                 SMALLINT CHECK (1-7)                     │
│ ✅ activa                     BOOLEAN DEFAULT TRUE                     │
│ 🔗 cedis_id                   INTEGER FK → cedis(id)                   │
│ 📅 fecha_creacion             TIMESTAMP WITH TIME ZONE DEFAULT NOW()  │
│                                                                         │
│ 🔒 FOREIGN KEY: cedis_id REFERENCES cedis(id) ON DELETE RESTRICT      │
│ 📊 INDEX: idx_rutas_dia_cedis(dia_semana, cedis_id)                   │
│ 📊 INDEX: idx_rutas_activa(activa)                                     │
└─────────────────┬──────────────────────────────────┬────────────────────┘
                  │                                  │
                  │ 1:N                              │ 1:N
                  │                                  │
┌─────────────────▼──────────────────────┐  ┌────────▼────────────────────┐
│     TABLA: rutas_clientes              │  │  TABLA: asignaciones_rutas  │
├────────────────────────────────────────┤  ├─────────────────────────────┤
│ 🔑 id            SERIAL PRIMARY KEY    │  │ 🔑 id        SERIAL PK      │
│ 🔗 ruta_id       INTEGER FK → rutas   │  │ 📅 fecha      DATE NOT NULL │
│ 🔗 cliente_id    INTEGER FK → clientes│  │ 🔗 ruta_id    INT FK →rutas│
│ 🔢 orden_visita  INTEGER NOT NULL     │  │ 🔗 vendedor_id INT FK →vend│
│                                        │  │ 📊 estado     VARCHAR(50)   │
│ 🔒 UNIQUE(ruta_id, cliente_id)        │  │              DEFAULT 'Pend' │
│ 🔒 UNIQUE(ruta_id, orden_visita)      │  │                             │
│ 🔒 FK: ruta_id → rutas CASCADE        │  │ 🔒 UNIQUE(fecha, ruta_id)   │
│ 🔒 FK: cliente_id → clientes RESTRICT │  │ 🔒 CHECK: estado IN (...)   │
│ 📊 INDEX: (ruta_id, orden_visita)     │  │ 📊 INDEX: (fecha, vendedor) │
└────────────────┬───────────────────────┘  │ 📊 INDEX: (fecha, ruta)     │
                 │                           │ 📊 INDEX: (estado)          │
                 │ N:1                       └──────────────┬──────────────┘
                 │                                          │
┌────────────────▼────────────────────────┐                │ N:1
│        TABLA: clientes                  │                │
├─────────────────────────────────────────┤  ┌─────────────▼─────────────┐
│ 🔑 id                 SERIAL PK         │  │   TABLA: vendedores       │
│ 🏢 nombre_comercial   VARCHAR(200)      │  ├───────────────────────────┤
│ 📍 direccion          TEXT NOT NULL     │  │ 🔑 id             SERIAL  │
│ 🌍 latitud            NUMERIC(9,6)      │  │ 👤 nombre_completo V(150) │
│ 🌍 longitud           NUMERIC(9,6)      │  │ 🏷️  codigo_empleado V(50) │
│ 📅 fecha_creacion     TIMESTAMP         │  │                  UNIQUE    │
│                                         │  │ 📅 fecha_creacion         │
└─────────────────────────────────────────┘  └───────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────┐
│            TABLA: routes (Compatibilidad con sistema actual)            │
├──────────────────────────────────────────────────────────────────────────┤
│ 🔑 id               VARCHAR(100) PRIMARY KEY                            │
│ 📝 name             VARCHAR(150) NOT NULL                               │
│ 🔗 cedis_id         VARCHAR(50) NOT NULL                                │
│ 📆 day_of_week      VARCHAR(20) NOT NULL                                │
│ 📋 client_ids       JSONB NOT NULL DEFAULT '[]'::jsonb                  │
│ ✅ is_active         BOOLEAN NOT NULL DEFAULT TRUE                       │
│ 📅 created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()             │
│ 🔄 updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()             │
│                                                                          │
│ 📊 INDEX: idx_routes_cedis_day(cedis_id, day_of_week)                   │
│ 📊 INDEX: idx_routes_active(is_active)                                  │
│ 📊 INDEX GIN: idx_routes_client_ids_gin(client_ids)                     │
│ 🔧 TRIGGER: update_routes_updated_at                                    │
└──────────────────────────────────────────────────────────────────────────┘
```

## 📊 Relaciones Detalladas

### 1. CEDIS → RUTAS (1:N)
```sql
cedis.id ─────────> rutas.cedis_id
  (1)                    (N)

Un CEDIS puede tener múltiples rutas
Una ruta pertenece a un solo CEDIS
ON DELETE RESTRICT: No se puede eliminar un CEDIS con rutas activas
```

### 2. RUTAS ↔ CLIENTES (N:M a través de rutas_clientes)
```sql
rutas.id ─────────> rutas_clientes.ruta_id
                           │
clientes.id ───────────────┘
                    rutas_clientes.cliente_id

Una ruta puede tener múltiples clientes (en orden)
Un cliente puede estar en múltiples rutas
rutas_clientes.orden_visita: Define secuencia de visitas
```

### 3. RUTAS → ASIGNACIONES → VENDEDORES (N:M a través de asignaciones_rutas)
```sql
rutas.id ───────────> asignaciones_rutas.ruta_id
                             │
vendedores.id ───────────────┘
                      asignaciones_rutas.vendedor_id

Una ruta puede ser asignada a diferentes vendedores en diferentes fechas
Un vendedor puede tener múltiples asignaciones
asignaciones_rutas.fecha: Fecha de la asignación
asignaciones_rutas.estado: Seguimiento del progreso
```

## 🔐 Constraints e Integridad

### Primary Keys
```sql
✅ cedis.id                     SERIAL
✅ vendedores.id                SERIAL
✅ clientes.id                  SERIAL
✅ rutas.id                     SERIAL
✅ rutas_clientes.id            SERIAL
✅ asignaciones_rutas.id        SERIAL
✅ routes.id                    VARCHAR(100)
```

### Foreign Keys con Políticas de Eliminación

```sql
rutas.cedis_id → cedis.id
  ON DELETE RESTRICT
  ❌ No permite eliminar CEDIS si tiene rutas

rutas_clientes.ruta_id → rutas.id
  ON DELETE CASCADE
  ✅ Elimina automáticamente relaciones al eliminar ruta

rutas_clientes.cliente_id → clientes.id
  ON DELETE RESTRICT
  ❌ No permite eliminar cliente si está en rutas

asignaciones_rutas.ruta_id → rutas.id
  ON DELETE RESTRICT
  ❌ No permite eliminar ruta si tiene asignaciones

asignaciones_rutas.vendedor_id → vendedores.id
  ON DELETE RESTRICT
  ❌ No permite eliminar vendedor si tiene asignaciones
```

### Unique Constraints

```sql
✅ cedis: UNIQUE(nombre, ciudad)
   → No duplicar centros de distribución

✅ vendedores: UNIQUE(codigo_empleado)
   → Código de empleado único

✅ rutas: UNIQUE(identificador_unico)
   → ID de ruta único

✅ rutas_clientes: UNIQUE(ruta_id, cliente_id)
   → Un cliente solo aparece una vez por ruta

✅ rutas_clientes: UNIQUE(ruta_id, orden_visita)
   → No duplicar orden de visita en una ruta

✅ asignaciones_rutas: UNIQUE(fecha, ruta_id)
   → Una ruta solo se asigna una vez por día

✅ routes: PRIMARY KEY(id)
   → ID único para compatibilidad
```

### Check Constraints

```sql
✅ rutas.dia_semana: CHECK (dia_semana >= 1 AND dia_semana <= 7)
   → Solo días válidos (1=Lunes, 7=Domingo)

✅ asignaciones_rutas.estado: CHECK (estado IN ('Pendiente', 'En Progreso', 'Completada', 'Cancelada'))
   → Solo estados permitidos
```

## 📈 Índices de Rendimiento

### Índices en rutas
```sql
📊 idx_rutas_dia_cedis(dia_semana, cedis_id)
   → Consultas: "Rutas del CEDIS X para el día Y"
   
📊 idx_rutas_activa(activa)
   → Filtrar rutas activas/inactivas rápidamente
```

### Índices en rutas_clientes
```sql
📊 idx_rutas_clientes_ruta_orden(ruta_id, orden_visita)
   → Obtener clientes de una ruta en orden
```

### Índices en asignaciones_rutas
```sql
📊 idx_asignaciones_fecha_vendedor(fecha, vendedor_id)
   → Consultas: "Asignaciones del vendedor X en fecha Y"
   
📊 idx_asignaciones_fecha_ruta(fecha, ruta_id)
   → Consultas: "Asignación de ruta X en fecha Y"
   
📊 idx_asignaciones_estado(estado)
   → Filtrar por estado de asignación
```

### Índices en routes (compatibilidad)
```sql
📊 idx_routes_cedis_day(cedis_id, day_of_week)
   → Compatibilidad con consultas existentes
   
📊 idx_routes_active(is_active)
   → Filtrar rutas activas
   
📊 idx_routes_client_ids_gin(client_ids) USING GIN
   → Búsqueda eficiente en array JSON de clientes
```

## 🔄 Triggers y Funciones

### Función: update_updated_at_column()
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';
```

### Trigger: Actualizar updated_at automáticamente
```sql
CREATE TRIGGER update_routes_updated_at
    BEFORE UPDATE ON routes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## 🎯 Casos de Uso Comunes

### 1. Obtener todas las rutas de un CEDIS en un día específico
```sql
SELECT r.*, c.nombre as cedis_nombre
FROM rutas r
JOIN cedis c ON r.cedis_id = c.id
WHERE r.cedis_id = 1 
  AND r.dia_semana = 1  -- Lunes
  AND r.activa = TRUE
ORDER BY r.nombre_descriptivo;
```

### 2. Obtener clientes de una ruta en orden de visita
```sql
SELECT c.*, rc.orden_visita
FROM clientes c
JOIN rutas_clientes rc ON c.id = rc.cliente_id
WHERE rc.ruta_id = 1
ORDER BY rc.orden_visita;
```

### 3. Obtener asignaciones de un vendedor para hoy
```sql
SELECT r.*, ar.estado, ar.fecha
FROM asignaciones_rutas ar
JOIN rutas r ON ar.ruta_id = r.id
JOIN vendedores v ON ar.vendedor_id = v.id
WHERE v.codigo_empleado = 'VEN001'
  AND ar.fecha = CURRENT_DATE;
```

### 4. Estadísticas de rutas por CEDIS
```sql
SELECT 
    c.nombre as cedis,
    COUNT(r.id) as total_rutas,
    SUM(CASE WHEN r.activa THEN 1 ELSE 0 END) as rutas_activas,
    COUNT(DISTINCT rc.cliente_id) as total_clientes
FROM cedis c
LEFT JOIN rutas r ON c.id = r.cedis_id
LEFT JOIN rutas_clientes rc ON r.id = rc.ruta_id
GROUP BY c.id, c.nombre
ORDER BY total_rutas DESC;
```

## 💾 Tamaño Estimado de Datos

```
┌────────────────────┬─────────────┬──────────────┐
│ Tabla              │ Registros   │ Tamaño       │
├────────────────────┼─────────────┼──────────────┤
│ cedis              │ ~10         │ < 1 MB       │
│ vendedores         │ ~50         │ < 1 MB       │
│ clientes           │ ~1,000      │ ~5 MB        │
│ rutas              │ ~100        │ ~1 MB        │
│ rutas_clientes     │ ~2,000      │ ~10 MB       │
│ asignaciones_rutas │ ~10,000     │ ~50 MB       │
│ routes             │ ~100        │ ~2 MB        │
├────────────────────┼─────────────┼──────────────┤
│ TOTAL              │             │ ~70 MB       │
└────────────────────┴─────────────┴──────────────┘

* Estimaciones para sistema mediano
* Con índices: ~140 MB
* Con WAL y overhead: ~200 MB
```

## 🚀 Rendimiento Esperado

```
┌────────────────────────────────┬──────────────┐
│ Operación                      │ Tiempo       │
├────────────────────────────────┼──────────────┤
│ SELECT ruta por ID             │ < 1 ms       │
│ SELECT rutas activas (100)     │ < 5 ms       │
│ SELECT clientes de ruta (20)   │ < 2 ms       │
│ INSERT nueva ruta              │ < 5 ms       │
│ UPDATE ruta                    │ < 5 ms       │
│ JOIN complejo (estadísticas)   │ < 50 ms      │
│ Búsqueda GIN en JSON           │ < 10 ms      │
└────────────────────────────────┴──────────────┘

* Con índices optimizados
* Base de datos en SSD
* Sin carga concurrente alta
```

---

**Documentación Completa:** README/MIGRATION_POSTGRESQL.md  
**Arquitectura:** README/ARCHITECTURE_HEXAGONAL_POSTGRESQL.md
