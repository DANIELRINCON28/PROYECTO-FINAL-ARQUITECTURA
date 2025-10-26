"""
SQLite Route Repository - Infrastructure Layer
Adaptador de persistencia que implementa el puerto RouteRepositoryPort.
Esta es la implementación técnica concreta de la abstracción del dominio.
"""
import sqlite3
from typing import List, Optional
import json
from src.domain.models.route import Route
from src.domain.ports.route_repository_port import RouteRepositoryPort


class SqliteRouteRepository(RouteRepositoryPort):
    """
    Implementación concreta del repositorio de rutas usando SQLite.
    Cumple con el contrato definido por RouteRepositoryPort.
    """
    
    def __init__(self, connection: sqlite3.Connection) -> None:
        """
        Inicializa el repositorio con una conexión SQLite.
        
        Args:
            connection: Conexión a la base de datos SQLite
        """
        self._conn = connection
        self._conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """
        Crea las tablas necesarias si no existen.
        RNF-RUT-03: Garantiza estructura de datos adecuada.
        """
        cursor = self._conn.cursor()
        
        # Tabla de rutas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                cedis_id TEXT NOT NULL,
                day_of_week TEXT NOT NULL,
                client_ids TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices para mejorar rendimiento (RNF-RUT-02)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_routes_cedis_day 
            ON routes(cedis_id, day_of_week)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_routes_active 
            ON routes(is_active)
        """)
        
        self._conn.commit()
    
    def save(self, route: Route) -> None:
        """
        Guarda una nueva ruta en la base de datos.
        
        Args:
            route: La ruta a guardar
            
        Raises:
            sqlite3.IntegrityError: Si la ruta ya existe
        """
        cursor = self._conn.cursor()
        
        # Serializar lista de client_ids a JSON
        client_ids_json = json.dumps(route.client_ids)
        
        cursor.execute("""
            INSERT INTO routes (id, name, cedis_id, day_of_week, client_ids, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            route.id,
            route.name,
            route.cedis_id,
            route.day_of_week,
            client_ids_json,
            1 if route.is_active else 0
        ))
        
        # No hacer commit aquí si estamos en una transacción
        # El commit se hace desde el servicio o manualmente
    
    def update(self, route: Route) -> None:
        """
        Actualiza una ruta existente.
        
        Args:
            route: La ruta a actualizar
            
        Raises:
            ValueError: Si la ruta no existe
        """
        cursor = self._conn.cursor()
        
        client_ids_json = json.dumps(route.client_ids)
        
        cursor.execute("""
            UPDATE routes 
            SET name = ?, 
                cedis_id = ?, 
                day_of_week = ?, 
                client_ids = ?, 
                is_active = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            route.name,
            route.cedis_id,
            route.day_of_week,
            client_ids_json,
            1 if route.is_active else 0,
            route.id
        ))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Ruta {route.id} no encontrada para actualizar")
    
    def find_by_id(self, route_id: str) -> Optional[Route]:
        """
        Busca una ruta por su ID.
        
        Args:
            route_id: ID de la ruta
            
        Returns:
            La ruta si existe, None en caso contrario
        """
        cursor = self._conn.cursor()
        
        cursor.execute("""
            SELECT id, name, cedis_id, day_of_week, client_ids, is_active
            FROM routes
            WHERE id = ?
        """, (route_id,))
        
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
        cursor = self._conn.cursor()
        
        cursor.execute("""
            SELECT id, name, cedis_id, day_of_week, client_ids, is_active
            FROM routes
            WHERE is_active = 1
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
        cursor = self._conn.cursor()
        
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
        cursor = self._conn.cursor()
        
        cursor.execute("DELETE FROM routes WHERE id = ?", (route_id,))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Ruta {route_id} no encontrada para eliminar")
    
    def get_by_cedis_and_day(self, cedis_id: str, day_of_week: str) -> List[Route]:
        """
        Obtiene rutas activas de un CEDIS en un día específico.
        
        Args:
            cedis_id: ID del CEDIS
            day_of_week: Día de la semana
            
        Returns:
            Lista de rutas que coinciden
        """
        cursor = self._conn.cursor()
        
        cursor.execute("""
            SELECT id, name, cedis_id, day_of_week, client_ids, is_active
            FROM routes
            WHERE cedis_id = ? AND day_of_week = ? AND is_active = 1
            ORDER BY name
        """, (cedis_id, day_of_week.upper()))
        
        rows = cursor.fetchall()
        return [self._row_to_route(row) for row in rows]
    
    def begin_transaction(self) -> None:
        """
        Inicia una transacción explícita.
        RNF-RUT-03: Garantiza integridad transaccional.
        """
        # SQLite inicia transacciones automáticamente, pero podemos hacerlo explícito
        self._conn.execute("BEGIN TRANSACTION")
    
    def commit_transaction(self) -> None:
        """
        Confirma la transacción actual.
        """
        self._conn.commit()
    
    def rollback_transaction(self) -> None:
        """
        Revierte la transacción actual.
        """
        self._conn.rollback()
    
    def _row_to_route(self, row: sqlite3.Row) -> Route:
        """
        Convierte una fila de base de datos a una entidad Route del dominio.
        
        Args:
            row: Fila de SQLite
            
        Returns:
            Entidad Route
        """
        # Deserializar client_ids de JSON
        client_ids = json.loads(row['client_ids'])
        
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
        self._conn.close()
