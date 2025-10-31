"""
Main Entry Point - Dependency Injection / Assembler
Este archivo ensambla todas las capas de la arquitectura hexagonal.
Aquí se realiza la inyección de dependencias.
"""
import sqlite3
import sys
from pathlib import Path
from typing import Optional

# Agregar el directorio src al path de Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.infrastructure.persistence.sqlite_route_repository import SqliteRouteRepository
from src.application.services.route_service import RouteService
from src.application.services.route_optimization_service import RouteOptimizationService
from src.infrastructure.services.google_maps_service import GoogleMapsOptimizationService
from src.infrastructure.ui.streamlit_app import run_ui
from config import Config


def main() -> None:
    """
    Función principal que ensambla la aplicación.
    
    Pasos:
    1. Validar configuración
    2. Configurar el adaptador de persistencia (SQLite)
    3. Configurar el servicio de optimización (Google Maps) si está disponible
    4. Inyectar adaptadores en los servicios de aplicación
    5. Iniciar el adaptador de UI (Streamlit), pasándole los servicios
    """
    
    # 1. Validar configuración
    print("=" * 60)
    print("🔧 CONFIGURACIÓN DE YEDISTRIBUCIONES")
    print("=" * 60)
    
    warnings = Config.validate_config()
    for warning in warnings:
        print(warning)
    
    if Config.is_google_maps_enabled():
        print("✅ Google Maps API configurada")
        print(f"📍 CEDIS: {Config.CEDIS_ADDRESS}")
    else:
        print("ℹ️  Optimización de rutas deshabilitada (sin API key)")
    
    print("=" * 60)
    print()
    
    # 2. Configurar el adaptador de persistencia
    db_path = Path(__file__).parent / Config.DATABASE_PATH
    
    print(f"📊 Conectando a la base de datos: {db_path}")
    db_conn = sqlite3.connect(str(db_path), check_same_thread=False)
    
    # Crear el repositorio (Adaptador Conducido)
    route_repo = SqliteRouteRepository(db_conn)
    print("✅ Repositorio de rutas inicializado")
    
    # 3. Configurar el servicio de optimización (opcional)
    optimization_service: Optional[RouteOptimizationService] = None
    
    if Config.is_google_maps_enabled():
        try:
            # Crear el adaptador de Google Maps
            google_maps_adapter = GoogleMapsOptimizationService(
                api_key=Config.GOOGLE_MAPS_API_KEY
            )
            
            # Probar conexión
            if google_maps_adapter.test_connection():
                # Crear el servicio de aplicación de optimización
                optimization_service = RouteOptimizationService(
                    route_repository=route_repo,
                    optimization_service=google_maps_adapter
                )
                print("✅ Servicio de optimización de rutas inicializado")
            else:
                print("⚠️  No se pudo conectar con Google Maps API")
        except Exception as e:
            print(f"⚠️  Error al inicializar optimización: {str(e)}")
    
    # 4. Inyectar adaptadores en el servicio de aplicación principal
    route_service = RouteService(repository=route_repo)
    print("✅ Servicio de rutas inicializado")
    
    # 5. Iniciar el adaptador de UI (Adaptador Conductor)
    print("🚀 Iniciando interfaz de usuario Streamlit...")
    print("=" * 60)
    run_ui(route_service, optimization_service)


if __name__ == "__main__":
    main()
