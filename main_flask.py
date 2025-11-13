"""
Main Entry Point - Dependency Injection / Assembler
Este archivo ensambla todas las capas de la arquitectura hexagonal.
Aquí se realiza la inyección de dependencias.

Migración: Flask App (de Streamlit a Flask)
"""
import sys
from pathlib import Path
from typing import Optional

# Agregar el directorio src al path de Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.infrastructure.persistence.postgres_route_repository import PostgresRouteRepository
from src.application.services.route_service import RouteService
from src.application.services.route_optimization_service import RouteOptimizationService
from src.infrastructure.services.google_maps_service import GoogleMapsOptimizationService
from src.infrastructure.ui.flask_app import run_flask_app
from config import Config


def main() -> None:
    """
    Función principal que ensambla la aplicación.
    
    Pasos:
    1. Validar configuración
    2. Configurar el adaptador de persistencia (PostgreSQL)
    3. Configurar el servicio de optimización (Google Maps) si está disponible
    4. Inyectar adaptadores en los servicios de aplicación
    5. Iniciar el adaptador de UI (Flask), pasándole los servicios
    """
    
    print("=" * 60)
    print("🔧 CONFIGURACIÓN DE YEDISTRIBUCIONES")
    print("=" * 60)
    print(f"Base de datos: {Config.DB_TYPE}")
    print(f"Host: {Config.DB_HOST}")
    print(f"Puerto: {Config.DB_PORT}")
    print(f"Base de datos: {Config.DB_NAME}")
    print(f"Optimización (Google Maps): {'✅ Habilitada' if Config.GOOGLE_MAPS_API_KEY else '❌ Deshabilitada'}")
    print("=" * 60)
    print()
    
    # 2. Configurar adaptador de persistencia (Driven Adapter - Infraestructura)
    print("📦 Configurando repositorio PostgreSQL...")
    connection_params = {
        'host': Config.DB_HOST,
        'port': Config.DB_PORT,
        'database': Config.DB_NAME,
        'user': Config.DB_USER,
        'password': Config.DB_PASSWORD
    }
    repository = PostgresRouteRepository(connection_params=connection_params)
    print("✅ Repositorio configurado")
    
    # 3. Configurar servicio de optimización (Driven Adapter - Infraestructura)
    optimization_service: Optional[RouteOptimizationService] = None
    if Config.GOOGLE_MAPS_API_KEY and Config.GOOGLE_MAPS_API_KEY.strip() and len(Config.GOOGLE_MAPS_API_KEY) > 10:
        try:
            print("🗺️ Configurando Google Maps API...")
            google_maps_adapter = GoogleMapsOptimizationService(
                api_key=Config.GOOGLE_MAPS_API_KEY
            )
            optimization_service = RouteOptimizationService(
                optimization_port=google_maps_adapter
            )
            print("✅ Google Maps configurado")
        except Exception as e:
            print(f"⚠️ Error al configurar Google Maps: {str(e)}")
            print("⚠️ La aplicación continuará sin optimización")
            optimization_service = None
    else:
        print("⚠️ Google Maps API Key no configurada - Optimización deshabilitada")
        print("   La aplicación funcionará con todas las funcionalidades básicas")
    
    # 4. Inyectar dependencias en servicios de aplicación
    print("🧩 Inyectando dependencias en capa de aplicación...")
    route_service = RouteService(repository=repository)
    print("✅ Servicios de aplicación configurados")
    
    print()
    print("=" * 60)
    print("🚀 INICIANDO APLICACIÓN FLASK")
    print("=" * 60)
    print("📍 URL: http://localhost:5000")
    print("🌐 Interfaz: Flask Web Application")
    print("🏗️ Arquitectura: Hexagonal (Ports & Adapters)")
    print("=" * 60)
    print()
    
    # 5. Iniciar adaptador de UI Flask (Driving Adapter - Infraestructura)
    try:
        run_flask_app(
            route_service=route_service,
            optimization_service=optimization_service,
            debug=Config.DEBUG,
            port=Config.FLASK_PORT
        )
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error al iniciar la aplicación: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
