"""
Script de Migración de Datos: SQLite → PostgreSQL
Migra todos los datos existentes de SQLite a la nueva base de datos PostgreSQL.

Este script mantiene la arquitectura hexagonal usando los puertos y adaptadores.
"""
import sqlite3
import psycopg2
import json
from pathlib import Path
from typing import List, Dict, Any
from config import Config


class DataMigrator:
    """
    Clase responsable de migrar datos de SQLite a PostgreSQL.
    
    Principio de Responsabilidad Única (SRP):
    - Solo se encarga de la migración de datos
    """
    
    def __init__(self, sqlite_path: str):
        """
        Inicializa el migrador de datos.
        
        Args:
            sqlite_path: Ruta al archivo SQLite
        """
        self.sqlite_path = sqlite_path
        self.postgres_params = Config.get_db_connection_params()
        self.stats = {
            'routes_migrated': 0,
            'routes_failed': 0,
            'errors': []
        }
    
    def migrate(self) -> bool:
        """
        Ejecuta la migración completa de datos.
        
        Returns:
            True si la migración fue exitosa, False en caso contrario
        """
        print("=" * 70)
        print("🔄 MIGRACIÓN DE DATOS: SQLite → PostgreSQL")
        print("=" * 70)
        
        # Verificar que existe el archivo SQLite
        if not Path(self.sqlite_path).exists():
            print(f"⚠️  No se encontró el archivo SQLite en: {self.sqlite_path}")
            print("   No hay datos para migrar. Comenzando con base de datos vacía.")
            return True
        
        try:
            # Conectar a ambas bases de datos
            print("\n📡 Conectando a las bases de datos...")
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row
            
            postgres_conn = psycopg2.connect(**self.postgres_params)
            postgres_conn.autocommit = False
            
            print("✅ Conexiones establecidas")
            
            # Migrar rutas
            print("\n🚚 Migrando rutas...")
            self._migrate_routes(sqlite_conn, postgres_conn)
            
            # Mostrar estadísticas
            self._show_statistics()
            
            # Cerrar conexiones
            sqlite_conn.close()
            postgres_conn.close()
            
            print("\n✅ Migración completada exitosamente")
            return True
            
        except Exception as e:
            print(f"\n❌ Error durante la migración: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _migrate_routes(self, sqlite_conn: sqlite3.Connection, 
                       postgres_conn: psycopg2.extensions.connection) -> None:
        """
        Migra las rutas de SQLite a PostgreSQL.
        
        Args:
            sqlite_conn: Conexión a SQLite
            postgres_conn: Conexión a PostgreSQL
        """
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        try:
            # Obtener todas las rutas de SQLite
            sqlite_cursor.execute("""
                SELECT id, name, cedis_id, day_of_week, client_ids, is_active,
                       created_at, updated_at
                FROM routes
            """)
            
            routes = sqlite_cursor.fetchall()
            total_routes = len(routes)
            
            if total_routes == 0:
                print("   ℹ️  No hay rutas para migrar")
                return
            
            print(f"   Encontradas {total_routes} rutas en SQLite")
            
            # Migrar cada ruta
            for i, route in enumerate(routes, 1):
                try:
                    # Preparar datos
                    route_data = {
                        'id': route['id'],
                        'name': route['name'],
                        'cedis_id': route['cedis_id'],
                        'day_of_week': route['day_of_week'],
                        'client_ids': route['client_ids'],
                        'is_active': bool(route['is_active']),
                        'created_at': route['created_at'] if route['created_at'] else 'CURRENT_TIMESTAMP',
                        'updated_at': route['updated_at'] if route['updated_at'] else 'CURRENT_TIMESTAMP'
                    }
                    
                    # Insertar en PostgreSQL
                    postgres_cursor.execute("""
                        INSERT INTO routes (id, name, cedis_id, day_of_week, 
                                          client_ids, is_active, created_at, updated_at)
                        VALUES (%(id)s, %(name)s, %(cedis_id)s, %(day_of_week)s,
                               %(client_ids)s::jsonb, %(is_active)s, 
                               %(created_at)s, %(updated_at)s)
                        ON CONFLICT (id) DO UPDATE
                        SET name = EXCLUDED.name,
                            cedis_id = EXCLUDED.cedis_id,
                            day_of_week = EXCLUDED.day_of_week,
                            client_ids = EXCLUDED.client_ids,
                            is_active = EXCLUDED.is_active,
                            updated_at = EXCLUDED.updated_at
                    """, route_data)
                    
                    self.stats['routes_migrated'] += 1
                    
                    # Mostrar progreso
                    if i % 10 == 0 or i == total_routes:
                        print(f"   Progreso: {i}/{total_routes} rutas migradas", end='\r')
                
                except Exception as e:
                    self.stats['routes_failed'] += 1
                    error_msg = f"Error migrando ruta {route['id']}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"\n   ⚠️  {error_msg}")
            
            # Commit de la transacción
            postgres_conn.commit()
            print(f"\n   ✅ {self.stats['routes_migrated']} rutas migradas correctamente")
            
        except Exception as e:
            postgres_conn.rollback()
            raise Exception(f"Error al migrar rutas: {str(e)}")
        finally:
            sqlite_cursor.close()
            postgres_cursor.close()
    
    def _show_statistics(self) -> None:
        """Muestra estadísticas de la migración."""
        print("\n" + "=" * 70)
        print("📊 ESTADÍSTICAS DE MIGRACIÓN")
        print("=" * 70)
        print(f"✅ Rutas migradas exitosamente: {self.stats['routes_migrated']}")
        
        if self.stats['routes_failed'] > 0:
            print(f"⚠️  Rutas con errores: {self.stats['routes_failed']}")
            print("\nErrores encontrados:")
            for error in self.stats['errors'][:10]:  # Mostrar solo los primeros 10
                print(f"   • {error}")
            if len(self.stats['errors']) > 10:
                print(f"   ... y {len(self.stats['errors']) - 10} errores más")
        
        print("=" * 70)


def verify_migration() -> bool:
    """
    Verifica que la migración se haya realizado correctamente.
    
    Returns:
        True si la verificación es exitosa
    """
    print("\n🔍 Verificando migración...")
    
    try:
        conn = psycopg2.connect(**Config.get_db_connection_params())
        cursor = conn.cursor()
        
        # Contar rutas en PostgreSQL
        cursor.execute("SELECT COUNT(*) FROM routes")
        routes_count = cursor.fetchone()[0]
        
        # Contar rutas activas
        cursor.execute("SELECT COUNT(*) FROM routes WHERE is_active = TRUE")
        active_count = cursor.fetchone()[0]
        
        print(f"✅ Total de rutas en PostgreSQL: {routes_count}")
        print(f"✅ Rutas activas: {active_count}")
        print(f"✅ Rutas inactivas: {routes_count - active_count}")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Error al verificar: {str(e)}")
        return False


if __name__ == "__main__":
    """
    Ejecutar este script directamente para migrar datos.
    """
    try:
        # Cargar variables de entorno
        from dotenv import load_dotenv
        load_dotenv()
        
        print("\n📝 Configuración de migración:")
        print(f"   SQLite: {Config.DATABASE_PATH if hasattr(Config, 'DATABASE_PATH') else 'yedistribuciones.db'}")
        print(f"   PostgreSQL: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
        print()
        
        # Determinar ruta de SQLite
        sqlite_path = Path(__file__).parent / 'yedistribuciones.db'
        
        # Ejecutar migración
        migrator = DataMigrator(str(sqlite_path))
        success = migrator.migrate()
        
        if success:
            # Verificar migración
            verify_migration()
            
            print("\n🎉 ¡Migración completada!")
            print("\n💡 Recomendaciones:")
            print("   1. Verificar que los datos migrados sean correctos")
            print("   2. Mantener una copia de seguridad del archivo SQLite")
            print("   3. Ejecutar 'python main.py' para probar la aplicación")
        else:
            print("\n⚠️  La migración finalizó con errores. Revisar los mensajes anteriores.")
    
    except Exception as e:
        print(f"\n💥 Error fatal: {str(e)}")
        import traceback
        traceback.print_exc()
