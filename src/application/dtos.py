"""
Data Transfer Objects (DTOs)
Para comunicación entre la capa de UI y la capa de aplicación.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CreateRouteDTO:
    """DTO para crear una nueva ruta."""
    name: str
    cedis_id: str
    day_of_week: str


@dataclass
class RouteDTO:
    """DTO para representar una ruta en la UI."""
    id: str
    name: str
    cedis_id: str
    day_of_week: str
    client_ids: List[str]
    client_count: int
    is_active: bool


@dataclass
class DivideRouteDTO:
    """DTO para dividir una ruta."""
    route_id_to_split: str
    split_point: int
    new_route_name_a: str
    new_route_name_b: str


@dataclass
class MergeRoutesDTO:
    """DTO para fusionar rutas."""
    route_id_a: str
    route_id_b: str
    new_merged_route_name: str


@dataclass
class AssignClientDTO:
    """DTO para asignar un cliente a una ruta."""
    route_id: str
    client_id: str


@dataclass
class ReorderClientsDTO:
    """DTO para reordenar clientes en una ruta."""
    route_id: str
    ordered_client_ids: List[str]
