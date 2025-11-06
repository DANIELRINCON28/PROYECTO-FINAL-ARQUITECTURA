"""
Script para Limpiar y Poblar Completamente la Base de Datos PostgreSQL
Este script:
1. Elimina todos los datos de las tablas (sin borrar la estructura)
2. Puebla las tablas con datos realistas y coherentes
3. Mantiene la integridad referencial
"""
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime, timedelta

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config


class DatabaseCleaner:
    """Clase para limpiar y poblar la base de datos."""
    
    def __init__(self):
        """Inicializa la conexión a la base de datos."""
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establece conexión con la base de datos."""
        try:
            self.conn = psycopg2.connect(**Config.get_db_connection_params())
            self.cursor = self.conn.cursor()
            print(f"✅ Conectado a {Config.DB_NAME}")
            return True
        except psycopg2.Error as e:
            print(f"❌ Error al conectar: {str(e)}")
            return False
    
    def disconnect(self):
        """Cierra la conexión."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✅ Desconectado de la base de datos")
    
    def clean_tables(self):
        """Elimina todos los datos de las tablas manteniendo la estructura."""
        print("\n" + "=" * 70)
        print("🗑️  LIMPIANDO TABLAS")
        print("=" * 70)
        
        # Orden importante: eliminar primero las tablas con foreign keys
        tables_to_clean = [
            'asignaciones_rutas',
            'rutas_clientes',
            'rutas',
            'clientes',
            'vendedores',
            'cedis'
        ]
        
        try:
            # Desactivar constraint checks temporalmente
            self.cursor.execute("SET session_replication_role = REPLICA;")
            
            for table in tables_to_clean:
                try:
                    self.cursor.execute(f"DELETE FROM {table}")
                    self.conn.commit()
                    print(f"  ✅ Limpiada tabla: {table}")
                except psycopg2.Error as e:
                    print(f"  ⚠️  Tabla {table} no existe o error: {str(e)}")
            
            # Reactivar constraint checks
            self.cursor.execute("SET session_replication_role = DEFAULT;")
            self.conn.commit()
            
            print("\n✅ Todas las tablas han sido limpiadas")
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Error al limpiar tablas: {str(e)}")
            raise
    
    def populate_cedis(self):
        """Puebla la tabla de CEDIS (Centros de Distribución)."""
        print("\n" + "=" * 70)
        print("📦 POBLANDO TABLA: CEDIS")
        print("=" * 70)
        
        cedis_data = [
            ('Bogotá Centro', 'Bogotá'),
            ('Bogotá Norte', 'Bogotá'),
            ('Bogotá Sur', 'Bogotá'),
            ('Medellín', 'Medellín'),
            ('Cali', 'Cali'),
            ('Barranquilla', 'Barranquilla'),
        ]
        
        try:
            for nombre, ciudad in cedis_data:
                self.cursor.execute(
                    """
                    INSERT INTO cedis (nombre, ciudad)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (nombre, ciudad)
                )
                cedis_id = self.cursor.fetchone()[0]
                print(f"  ✅ CEDIS: {nombre} ({ciudad}) - ID: {cedis_id}")
            
            self.conn.commit()
            print(f"\n✅ {len(cedis_data)} CEDIS creados")
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Error al poblar CEDIS: {str(e)}")
            raise
    
    def populate_vendedores(self):
        """Puebla la tabla de vendedores."""
        print("\n" + "=" * 70)
        print("👤 POBLANDO TABLA: VENDEDORES")
        print("=" * 70)
        
        vendedores_data = [
            ('Juan Carlos López', 'VEN_001'),
            ('María García Rodríguez', 'VEN_002'),
            ('Carlos Alberto Martínez', 'VEN_003'),
            ('Ana María Sánchez', 'VEN_004'),
            ('Roberto Díaz Flores', 'VEN_005'),
            ('Patricia González', 'VEN_006'),
            ('Fernando Ramírez', 'VEN_007'),
            ('Isabel Torres', 'VEN_008'),
            ('Miguel Ángel Ruiz', 'VEN_009'),
            ('Laura Quintero', 'VEN_010'),
        ]
        
        try:
            for nombre, codigo in vendedores_data:
                self.cursor.execute(
                    """
                    INSERT INTO vendedores (nombre_completo, codigo_empleado)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (nombre, codigo)
                )
                vendedor_id = self.cursor.fetchone()[0]
                print(f"  ✅ Vendedor: {nombre} ({codigo}) - ID: {vendedor_id}")
            
            self.conn.commit()
            print(f"\n✅ {len(vendedores_data)} vendedores creados")
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Error al poblar vendedores: {str(e)}")
            raise
    
    def populate_clientes(self):
        """Puebla la tabla de clientes con coordenadas realistas de Bogotá."""
        print("\n" + "=" * 70)
        print("🏢 POBLANDO TABLA: CLIENTES")
        print("=" * 70)
        
        # Clientes con coordenadas aproximadas en Bogotá
        clientes_data = [
            ('Almacén Éxito Centro', 'Cra 9 #10-65, Bogotá', 4.7100, -74.0742),
            ('Carrefour Calle 100', 'Cll 100 #50-20, Bogotá', 4.7290, -74.0517),
            ('D1 Chapinero', 'Cra 12 #51-20, Bogotá', 4.7131, -74.0566),
            ('Makro Bogotá Norte', 'Av. Cra 50 #112-60, Bogotá', 4.8265, -74.0418),
            ('Carrefour Dorado', 'Cra 9 #108-60, Bogotá', 4.8098, -74.0739),
            ('Éxito Usaquén', 'Cra 7 #126-80, Bogotá', 4.8491, -74.0301),
            ('D1 Suba', 'Cra 89 #139-50, Bogotá', 4.8761, -74.0906),
            ('Falabella La Romana', 'Cll 82 #72-82, Bogotá', 4.7577, -74.0937),
            ('Carrefour Bosa', 'Cll 66 #85-70, Bogotá', 4.7328, -74.1648),
            ('Makro Sur', 'Cra 3 #26-10, Bogotá', 4.6181, -74.0864),
            ('Almacén Éxito Hayuelos', 'Cra 71 #52-20, Bogotá', 4.7154, -74.1517),
            ('Carrefour Occidente', 'Cll 24 #79-85, Bogotá', 4.6705, -74.1386),
            ('D1 Teusaquillo', 'Cra 19 #62-45, Bogotá', 4.7286, -74.0785),
            ('Éxito Conmutador', 'Cll 30 #5-50, Bogotá', 4.6912, -74.0686),
            ('Carrefour Corabastos', 'Diag 20 #30-68, Bogotá', 4.6581, -74.1135),
            ('Makro Aéreo', 'Cra 7 #44-68, Bogotá', 4.7072, -74.0776),
            ('Almacén Éxito Chapinero', 'Cra 7 #53-85, Bogotá', 4.7162, -74.0502),
            ('D1 Calle 116', 'Cra 7 #116-30, Bogotá', 4.8315, -74.0482),
            ('Falabella Centro Andino', 'Cra 11A #82-71, Bogotá', 4.7566, -74.0486),
            ('Carrefour Empalme', 'Cra 15 #63-85, Bogotá', 4.7318, -74.0906),
            ('Éxito Éxito Candelaria', 'Cra 3 #11-82, Bogotá', 4.6027, -74.0833),
        ]
        
        try:
            for nombre, direccion, latitud, longitud in clientes_data:
                self.cursor.execute(
                    """
                    INSERT INTO clientes (nombre_comercial, direccion, latitud, longitud)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (nombre, direccion, latitud, longitud)
                )
                cliente_id = self.cursor.fetchone()[0]
                print(f"  ✅ Cliente: {nombre} - ID: {cliente_id}")
            
            self.conn.commit()
            print(f"\n✅ {len(clientes_data)} clientes creados")
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Error al poblar clientes: {str(e)}")
            raise
    
    def populate_rutas(self):
        """Puebla la tabla de rutas."""
        print("\n" + "=" * 70)
        print("🚚 POBLANDO TABLA: RUTAS")
        print("=" * 70)
        
        # Primero obtener los IDs de CEDIS
        self.cursor.execute("SELECT id FROM cedis WHERE nombre LIKE '%Bogotá%' LIMIT 3")
        cedis_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not cedis_ids:
            print("❌ No hay CEDIS disponibles")
            return
        
        rutas_data = [
            ('RUTA_BOG_NORTE_01', 'Ruta Bogotá Norte - Lunes', 1, cedis_ids[0]),
            ('RUTA_BOG_NORTE_02', 'Ruta Bogotá Norte - Martes', 2, cedis_ids[0]),
            ('RUTA_BOG_CENTRO_01', 'Ruta Bogotá Centro - Miércoles', 3, cedis_ids[1]),
            ('RUTA_BOG_CENTRO_02', 'Ruta Bogotá Centro - Jueves', 4, cedis_ids[1]),
            ('RUTA_BOG_SUR_01', 'Ruta Bogotá Sur - Viernes', 5, cedis_ids[2]),
            ('RUTA_BOG_SUR_02', 'Ruta Bogotá Sur - Lunes', 1, cedis_ids[2]),
            ('RUTA_BOG_OESTE_01', 'Ruta Bogotá Occidente - Martes', 2, cedis_ids[0]),
            ('RUTA_BOG_ESTE_01', 'Ruta Bogotá Oriente - Miércoles', 3, cedis_ids[1]),
        ]
        
        try:
            ruta_ids = {}
            for identificador, nombre, dia, cedis_id in rutas_data:
                self.cursor.execute(
                    """
                    INSERT INTO rutas (identificador_unico, nombre_descriptivo, dia_semana, cedis_id, activa)
                    VALUES (%s, %s, %s, %s, TRUE)
                    RETURNING id
                    """,
                    (identificador, nombre, dia, cedis_id)
                )
                ruta_id = self.cursor.fetchone()[0]
                ruta_ids[identificador] = ruta_id
                dias_semana = ['', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                print(f"  ✅ Ruta: {nombre} ({dias_semana[dia]}) - ID: {ruta_id}")
            
            self.conn.commit()
            print(f"\n✅ {len(rutas_data)} rutas creadas")
            return ruta_ids
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Error al poblar rutas: {str(e)}")
            raise
    
    def populate_rutas_clientes(self, ruta_ids):
        """Puebla la tabla de asociación rutas_clientes."""
        print("\n" + "=" * 70)
        print("🔗 POBLANDO TABLA: RUTAS_CLIENTES")
        print("=" * 70)
        
        # Obtener IDs de clientes
        self.cursor.execute("SELECT id FROM clientes ORDER BY id")
        cliente_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not cliente_ids or not ruta_ids:
            print("❌ No hay clientes o rutas disponibles")
            return
        
        # Asignar clientes a rutas de forma distribuida
        asignaciones = []
        cliente_idx = 0
        
        try:
            for ruta_idx, (identificador, ruta_id) in enumerate(ruta_ids.items()):
                # Asignar 3-4 clientes por ruta
                num_clientes = 3 + (ruta_idx % 2)
                
                for orden in range(1, num_clientes + 1):
                    if cliente_idx < len(cliente_ids):
                        cliente_id = cliente_ids[cliente_idx]
                        
                        self.cursor.execute(
                            """
                            INSERT INTO rutas_clientes (ruta_id, cliente_id, orden_visita)
                            VALUES (%s, %s, %s)
                            """,
                            (ruta_id, cliente_id, orden)
                        )
                        
                        asignaciones.append((ruta_id, cliente_id, orden))
                        cliente_idx += 1
                        
                        print(f"  ✅ Ruta {ruta_id}: Cliente {cliente_id} (orden {orden})")
            
            self.conn.commit()
            print(f"\n✅ {len(asignaciones)} asociaciones ruta-cliente creadas")
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Error al poblar rutas_clientes: {str(e)}")
            raise
    
    def populate_asignaciones_rutas(self, ruta_ids):
        """Puebla la tabla de asignaciones de rutas a vendedores."""
        print("\n" + "=" * 70)
        print("📋 POBLANDO TABLA: ASIGNACIONES_RUTAS")
        print("=" * 70)
        
        # Obtener vendedores
        self.cursor.execute("SELECT id FROM vendedores")
        vendedor_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not vendedor_ids or not ruta_ids:
            print("❌ No hay vendedores o rutas disponibles")
            return
        
        try:
            asignaciones_count = 0
            fecha_inicio = datetime.now() - timedelta(days=7)
            
            # Crear asignaciones para las próximas 2 semanas
            for i in range(14):
                fecha = fecha_inicio + timedelta(days=i)
                
                # Asignar cada ruta a un vendedor diferente
                for ruta_idx, (identificador, ruta_id) in enumerate(ruta_ids.items()):
                    vendedor_id = vendedor_ids[ruta_idx % len(vendedor_ids)]
                    
                    self.cursor.execute(
                        """
                        INSERT INTO asignaciones_rutas 
                        (fecha, ruta_id, vendedor_id, estado)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (fecha.date(), ruta_id, vendedor_id, 'Pendiente')
                    )
                    asignaciones_count += 1
            
            self.conn.commit()
            print(f"\n✅ {asignaciones_count} asignaciones de ruta creadas")
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"❌ Error al poblar asignaciones: {str(e)}")
            raise
    
    def show_statistics(self):
        """Muestra estadísticas de la base de datos."""
        print("\n" + "=" * 70)
        print("📊 ESTADÍSTICAS DE LA BASE DE DATOS")
        print("=" * 70)
        
        try:
            tables_stats = [
                ('cedis', 'CEDIS'),
                ('vendedores', 'Vendedores'),
                ('clientes', 'Clientes'),
                ('rutas', 'Rutas'),
                ('rutas_clientes', 'Rutas-Clientes'),
                ('asignaciones_rutas', 'Asignaciones'),
            ]
            
            for table, label in tables_stats:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"  📋 {label}: {count} registros")
            
        except psycopg2.Error as e:
            print(f"❌ Error al obtener estadísticas: {str(e)}")
    
    def run_full_process(self):
        """Ejecuta el proceso completo de limpieza y población."""
        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + "  🔄 LIMPIEZA Y POBLACIÓN COMPLETA DE LA BASE DE DATOS".center(68) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "=" * 68 + "╝")
        
        try:
            # Conectar
            if not self.connect():
                return False
            
            # Limpiar
            self.clean_tables()
            
            # Poblar
            self.populate_cedis()
            self.populate_vendedores()
            self.populate_clientes()
            ruta_ids = self.populate_rutas()
            
            if ruta_ids:
                self.populate_rutas_clientes(ruta_ids)
                self.populate_asignaciones_rutas(ruta_ids)
            
            # Mostrar estadísticas
            self.show_statistics()
            
            print("\n" + "=" * 70)
            print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
            print("=" * 70)
            print("\n🎉 La base de datos ha sido limpiada y poblada completamente.")
            print("   Puedes ahora ejecutar: streamlit run main.py")
            print()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error fatal: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.disconnect()


if __name__ == "__main__":
    """Punto de entrada del script."""
    cleaner = DatabaseCleaner()
    success = cleaner.run_full_process()
    exit(0 if success else 1)
