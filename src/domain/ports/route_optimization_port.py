"""
Route Optimization Port (Output Port)
Define el contrato para servicios de optimización de rutas.
Abstracción que permite la inversión de dependencias (DIP).
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class RouteOptimizationResult:
    """Resultado de la optimización de ruta."""
    optimized_order: List[int]  # Índices en orden óptimo
    total_distance_km: float
    total_duration_minutes: float
    waypoints: List[Dict[str, float]]  # Lista de coordenadas ordenadas


@dataclass
class ClientLocation:
    """Ubicación de un cliente."""
    client_id: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RouteOptimizationPort(ABC):
    """
    Puerto de salida para servicios de optimización de rutas.
    Permite integrar diferentes proveedores (Google Maps, OpenRoute, etc.)
    sin afectar la lógica de negocio.
    """
    
    @abstractmethod
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convierte una dirección en coordenadas geográficas.
        
        Args:
            address: Dirección a geocodificar
            
        Returns:
            Tupla (latitud, longitud) o None si no se encuentra
        """
        pass
    
    @abstractmethod
    def calculate_distance_matrix(
        self, 
        origins: List[Tuple[float, float]], 
        destinations: List[Tuple[float, float]]
    ) -> List[List[float]]:
        """
        Calcula matriz de distancias entre múltiples puntos.
        
        Args:
            origins: Lista de coordenadas de origen
            destinations: Lista de coordenadas de destino
            
        Returns:
            Matriz de distancias en kilómetros
        """
        pass
    
    @abstractmethod
    def optimize_route(
        self, 
        origin: Tuple[float, float],
        waypoints: List[Tuple[float, float]],
        destination: Optional[Tuple[float, float]] = None
    ) -> RouteOptimizationResult:
        """
        Optimiza el orden de visita de múltiples puntos.
        
        Args:
            origin: Punto de inicio (CEDIS)
            waypoints: Lista de puntos a visitar (clientes)
            destination: Punto final (opcional, por defecto regresa al origin)
            
        Returns:
            Resultado con orden optimizado y métricas
        """
        pass
    
    @abstractmethod
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
        pass
