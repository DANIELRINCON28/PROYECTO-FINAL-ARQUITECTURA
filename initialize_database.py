"""
Inicialización de la Base de Datos PostgreSQL - RutasDB
Crea todas las tablas necesarias según el modelo de Django proporcionado.

Este script sigue la arquitectura hexagonal manteniendo la capa de infraestructura
separada de la lógica de dominio.
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import Config


def create_database_if_not_exists():
    """
    Crea la base de datos RutasDB si no existe.
    Se conecta a la base de datos 'postgres' por defecto para crearla.
    """
    print("🔧 Verificando existencia de la base de datos...")
    
    # Conectar a la base de datos 'postgres' por defecto
    conn_params = Config.get_db_connection_params()
    default_conn = psycopg2.connect(
        host=conn_params['host'],
        port=conn_params['port'],
        user=conn_params['user'],
        password=conn_params['password'],
        database='postgres'  # Base de datos por defecto
    )
    default_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = default_conn.cursor()
    
    # Verificar si la base de datos existe
    cursor.execute("""
        SELECT 1 FROM pg_database WHERE datname = %s
    """, (Config.DB_NAME,))
    
    exists = cursor.fetchone()
    
    if not exists:
        print(f"📊 Creando base de datos '{Config.DB_NAME}'...")
        cursor.execute(f'CREATE DATABASE "{Config.DB_NAME}"')
        print(f"✅ Base de datos '{Config.DB_NAME}' creada exitosamente")
    else:
        print(f"ℹ️  La base de datos '{Config.DB_NAME}' ya existe")
    
    cursor.close()
    default_conn.close()


def initialize_database():
    """
    Inicializa todas las tablas en la base de datos RutasDB.
    Basado en el modelo de Django proporcionado.
    """
    print("=" * 70)
    print("🚀 INICIALIZACIÓN DE BASE DE DATOS POSTGRESQL - RutasDB")
    print("=" * 70)
    
    # Crear base de datos si no existe
    create_database_if_not_exists()
    
    # Conectar a la base de datos recién creada
    print(f"\n📡 Conectando a '{Config.DB_NAME}'...")
    conn = psycopg2.connect(**Config.get_db_connection_params())
    cursor = conn.cursor()
    
    try:
        print("\n🏗️  Creando tablas...")
        
        # 1. Tabla CEDIS (Centros de Distribución)
        print("  📦 Creando tabla 'cedis'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cedis (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                ciudad VARCHAR(100) NOT NULL,
                fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT cedis_nombre_ciudad_unique UNIQUE (nombre, ciudad)
            )
        """)
        
        # 2. Tabla Vendedores
        print("  👤 Creando tabla 'vendedores'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendedores (
                id SERIAL PRIMARY KEY,
                nombre_completo VARCHAR(150) NOT NULL,
                codigo_empleado VARCHAR(50) NOT NULL UNIQUE,
                fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Tabla Clientes
        print("  🏢 Creando tabla 'clientes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nombre_comercial VARCHAR(200) NOT NULL,
                direccion TEXT NOT NULL,
                latitud NUMERIC(9, 6),
                longitud NUMERIC(9, 6),
                fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 4. Tabla Rutas
        print("  🚚 Creando tabla 'rutas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rutas (
                id SERIAL PRIMARY KEY,
                identificador_unico VARCHAR(50) NOT NULL UNIQUE,
                nombre_descriptivo VARCHAR(150) NOT NULL,
                dia_semana SMALLINT NOT NULL CHECK (dia_semana >= 1 AND dia_semana <= 7),
                activa BOOLEAN NOT NULL DEFAULT TRUE,
                cedis_id INTEGER NOT NULL,
                fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_rutas_cedis FOREIGN KEY (cedis_id) 
                    REFERENCES cedis(id) ON DELETE RESTRICT
            )
        """)
        
        # 5. Tabla RutaCliente (Relación muchos a muchos)
        print("  🔗 Creando tabla 'rutas_clientes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rutas_clientes (
                id SERIAL PRIMARY KEY,
                ruta_id INTEGER NOT NULL,
                cliente_id INTEGER NOT NULL,
                orden_visita INTEGER NOT NULL,
                CONSTRAINT fk_rutas_clientes_ruta FOREIGN KEY (ruta_id)
                    REFERENCES rutas(id) ON DELETE CASCADE,
                CONSTRAINT fk_rutas_clientes_cliente FOREIGN KEY (cliente_id)
                    REFERENCES clientes(id) ON DELETE RESTRICT,
                CONSTRAINT unique_ruta_cliente UNIQUE (ruta_id, cliente_id),
                CONSTRAINT unique_ruta_orden UNIQUE (ruta_id, orden_visita)
            )
        """)
        
        # 6. Tabla AsignacionRuta
        print("  📋 Creando tabla 'asignaciones_rutas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asignaciones_rutas (
                id SERIAL PRIMARY KEY,
                fecha DATE NOT NULL,
                ruta_id INTEGER NOT NULL,
                vendedor_id INTEGER NOT NULL,
                estado VARCHAR(50) NOT NULL DEFAULT 'Pendiente',
                CONSTRAINT fk_asignaciones_ruta FOREIGN KEY (ruta_id)
                    REFERENCES rutas(id) ON DELETE RESTRICT,
                CONSTRAINT fk_asignaciones_vendedor FOREIGN KEY (vendedor_id)
                    REFERENCES vendedores(id) ON DELETE RESTRICT,
                CONSTRAINT unique_fecha_ruta UNIQUE (fecha, ruta_id),
                CONSTRAINT check_estado CHECK (estado IN ('Pendiente', 'En Progreso', 'Completada', 'Cancelada'))
            )
        """)
        
        # 7. Tabla Routes (para compatibilidad con el sistema actual)
        print("  🛣️  Creando tabla 'routes' (compatibilidad)...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id VARCHAR(100) PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                cedis_id VARCHAR(50) NOT NULL,
                day_of_week VARCHAR(20) NOT NULL,
                client_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("\n📊 Creando índices para optimización...")
        
        # Índices para Rutas
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rutas_dia_cedis 
            ON rutas(dia_semana, cedis_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rutas_activa 
            ON rutas(activa)
        """)
        
        # Índices para RutasClientes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rutas_clientes_ruta_orden 
            ON rutas_clientes(ruta_id, orden_visita)
        """)
        
        # Índices para AsignacionesRutas
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_asignaciones_fecha_vendedor 
            ON asignaciones_rutas(fecha, vendedor_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_asignaciones_fecha_ruta 
            ON asignaciones_rutas(fecha, ruta_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_asignaciones_estado 
            ON asignaciones_rutas(estado)
        """)
        
        # Índices para tabla Routes (compatibilidad)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_routes_cedis_day 
            ON routes(cedis_id, day_of_week)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_routes_active 
            ON routes(is_active)
        """)
        
        # Índice JSONB para client_ids
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_routes_client_ids_gin 
            ON routes USING gin(client_ids)
        """)
        
        print("\n🔧 Creando funciones auxiliares...")
        
        # Función para actualizar timestamp automáticamente
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        # Trigger para actualizar updated_at en routes
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_routes_updated_at ON routes;
            CREATE TRIGGER update_routes_updated_at
                BEFORE UPDATE ON routes
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)
        
        # Commit de todos los cambios
        conn.commit()
        
        print("\n" + "=" * 70)
        print("✅ Base de datos inicializada exitosamente")
        print("=" * 70)
        
        # Mostrar resumen
        print("\n📋 RESUMEN DE TABLAS CREADAS:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        for i, (table_name,) in enumerate(tables, 1):
            print(f"  {i}. {table_name}")
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"\n❌ Error al inicializar la base de datos: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def verify_database():
    """
    Verifica que la base de datos esté correctamente configurada.
    """
    print("\n🔍 Verificando configuración de la base de datos...")
    
    try:
        conn = psycopg2.connect(**Config.get_db_connection_params())
        cursor = conn.cursor()
        
        # Contar tablas
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        
        table_count = cursor.fetchone()[0]
        
        print(f"✅ Conexión exitosa")
        print(f"✅ {table_count} tablas encontradas")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Error al verificar: {str(e)}")
        return False


if __name__ == "__main__":
    """
    Ejecutar este script directamente inicializa la base de datos.
    """
    try:
        # Cargar variables de entorno desde .env si existe
        from dotenv import load_dotenv
        load_dotenv()
        
        print("\n📝 Configuración actual:")
        print(f"   Host: {Config.DB_HOST}")
        print(f"   Puerto: {Config.DB_PORT}")
        print(f"   Base de datos: {Config.DB_NAME}")
        print(f"   Usuario: {Config.DB_USER}")
        print()
        
        # Inicializar
        initialize_database()
        
        # Verificar
        verify_database()
        
        print("\n🎉 ¡Listo! La base de datos está preparada para usar.")
        print("\n💡 Próximos pasos:")
        print("   1. Ejecutar 'python init_sample_data.py' para cargar datos de ejemplo")
        print("   2. Ejecutar 'python main.py' para iniciar la aplicación")
        
    except Exception as e:
        print(f"\n💥 Error fatal: {str(e)}")
        import traceback
        traceback.print_exc()
