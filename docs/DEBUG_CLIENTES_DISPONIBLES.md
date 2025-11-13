# 🔧 Debugging: Clientes Disponibles No Se Muestran

**Fecha:** 13 de Noviembre de 2025  
**Problema:** Después de eliminar todos los clientes de una ruta, no aparecen en "Clientes Disponibles"  
**Estado:** 🔍 Investigando con logging mejorado

---

## 📋 Problema Reportado

**Síntoma:**
- Usuario elimina todos los clientes de una ruta
- Sección "Clientes Disponibles" muestra: "No hay clientes disponibles"
- Los clientes deberían estar disponibles para asignar a otras rutas

---

## 🔍 Posibles Causas

### Hipótesis 1: Error en Query a Base de Datos
- La función `get_available_clients()` puede estar fallando silenciosamente
- Retorna lista vacía `[]` sin mostrar error al usuario

### Hipótesis 2: Problema de Conexión
- Configuración de PostgreSQL incorrecta
- Timeout o error de red

### Hipótesis 3: Tabla Vacía
- No hay registros en tabla `clientes`
- Query correcta pero sin resultados

### Hipótesis 4: Error en Template
- Filtrado en Jinja2 elimina todos los clientes
- Problema con comparación de IDs (string vs int)

---

## 🛠️ Cambios Aplicados para Debugging

### 1. Logging Detallado en `get_available_clients()`

**Archivo:** `src/application/services/route_service.py`

```python
def get_available_clients(self) -> List:
    try:
        # ... conexión ...
        
        print(f"📊 DEBUG get_available_clients: Query ejecutada, obteniendo resultados...")
        
        rows = cursor.fetchall()
        print(f"📊 DEBUG get_available_clients: {len(rows)} filas obtenidas de BD")
        
        clients = []
        for row in rows:
            client = Client(...)
            clients.append(client)
            print(f"  - Cliente cargado: ID={client.id}, Nombre={client.name}")
        
        print(f"✅ get_available_clients: Retornando {len(clients)} clientes")
        return clients
        
    except Exception as e:
        import traceback
        print(f"⚠️ Warning: No se pudieron cargar clientes desde BD: {e}")
        print(traceback.format_exc())
        return []
```

### 2. Logging en Vista Flask

**Archivo:** `src/infrastructure/ui/flask_app.py`

```python
@app.route('/routes/<route_id>/clients')
def manage_clients(route_id: str):
    # ...
    all_clients = service.get_available_clients()
    print(f"📊 DEBUG: Total clientes disponibles cargados: {len(all_clients)}")
    
    # ...
    print(f"📊 DEBUG: Clientes en ruta: {len(route_clients_info)}")
    print(f"📊 DEBUG: IDs en ruta: {route.client_ids}")
```

### 3. Traceback Completo en Errores

Ahora ambos métodos (`get_available_clients` y `get_client_info`) imprimen traceback completo cuando hay excepciones.

---

## 🧪 Instrucciones para el Usuario

### Paso 1: Reiniciar Flask
```powershell
# Detener Flask (Ctrl+C)
python main_flask.py
```

### Paso 2: Ir a Gestionar Clientes
1. Abrir http://localhost:5000/routes
2. Seleccionar cualquier ruta (ej: RUTA_BOG_NORTE_01)
3. Clic en "Gestionar Clientes"

### Paso 3: Observar Logs en Terminal

**Logs Esperados (si funciona correctamente):**
```
📊 DEBUG get_available_clients: Query ejecutada, obteniendo resultados...
📊 DEBUG get_available_clients: 21 filas obtenidas de BD
  - Cliente cargado: ID=43, Nombre=Almacén Éxito Centro
  - Cliente cargado: ID=44, Nombre=Carrefour Calle 100
  - Cliente cargado: ID=45, Nombre=D1 Chapinero
  ...
✅ get_available_clients: Retornando 21 clientes
📊 DEBUG: Total clientes disponibles cargados: 21
📊 DEBUG: Clientes en ruta: 0
📊 DEBUG: IDs en ruta: []
```

**Logs Esperados (si hay error):**
```
⚠️ Warning: No se pudieron cargar clientes desde BD: [mensaje de error]
Traceback (most recent call last):
  ...
📊 DEBUG: Total clientes disponibles cargados: 0
```

### Paso 4: Copiar y Compartir Logs

**Por favor copia TODOS los logs que aparezcan** desde que accedes a "Gestionar Clientes" hasta que cargue la página.

---

## 🔍 Verificaciones Adicionales

### Verificar que hay clientes en BD
```sql
-- Ejecutar en pgAdmin
SELECT COUNT(*) as total_clientes FROM clientes;

-- Ver primeros 5 clientes
SELECT id, nombre_comercial, direccion 
FROM clientes 
ORDER BY nombre_comercial 
LIMIT 5;
```

**Resultado esperado:**
- Total > 0
- Al menos algunos clientes visibles

### Verificar ruta sin clientes
```sql
-- Ver clientes en ruta RUTA_BOG_NORTE_01
SELECT rc.cliente_id, c.nombre_comercial
FROM rutas_clientes rc
JOIN clientes c ON c.id = rc.cliente_id
WHERE rc.ruta_id = (
    SELECT id FROM rutas WHERE identificador_unico = 'RUTA_BOG_NORTE_01'
);
```

**Resultado esperado después de eliminar todos:**
- 0 filas (ruta vacía)

---

## 📊 Diagnóstico por Logs

### Caso A: Lista Vacía con Error
```
⚠️ Warning: No se pudieron cargar clientes desde BD: [error]
📊 DEBUG: Total clientes disponibles cargados: 0
```
**Causa:** Error de conexión o query SQL  
**Solución:** Revisar error específico y corregir

### Caso B: Lista Vacía sin Error
```
📊 DEBUG get_available_clients: 0 filas obtenidas de BD
✅ get_available_clients: Retornando 0 clientes
📊 DEBUG: Total clientes disponibles cargados: 0
```
**Causa:** Tabla `clientes` vacía  
**Solución:** Insertar clientes de prueba en BD

### Caso C: Clientes Cargados pero No Visibles
```
✅ get_available_clients: Retornando 21 clientes
📊 DEBUG: Total clientes disponibles cargados: 21
[Pero en pantalla: "No hay clientes disponibles"]
```
**Causa:** Problema en template (filtrado Jinja2)  
**Solución:** Revisar lógica en `manage_clients.html`

---

## 🎯 Próximos Pasos Según Resultado

### Si `get_available_clients()` retorna 0 clientes

1. **Verificar tabla clientes:**
   ```sql
   SELECT * FROM clientes LIMIT 5;
   ```

2. **Si tabla está vacía**, insertar datos de prueba:
   ```sql
   INSERT INTO clientes (nombre_comercial, direccion, latitud, longitud, fecha_creacion)
   VALUES 
   ('Tienda La Estrella', 'Calle 45 #12-34, Bogotá', 4.678, -74.050, NOW()),
   ('Supermercado El Sol', 'Carrera 7 #89-12, Bogotá', 4.690, -74.048, NOW()),
   ('Distribuidora Norte', 'Av. Caracas #100-20, Bogotá', 4.720, -74.052, NOW());
   ```

### Si `get_available_clients()` retorna clientes pero no se ven

1. **Revisar template:** Verificar lógica de filtrado en líneas 34-38 de `manage_clients.html`
2. **Verificar tipos de datos:** Comparar `client.id` (string) vs `route.client_ids` (array de strings)

### Si hay error de conexión

1. **Verificar config.py:**
   ```python
   POSTGRES_HOST = 'localhost'
   POSTGRES_PORT = 5432
   POSTGRES_DB = 'RutasDB'
   POSTGRES_USER = 'postgres'
   POSTGRES_PASSWORD = 'tu_password'
   ```

---

## 📁 Archivos Modificados en Este Debug

```
✏️ Modificados (2 archivos):
├── src/application/services/route_service.py
│   ├── get_available_clients() - Logging detallado
│   └── get_client_info() - Traceback en errores
│
├── src/infrastructure/ui/flask_app.py
│   └── manage_clients() - Debug de conteo
│
└── docs/DEBUG_CLIENTES_DISPONIBLES.md (ESTE ARCHIVO)
```

---

## ✅ Checklist de Verificación

- [ ] Flask reiniciado después de cambios
- [ ] Navegado a "Gestionar Clientes"
- [ ] Logs capturados desde terminal
- [ ] Verificado que tabla `clientes` tiene datos (pgAdmin)
- [ ] Verificado que ruta está vacía (sin clientes asignados)
- [ ] Logs copiados para análisis

---

## 📞 Información Necesaria del Usuario

Por favor proporciona:

1. **Logs completos** desde que cargas "Gestionar Clientes"
2. **Cantidad de clientes en BD:**
   ```sql
   SELECT COUNT(*) FROM clientes;
   ```
3. **Clientes en ruta actual:**
   ```sql
   SELECT COUNT(*) FROM rutas_clientes WHERE ruta_id = [id_ruta];
   ```

---

**Documentación generada:** 13/Nov/2025  
**Estado:** 🔍 Esperando logs del usuario para diagnosticar  
**Próximo paso:** Analizar output de debugging para identificar causa exacta
