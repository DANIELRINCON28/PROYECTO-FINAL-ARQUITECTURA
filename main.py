"""
Main Entry Point - Dependency Injection / Assembler
Este archivo ensambla todas las capas de la arquitectura hexagonal.
Aquí se realiza la inyección de dependencias.
"""
import sqlite3
import sys
from pathlib import Path

# Agregar el directorio src al path de Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.infrastructure.persistence.sqlite_route_repository import SqliteRouteRepository
from src.application.services.route_service import RouteService
from src.infrastructure.ui.streamlit_app import run_ui


def main() -> None:
    """
    Función principal que ensambla la aplicación.
    
    Pasos:
    1. Configurar el adaptador de persistencia (SQLite)
    2. Inyectar el adaptador en el servicio de aplicación
    3. Iniciar el adaptador de UI (Streamlit), pasándole el servicio
    """
    
    # 1. Configurar el adaptador de persistencia
    # La base de datos se creará en el directorio del proyecto
    db_path = Path(__file__).parent / "yedistribuciones.db"
    
    print(f"📊 Conectando a la base de datos: {db_path}")
    db_conn = sqlite3.connect(str(db_path), check_same_thread=False)
    
    # Crear el repositorio (Adaptador Conducido)
    route_repo = SqliteRouteRepository(db_conn)
    print("✅ Repositorio de rutas inicializado")
    
    # 2. Inyectar el adaptador en el servicio de aplicación
    route_service = RouteService(repository=route_repo)
    print("✅ Servicio de rutas inicializado")
    
    # 3. Iniciar el adaptador de UI (Adaptador Conductor)
    print("🚀 Iniciando interfaz de usuario Streamlit...")
    print("=" * 60)
    run_ui(route_service)


if __name__ == "__main__":
    main()
