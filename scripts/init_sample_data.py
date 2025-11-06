"""
Script de inicialización de datos de ejemplo.
Ejecutar este script para poblar la base de datos con datos de prueba.
"""
import sqlite3
import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.infrastructure.persistence.sqlite_route_repository import SqliteRouteRepository
from src.application.services.route_service import RouteService
from src.application.dtos import CreateRouteDTO


def initialize_sample_data():
    """
    Inicializa la base de datos con datos de ejemplo.
    """
    print("🔧 Inicializando datos de ejemplo...")
    
    # Conectar a la base de datos
    db_path = Path(__file__).parent / "yedistribuciones.db"
    db_conn = sqlite3.connect(str(db_path))
    
    # Crear repositorio y servicio
    route_repo = SqliteRouteRepository(db_conn)
    route_service = RouteService(repository=route_repo)
    
    print("\n📋 Creando rutas de ejemplo...")
    
    # Datos de ejemplo
    sample_routes = [
        {
            "name": "Ruta Norte 1",
            "cedis_id": "CEDIS_BOG_01",
            "day_of_week": "LUNES",
            "clients": ["CLI_001", "CLI_002", "CLI_003", "CLI_004"]
        },
        {
            "name": "Ruta Norte 2",
            "cedis_id": "CEDIS_BOG_01",
            "day_of_week": "MARTES",
            "clients": ["CLI_005", "CLI_006", "CLI_007"]
        },
        {
            "name": "Ruta Sur 1",
            "cedis_id": "CEDIS_BOG_01",
            "day_of_week": "LUNES",
            "clients": ["CLI_008", "CLI_009", "CLI_010", "CLI_011", "CLI_012"]
        },
        {
            "name": "Ruta Occidente",
            "cedis_id": "CEDIS_MED_01",
            "day_of_week": "MIÉRCOLES",
            "clients": ["CLI_013", "CLI_014", "CLI_015"]
        },
        {
            "name": "Ruta Centro",
            "cedis_id": "CEDIS_BOG_01",
            "day_of_week": "VIERNES",
            "clients": ["CLI_016", "CLI_017", "CLI_018", "CLI_019"]
        }
    ]
    
    created_routes = []
    
    for route_data in sample_routes:
        try:
            # Crear ruta
            dto = CreateRouteDTO(
                name=route_data["name"],
                cedis_id=route_data["cedis_id"],
                day_of_week=route_data["day_of_week"]
            )
            
            route = route_service.create_route(dto)
            
            # Asignar clientes
            for client_id in route_data["clients"]:
                route_service.assign_client_to_route(route.id, client_id)
            
            created_routes.append(route)
            print(f"  ✅ Creada: {route.name} - {route.day_of_week} - {len(route_data['clients'])} clientes")
        
        except Exception as e:
            print(f"  ❌ Error creando {route_data['name']}: {str(e)}")
    
    print(f"\n✅ Datos de ejemplo inicializados exitosamente!")
    print(f"📊 Total de rutas creadas: {len(created_routes)}")
    
    # Cerrar conexión
    db_conn.commit()
    db_conn.close()
    
    print("\n🚀 Puede ahora ejecutar: streamlit run main.py")


if __name__ == "__main__":
    initialize_sample_data()
