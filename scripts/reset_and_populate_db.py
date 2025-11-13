"""
Script para limpiar y repoblar la base de datos con datos coherentes
Ejecutar: python scripts/reset_and_populate_db.py
"""
import sys
import os
from datetime import datetime, date

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import psycopg2
from config import Config


def get_connection():
    """Obtener conexión a PostgreSQL"""
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=int(Config.DB_PORT),
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )


def limpiar_tablas(conn):
    """Limpiar todas las tablas en el orden correcto (respetando FKs)"""
    print("🗑️  Limpiando base de datos...")
    
    cursor = conn.cursor()
    
    try:
        # Orden de eliminación (hijos antes que padres)
        tablas = [
            'asignaciones_rutas',
            'rutas_clientes',
            'rutas',
            'clientes',
            'cedis',
            'vendedores'
        ]
        
        for tabla in tablas:
            cursor.execute(f"DELETE FROM {tabla}")
            print(f"  ✅ Tabla '{tabla}' limpiada")
        
        # Reiniciar secuencias de IDs
        secuencias = [
            'cedis_id_seq',
            'clientes_id_seq',
            'rutas_id_seq',
            'rutas_clientes_id_seq',
            'vendedores_id_seq',
            'asignaciones_rutas_id_seq'
        ]
        
        for secuencia in secuencias:
            try:
                cursor.execute(f"ALTER SEQUENCE {secuencia} RESTART WITH 1")
                print(f"  🔄 Secuencia '{secuencia}' reiniciada")
            except psycopg2.Error as e:
                print(f"  ⚠️  Secuencia '{secuencia}' no existe o ya está en 1")
        
        conn.commit()
        print("✅ Base de datos limpiada exitosamente\n")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al limpiar tablas: {e}")
        raise


def poblar_cedis(conn):
    """Poblar tabla CEDIS con centros de distribución por ciudad"""
    print("📦 Poblando CEDIS...")
    
    cursor = conn.cursor()
    
    cedis_data = [
        # Bogotá (3 CEDIS)
        ('CEDIS Bogotá Centro', 'Bogotá'),
        ('CEDIS Bogotá Norte', 'Bogotá'),
        ('CEDIS Bogotá Sur', 'Bogotá'),
        
        # Medellín (2 CEDIS)
        ('CEDIS Medellín Centro', 'Medellín'),
        ('CEDIS Medellín Norte', 'Medellín'),
        
        # Cali (2 CEDIS)
        ('CEDIS Cali Centro', 'Cali'),
        ('CEDIS Cali Sur', 'Cali'),
        
        # Barranquilla (1 CEDIS)
        ('CEDIS Barranquilla Centro', 'Barranquilla'),
    ]
    
    cedis_ids = {}
    
    for nombre, ciudad in cedis_data:
        cursor.execute("""
            INSERT INTO cedis (nombre, ciudad, fecha_creacion)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (nombre, ciudad, datetime.now()))
        
        cedis_id = cursor.fetchone()[0]
        cedis_ids[nombre] = cedis_id
        print(f"  ✅ {nombre} (ID: {cedis_id})")
    
    conn.commit()
    print(f"✅ {len(cedis_data)} CEDIS creados\n")
    
    return cedis_ids


def poblar_clientes(conn):
    """Poblar tabla clientes con datos realistas por ciudad"""
    print("👥 Poblando Clientes...")
    
    cursor = conn.cursor()
    
    clientes_data = [
        # Bogotá (15 clientes)
        ('Almacén Éxito Centro', 'Cra 9 #10-65, Bogotá', 4.710000, -74.074200),
        ('Carrefour Calle 100', 'Cll 100 #50-20, Bogotá', 4.729000, -74.051700),
        ('D1 Chapinero', 'Cra 12 #51-20, Bogotá', 4.713100, -74.056600),
        ('Makro Bogotá Norte', 'Av. Cra 50 #112-60, Bogotá', 4.826500, -74.041800),
        ('Carrefour Dorado', 'Cra 9 #108-60, Bogotá', 4.809800, -74.073900),
        ('Éxito Usaquén', 'Cra 7 #126-80, Bogotá', 4.849100, -74.030100),
        ('D1 Suba', 'Cra 89 #139-50, Bogotá', 4.876100, -74.090600),
        ('Falabella La Romana', 'Cll 82 #72-82, Bogotá', 4.757700, -74.093700),
        ('Carrefour Bosa', 'Cll 66 #85-70, Bogotá', 4.732800, -74.164800),
        ('Makro Sur', 'Cra 3 #26-10, Bogotá', 4.618100, -74.086400),
        ('Almacén Éxito Hayuelos', 'Cra 71 #52-20, Bogotá', 4.715400, -74.151700),
        ('Carrefour Occidente', 'Cll 24 #79-85, Bogotá', 4.670500, -74.138600),
        ('D1 Teusaquillo', 'Cra 19 #62-45, Bogotá', 4.728600, -74.078500),
        ('Éxito Conmutador', 'Cll 30 #5-50, Bogotá', 4.691200, -74.068600),
        ('Carrefour Corabastos', 'Diag 20 #30-68, Bogotá', 4.658100, -74.113500),
        
        # Medellín (8 clientes)
        ('Éxito Envigado', 'Cra 43A #34-95, Medellín', 6.175300, -75.580900),
        ('Carrefour Laureles', 'Cll 33 #76-15, Medellín', 6.244200, -75.590800),
        ('D1 Poblado', 'Cra 43B #10-50, Medellín', 6.208500, -75.568400),
        ('Makro Medellín', 'Cra 65 #8B-91, Medellín', 6.230800, -75.602300),
        ('Éxito San Diego', 'Cll 34 #43-66, Medellín', 6.236600, -75.575200),
        ('Carrefour Unicentro', 'Cra 66B #34A-76, Medellín', 6.257200, -75.595000),
        ('D1 Belén', 'Cra 76 #30-95, Medellín', 6.232900, -75.611500),
        ('Falabella Premium Plaza', 'Cra 43A #1-50, Medellín', 6.194800, -75.575700),
        
        # Cali (6 clientes)
        ('Éxito Chipichape', 'Cra 38 #14-50, Cali', 3.462400, -76.538900),
        ('Carrefour La Flora', 'Cll 13 #100-100, Cali', 3.371100, -76.529800),
        ('D1 Ciudad Jardín', 'Cra 100 #11-50, Cali', 3.374300, -76.529200),
        ('Makro Cali Sur', 'Cra 8 #14-60, Cali', 3.424200, -76.528400),
        ('Éxito Palmetto', 'Cll 10 #122-50, Cali', 3.369500, -76.546200),
        ('Carrefour Limonar', 'Cra 23 #10-35, Cali', 3.376800, -76.521900),
        
        # Barranquilla (4 clientes)
        ('Éxito Barranquilla Centro', 'Cra 43 #32-15, Barranquilla', 10.998600, -74.806400),
        ('Carrefour Buenavista', 'Cll 98 #46-25, Barranquilla', 11.020800, -74.823100),
        ('D1 Riomar', 'Cra 51B #87-50, Barranquilla', 11.013700, -74.817200),
        ('Makro Barranquilla', 'Cra 38 #74-176, Barranquilla', 11.009300, -74.803500),
    ]
    
    cliente_ids = []
    
    for nombre, direccion, latitud, longitud in clientes_data:
        cursor.execute("""
            INSERT INTO clientes (nombre_comercial, direccion, latitud, longitud, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (nombre, direccion, latitud, longitud, datetime.now()))
        
        cliente_id = cursor.fetchone()[0]
        cliente_ids.append(cliente_id)
        print(f"  ✅ {nombre} (ID: {cliente_id})")
    
    conn.commit()
    print(f"✅ {len(clientes_data)} Clientes creados\n")
    
    return cliente_ids


def poblar_vendedores(conn):
    """Poblar tabla vendedores"""
    print("👨‍💼 Poblando Vendedores...")
    
    cursor = conn.cursor()
    
    vendedores_data = [
        ('Juan Carlos Pérez', 'VEN-001'),
        ('María Fernanda Gómez', 'VEN-002'),
        ('Carlos Andrés Rodríguez', 'VEN-003'),
        ('Ana Lucía Martínez', 'VEN-004'),
        ('Diego Alejandro López', 'VEN-005'),
        ('Laura Sofía Ramírez', 'VEN-006'),
        ('Miguel Ángel Torres', 'VEN-007'),
        ('Camila Andrea Sánchez', 'VEN-008'),
    ]
    
    vendedor_ids = {}
    
    for nombre, codigo in vendedores_data:
        cursor.execute("""
            INSERT INTO vendedores (nombre_completo, codigo_empleado, fecha_creacion)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (nombre, codigo, datetime.now()))
        
        vendedor_id = cursor.fetchone()[0]
        vendedor_ids[codigo] = vendedor_id
        print(f"  ✅ {nombre} ({codigo}) - ID: {vendedor_id}")
    
    conn.commit()
    print(f"✅ {len(vendedores_data)} Vendedores creados\n")
    
    return vendedor_ids


def poblar_rutas(conn, cedis_ids, cliente_ids):
    """Poblar tabla rutas con asignaciones coherentes por ciudad"""
    print("🚚 Poblando Rutas...")
    
    cursor = conn.cursor()
    
    # Mapeo de clientes por ciudad (basado en los índices de cliente_ids)
    clientes_bogota = cliente_ids[0:15]   # Primeros 15
    clientes_medellin = cliente_ids[15:23]  # Siguientes 8
    clientes_cali = cliente_ids[23:29]      # Siguientes 6
    clientes_barranquilla = cliente_ids[29:33]  # Últimos 4
    
    rutas_data = [
        # Bogotá Centro (CEDIS 1)
        ('RUTA_BOG_CENTRO_01', 'Ruta Bogotá Centro - Lunes', 1, cedis_ids['CEDIS Bogotá Centro'], clientes_bogota[0:3]),
        ('RUTA_BOG_CENTRO_02', 'Ruta Bogotá Centro - Martes', 2, cedis_ids['CEDIS Bogotá Centro'], clientes_bogota[3:5]),
        
        # Bogotá Norte (CEDIS 2)
        ('RUTA_BOG_NORTE_01', 'Ruta Bogotá Norte - Lunes', 1, cedis_ids['CEDIS Bogotá Norte'], clientes_bogota[5:8]),
        ('RUTA_BOG_NORTE_02', 'Ruta Bogotá Norte - Martes', 2, cedis_ids['CEDIS Bogotá Norte'], clientes_bogota[8:10]),
        
        # Bogotá Sur (CEDIS 3)
        ('RUTA_BOG_SUR_01', 'Ruta Bogotá Sur - Miércoles', 3, cedis_ids['CEDIS Bogotá Sur'], clientes_bogota[10:13]),
        ('RUTA_BOG_SUR_02', 'Ruta Bogotá Sur - Jueves', 4, cedis_ids['CEDIS Bogotá Sur'], clientes_bogota[13:15]),
        
        # Medellín Centro (CEDIS 4)
        ('RUTA_MED_CENTRO_01', 'Ruta Medellín Centro - Lunes', 1, cedis_ids['CEDIS Medellín Centro'], clientes_medellin[0:4]),
        
        # Medellín Norte (CEDIS 5)
        ('RUTA_MED_NORTE_01', 'Ruta Medellín Norte - Martes', 2, cedis_ids['CEDIS Medellín Norte'], clientes_medellin[4:8]),
        
        # Cali Centro (CEDIS 6)
        ('RUTA_CALI_CENTRO_01', 'Ruta Cali Centro - Miércoles', 3, cedis_ids['CEDIS Cali Centro'], clientes_cali[0:3]),
        
        # Cali Sur (CEDIS 7)
        ('RUTA_CALI_SUR_01', 'Ruta Cali Sur - Jueves', 4, cedis_ids['CEDIS Cali Sur'], clientes_cali[3:6]),
        
        # Barranquilla (CEDIS 8)
        ('RUTA_BAQ_CENTRO_01', 'Ruta Barranquilla Centro - Viernes', 5, cedis_ids['CEDIS Barranquilla Centro'], clientes_barranquilla[0:4]),
    ]
    
    ruta_ids = {}
    
    for identificador, nombre, dia, cedis_id, clientes in rutas_data:
        # Insertar ruta
        cursor.execute("""
            INSERT INTO rutas (identificador_unico, nombre_descriptivo, dia_semana, activa, cedis_id, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (identificador, nombre, dia, True, cedis_id, datetime.now()))
        
        ruta_id = cursor.fetchone()[0]
        ruta_ids[identificador] = ruta_id
        
        print(f"  ✅ {nombre} (ID: {ruta_id})")
        
        # Insertar clientes en la ruta
        for orden, cliente_id in enumerate(clientes, start=1):
            cursor.execute("""
                INSERT INTO rutas_clientes (ruta_id, cliente_id, orden_visita)
                VALUES (%s, %s, %s)
            """, (ruta_id, cliente_id, orden))
            print(f"     └─ Cliente ID {cliente_id} en orden {orden}")
    
    conn.commit()
    print(f"✅ {len(rutas_data)} Rutas creadas con clientes asignados\n")
    
    return ruta_ids


def poblar_asignaciones(conn, ruta_ids, vendedor_ids):
    """Poblar tabla asignaciones_rutas"""
    print("📋 Poblando Asignaciones de Rutas...")
    
    cursor = conn.cursor()
    
    # Asignaciones de ejemplo para la semana actual
    fecha_hoy = date.today()
    
    asignaciones_data = [
        (fecha_hoy, 'RUTA_BOG_CENTRO_01', 'VEN-001', 'Completada'),
        (fecha_hoy, 'RUTA_BOG_NORTE_01', 'VEN-002', 'En Progreso'),
        (fecha_hoy, 'RUTA_MED_CENTRO_01', 'VEN-003', 'Pendiente'),
        (fecha_hoy, 'RUTA_CALI_CENTRO_01', 'VEN-004', 'Pendiente'),
        (fecha_hoy, 'RUTA_BAQ_CENTRO_01', 'VEN-005', 'Pendiente'),
    ]
    
    for fecha, ruta_key, vendedor_key, estado in asignaciones_data:
        cursor.execute("""
            INSERT INTO asignaciones_rutas (fecha, ruta_id, vendedor_id, estado)
            VALUES (%s, %s, %s, %s)
        """, (fecha, ruta_ids[ruta_key], vendedor_ids[vendedor_key], estado))
        
        print(f"  ✅ {ruta_key} → {vendedor_key} ({estado})")
    
    conn.commit()
    print(f"✅ {len(asignaciones_data)} Asignaciones creadas\n")


def main():
    """Función principal"""
    print("=" * 70)
    print("🔄 RESET Y POBLACIÓN DE BASE DE DATOS")
    print("=" * 70)
    print()
    
    try:
        # Conectar a la base de datos
        print("🔌 Conectando a PostgreSQL...")
        conn = get_connection()
        print(f"✅ Conectado a {Config.DB_NAME}@{Config.DB_HOST}\n")
        
        # 1. Limpiar tablas
        limpiar_tablas(conn)
        
        # 2. Poblar CEDIS
        cedis_ids = poblar_cedis(conn)
        
        # 3. Poblar Clientes
        cliente_ids = poblar_clientes(conn)
        
        # 4. Poblar Vendedores
        vendedor_ids = poblar_vendedores(conn)
        
        # 5. Poblar Rutas con clientes
        ruta_ids = poblar_rutas(conn, cedis_ids, cliente_ids)
        
        # 6. Poblar Asignaciones
        poblar_asignaciones(conn, ruta_ids, vendedor_ids)
        
        # Cerrar conexión
        conn.close()
        
        print("=" * 70)
        print("✅ BASE DE DATOS POBLADA EXITOSAMENTE")
        print("=" * 70)
        print()
        print("📊 Resumen:")
        print(f"  • CEDIS: {len(cedis_ids)}")
        print(f"  • Clientes: {len(cliente_ids)}")
        print(f"  • Vendedores: {len(vendedor_ids)}")
        print(f"  • Rutas: {len(ruta_ids)}")
        print(f"  • Asignaciones: 5")
        print()
        print("🚀 Puedes iniciar la aplicación Flask ahora:")
        print("   python main_flask.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
