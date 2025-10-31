"""
PostgreSQL Route Repository - Infrastructure Layer
Adaptador de persistencia que implementa el puerto RouteRepositoryPort.
Esta es la implementación técnica concreta usando PostgreSQL.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
import json
from contextlib import contextmanager

from src.domain.models.route import Route
from src.domain.ports.route_repository_port import RouteRepositoryPort


class PostgresRouteRepository(RouteRepositoryPort):
    """
    Implementación concreta del repositorio de rutas usando PostgreSQL.
    Cumple con el contrato definido por RouteRepositoryPort.
    
    Principios SOLID aplicados:
    - Single Responsibility: Solo maneja persistencia de rutas
    - Open/Closed: Extensible sin modificar la interfaz
    - Liskov Substitution: Puede reemplazar a cualquier RouteRepositoryPort
    - Interface Segregation: Implementa solo métodos necesarios
    - Dependency Inversion: Depende de abstracción (RouteRepositoryPort)
    """
    
    def __init__(self, connection_params: dict) -> None:
        """
        Inicializa el repositorio con parámetros de conexión PostgreSQL.
        
        Args:
            connection_params: Diccionario con parámetros de conexión
                - host: Host del servidor PostgreSQL
                - port: Puerto del servidor
                - database: Nombre de la base de datos
                - user: Usuario de la base de datos
                - password: Contraseña del usuario
        """
        self._connection_params = connection_params
        self._conn = None
        self._in_transaction = False
        self._connect()
    
    def _connect(self) -> None:
        """Establece la conexión con PostgreSQL."""
        try:
            self._conn = psycopg2.connect(**self._connection_params)
            self._conn.autocommit = False  # Manejo manual de transacciones
        except psycopg2.Error as e:
            raise ConnectionError(f"Error al conectar con PostgreSQL: {str(e)}")
    
    @contextmanager
    def _get_cursor(self):
        """
        Context manager para manejo seguro de cursores.
        Garantiza que los cursores se cierren apropiadamente.
        """
        cursor = self._conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
        finally:
            cursor.close()
    
    def save(self, route: Route) -> None:
        """
        Guarda una nueva ruta en la base de datos.
        
        Args:
            route: La ruta a guardar
            
        Raises:
            psycopg2.IntegrityError: Si la ruta ya existe
        """
        with self._get_cursor() as cursor:
            client_ids_json = json.dumps(route.client_ids)
            
            cursor.execute("""
                INSERT INTO routes (id, name, cedis_id, day_of_week, client_ids, is_active)
                VALUES (%(id)s, %(name)s, %(cedis_id)s, %(day_of_week)s, %(client_ids)s, %(is_active)s)
            """, {
                'id': route.id,
                'name': route.name,
                'cedis_id': route.cedis_id,
                'day_of_week': route.day_of_week,
                'client_ids': client_ids_json,
                'is_active': route.is_active
            })
            
            # Si no estamos en una transacción explícita, hacer commit
            if not self._in_transaction:
                self._conn.commit()
    
    def update(self, route: Route) -> None:
        """
        Actualiza una ruta existente.
        
        Args:
            route: La ruta a actualizar
            
        Raises:
            ValueError: Si la ruta no existe
        """
        with self._get_cursor() as cursor:
            client_ids_json = json.dumps(route.client_ids)
            
            cursor.execute("""
                UPDATE routes 
                SET name = %(name)s, 
                    cedis_id = %(cedis_id)s, 
                    day_of_week = %(day_of_week)s, 
                    client_ids = %(client_ids)s, 
                    is_active = %(is_active)s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %(id)s
            """, {
                'id': route.id,
                'name': route.name,
                'cedis_id': route.cedis_id,
                'day_of_week': route.day_of_week,
                'client_ids': client_ids_json,
                'is_active': route.is_active
            })
            
            if cursor.rowcount == 0:
                raise ValueError(f"Ruta {route.id} no encontrada para actualizar")
            
            # Si no estamos en una transacción explícita, hacer commit
            if not self._in_transaction:
                self._conn.commit()
    
    def find_by_id(self, route_id: str) -> Optional[Route]:
        """
        Busca una ruta por su ID.
        
        Args:
            route_id: ID de la ruta
            
        Returns:
            La ruta si existe, None en caso contrario
        """
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, name, cedis_id, day_of_week, client_ids, is_active
                FROM routes
                WHERE id = %(route_id)s
            """, {'route_id': route_id})
            
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return self._row_to_route(row)
    
    def get_all(self) -> List[Route]:
        """
        Obtiene todas las rutas activas.
        
        Returns:
            Lista de rutas activas
        """
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, name, cedis_id, day_of_week, client_ids, is_active
                FROM routes
                WHERE is_active = TRUE
                ORDER BY name
            """)
            
            rows = cursor.fetchall()
            return [self._row_to_route(row) for row in rows]
    
    def get_all_including_inactive(self) -> List[Route]:
        """
        Obtiene todas las rutas (activas e inactivas).
        
        Returns:
            Lista de todas las rutas
        """
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, name, cedis_id, day_of_week, client_ids, is_active
                FROM routes
                ORDER BY is_active DESC, name
            """)
            
            rows = cursor.fetchall()
            return [self._row_to_route(row) for row in rows]
    
    def delete(self, route_id: str) -> None:
        """
        Elimina físicamente una ruta (hard delete).
        
        Args:
            route_id: ID de la ruta a eliminar
            
        Raises:
            ValueError: Si la ruta no existe
        """
        with self._get_cursor() as cursor:
            cursor.execute("DELETE FROM routes WHERE id = %(route_id)s", 
                         {'route_id': route_id})
            
            if cursor.rowcount == 0:
                raise ValueError(f"Ruta {route_id} no encontrada para eliminar")
            
            # Si no estamos en una transacción explícita, hacer commit
            if not self._in_transaction:
                self._conn.commit()
    
    def get_by_cedis_and_day(self, cedis_id: str, day_of_week: str) -> List[Route]:
        """
        Obtiene rutas activas de un CEDIS en un día específico.
        
        Args:
            cedis_id: ID del CEDIS
            day_of_week: Día de la semana
            
        Returns:
            Lista de rutas que coinciden
        """
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, name, cedis_id, day_of_week, client_ids, is_active
                FROM routes
                WHERE cedis_id = %(cedis_id)s 
                  AND UPPER(day_of_week) = UPPER(%(day_of_week)s)
                  AND is_active = TRUE
                ORDER BY name
            """, {
                'cedis_id': cedis_id,
                'day_of_week': day_of_week
            })
            
            rows = cursor.fetchall()
            return [self._row_to_route(row) for row in rows]
    
    def begin_transaction(self) -> None:
        """
        Inicia una transacción explícita.
        RNF-RUT-03: Garantiza integridad transaccional.
        """
        self._in_transaction = True
    
    def commit_transaction(self) -> None:
        """
        Confirma la transacción actual.
        """
        self._conn.commit()
        self._in_transaction = False
    
    def rollback_transaction(self) -> None:
        """
        Revierte la transacción actual.
        """
        self._conn.rollback()
        self._in_transaction = False
    
    def _row_to_route(self, row: dict) -> Route:
        """
        Convierte una fila de base de datos a una entidad Route del dominio.
        
        Args:
            row: Fila de PostgreSQL (diccionario)
            
        Returns:
            Entidad Route
        """
        # Deserializar client_ids de JSON
        client_ids = json.loads(row['client_ids']) if isinstance(row['client_ids'], str) else row['client_ids']
        
        return Route(
            id=row['id'],
            name=row['name'],
            cedis_id=row['cedis_id'],
            day_of_week=row['day_of_week'],
            client_ids=client_ids,
            is_active=bool(row['is_active'])
        )
    
    def close(self) -> None:
        """
        Cierra la conexión a la base de datos.
        """
        if self._conn:
            self._conn.close()
    
    def __enter__(self):
        """Soporte para context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del contexto."""
        if exc_type is not None:
            self.rollback_transaction()
        self.close()
