"""
Route Builder Pattern
Patrón de Diseño: Builder

Propósito: Facilitar la construcción compleja de objetos Route paso a paso,
permitiendo crear rutas con diferentes configuraciones de manera fluida y legible.

Ventajas:
- Construcción paso a paso de objetos complejos
- Código más legible y mantenible
- Validación incremental durante la construcción
- Separación de la lógica de construcción de la representación

Ubicación: src/domain/builders/route_builder.py
"""
from typing import List, Optional
import uuid
from datetime import datetime

from src.domain.models.route import Route


class RouteBuilder:
    """
    Builder para construir objetos Route de manera fluida.
    
    Implementa el patrón Builder para facilitar la creación de rutas
    con diferentes configuraciones, validando cada paso.
    
    Example:
        >>> builder = RouteBuilder()
        >>> route = (builder
        ...     .with_name("Ruta Norte")
        ...     .with_cedis("CEDIS_BOGOTA")
        ...     .with_day("LUNES")
        ...     .with_clients(["CLI_001", "CLI_002"])
        ...     .build())
    """
    
    def __init__(self):
        """Inicializa el builder con valores por defecto."""
        self._reset()
    
    def _reset(self) -> None:
        """Resetea el estado interno del builder."""
        self._id: Optional[str] = None
        self._name: Optional[str] = None
        self._cedis_id: Optional[str] = None
        self._day_of_week: Optional[str] = None
        self._client_ids: List[str] = []
        self._is_active: bool = True
    
    def with_id(self, route_id: str) -> 'RouteBuilder':
        """
        Establece el ID de la ruta.
        
        Args:
            route_id: ID único de la ruta
            
        Returns:
            Builder para encadenamiento
        """
        if not route_id or not route_id.strip():
            raise ValueError("El ID no puede estar vacío")
        self._id = route_id
        return self
    
    def with_auto_id(self) -> 'RouteBuilder':
        """
        Genera automáticamente un UUID para la ruta.
        
        Returns:
            Builder para encadenamiento
        """
        self._id = str(uuid.uuid4())
        return self
    
    def with_name(self, name: str) -> 'RouteBuilder':
        """
        Establece el nombre de la ruta.
        
        Args:
            name: Nombre descriptivo de la ruta
            
        Returns:
            Builder para encadenamiento
            
        Raises:
            ValueError: Si el nombre está vacío
        """
        if not name or not name.strip():
            raise ValueError("El nombre no puede estar vacío")
        self._name = name.strip()
        return self
    
    def with_cedis(self, cedis_id: str) -> 'RouteBuilder':
        """
        Establece el CEDIS de origen.
        
        Args:
            cedis_id: ID del CEDIS
            
        Returns:
            Builder para encadenamiento
            
        Raises:
            ValueError: Si el CEDIS está vacío
        """
        if not cedis_id or not cedis_id.strip():
            raise ValueError("El CEDIS no puede estar vacío")
        self._cedis_id = cedis_id
        return self
    
    def with_day(self, day_of_week: str) -> 'RouteBuilder':
        """
        Establece el día de la semana.
        
        Args:
            day_of_week: Día de la semana (LUNES, MARTES, etc.)
            
        Returns:
            Builder para encadenamiento
            
        Raises:
            ValueError: Si el día es inválido
        """
        valid_days = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
        day_upper = day_of_week.upper()
        
        if day_upper not in valid_days:
            raise ValueError(f"Día inválido. Debe ser uno de: {', '.join(valid_days)}")
        
        self._day_of_week = day_upper
        return self
    
    def with_client(self, client_id: str) -> 'RouteBuilder':
        """
        Agrega un cliente a la ruta.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Builder para encadenamiento
            
        Raises:
            ValueError: Si el cliente está vacío o duplicado
        """
        if not client_id or not client_id.strip():
            raise ValueError("El ID del cliente no puede estar vacío")
        
        if client_id in self._client_ids:
            raise ValueError(f"El cliente {client_id} ya existe en la ruta")
        
        self._client_ids.append(client_id)
        return self
    
    def with_clients(self, client_ids: List[str]) -> 'RouteBuilder':
        """
        Agrega múltiples clientes a la ruta.
        
        Args:
            client_ids: Lista de IDs de clientes
            
        Returns:
            Builder para encadenamiento
            
        Raises:
            ValueError: Si hay clientes duplicados
        """
        for client_id in client_ids:
            if not client_id or not client_id.strip():
                raise ValueError("Los IDs de clientes no pueden estar vacíos")
            
            if client_id in self._client_ids:
                raise ValueError(f"El cliente {client_id} ya existe en la ruta")
            
            self._client_ids.append(client_id)
        
        return self
    
    def with_active_status(self, is_active: bool) -> 'RouteBuilder':
        """
        Establece el estado de activación de la ruta.
        
        Args:
            is_active: True si la ruta está activa
            
        Returns:
            Builder para encadenamiento
        """
        self._is_active = is_active
        return self
    
    def build(self) -> Route:
        """
        Construye y retorna el objeto Route.
        
        Returns:
            Instancia de Route construida
            
        Raises:
            ValueError: Si faltan campos obligatorios
        """
        # Validar campos obligatorios
        if self._id is None:
            raise ValueError("Debe especificar un ID o usar with_auto_id()")
        
        if self._name is None:
            raise ValueError("Debe especificar un nombre con with_name()")
        
        if self._cedis_id is None:
            raise ValueError("Debe especificar un CEDIS con with_cedis()")
        
        if self._day_of_week is None:
            raise ValueError("Debe especificar un día con with_day()")
        
        # Construir el objeto Route
        route = Route(
            id=self._id,
            name=self._name,
            cedis_id=self._cedis_id,
            day_of_week=self._day_of_week,
            client_ids=self._client_ids.copy(),  # Copia para evitar mutación
            is_active=self._is_active
        )
        
        # Resetear para permitir construir otra ruta
        self._reset()
        
        return route
    
    @staticmethod
    def create_simple(name: str, cedis_id: str, day_of_week: str) -> Route:
        """
        Método de conveniencia para crear una ruta simple sin clientes.
        
        Args:
            name: Nombre de la ruta
            cedis_id: ID del CEDIS
            day_of_week: Día de la semana
            
        Returns:
            Route construida
            
        Example:
            >>> route = RouteBuilder.create_simple("Ruta Sur", "CEDIS_BOGOTA", "MARTES")
        """
        return (RouteBuilder()
                .with_auto_id()
                .with_name(name)
                .with_cedis(cedis_id)
                .with_day(day_of_week)
                .build())
    
    @staticmethod
    def create_with_clients(name: str, cedis_id: str, day_of_week: str, client_ids: List[str]) -> Route:
        """
        Método de conveniencia para crear una ruta con clientes.
        
        Args:
            name: Nombre de la ruta
            cedis_id: ID del CEDIS
            day_of_week: Día de la semana
            client_ids: Lista de IDs de clientes
            
        Returns:
            Route construida
            
        Example:
            >>> route = RouteBuilder.create_with_clients(
            ...     "Ruta Norte",
            ...     "CEDIS_BOGOTA",
            ...     "LUNES",
            ...     ["CLI_001", "CLI_002", "CLI_003"]
            ... )
        """
        return (RouteBuilder()
                .with_auto_id()
                .with_name(name)
                .with_cedis(cedis_id)
                .with_day(day_of_week)
                .with_clients(client_ids)
                .build())


class RouteDirector:
    """
    Director para construir rutas con configuraciones predefinidas.
    
    El Director conoce recetas específicas para construir rutas comunes,
    simplificando la creación de rutas estándar.
    """
    
    def __init__(self, builder: RouteBuilder):
        """
        Inicializa el director con un builder.
        
        Args:
            builder: Instancia de RouteBuilder
        """
        self._builder = builder
    
    def construct_weekly_route(self, name_prefix: str, cedis_id: str, day: str) -> Route:
        """
        Construye una ruta semanal estándar.
        
        Args:
            name_prefix: Prefijo para el nombre
            cedis_id: ID del CEDIS
            day: Día de la semana
            
        Returns:
            Route construida
        """
        route_name = f"{name_prefix} - {day}"
        return (self._builder
                .with_auto_id()
                .with_name(route_name)
                .with_cedis(cedis_id)
                .with_day(day)
                .with_active_status(True)
                .build())
    
    def construct_emergency_route(self, cedis_id: str) -> Route:
        """
        Construye una ruta de emergencia para entregas urgentes.
        
        Args:
            cedis_id: ID del CEDIS
            
        Returns:
            Route construida
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        route_name = f"Ruta Emergencia {timestamp}"
        
        return (self._builder
                .with_auto_id()
                .with_name(route_name)
                .with_cedis(cedis_id)
                .with_day("LUNES")  # Default día
                .with_active_status(True)
                .build())
