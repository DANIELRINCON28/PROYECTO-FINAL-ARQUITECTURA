"""
Script de Ejemplo: Optimización Inteligente de Rutas (TSP)

Este script demuestra cómo usar el módulo de optimización inteligente
para reordenar clientes en una ruta minimizando la distancia total.

Ejecutar:
    python scripts/example_optimize_route.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.application.factories.service_factory import ServiceFactory
from src.application.dtos import OptimizeRouteDTO
from src.domain.models.client import Client
from config import Config


def print_separator():
    """Imprime una línea separadora."""
    print("=" * 80)


def main():
    """Función principal del script."""
    print_separator()
    print("🚀 DEMOSTRACIÓN: Optimización Inteligente de Rutas (TSP)")
    print_separator()
    
    # 1. Crear factory y servicios
    print("\n1️⃣ Inicializando servicios...")
    factory = ServiceFactory()
    optimization_service = factory.create_optimization_service()
    
    if not optimization_service:
        print("❌ Error: No se pudo crear el servicio de optimización")
        return
    
    print("✅ Servicios creados exitosamente")
    
    # 2. Verificar disponibilidad
    print("\n2️⃣ Verificando disponibilidad de servicios...")
    availability = optimization_service.check_optimization_availability()
    
    print(f"   • Google Maps API: {'✅' if availability.get('geo_distance_provider_available') else '❌'}")
    print(f"   • OR-Tools TSP Solver: {'✅' if availability.get('optimization_solver_available') else '⚠️ (usando fallback)'}")
    print(f"   • Optimización Inteligente: {'✅' if availability.get('intelligent_optimization_available') else '❌'}")
    
    if not availability.get('intelligent_optimization_available'):
        print("\n⚠️ La optimización inteligente no está disponible.")
        print("   Verifique que:")
        print("   - GOOGLE_MAPS_API_KEY esté configurada en .env")
        print("   - googlemaps y ortools estén instalados")
        return
    
    # 3. Crear clientes de ejemplo en Bogotá
    print("\n3️⃣ Creando datos de ejemplo...")
    print(f"   CEDIS: {Config.CEDIS_ADDRESS}")
    print(f"   Coordenadas: ({Config.CEDIS_LATITUDE}, {Config.CEDIS_LONGITUDE})")
    
    # Clientes ficticios en diferentes zonas de Bogotá
    example_clients = [
        Client(
            id="client-001",
            name="Cliente Norte",
            address="Calle 127 con Autopista Norte, Bogotá",
            latitude=4.7275,
            longitude=-74.0386,
            phone="3001234567"
        ),
        Client(
            id="client-002",
            name="Cliente Sur",
            address="Av. Boyacá con Av. Américas, Bogotá",
            latitude=4.6390,
            longitude=-74.1164,
            phone="3001234568"
        ),
        Client(
            id="client-003",
            name="Cliente Centro",
            address="Plaza de Bolívar, Bogotá",
            latitude=4.5981,
            longitude=-74.0758,
            phone="3001234569"
        ),
        Client(
            id="client-004",
            name="Cliente Occidente",
            address="Av. Ciudad de Cali con Calle 26, Bogotá",
            latitude=4.6598,
            longitude=-74.1376,
            phone="3001234570"
        )
    ]
    
    print(f"   Clientes creados: {len(example_clients)}")
    for i, client in enumerate(example_clients, 1):
        print(f"      {i}. {client.name} - ({client.latitude}, {client.longitude})")
    
    # 4. Crear una ruta de ejemplo (en un caso real, esta vendría de la BD)
    print("\n4️⃣ Preparando solicitud de optimización...")
    
    # Nota: En un caso real, primero crearías la ruta en la BD y asignarías clientes
    # Aquí solo demostramos la estructura del DTO
    
    dto = OptimizeRouteDTO(
        route_id="demo-route-001",
        cedis_latitude=Config.CEDIS_LATITUDE,
        cedis_longitude=Config.CEDIS_LONGITUDE,
        optimization_strategy="distance"  # Minimizar distancia
    )
    
    print(f"   • ID Ruta: {dto.route_id}")
    print(f"   • Estrategia: {dto.optimization_strategy}")
    print(f"   • Clientes a optimizar: {len(example_clients)}")
    
    # 5. Información sobre el proceso
    print("\n5️⃣ Proceso de optimización:")
    print("   1. Calcular matriz de distancias (Google Maps Distance Matrix API)")
    print("   2. Resolver problema TSP (OR-Tools)")
    print("   3. Reordenar clientes por orden óptimo")
    print("   4. Actualizar ruta en base de datos")
    print("   5. Retornar resultado con métricas")
    
    print("\n" + "=" * 80)
    print("📝 NOTA: Este es un script de demostración")
    print("=" * 80)
    print("\nPara usar la optimización en producción:")
    print("1. Crear una ruta usando RouteService.create_route()")
    print("2. Asignar clientes usando RouteService.assign_client_to_route()")
    print("3. Llamar a optimization_service.optimize_route_intelligent(dto, clients)")
    print("4. La ruta se actualizará automáticamente con el orden optimizado")
    
    print("\n💡 Ejemplo de código:")
    print("""
    # 1. Crear ruta
    route_service = factory.create_route_service()
    route = route_service.create_route(CreateRouteDTO(...))
    
    # 2. Asignar clientes
    for client_id in client_ids:
        route_service.assign_client_to_route(route.id, client_id)
    
    # 3. Optimizar
    dto = OptimizeRouteDTO(
        route_id=route.id,
        cedis_latitude=Config.CEDIS_LATITUDE,
        cedis_longitude=Config.CEDIS_LONGITUDE,
        optimization_strategy="distance"
    )
    
    result = optimization_service.optimize_route_intelligent(dto, clients)
    
    # 4. Ver resultado
    print(f"Distancia total: {result.total_distance_km:.2f} km")
    print(f"Orden optimizado: {result.optimized_client_order}")
    """)
    
    print("\n" + "=" * 80)
    print("✅ Demostración completada")
    print("=" * 80)
    print("\n📚 Para más información, consulte:")
    print("   docs/ROUTE_OPTIMIZATION_TSP.md")
    print_separator()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
