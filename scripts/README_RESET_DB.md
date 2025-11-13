# 🔄 Reset y Población de Base de Datos

Script para limpiar completamente y repoblar la base de datos PostgreSQL con datos coherentes y realistas.

---

## 📋 Problema que Resuelve

- ❌ Rutas de "Bogotá Sur" asignadas a CEDIS de otras ciudades
- ❌ Clientes asignados a rutas de ciudades incorrectas
- ❌ Datos inconsistentes o de prueba mezclados
- ❌ Secuencias de IDs desincronizadas

## ✅ Solución

Este script:
1. **Limpia** todas las tablas respetando foreign keys
2. **Reinicia** secuencias de IDs a 1
3. **Pobla** con datos coherentes:
   - CEDIS organizados por ciudad
   - Clientes con coordenadas reales
   - Rutas asignadas al CEDIS correcto de su ciudad
   - Vendedores realistas
   - Asignaciones de ejemplo

---

## 🗄️ Datos que se Crearán

### CEDIS (8 centros)
```
Bogotá (3):
├── CEDIS Bogotá Centro
├── CEDIS Bogotá Norte
└── CEDIS Bogotá Sur

Medellín (2):
├── CEDIS Medellín Centro
└── CEDIS Medellín Norte

Cali (2):
├── CEDIS Cali Centro
└── CEDIS Cali Sur

Barranquilla (1):
└── CEDIS Barranquilla Centro
```

### Clientes (33 clientes)
```
Bogotá: 15 clientes
├── Almacén Éxito Centro
├── Carrefour Calle 100
├── D1 Chapinero
├── Makro Bogotá Norte
└── ... (11 más)

Medellín: 8 clientes
├── Éxito Envigado
├── Carrefour Laureles
└── ... (6 más)

Cali: 6 clientes
├── Éxito Chipichape
└── ... (5 más)

Barranquilla: 4 clientes
├── Éxito Barranquilla Centro
└── ... (3 más)
```

### Rutas (11 rutas)
```
Bogotá:
├── RUTA_BOG_CENTRO_01 (Lunes) → 3 clientes
├── RUTA_BOG_CENTRO_02 (Martes) → 2 clientes
├── RUTA_BOG_NORTE_01 (Lunes) → 3 clientes
├── RUTA_BOG_NORTE_02 (Martes) → 2 clientes
├── RUTA_BOG_SUR_01 (Miércoles) → 3 clientes
└── RUTA_BOG_SUR_02 (Jueves) → 2 clientes

Medellín:
├── RUTA_MED_CENTRO_01 (Lunes) → 4 clientes
└── RUTA_MED_NORTE_01 (Martes) → 4 clientes

Cali:
├── RUTA_CALI_CENTRO_01 (Miércoles) → 3 clientes
└── RUTA_CALI_SUR_01 (Jueves) → 3 clientes

Barranquilla:
└── RUTA_BAQ_CENTRO_01 (Viernes) → 4 clientes
```

### Vendedores (8 vendedores)
```
VEN-001: Juan Carlos Pérez
VEN-002: María Fernanda Gómez
VEN-003: Carlos Andrés Rodríguez
VEN-004: Ana Lucía Martínez
VEN-005: Diego Alejandro López
VEN-006: Laura Sofía Ramírez
VEN-007: Miguel Ángel Torres
VEN-008: Camila Andrea Sánchez
```

### Asignaciones (5 ejemplos)
```
RUTA_BOG_CENTRO_01 → VEN-001 (Completada)
RUTA_BOG_NORTE_01 → VEN-002 (En Progreso)
RUTA_MED_CENTRO_01 → VEN-003 (Pendiente)
RUTA_CALI_CENTRO_01 → VEN-004 (Pendiente)
RUTA_BAQ_CENTRO_01 → VEN-005 (Pendiente)
```

---

## 🚀 Cómo Ejecutar

### Opción 1: Directamente con Python

```powershell
python scripts/reset_and_populate_db.py
```

### Opción 2: Desde el directorio scripts

```powershell
cd scripts
python reset_and_populate_db.py
cd ..
```

---

## 📊 Output Esperado

```
======================================================================
🔄 RESET Y POBLACIÓN DE BASE DE DATOS
======================================================================

🔌 Conectando a PostgreSQL...
✅ Conectado a RutasDB@localhost

🗑️  Limpiando base de datos...
  ✅ Tabla 'asignaciones_rutas' limpiada
  ✅ Tabla 'rutas_clientes' limpiada
  ✅ Tabla 'rutas' limpiada
  ✅ Tabla 'clientes' limpiada
  ✅ Tabla 'cedis' limpiada
  ✅ Tabla 'vendedores' limpiada
  🔄 Secuencia 'cedis_id_seq' reiniciada
  ...
✅ Base de datos limpiada exitosamente

📦 Poblando CEDIS...
  ✅ CEDIS Bogotá Centro (ID: 1)
  ✅ CEDIS Bogotá Norte (ID: 2)
  ...
✅ 8 CEDIS creados

👥 Poblando Clientes...
  ✅ Almacén Éxito Centro (ID: 1)
  ✅ Carrefour Calle 100 (ID: 2)
  ...
✅ 33 Clientes creados

👨‍💼 Poblando Vendedores...
  ✅ Juan Carlos Pérez (VEN-001) - ID: 1
  ...
✅ 8 Vendedores creados

🚚 Poblando Rutas...
  ✅ Ruta Bogotá Centro - Lunes (ID: 1)
     └─ Cliente ID 1 en orden 1
     └─ Cliente ID 2 en orden 2
     └─ Cliente ID 3 en orden 3
  ...
✅ 11 Rutas creadas con clientes asignados

📋 Poblando Asignaciones de Rutas...
  ✅ RUTA_BOG_CENTRO_01 → VEN-001 (Completada)
  ...
✅ 5 Asignaciones creadas

======================================================================
✅ BASE DE DATOS POBLADA EXITOSAMENTE
======================================================================

📊 Resumen:
  • CEDIS: 8
  • Clientes: 33
  • Vendedores: 8
  • Rutas: 11
  • Asignaciones: 5

🚀 Puedes iniciar la aplicación Flask ahora:
   python main_flask.py
```

---

## ⚙️ Requisitos

- Python 3.11+
- PostgreSQL 15+ corriendo
- Base de datos `RutasDB` creada
- `config.py` con credenciales correctas:
  ```python
  DB_HOST = 'localhost'
  DB_PORT = '5432'
  DB_NAME = 'RutasDB'
  DB_USER = 'postgres'
  DB_PASSWORD = 'tu_password'
  ```

---

## 🔍 Verificar Resultados

### En pgAdmin

```sql
-- Ver CEDIS
SELECT * FROM cedis ORDER BY id;

-- Ver clientes por ciudad (primeras palabras de dirección)
SELECT id, nombre_comercial, direccion 
FROM clientes 
ORDER BY direccion;

-- Ver rutas con su CEDIS
SELECT r.identificador_unico, r.nombre_descriptivo, c.nombre as cedis
FROM rutas r
JOIN cedis c ON c.id = r.cedis_id
ORDER BY r.identificador_unico;

-- Ver coherencia: rutas de Bogotá con CEDIS de Bogotá
SELECT 
    r.identificador_unico, 
    r.nombre_descriptivo, 
    c.nombre as cedis,
    c.ciudad
FROM rutas r
JOIN cedis c ON c.id = r.cedis_id
WHERE r.identificador_unico LIKE 'RUTA_BOG%'
ORDER BY r.identificador_unico;

-- Contar clientes por ruta
SELECT r.identificador_unico, COUNT(rc.cliente_id) as num_clientes
FROM rutas r
LEFT JOIN rutas_clientes rc ON rc.ruta_id = r.id
GROUP BY r.identificador_unico
ORDER BY r.identificador_unico;
```

---

## ⚠️ Advertencias

### ❌ ESTO BORRARÁ TODOS LOS DATOS

Este script elimina **TODOS** los datos de las siguientes tablas:
- `asignaciones_rutas`
- `rutas_clientes`
- `rutas`
- `clientes`
- `cedis`
- `vendedores`

### 🔒 Recomendación para Producción

Si estás en producción y quieres hacer backup:

```powershell
# Hacer backup antes de limpiar
pg_dump -U postgres -d RutasDB -F c -f backup_antes_reset.backup

# Ejecutar script
python scripts/reset_and_populate_db.py

# Si algo sale mal, restaurar:
pg_restore -U postgres -d RutasDB -c backup_antes_reset.backup
```

---

## 🎯 Coherencia Garantizada

### ✅ Rutas de Bogotá → CEDIS de Bogotá
```
RUTA_BOG_CENTRO_01 → CEDIS Bogotá Centro
RUTA_BOG_NORTE_02 → CEDIS Bogotá Norte
RUTA_BOG_SUR_01 → CEDIS Bogotá Sur
```

### ✅ Clientes de Bogotá → Rutas de Bogotá
```
Almacén Éxito Centro (Bogotá) → RUTA_BOG_CENTRO_01
Carrefour Calle 100 (Bogotá) → RUTA_BOG_CENTRO_01
```

### ✅ Sin Mezclas de Ciudades
- ❌ **ANTES:** "RUTA_BOG_SUR_01" con CEDIS de Medellín
- ✅ **DESPUÉS:** "RUTA_BOG_SUR_01" con "CEDIS Bogotá Sur"

---

## 🐛 Troubleshooting

### Error: "could not connect to server"
```
Solución: Verifica que PostgreSQL esté corriendo
• Windows: Busca "Services" → "PostgreSQL"
• Asegúrate de que config.py tenga las credenciales correctas
```

### Error: "relation does not exist"
```
Solución: Verifica que las tablas existan
• Ejecuta las migraciones de Django primero
• O crea el esquema manualmente con el SQL del modelo
```

### Error: "foreign key constraint"
```
Solución: El script ya maneja esto correctamente
• Elimina en orden: hijos → padres
• Si persiste, revisa que no haya constraints adicionales
```

---

## 📚 Archivos Relacionados

- `scripts/reset_and_populate_db.py` - Este script
- `src/domain/models/models.py` - Modelos Django
- `config.py` - Configuración de BD
- `docs/DATABASE_SCHEMA.md` - Documentación del esquema

---

## ✅ Después de Ejecutar

1. **Reinicia Flask:**
   ```powershell
   python main_flask.py
   ```

2. **Verifica en la UI:**
   - http://localhost:5000
   - Dashboard debe mostrar 11 rutas
   - Ver Rutas debe listar todas coherentemente
   - Gestionar Clientes debe mostrar disponibles sin ruta

3. **Prueba funcionalidad:**
   - ✅ Crear nueva ruta
   - ✅ Asignar clientes a ruta
   - ✅ Eliminar clientes de ruta
   - ✅ Reordenar clientes
   - ✅ Dividir ruta
   - ✅ Fusionar rutas

---

**Script generado:** 13/Nov/2025  
**Autor:** GitHub Copilot + Usuario  
**Versión:** 1.0.0  
**Estado:** ✅ Listo para usar
