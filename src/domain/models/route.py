"""
Route Domain Model
Contiene la lógica de negocio pura para la gestión de rutas.
Este modelo NO depende de ninguna tecnología de persistencia.
"""
from typing import List, Tuple
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class Route:
    """
    Entidad Route del dominio.
    Contiene la lógica de negocio para operaciones de rutas.
    """
    id: str
    name: str
    cedis_id: str
    day_of_week: str
    client_ids: List[str] = field(default_factory=list)
    is_active: bool = True
    
    def __post_init__(self) -> None:
        """Validaciones de negocio."""
        valid_days = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
        
        if not self.id or not self.id.strip():
            raise ValueError("El ID de la ruta es obligatorio")
        if not self.name or not self.name.strip():
            raise ValueError("El nombre de la ruta es obligatorio")
        if not self.cedis_id or not self.cedis_id.strip():
            raise ValueError("El CEDIS es obligatorio")
        if self.day_of_week.upper() not in valid_days:
            raise ValueError(f"Día de la semana inválido. Debe ser uno de: {', '.join(valid_days)}")
    
    def add_client(self, client_id: str) -> None:
        """
        Agrega un cliente al final de la ruta.
        
        Args:
            client_id: ID del cliente a agregar
            
        Raises:
            ValueError: Si el cliente ya existe en la ruta
        """
        if not client_id or not client_id.strip():
            raise ValueError("El ID del cliente es obligatorio")
        
        if client_id in self.client_ids:
            raise ValueError(f"El cliente {client_id} ya está en la ruta")
        
        self.client_ids.append(client_id)
    
    def remove_client(self, client_id: str) -> None:
        """
        Elimina un cliente de la ruta.
        
        Args:
            client_id: ID del cliente a eliminar
            
        Raises:
            ValueError: Si el cliente no existe en la ruta
        """
        if client_id not in self.client_ids:
            raise ValueError(f"El cliente {client_id} no está en la ruta")
        
        self.client_ids.remove(client_id)
    
    def reorder_clients(self, ordered_client_ids: List[str]) -> None:
        """
        Reordena los clientes de la ruta.
        
        Args:
            ordered_client_ids: Nueva lista ordenada de IDs de clientes
            
        Raises:
            ValueError: Si la lista no contiene los mismos clientes
        """
        if set(ordered_client_ids) != set(self.client_ids):
            raise ValueError("La lista de clientes debe contener exactamente los mismos clientes")
        
        self.client_ids = ordered_client_ids.copy()
    
    def divide_route(self, split_index: int) -> Tuple['Route', 'Route']:
        """
        Divide la ruta en dos nuevas rutas en el índice especificado.
        Retorna dos nuevas instancias de Route (inmutabilidad preferida).
        
        Args:
            split_index: Índice donde se dividirá la ruta (0-based)
            
        Returns:
            Tupla con dos nuevas rutas (route_a, route_b)
            
        Raises:
            ValueError: Si el índice de división es inválido
        """
        if split_index <= 0 or split_index >= len(self.client_ids):
            raise ValueError(
                f"Índice de división inválido. Debe estar entre 1 y {len(self.client_ids) - 1}"
            )
        
        if len(self.client_ids) < 2:
            raise ValueError("No se puede dividir una ruta con menos de 2 clientes")
        
        # División de clientes
        clients_part_a = self.client_ids[:split_index]
        clients_part_b = self.client_ids[split_index:]
        
        # Crear nueva ruta A (primera parte)
        route_a = Route(
            id=f"{self.id}_A",
            name=f"{self.name}_A",
            cedis_id=self.cedis_id,
            day_of_week=self.day_of_week,
            client_ids=clients_part_a.copy(),
            is_active=True
        )
        
        # Crear nueva ruta B (segunda parte)
        route_b = Route(
            id=f"{self.id}_B",
            name=f"{self.name}_B",
            cedis_id=self.cedis_id,
            day_of_week=self.day_of_week,
            client_ids=clients_part_b.copy(),
            is_active=True
        )
        
        return route_a, route_b
    
    def merge_routes(self, other_route: 'Route') -> 'Route':
        """
        Fusiona esta ruta con otra ruta, combinando sus clientes.
        Retorna una nueva instancia de Route (inmutabilidad preferida).
        
        Args:
            other_route: La otra ruta a fusionar
            
        Returns:
            Nueva ruta fusionada
            
        Raises:
            ValueError: Si las rutas no son compatibles para fusión
        """
        if not isinstance(other_route, Route):
            raise ValueError("El parámetro debe ser una instancia de Route")
        
        # Validar compatibilidad de fusión
        if self.cedis_id != other_route.cedis_id:
            raise ValueError("Solo se pueden fusionar rutas del mismo CEDIS")
        
        if self.day_of_week != other_route.day_of_week:
            raise ValueError("Solo se pueden fusionar rutas del mismo día de la semana")
        
        # Combinar clientes, evitando duplicados
        merged_client_ids = self.client_ids.copy()
        for client_id in other_route.client_ids:
            if client_id not in merged_client_ids:
                merged_client_ids.append(client_id)
        
        # Crear nueva ruta fusionada
        merged_route = Route(
            id=f"{self.id}_MERGED",
            name=f"{self.name}_MERGED",
            cedis_id=self.cedis_id,
            day_of_week=self.day_of_week,
            client_ids=merged_client_ids,
            is_active=True
        )
        
        return merged_route
    
    def deactivate(self) -> None:
        """Desactiva la ruta (soft delete)."""
        self.is_active = False
    
    def activate(self) -> None:
        """Activa la ruta."""
        self.is_active = True
    
    def __str__(self) -> str:
        """Representación en string de la ruta."""
        status = "Activa" if self.is_active else "Inactiva"
        return (
            f"Ruta {self.name} (ID: {self.id}) - {self.day_of_week} - "
            f"CEDIS: {self.cedis_id} - Clientes: {len(self.client_ids)} - {status}"
        )
