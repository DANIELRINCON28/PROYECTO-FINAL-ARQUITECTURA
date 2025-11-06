"""
Client Domain Model
Representa un cliente en el dominio de negocio.
"""
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Client:
    """
    Entidad Cliente del dominio.
    Inmutable para garantizar integridad.
    """
    id: str
    name: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def __post_init__(self) -> None:
        """Validaciones de negocio."""
        if not self.id or not self.id.strip():
            raise ValueError("El ID del cliente es obligatorio")
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del cliente es obligatorio")
        if not self.address or not self.address.strip():
            raise ValueError("La dirección del cliente es obligatoria")
    
    def has_coordinates(self) -> bool:
        """Verifica si el cliente tiene coordenadas geográficas."""
        return self.latitude is not None and self.longitude is not None
