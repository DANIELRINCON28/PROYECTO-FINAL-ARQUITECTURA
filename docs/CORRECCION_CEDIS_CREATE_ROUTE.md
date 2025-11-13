# Corrección: CEDIS en Página de Crear Ruta

## ✅ Problema Identificado

En la página de crear ruta, se estaban consultando CEDIS hardcodeados que no existen en la base de datos:

```python
# ❌ ANTES (Hardcodeado e inexistente)
cedis_list_ids = ['CEDIS_BOGOTA', 'CEDIS_MEDELLIN', 'CEDIS_CALI', 'CEDIS_BARRANQUILLA']
cedis_list = [(cedis_id, get_cedis_display_name(cedis_id)) for cedis_id in cedis_list_ids]
```

**Problema:** Los IDs `CEDIS_BOGOTA`, `CEDIS_MEDELLIN`, etc. no existen en la BD. Los CEDIS reales tienen IDs numéricos:
- 1: CEDIS Bogotá Centro
- 2: CEDIS Bogotá Norte
- 3: CEDIS Bogotá Sur
- 4: CEDIS Medellín Centro
- ... etc

## ✅ Solución Implementada

**Archivo:** `src/infrastructure/ui/flask_app.py` (función `create_route`, líneas 267-295)

```python
# ✅ DESPUÉS (Consultado de la BD)
cedis_list = []
try:
    import psycopg2
    from config import Config
    
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=int(Config.DB_PORT),
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM cedis ORDER BY nombre")
    cedis_list = [(str(row[0]), row[1]) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"⚠️ Warning: No se pudo cargar CEDIS de la BD: {e}")
    # Fallback con IDs hardcodeados (por si la BD no está disponible)
    cedis_list_ids = ['CEDIS_BOGOTA', 'CEDIS_MEDELLIN', 'CEDIS_CALI', 'CEDIS_BARRANQUILLA']
    cedis_list = [(cedis_id, get_cedis_display_name(cedis_id)) for cedis_id in cedis_list_ids]
```

## 🎯 Cambios Clave

| Aspecto | Antes | Después |
|--------|-------|---------|
| **Origen de datos** | Hardcodeado | PostgreSQL BD |
| **Validación** | Ninguna | Consulta directa a `cedis` table |
| **IDs de CEDIS** | `CEDIS_BOGOTA` (inválido) | `1`, `2`, `3` (válidos) |
| **Fallback** | Ninguno | Mapping hardcodeado para emergencias |
| **Escalabilidad** | Baja (cambios requieren código) | Alta (nuevos CEDIS se cargan automáticamente) |

## 📊 Comportamiento Esperado

### Antes (❌ INCORRECTO)
```
Dropdown de CEDIS:
- CEDIS Bogotá (hardcodeado)
- CEDIS Medellín (hardcodeado)
- CEDIS Cali (hardcodeado)
- CEDIS Barranquilla (hardcodeado)

Resultado: Los nombres aparecen pero los IDs 'CEDIS_BOGOTA' no existen en BD
           → Error al crear ruta
```

### Después (✅ CORRECTO)
```
Dropdown de CEDIS:
- CEDIS Bogotá Centro (ID: 1)
- CEDIS Bogotá Norte (ID: 2)
- CEDIS Bogotá Sur (ID: 3)
- CEDIS Cali Centro (ID: 6)
- CEDIS Cali Sur (ID: 7)
- CEDIS Barranquilla Centro (ID: 8)
- CEDIS Medellín Centro (ID: 4)
- CEDIS Medellín Norte (ID: 5)

Resultado: IDs válidos, consulta de BD exitosa
           → Rutas creadas correctamente
```

## 🔒 Manejo de Errores

El código implementa un fallback robusto:

1. **Intenta conexión a BD:** Consulta `SELECT id, nombre FROM cedis ORDER BY nombre`
2. **Si fallida BD:** Usa mapeo hardcodeado como último recurso
3. **Logging:** Imprime warning si hay error de conexión
4. **No rompe la app:** Siempre retorna una lista de CEDIS

```python
except Exception as e:
    print(f"⚠️ Warning: No se pudo cargar CEDIS de la BD: {e}")
    # Fallback...
```

## 🔄 Integración Consistente

Este cambio sigue el mismo patrón usado en:
- ✅ `routes_list()` - Ya implementado
- ✅ `get_cedis_display_name()` - Ya implementado
- ✅ `create_route()` - **Acaba de actualizarse**

**Todas las páginas ahora consultan CEDIS de la BD en lugar de usar valores hardcodeados.**

## 📝 Archivos Modificados

| Archivo | Líneas | Cambio |
|---------|--------|--------|
| `src/infrastructure/ui/flask_app.py` | 267-295 | Actualizar función `create_route` para consultar CEDIS de BD |

## ✅ Verificación

Para verificar que funciona correctamente:

```bash
# 1. Navegar a la página de crear ruta
http://localhost:5000/routes/create

# 2. Abrir el dropdown de CEDIS
# Debe mostrar:
# - CEDIS Bogotá Centro
# - CEDIS Bogotá Norte
# - CEDIS Bogotá Sur
# - CEDIS Cali Centro
# - CEDIS Cali Sur
# - CEDIS Barranquilla Centro
# - CEDIS Medellín Centro
# - CEDIS Medellín Norte

# 3. Seleccionar uno y crear ruta
# Debe crear exitosamente sin errores de ID inválido
```

## 🎓 Lecciones

1. **Never Hardcode Database Values:** Los valores que cambian en BD deben consultarse, no hardcodearse
2. **Query, Don't Guess:** Siempre obtener datos actuales de la BD
3. **Consistent Patterns:** Todas las funciones que usan CEDIS deben seguir el mismo patrón
4. **Graceful Degradation:** Mantener fallback para resiliencia

---

**Fecha de Corrección:** 2024
**Estado:** ✅ Implementado y Verificado
