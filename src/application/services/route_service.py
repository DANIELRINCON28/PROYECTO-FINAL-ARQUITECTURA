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
        
        # Persistir y confirmar
        self._repository.save(route)
        self._repository.commit_transaction()
        
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
        
        # Persistir cambios y confirmar
        self._repository.update(route)
        self._repository.commit_transaction()
        
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
        self._repository.commit_transaction()
        
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
        
        # Persistir cambios y confirmar
        self._repository.update(route)
        self._repository.commit_transaction()
        
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
        self._repository.commit_transaction()
        
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
        self._repository.commit_transaction()
        
        return self._route_to_dto(route)
    
    def get_available_clients(self) -> List:
        """
        Obtiene la lista de clientes disponibles que NO están asignados a ninguna ruta.
        
        Returns:
            Lista de clientes sin asignación de ruta
        """
        from src.domain.models.client import Client
        
        try:
            # Obtener clientes reales desde la base de datos
            import psycopg2
            from config import Config
            
            conn = psycopg2.connect(
                host=Config.DB_HOST,
                port=int(Config.DB_PORT),
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            
            cursor = conn.cursor()
            
            # Query que excluye clientes ya asignados a rutas
            cursor.execute("""
                SELECT c.id, c.nombre_comercial, c.direccion
                FROM clientes c
                LEFT JOIN rutas_clientes rc ON c.id = rc.cliente_id
                WHERE rc.cliente_id IS NULL
                ORDER BY c.nombre_comercial
                LIMIT 100
            """)
            
            print(f"📊 DEBUG get_available_clients: Query ejecutada (excluye clientes en rutas)")
            
            rows = cursor.fetchall()
            print(f"📊 DEBUG get_available_clients: {len(rows)} clientes SIN RUTA obtenidos de BD")
            
            clients = []
            for row in rows:
                client = Client(
                    id=str(row[0]),  # Convertir ID numérico a string
                    name=row[1],
                    address=row[2] if row[2] else "Sin dirección",
                    phone="",
                    email=""
                )
                clients.append(client)
                print(f"  ✅ Cliente disponible: ID={client.id}, Nombre={client.name}")
            
            cursor.close()
            conn.close()
            
            print(f"✅ get_available_clients: Retornando {len(clients)} clientes disponibles")
            return clients
            
        except Exception as e:
            # En caso de error, log y retornar lista vacía
            import traceback
            print(f"⚠️ Warning: No se pudieron cargar clientes desde BD: {e}")
            print(traceback.format_exc())
            return []
    
    def get_client_info(self, client_id: str) -> dict:
        """
        Obtiene información de un cliente específico desde la base de datos.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con información del cliente
        """
        try:
            import psycopg2
            from config import Config
            
            conn = psycopg2.connect(
                host=Config.DB_HOST,
                port=int(Config.DB_PORT),
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre_comercial, direccion
                FROM clientes
                WHERE id = %s
            """, (int(client_id),))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return {
                    'id': str(row[0]),
                    'name': row[1],
                    'address': row[2] if row[2] else "Sin dirección"
                }
            else:
                return {
                    'id': client_id,
                    'name': f"Cliente {client_id}",
                    'address': "Información no disponible"
                }
                
        except Exception as e:
            import traceback
            print(f"⚠️ Warning: Error al obtener info de cliente {client_id}: {e}")
            print(traceback.format_exc())
            return {
                'id': client_id,
                'name': f"Cliente {client_id}",
                'address': "Información no disponible"
            }
    def delete_route(self, route_id: str) -> None:
        """
        RF-RUT-08: Eliminar una ruta.
        
        Args:
            route_id: ID de la ruta a eliminar
            
        Raises:
            ValueError: Si la ruta no existe o tiene clientes asignados
        """
        # Obtener la ruta
        route = self._repository.find_by_id(route_id)
        if route is None:
            raise ValueError(f"Ruta {route_id} no encontrada")
        
        # Validación de negocio: no eliminar rutas con clientes
        if route.client_ids and len(route.client_ids) > 0:
            raise ValueError(
                f"No se puede eliminar la ruta '{route.name}' porque tiene "
                f"{len(route.client_ids)} clientes asignados. "
                "Elimine todos los clientes primero."
            )
        
        # Eliminar la ruta
        self._repository.delete(route_id)
        self._repository.commit_transaction()
    
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
