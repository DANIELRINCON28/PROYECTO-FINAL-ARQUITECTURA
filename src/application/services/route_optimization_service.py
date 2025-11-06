"""
Route Optimization Application Service
Casos de uso relacionados con optimización de rutas usando servicios externos.
"""
from typing import List, Dict, Optional, Tuple
from src.domain.ports.route_repository_port import RouteRepositoryPort
from src.domain.ports.route_optimization_port import (
    RouteOptimizationPort,
    ClientLocation,
    RouteOptimizationResult
)
from src.domain.models.route import Route


class RouteOptimizationService:
    """
    Servicio de aplicación para optimización de rutas.
    Coordina entre el repositorio de rutas y el servicio de optimización.
    
    Patrón de Diseño: Service Layer Pattern
    - Orquesta múltiples operaciones del dominio
    - Mantiene la lógica de coordinación fuera del dominio
    """
    
    def __init__(
        self,
        route_repository: RouteRepositoryPort,
        optimization_service: RouteOptimizationPort
    ) -> None:
        """
        Inyección de dependencias: recibe abstracciones (puertos).
        
        Args:
            route_repository: Puerto del repositorio de rutas
            optimization_service: Puerto del servicio de optimización
        """
        self._route_repo = route_repository
        self._optimizer = optimization_service
    
    def geocode_clients(
        self,
        clients: List[ClientLocation]
    ) -> List[ClientLocation]:
        """
        Geocodifica las direcciones de múltiples clientes.
        
        Args:
            clients: Lista de ubicaciones de clientes
            
        Returns:
            Lista de clientes con coordenadas actualizadas
        """
        geocoded_clients = []
        
        for client in clients:
            if client.latitude is None or client.longitude is None:
                # Geocodificar dirección
                coords = self._optimizer.geocode_address(client.address)
                
                if coords:
                    # Crear nuevo objeto con coordenadas
                    geocoded_client = ClientLocation(
                        client_id=client.client_id,
                        address=client.address,
                        latitude=coords[0],
                        longitude=coords[1]
                    )
                    geocoded_clients.append(geocoded_client)
                else:
                    # Mantener sin coordenadas
                    geocoded_clients.append(client)
            else:
                geocoded_clients.append(client)
        
        return geocoded_clients
    
    def optimize_route_order(
        self,
        route_id: str,
        cedis_location: Tuple[float, float],
        client_locations: List[ClientLocation]
    ) -> RouteOptimizationResult:
        """
        Optimiza el orden de visita de clientes en una ruta.
        
        Args:
            route_id: ID de la ruta a optimizar
            cedis_location: Coordenadas del CEDIS (punto de inicio)
            client_locations: Lista de ubicaciones de clientes
            
        Returns:
            Resultado de optimización con nuevo orden
        """
        # Filtrar solo clientes con coordenadas
        clients_with_coords = [
            c for c in client_locations 
            if c.latitude is not None and c.longitude is not None
        ]
        
        if len(clients_with_coords) == 0:
            raise ValueError("Ningún cliente tiene coordenadas para optimizar")
        
        # Extraer coordenadas
        waypoints = [
            (c.latitude, c.longitude) 
            for c in clients_with_coords
        ]
        
        # Optimizar usando el servicio externo
        result = self._optimizer.optimize_route(
            origin=cedis_location,
            waypoints=waypoints,
            destination=cedis_location  # Regresar al CEDIS
        )
        
        return result
    
    def calculate_route_metrics(
        self,
        cedis_location: Tuple[float, float],
        client_locations: List[ClientLocation]
    ) -> Dict[str, float]:
        """
        Calcula métricas de la ruta (distancia total, tiempo estimado).
        
        Args:
            cedis_location: Coordenadas del CEDIS
            client_locations: Lista de ubicaciones de clientes en orden
            
        Returns:
            Diccionario con métricas calculadas
        """
        clients_with_coords = [
            c for c in client_locations 
            if c.latitude is not None and c.longitude is not None
        ]
        
        if len(clients_with_coords) == 0:
            return {
                'total_distance_km': 0.0,
                'total_duration_minutes': 0.0,
                'clients_count': 0
            }
        
        waypoints = [
            (c.latitude, c.longitude) 
            for c in clients_with_coords
        ]
        
        # Calcular sin optimizar (orden actual)
        all_points = [cedis_location] + waypoints + [cedis_location]
        
        directions = self._optimizer.get_route_directions(all_points)
        
        if directions and 'legs' in directions:
            total_distance_m = sum(leg['distance']['value'] for leg in directions['legs'])
            total_duration_s = sum(leg['duration']['value'] for leg in directions['legs'])
            
            return {
                'total_distance_km': total_distance_m / 1000.0,
                'total_duration_minutes': total_duration_s / 60.0,
                'clients_count': len(clients_with_coords)
            }
        
        return {
            'total_distance_km': 0.0,
            'total_duration_minutes': 0.0,
            'clients_count': len(clients_with_coords)
        }
    
    def suggest_route_split(
        self,
        route_id: str,
        max_distance_km: float,
        max_duration_hours: float,
        cedis_location: Tuple[float, float],
        client_locations: List[ClientLocation]
    ) -> Dict:
        """
        Sugiere si una ruta debería dividirse basándose en métricas reales.
        
        Args:
            route_id: ID de la ruta
            max_distance_km: Distancia máxima permitida
            max_duration_hours: Duración máxima permitida
            cedis_location: Ubicación del CEDIS
            client_locations: Ubicaciones de clientes
            
        Returns:
            Diccionario con sugerencia y punto de división
        """
        metrics = self.calculate_route_metrics(cedis_location, client_locations)
        
        should_split = (
            metrics['total_distance_km'] > max_distance_km or
            metrics['total_duration_minutes'] > max_duration_hours * 60
        )
        
        split_suggestion = {
            'should_split': should_split,
            'reason': [],
            'current_metrics': metrics,
            'suggested_split_point': len(client_locations) // 2 if should_split else None
        }
        
        if metrics['total_distance_km'] > max_distance_km:
            split_suggestion['reason'].append(
                f"Distancia ({metrics['total_distance_km']:.1f} km) excede límite ({max_distance_km} km)"
            )
        
        if metrics['total_duration_minutes'] > max_duration_hours * 60:
            split_suggestion['reason'].append(
                f"Duración ({metrics['total_duration_minutes']:.1f} min) excede límite ({max_duration_hours * 60} min)"
            )
        
        return split_suggestion
    
    def test_optimization_service(self) -> bool:
        """
        Prueba la conexión con el servicio de optimización.
        
        Returns:
            True si el servicio está disponible
        """
        try:
            test_address = "Bogotá, Colombia"
            result = self._optimizer.geocode_address(test_address)
            return result is not None
        except Exception as e:
            print(f"Error probando servicio de optimización: {str(e)}")
            return False
