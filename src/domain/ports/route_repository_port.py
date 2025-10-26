"""
Route Repository Port (Output Port)
Define el contrato que debe cumplir cualquier repositorio de rutas.
Esta es una abstracción que permite la inversión de dependencias (DIP).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.route import Route


class RouteRepositoryPort(ABC):
    """
    Puerto de salida para el repositorio de rutas.
    La capa de dominio y aplicación dependen de esta abstracción,
    no de implementaciones concretas.
    """
    
    @abstractmethod
    def save(self, route: Route) -> None:
        """
        Guarda una nueva ruta en el repositorio.
        
        Args:
            route: La ruta a guardar
            
        Raises:
            Exception: Si ocurre un error al guardar
        """
        pass
    
    @abstractmethod
    def update(self, route: Route) -> None:
        """
        Actualiza una ruta existente en el repositorio.
        
        Args:
            route: La ruta a actualizar
            
        Raises:
            Exception: Si la ruta no existe o hay error al actualizar
        """
        pass
    
    @abstractmethod
    def find_by_id(self, route_id: str) -> Optional[Route]:
        """
        Busca una ruta por su ID.
        
        Args:
            route_id: ID de la ruta a buscar
            
        Returns:
            La ruta si existe, None en caso contrario
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[Route]:
        """
        Obtiene todas las rutas activas del repositorio.
        
        Returns:
            Lista de todas las rutas activas
        """
        pass
    
    @abstractmethod
    def get_all_including_inactive(self) -> List[Route]:
        """
        Obtiene todas las rutas (activas e inactivas) del repositorio.
        
        Returns:
            Lista de todas las rutas
        """
        pass
    
    @abstractmethod
    def delete(self, route_id: str) -> None:
        """
        Elimina físicamente una ruta del repositorio.
        
        Args:
            route_id: ID de la ruta a eliminar
            
        Raises:
            Exception: Si la ruta no existe o hay error al eliminar
        """
        pass
    
    @abstractmethod
    def get_by_cedis_and_day(self, cedis_id: str, day_of_week: str) -> List[Route]:
        """
        Obtiene todas las rutas activas de un CEDIS en un día específico.
        
        Args:
            cedis_id: ID del CEDIS
            day_of_week: Día de la semana
            
        Returns:
            Lista de rutas que coinciden con los criterios
        """
        pass
    
    @abstractmethod
    def begin_transaction(self) -> None:
        """
        Inicia una transacción de base de datos.
        Necesario para garantizar integridad en operaciones complejas.
        """
        pass
    
    @abstractmethod
    def commit_transaction(self) -> None:
        """
        Confirma la transacción actual.
        """
        pass
    
    @abstractmethod
    def rollback_transaction(self) -> None:
        """
        Revierte la transacción actual.
        """
        pass
