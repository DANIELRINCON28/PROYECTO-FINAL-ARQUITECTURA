"""
Geo Distance Provider Port (Domain Layer)
Puerto abstracto para obtener distancias entre coordenadas geográficas.
NO depende de ninguna tecnología externa (Google Maps, OpenStreetMap, etc.)
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class GeoCoordinate:
    """Value Object que representa una coordenada geográfica."""
    latitude: float
    longitude: float
    
    def __post_init__(self) -> None:
        """Validaciones de coordenadas."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitud inválida: {self.latitude}. Debe estar entre -90 y 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitud inválida: {self.longitude}. Debe estar entre -180 y 180")


@dataclass
class DistanceResult:
    """Value Object que representa el resultado de una medición de distancia."""
    distance_km: float
    duration_minutes: float
    
    def __post_init__(self) -> None:
        """Validaciones de resultados."""
        if self.distance_km < 0:
            raise ValueError("La distancia no puede ser negativa")
        if self.duration_minutes < 0:
            raise ValueError("La duración no puede ser negativa")


class GeoDistanceProviderPort(ABC):
    """
    Puerto abstracto para proveedores de cálculo de distancias geográficas.
    
    Patrón de Diseño: Port (Hexagonal Architecture)
    - Define el contrato que deben cumplir los adaptadores de infraestructura
    - Permite cambiar la implementación sin afectar el dominio
    """
    
    @abstractmethod
    def calculate_distance(
        self, 
        origin: GeoCoordinate, 
        destination: GeoCoordinate
    ) -> DistanceResult:
        """
        Calcula la distancia y tiempo entre dos coordenadas.
        
        Args:
            origin: Coordenada de origen
            destination: Coordenada de destino
            
        Returns:
            DistanceResult con distancia en km y duración en minutos
            
        Raises:
            Exception: Si no se puede calcular la distancia
        """
        pass
    
    @abstractmethod
    def calculate_distance_matrix(
        self, 
        origins: List[GeoCoordinate], 
        destinations: List[GeoCoordinate]
    ) -> List[List[DistanceResult]]:
        """
        Calcula una matriz de distancias entre múltiples orígenes y destinos.
        
        Args:
            origins: Lista de coordenadas de origen
            destinations: Lista de coordenadas de destino
            
        Returns:
            Matriz bidimensional donde [i][j] es la distancia del origen i al destino j
            
        Raises:
            Exception: Si no se puede calcular la matriz
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica si el proveedor está disponible y configurado correctamente.
        
        Returns:
            True si el servicio está disponible, False en caso contrario
        """
        pass
