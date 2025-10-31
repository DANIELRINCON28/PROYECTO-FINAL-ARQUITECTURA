"""
Configuración de la aplicación Yedistribuciones
Gestiona variables de entorno y configuraciones del sistema.
"""
import os
from typing import Optional


class Config:
    """
    Configuración centralizada de la aplicación.
    
    Patrón de Diseño: Singleton Pattern (implícito)
    - Una única fuente de verdad para la configuración
    """
    
    # Google Maps API
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv(
        'GOOGLE_MAPS_API_KEY',
        None  # Valor por defecto: None (sin API key)
    )
    
    # Ubicación del CEDIS (Centro de Distribución)
    # Coordenadas por defecto: Bogotá, Colombia
    CEDIS_LATITUDE: float = float(os.getenv('CEDIS_LATITUDE', '4.7110'))
    CEDIS_LONGITUDE: float = float(os.getenv('CEDIS_LONGITUDE', '-74.0721'))
    CEDIS_ADDRESS: str = os.getenv('CEDIS_ADDRESS', 'Bogotá, Colombia')
    
    # Base de datos PostgreSQL
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: str = os.getenv('DB_PORT', '5432')
    DB_NAME: str = os.getenv('DB_NAME', 'RutasDB')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    
    # Configuración de pool de conexiones
    DB_MIN_CONNECTIONS: int = int(os.getenv('DB_MIN_CONNECTIONS', '1'))
    DB_MAX_CONNECTIONS: int = int(os.getenv('DB_MAX_CONNECTIONS', '10'))
    
    # Límites de ruta (para sugerencias de división)
    MAX_ROUTE_DISTANCE_KM: float = float(os.getenv('MAX_ROUTE_DISTANCE_KM', '100.0'))
    MAX_ROUTE_DURATION_HOURS: float = float(os.getenv('MAX_ROUTE_DURATION_HOURS', '8.0'))
    
    @classmethod
    def is_google_maps_enabled(cls) -> bool:
        """
        Verifica si Google Maps API está configurada.
        
        Returns:
            True si hay una API key configurada
        """
        return cls.GOOGLE_MAPS_API_KEY is not None and cls.GOOGLE_MAPS_API_KEY.strip() != ''
    
    @classmethod
    def get_cedis_location(cls) -> tuple[float, float]:
        """
        Obtiene las coordenadas del CEDIS.
        
        Returns:
            Tupla (latitud, longitud)
        """
        return (cls.CEDIS_LATITUDE, cls.CEDIS_LONGITUDE)
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        Construye la URL de conexión a PostgreSQL.
        
        Returns:
            URL de conexión en formato DSN
        """
        return (
            f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@"
            f"{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )
    
    @classmethod
    def get_db_connection_params(cls) -> dict:
        """
        Retorna los parámetros de conexión a PostgreSQL.
        
        Returns:
            Diccionario con parámetros de conexión
        """
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD
        }
    
    @classmethod
    def validate_config(cls) -> list[str]:
        """
        Valida la configuración y retorna advertencias si hay problemas.
        
        Returns:
            Lista de mensajes de advertencia
        """
        warnings = []
        
        if not cls.is_google_maps_enabled():
            warnings.append(
                "⚠️ Google Maps API Key no configurada. "
                "La optimización de rutas no estará disponible."
            )
        
        if cls.MAX_ROUTE_DISTANCE_KM <= 0:
            warnings.append("⚠️ MAX_ROUTE_DISTANCE_KM debe ser mayor a 0")
        
        if cls.MAX_ROUTE_DURATION_HOURS <= 0:
            warnings.append("⚠️ MAX_ROUTE_DURATION_HOURS debe ser mayor a 0")
        
        if not cls.DB_PASSWORD:
            warnings.append("⚠️ DB_PASSWORD no configurada. Se recomienda usar una contraseña segura.")
        
        return warnings


# Instrucciones para configurar la API key
SETUP_INSTRUCTIONS = """
📝 CONFIGURACIÓN DE GOOGLE MAPS API

Para habilitar la optimización de rutas, necesitas una API key de Google Maps.

Opción 1: Variable de Entorno (Recomendado)
-------------------------------------------
Windows PowerShell:
    $env:GOOGLE_MAPS_API_KEY="tu_api_key_aqui"
    
Windows CMD:
    set GOOGLE_MAPS_API_KEY=tu_api_key_aqui

Linux/Mac:
    export GOOGLE_MAPS_API_KEY="tu_api_key_aqui"

Opción 2: Archivo .env
----------------------
1. Crea un archivo llamado .env en la raíz del proyecto
2. Agrega la línea:
    GOOGLE_MAPS_API_KEY=tu_api_key_aqui

Opción 3: Editar config.py directamente (No recomendado para producción)
------------------------------------------------------------------------
Cambia la línea:
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv('GOOGLE_MAPS_API_KEY', None)
Por:
    GOOGLE_MAPS_API_KEY: Optional[str] = "tu_api_key_aqui"

Cómo obtener una API key:
--------------------------
1. Ve a: https://console.cloud.google.com/
2. Crea un proyecto o selecciona uno existente
3. Habilita las siguientes APIs:
   - Directions API
   - Distance Matrix API
   - Geocoding API
4. Ve a "Credenciales" y crea una API key
5. (Opcional) Restringe la API key para mayor seguridad

Configurar ubicación del CEDIS:
-------------------------------
$env:CEDIS_LATITUDE="4.7110"
$env:CEDIS_LONGITUDE="-74.0721"
$env:CEDIS_ADDRESS="Calle 123 # 45-67, Bogotá"
"""

if __name__ == "__main__":
    # Ejecutar este archivo directamente muestra la configuración actual
    print("=" * 60)
    print("CONFIGURACIÓN ACTUAL DE YEDISTRIBUCIONES")
    print("=" * 60)
    print(f"Google Maps API: {'✅ Configurada' if Config.is_google_maps_enabled() else '❌ No configurada'}")
    print(f"CEDIS: {Config.CEDIS_ADDRESS}")
    print(f"  Latitud: {Config.CEDIS_LATITUDE}")
    print(f"  Longitud: {Config.CEDIS_LONGITUDE}")
    print(f"Base de datos: PostgreSQL")
    print(f"  Host: {Config.DB_HOST}")
    print(f"  Puerto: {Config.DB_PORT}")
    print(f"  Nombre: {Config.DB_NAME}")
    print(f"  Usuario: {Config.DB_USER}")
    print(f"Límite distancia: {Config.MAX_ROUTE_DISTANCE_KM} km")
    print(f"Límite duración: {Config.MAX_ROUTE_DURATION_HOURS} horas")
    print("=" * 60)
    
    warnings = Config.validate_config()
    if warnings:
        print("\n⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"  {warning}")
        print("\n")
        print(SETUP_INSTRUCTIONS)
