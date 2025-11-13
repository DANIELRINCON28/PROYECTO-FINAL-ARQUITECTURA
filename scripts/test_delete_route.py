"""
Script de prueba: Funcionalidad de Eliminar Ruta
Prueba la implementación completa del caso de uso RF-RUT-08.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.application.services.route_service import RouteService
from src.infrastructure.persistence.postgres_route_repository import PostgresRouteRepository
from src.application.dtos import CreateRouteDTO
from config import Config


def test_delete_route():
    """Prueba la eliminación de rutas."""
    print("🧪 Iniciando prueba de eliminación de rutas...\n")
    
    # Configurar repositorio
    connection_params = {
        'host': Config.DB_HOST,
        'port': int(Config.DB_PORT),
        'database': Config.DB_NAME,
        'user': Config.DB_USER,
        'password': Config.DB_PASSWORD
    }
    
    repository = PostgresRouteRepository(connection_params)
    service = RouteService(repository)
    
    # Test 1: Crear y eliminar ruta sin clientes
    print("📝 Test 1: Crear y eliminar ruta sin clientes")
    print("-" * 50)
    
    try:
        # Crear ruta de prueba
        dto = CreateRouteDTO(
            name="Ruta Test Eliminación",
            cedis_id="13",
            day_of_week="LUNES"
        )
        
        route = service.create_route(dto)
        print(f"✅ Ruta creada: {route.id} - {route.name}")
        
        # Intentar eliminar (debería funcionar)
        service.delete_route(route.id)
        print(f"✅ Ruta eliminada exitosamente\n")
        
    except Exception as e:
        print(f"❌ Error en Test 1: {e}\n")
        return False
    
    # Test 2: Intentar eliminar ruta con clientes
    print("📝 Test 2: Intentar eliminar ruta con clientes (debe fallar)")
    print("-" * 50)
    
    try:
        # Buscar una ruta con clientes
        all_routes = service.get_all_routes(include_inactive=False)
        route_with_clients = None
        
        for route in all_routes:
            if route.client_count > 0:
                route_with_clients = route
                break
        
        if route_with_clients:
            print(f"📍 Ruta encontrada: {route_with_clients.name} ({route_with_clients.client_count} clientes)")
            
            try:
                service.delete_route(route_with_clients.id)
                print("❌ ERROR: No debería permitir eliminar ruta con clientes\n")
                return False
            except ValueError as e:
                print(f"✅ Validación correcta: {e}\n")
        else:
            print("⚠️ No hay rutas con clientes para probar\n")
    
    except Exception as e:
        print(f"❌ Error en Test 2: {e}\n")
        return False
    
    # Test 3: Intentar eliminar ruta inexistente
    print("📝 Test 3: Intentar eliminar ruta inexistente (debe fallar)")
    print("-" * 50)
    
    try:
        service.delete_route("id-inexistente-999")
        print("❌ ERROR: No debería permitir eliminar ruta inexistente\n")
        return False
    except ValueError as e:
        print(f"✅ Validación correcta: {e}\n")
    
    print("=" * 50)
    print("✅ Todos los tests pasaron exitosamente!")
    print("=" * 50)
    return True


if __name__ == '__main__':
    try:
        success = test_delete_route()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
