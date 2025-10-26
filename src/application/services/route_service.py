"""
Route Service - Application Layer
Implementa los casos de uso del módulo de Gestión de Rutas.
Depende SOLO de abstracciones (puertos), NO de implementaciones concretas.
"""
from typing import List, Optional
import uuid
from src.domain.models.route import Route
from src.domain.ports.route_repository_port import RouteRepositoryPort
from src.application.dtos import RouteDTO, CreateRouteDTO, DivideRouteDTO, MergeRoutesDTO


class RouteService:
    """
    Servicio de aplicación para gestión de rutas.
    Orquesta los casos de uso y coordina con el dominio y los puertos.
    """
    
    def __init__(self, repository: RouteRepositoryPort) -> None:
        """
        Inyección de dependencias: recibe el puerto, NO la implementación.
        
        Args:
            repository: Puerto del repositorio de rutas
        """
        self._repository = repository
    
    def create_route(self, dto: CreateRouteDTO) -> RouteDTO:
        """
        RF-RUT-01: Crear una nueva ruta.
        
        Args:
            dto: Datos para crear la ruta
            
        Returns:
            DTO de la ruta creada
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        # Generar ID único
        route_id = str(uuid.uuid4())
        
        # Crear entidad de dominio
        route = Route(
            id=route_id,
            name=dto.name,
            cedis_id=dto.cedis_id,
            day_of_week=dto.day_of_week.upper(),
            client_ids=[],
            is_active=True
        )
        
        # Persistir
        self._repository.save(route)
        
        # Retornar DTO
        return self._route_to_dto(route)
    
    def assign_client_to_route(self, route_id: str, client_id: str) -> RouteDTO:
        """
        RF-RUT-02: Asignar un cliente a una ruta.
        
        Args:
            route_id: ID de la ruta
            client_id: ID del cliente a asignar
            
        Returns:
            DTO de la ruta actualizada
            
        Raises:
            ValueError: Si la ruta no existe o el cliente ya está asignado
        """
        route = self._repository.find_by_id(route_id)
        if route is None:
            raise ValueError(f"Ruta {route_id} no encontrada")
        
        # Lógica de dominio
        route.add_client(client_id)
        
        # Persistir cambios
        self._repository.update(route)
        
        return self._route_to_dto(route)
    
    def remove_client_from_route(self, route_id: str, client_id: str) -> RouteDTO:
        """
        Eliminar un cliente de una ruta.
        
        Args:
            route_id: ID de la ruta
            client_id: ID del cliente a eliminar
            
        Returns:
            DTO de la ruta actualizada
        """
        route = self._repository.find_by_id(route_id)
        if route is None:
            raise ValueError(f"Ruta {route_id} no encontrada")
        
        route.remove_client(client_id)
        self._repository.update(route)
        
        return self._route_to_dto(route)
    
    def reorder_clients_in_route(self, route_id: str, ordered_client_ids: List[str]) -> RouteDTO:
        """
        RF-RUT-03: Reordenar clientes en una ruta.
        
        Args:
            route_id: ID de la ruta
            ordered_client_ids: Nueva lista ordenada de IDs de clientes
            
        Returns:
            DTO de la ruta actualizada
            
        Raises:
            ValueError: Si la ruta no existe o la lista de clientes es inválida
        """
        route = self._repository.find_by_id(route_id)
        if route is None:
            raise ValueError(f"Ruta {route_id} no encontrada")
        
        # Lógica de dominio
        route.reorder_clients(ordered_client_ids)
        
        # Persistir cambios
        self._repository.update(route)
        
        return self._route_to_dto(route)
    
    def divide_route_use_case(
        self,
        route_id_to_split: str,
        split_point: int,
        new_route_name_a: str,
        new_route_name_b: str
    ) -> tuple[RouteDTO, RouteDTO]:
        """
        RF-RUT-06: Dividir una ruta en dos.
        RNF-RUT-03: Garantiza integridad transaccional.
        
        Args:
            route_id_to_split: ID de la ruta a dividir
            split_point: Índice donde se dividirá
            new_route_name_a: Nombre para la primera ruta resultante
            new_route_name_b: Nombre para la segunda ruta resultante
            
        Returns:
            Tupla con los DTOs de las dos rutas creadas
            
        Raises:
            ValueError: Si la ruta no existe o la división falla
        """
        try:
            # Iniciar transacción
            self._repository.begin_transaction()
            
            # Recuperar ruta original
            original_route = self._repository.find_by_id(route_id_to_split)
            if original_route is None:
                raise ValueError(f"Ruta {route_id_to_split} no encontrada")
            
            # Lógica de dominio: dividir
            route_a, route_b = original_route.divide_route(split_point)
            
            # Personalizar nombres
            route_a.name = new_route_name_a
            route_b.name = new_route_name_b
            
            # Generar nuevos IDs únicos
            route_a.id = str(uuid.uuid4())
            route_b.id = str(uuid.uuid4())
            
            # Desactivar ruta original (soft delete)
            original_route.deactivate()
            self._repository.update(original_route)
            
            # Guardar nuevas rutas
            self._repository.save(route_a)
            self._repository.save(route_b)
            
            # Confirmar transacción
            self._repository.commit_transaction()
            
            return self._route_to_dto(route_a), self._route_to_dto(route_b)
        
        except Exception as e:
            # Revertir en caso de error
            self._repository.rollback_transaction()
            raise e
    
    def merge_routes_use_case(
        self,
        route_id_a: str,
        route_id_b: str,
        new_merged_route_name: str
    ) -> RouteDTO:
        """
        RF-RUT-07: Fusionar dos rutas en una.
        RNF-RUT-03: Garantiza integridad transaccional.
        
        Args:
            route_id_a: ID de la primera ruta
            route_id_b: ID de la segunda ruta
            new_merged_route_name: Nombre para la ruta fusionada
            
        Returns:
            DTO de la ruta fusionada
            
        Raises:
            ValueError: Si alguna ruta no existe o la fusión falla
        """
        try:
            # Iniciar transacción
            self._repository.begin_transaction()
            
            # Recuperar ambas rutas
            route_a = self._repository.find_by_id(route_id_a)
            if route_a is None:
                raise ValueError(f"Ruta {route_id_a} no encontrada")
            
            route_b = self._repository.find_by_id(route_id_b)
            if route_b is None:
                raise ValueError(f"Ruta {route_id_b} no encontrada")
            
            # Lógica de dominio: fusionar
            merged_route = route_a.merge_routes(route_b)
            
            # Personalizar nombre y generar ID único
            merged_route.name = new_merged_route_name
            merged_route.id = str(uuid.uuid4())
            
            # Desactivar rutas originales (soft delete)
            route_a.deactivate()
            route_b.deactivate()
            self._repository.update(route_a)
            self._repository.update(route_b)
            
            # Guardar ruta fusionada
            self._repository.save(merged_route)
            
            # Confirmar transacción
            self._repository.commit_transaction()
            
            return self._route_to_dto(merged_route)
        
        except Exception as e:
            # Revertir en caso de error
            self._repository.rollback_transaction()
            raise e
    
    def get_route_by_id(self, route_id: str) -> Optional[RouteDTO]:
        """
        Obtener una ruta por su ID.
        
        Args:
            route_id: ID de la ruta
            
        Returns:
            DTO de la ruta o None si no existe
        """
        route = self._repository.find_by_id(route_id)
        return self._route_to_dto(route) if route else None
    
    def get_all_routes(self, include_inactive: bool = False) -> List[RouteDTO]:
        """
        RF-RUT-04: Visualizar todas las rutas.
        
        Args:
            include_inactive: Si incluir rutas inactivas
            
        Returns:
            Lista de DTOs de todas las rutas
        """
        if include_inactive:
            routes = self._repository.get_all_including_inactive()
        else:
            routes = self._repository.get_all()
        
        return [self._route_to_dto(route) for route in routes]
    
    def get_routes_by_cedis_and_day(self, cedis_id: str, day_of_week: str) -> List[RouteDTO]:
        """
        Obtener rutas de un CEDIS en un día específico.
        
        Args:
            cedis_id: ID del CEDIS
            day_of_week: Día de la semana
            
        Returns:
            Lista de DTOs de rutas que coinciden
        """
        routes = self._repository.get_by_cedis_and_day(cedis_id, day_of_week.upper())
        return [self._route_to_dto(route) for route in routes]
    
    def deactivate_route(self, route_id: str) -> RouteDTO:
        """
        Desactivar una ruta (soft delete).
        
        Args:
            route_id: ID de la ruta a desactivar
            
        Returns:
            DTO de la ruta desactivada
        """
        route = self._repository.find_by_id(route_id)
        if route is None:
            raise ValueError(f"Ruta {route_id} no encontrada")
        
        route.deactivate()
        self._repository.update(route)
        
        return self._route_to_dto(route)
    
    def activate_route(self, route_id: str) -> RouteDTO:
        """
        Activar una ruta.
        
        Args:
            route_id: ID de la ruta a activar
            
        Returns:
            DTO de la ruta activada
        """
        route = self._repository.find_by_id(route_id)
        if route is None:
            raise ValueError(f"Ruta {route_id} no encontrada")
        
        route.activate()
        self._repository.update(route)
        
        return self._route_to_dto(route)
    
    def _route_to_dto(self, route: Route) -> RouteDTO:
        """
        Convierte una entidad de dominio Route a un DTO.
        
        Args:
            route: Entidad de dominio
            
        Returns:
            DTO para la UI
        """
        return RouteDTO(
            id=route.id,
            name=route.name,
            cedis_id=route.cedis_id,
            day_of_week=route.day_of_week,
            client_ids=route.client_ids.copy(),
            client_count=len(route.client_ids),
            is_active=route.is_active
        )
