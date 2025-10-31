"""
Google Maps Route Optimization Service - Infrastructure Adapter
Implementación concreta del puerto RouteOptimizationPort usando Google Maps API.
Este adaptador sigue el patrón Adapter para integrar servicios externos.
"""
import googlemaps
from typing import List, Tuple, Dict, Optional
from datetime import datetime
from src.domain.ports.route_optimization_port import (
    RouteOptimizationPort,
    RouteOptimizationResult,
    ClientLocation
)


class GoogleMapsOptimizationService(RouteOptimizationPort):
    """
    Adaptador que implementa RouteOptimizationPort usando Google Maps API.
    
    Patrón de Diseño: Adapter Pattern
    - Adapta la API de Google Maps a nuestra abstracción del dominio
    - Permite cambiar de proveedor sin afectar la lógica de negocio
    """
    
    def __init__(self, api_key: str) -> None:
        """
        Inicializa el servicio con la API Key de Google Maps.
        
        Args:
            api_key: Clave de API de Google Maps
        """
        if not api_key or api_key.strip() == "":
            raise ValueError("API Key de Google Maps es requerida")
        
        self._client = googlemaps.Client(key=api_key)
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convierte una dirección en coordenadas usando Google Geocoding API.
        
        Args:
            address: Dirección a geocodificar
            
        Returns:
            Tupla (latitud, longitud) o None si no se encuentra
        """
        try:
            result = self._client.geocode(address)
            
            if result and len(result) > 0:
                location = result[0]['geometry']['location']
                return (location['lat'], location['lng'])
            
            return None
        
        except Exception as e:
            print(f"Error en geocodificación: {str(e)}")
            return None
    
    def calculate_distance_matrix(
        self, 
        origins: List[Tuple[float, float]], 
        destinations: List[Tuple[float, float]]
    ) -> List[List[float]]:
        """
        Calcula matriz de distancias usando Google Distance Matrix API.
        
        Args:
            origins: Lista de coordenadas de origen
            destinations: Lista de coordenadas de destino
            
        Returns:
            Matriz de distancias en kilómetros
        """
        try:
            result = self._client.distance_matrix(
                origins=origins,
                destinations=destinations,
                mode="driving",
                units="metric"
            )
            
            matrix = []
            for row in result['rows']:
                distances = []
                for element in row['elements']:
                    if element['status'] == 'OK':
                        # Convertir metros a kilómetros
                        distance_km = element['distance']['value'] / 1000.0
                        distances.append(distance_km)
                    else:
                        distances.append(float('inf'))
                matrix.append(distances)
            
            return matrix
        
        except Exception as e:
            print(f"Error calculando matriz de distancias: {str(e)}")
            return [[float('inf')] * len(destinations) for _ in origins]
    
    def optimize_route(
        self, 
        origin: Tuple[float, float],
        waypoints: List[Tuple[float, float]],
        destination: Optional[Tuple[float, float]] = None
    ) -> RouteOptimizationResult:
        """
        Optimiza ruta usando Google Directions API con waypoint optimization.
        
        Args:
            origin: Punto de inicio (CEDIS)
            waypoints: Lista de puntos a visitar (clientes)
            destination: Punto final (si None, regresa al origin)
            
        Returns:
            Resultado con orden optimizado y métricas
        """
        if destination is None:
            destination = origin
        
        try:
            # Usar Google Directions API con optimización de waypoints
            result = self._client.directions(
                origin=origin,
                destination=destination,
                waypoints=waypoints,
                optimize_waypoints=True,  # ¡Optimización automática!
                mode="driving"
            )
            
            if not result or len(result) == 0:
                # Fallback: orden original
                return self._create_fallback_result(origin, waypoints, destination)
            
            route = result[0]
            
            # Obtener orden optimizado de waypoints
            waypoint_order = route.get('waypoint_order', list(range(len(waypoints))))
            
            # Calcular distancia y duración total
            total_distance_m = 0
            total_duration_s = 0
            
            for leg in route['legs']:
                total_distance_m += leg['distance']['value']
                total_duration_s += leg['duration']['value']
            
            # Construir lista de waypoints en orden optimizado
            optimized_waypoints = [origin]
            for idx in waypoint_order:
                optimized_waypoints.append(waypoints[idx])
            if destination != origin:
                optimized_waypoints.append(destination)
            
            # Convertir coordenadas a diccionarios
            waypoints_dicts = [
                {'lat': coord[0], 'lng': coord[1]} 
                for coord in optimized_waypoints
            ]
            
            return RouteOptimizationResult(
                optimized_order=waypoint_order,
                total_distance_km=total_distance_m / 1000.0,
                total_duration_minutes=total_duration_s / 60.0,
                waypoints=waypoints_dicts
            )
        
        except Exception as e:
            print(f"Error optimizando ruta: {str(e)}")
            return self._create_fallback_result(origin, waypoints, destination)
    
    def get_route_directions(
        self,
        waypoints: List[Tuple[float, float]]
    ) -> Dict:
        """
        Obtiene direcciones detalladas de la ruta.
        
        Args:
            waypoints: Lista ordenada de puntos
            
        Returns:
            Diccionario con información de la ruta
        """
        if len(waypoints) < 2:
            return {}
        
        try:
            origin = waypoints[0]
            destination = waypoints[-1]
            intermediate = waypoints[1:-1] if len(waypoints) > 2 else []
            
            result = self._client.directions(
                origin=origin,
                destination=destination,
                waypoints=intermediate,
                mode="driving"
            )
            
            if result and len(result) > 0:
                return result[0]
            
            return {}
        
        except Exception as e:
            print(f"Error obteniendo direcciones: {str(e)}")
            return {}
    
    def _create_fallback_result(
        self,
        origin: Tuple[float, float],
        waypoints: List[Tuple[float, float]],
        destination: Tuple[float, float]
    ) -> RouteOptimizationResult:
        """
        Crea un resultado con orden original cuando falla la optimización.
        """
        all_points = [origin] + waypoints
        if destination != origin:
            all_points.append(destination)
        
        waypoints_dicts = [
            {'lat': coord[0], 'lng': coord[1]} 
            for coord in all_points
        ]
        
        return RouteOptimizationResult(
            optimized_order=list(range(len(waypoints))),
            total_distance_km=0.0,
            total_duration_minutes=0.0,
            waypoints=waypoints_dicts
        )
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con Google Maps API.
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            # Geocodificar una dirección conocida para probar
            result = self._client.geocode("Bogotá, Colombia")
            return result is not None and len(result) > 0
        except Exception as e:
            print(f"Error probando conexión: {str(e)}")
            return False
