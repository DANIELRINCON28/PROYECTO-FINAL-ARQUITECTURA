"""
Script para eliminar la tabla 'routes' de la base de datos.
"""
import psycopg2
from config import Config


def drop_routes_table():
    """Elimina la tabla 'routes' de la base de datos."""
    print("=" * 70)
    print("🗑️  ELIMINANDO TABLA: ROUTES")
    print("=" * 70)
    
    try:
        conn = psycopg2.connect(**Config.get_db_connection_params())
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'routes'
            )
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            # Eliminar la tabla
            cursor.execute("DROP TABLE IF EXISTS routes CASCADE")
            conn.commit()
            print("✅ Tabla 'routes' eliminada exitosamente")
        else:
            print("ℹ️  La tabla 'routes' no existe en la base de datos")
        
        cursor.close()
        conn.close()
        
        print("=" * 70)
        
    except psycopg2.Error as e:
        print(f"❌ Error al eliminar tabla: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    success = drop_routes_table()
    exit(0 if success else 1)
