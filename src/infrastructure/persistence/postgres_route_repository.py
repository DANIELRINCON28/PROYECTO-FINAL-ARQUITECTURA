"""
PostgreSQL Route Repository - Infrastructure Layer
Adaptador de persistencia que implementa el puerto RouteRepositoryPort.
Esta es la implementación técnica concreta usando PostgreSQL con tabla 'rutas'.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from contextlib import contextmanager

from src.domain.models.route import Route
from src.domain.ports.route_repository_port import RouteRepositoryPort


class PostgresRouteRepository(RouteRepositoryPort):
    """
    Implementación concreta del repositorio de rutas usando PostgreSQL.
    Cumple con el contrato definido por RouteRepositoryPort.
    
    Mapea la tabla 'rutas' (estructura relacional) a la entidad Route del dominio.
    
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
            try:
                # Obtener el cedis_id basado en el nombre o crear uno
                cedis_id = self._get_or_create_cedis(cursor, route.cedis_id)
                
                # Insertar en la tabla rutas
                cursor.execute("""
                    INSERT INTO rutas (identificador_unico, nombre_descriptivo, dia_semana, cedis_id, activa)
                    VALUES (%(id)s, %(name)s, %(day_of_week)s, %(cedis_id)s, %(is_active)s)
                    RETURNING id
                """, {
                    'id': route.id,
                    'name': route.name,
                    'day_of_week': self._convert_day_name_to_number(route.day_of_week),
                    'cedis_id': cedis_id,
                    'is_active': route.is_active
                })
                
                # Obtener el ID de la ruta insertada
                ruta_id = cursor.fetchone()['id']
                
                # Insertar los clientes asociados
                for orden, client_id in enumerate(route.client_ids, 1):
                    # Convertir client_id a entero de forma segura
                    try:
                        cliente_id_int = int(client_id)
                    except (ValueError, TypeError):
                        raise ValueError(f"ID de cliente inválido: {client_id}. Debe ser un número.")
                    
                    # Verificar que el cliente existe en la BD antes de insertar
                    cursor.execute("SELECT 1 FROM clientes WHERE id = %(cliente_id)s", 
                                 {'cliente_id': cliente_id_int})
                    if cursor.fetchone() is None:
                        raise ValueError(f"El cliente con ID {cliente_id_int} no existe en la base de datos.")
                    
                    cursor.execute("""
                        INSERT INTO rutas_clientes (ruta_id, cliente_id, orden_visita)
                        VALUES (%(ruta_id)s, %(cliente_id)s, %(orden)s)
                    """, {
                        'ruta_id': ruta_id,
                        'cliente_id': cliente_id_int,
                        'orden': orden
                    })
                
                # Si no estamos en una transacción explícita, hacer commit
                if not self._in_transaction:
                    self._conn.commit()
                    
            except psycopg2.Error as e:
                if not self._in_transaction:
                    self._conn.rollback()
                raise
    
    def update(self, route: Route) -> None:
        """
        Actualiza una ruta existente.
        
        Args:
            route: La ruta a actualizar
            
        Raises:
            ValueError: Si la ruta no existe
        """
        with self._get_cursor() as cursor:
            try:
                # Buscar la ruta por identificador_unico
                cursor.execute("""
                    SELECT id FROM rutas WHERE identificador_unico = %(id)s
                """, {'id': route.id})
                
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"Ruta {route.id} no encontrada para actualizar")
                
                ruta_id = result['id']
                cedis_id = self._get_or_create_cedis(cursor, route.cedis_id)
                
                # Actualizar la ruta
                cursor.execute("""
                    UPDATE rutas 
                    SET nombre_descriptivo = %(name)s, 
                        dia_semana = %(day_of_week)s, 
                        cedis_id = %(cedis_id)s, 
                        activa = %(is_active)s
                    WHERE id = %(ruta_id)s
                """, {
                    'name': route.name,
                    'day_of_week': self._convert_day_name_to_number(route.day_of_week),
                    'cedis_id': cedis_id,
                    'is_active': route.is_active,
                    'ruta_id': ruta_id
                })
                
                # Eliminar clientes antiguos
                cursor.execute("DELETE FROM rutas_clientes WHERE ruta_id = %(ruta_id)s", 
                             {'ruta_id': ruta_id})
                
                # Insertar nuevos clientes
                for orden, client_id in enumerate(route.client_ids, 1):
                    # Convertir client_id a entero de forma segura
                    try:
                        cliente_id_int = int(client_id)
                    except (ValueError, TypeError):
                        raise ValueError(f"ID de cliente inválido: {client_id}. Debe ser un número.")
                    
                    # Verificar que el cliente existe en la BD antes de insertar
                    cursor.execute("SELECT 1 FROM clientes WHERE id = %(cliente_id)s", 
                                 {'cliente_id': cliente_id_int})
                    if cursor.fetchone() is None:
                        raise ValueError(f"El cliente con ID {cliente_id_int} no existe en la base de datos.")
                    
                    cursor.execute("""
                        INSERT INTO rutas_clientes (ruta_id, cliente_id, orden_visita)
                        VALUES (%(ruta_id)s, %(cliente_id)s, %(orden)s)
                    """, {
                        'ruta_id': ruta_id,
                        'cliente_id': cliente_id_int,
                        'orden': orden
                    })
                
                # Si no estamos en una transacción explícita, hacer commit
                if not self._in_transaction:
                    self._conn.commit()
                    
            except psycopg2.Error as e:
                if not self._in_transaction:
                    self._conn.rollback()
                raise
    
    def find_by_id(self, route_id: str) -> Optional[Route]:
        """
        Busca una ruta por su ID (identificador_unico).
        
        Args:
            route_id: ID de la ruta
            
        Returns:
            La ruta si existe, None en caso contrario
        """
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, identificador_unico, nombre_descriptivo, dia_semana, cedis_id, activa
                FROM rutas
                WHERE identificador_unico = %(route_id)s
            """, {'route_id': route_id})
            
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return self._row_to_route(cursor, row)
    
    def get_all(self) -> List[Route]:
        """
        Obtiene todas las rutas activas.
        
        Returns:
            Lista de rutas activas
        """
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, identificador_unico, nombre_descriptivo, dia_semana, cedis_id, activa
                FROM rutas
                WHERE activa = TRUE
                ORDER BY nombre_descriptivo
            """)
            
            rows = cursor.fetchall()
            return [self._row_to_route(cursor, row) for row in rows]
    
    def get_all_including_inactive(self) -> List[Route]:
        """
        Obtiene todas las rutas (activas e inactivas).
        
        Returns:
            Lista de todas las rutas
        """
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, identificador_unico, nombre_descriptivo, dia_semana, cedis_id, activa
                FROM rutas
                ORDER BY activa DESC, nombre_descriptivo
            """)
            
            rows = cursor.fetchall()
            return [self._row_to_route(cursor, row) for row in rows]
    
    def delete(self, route_id: str) -> None:
        """
        Elimina físicamente una ruta (hard delete).
        
        Args:
            route_id: ID de la ruta a eliminar
            
        Raises:
            ValueError: Si la ruta no existe
        """
        with self._get_cursor() as cursor:
            try:
                # Buscar la ruta
                cursor.execute("""
                    SELECT id FROM rutas WHERE identificador_unico = %(id)s
                """, {'id': route_id})
                
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"Ruta {route_id} no encontrada para eliminar")
                
                ruta_id = result['id']
                
                # Eliminar clientes asociados
                cursor.execute("DELETE FROM rutas_clientes WHERE ruta_id = %(ruta_id)s", 
                             {'ruta_id': ruta_id})
                
                # Eliminar la ruta
                cursor.execute("DELETE FROM rutas WHERE id = %(ruta_id)s", 
                             {'ruta_id': ruta_id})
                
                # Si no estamos en una transacción explícita, hacer commit
                if not self._in_transaction:
                    self._conn.commit()
                    
            except psycopg2.Error as e:
                if not self._in_transaction:
                    self._conn.rollback()
                raise
    
    def get_by_cedis_and_day(self, cedis_id: str, day_of_week: str) -> List[Route]:
        """
        Obtiene rutas activas de un CEDIS en un día específico.
        
        Args:
            cedis_id: ID del CEDIS
            day_of_week: Día de la semana (nombre o número)
            
        Returns:
            Lista de rutas que coinciden
        """
        with self._get_cursor() as cursor:
            dia_numero = self._convert_day_name_to_number(day_of_week)
            
            cursor.execute("""
                SELECT id, identificador_unico, nombre_descriptivo, dia_semana, cedis_id, activa
                FROM rutas
                WHERE cedis_id = %(cedis_id)s 
                  AND dia_semana = %(day_of_week)s
                  AND activa = TRUE
                ORDER BY nombre_descriptivo
            """, {
                'cedis_id': int(cedis_id) if isinstance(cedis_id, str) and cedis_id.isdigit() else 0,
                'day_of_week': dia_numero
            })
            
            rows = cursor.fetchall()
            return [self._row_to_route(cursor, row) for row in rows]
    
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
    
    def _row_to_route(self, cursor: RealDictCursor, row: dict) -> Route:
        """
        Convierte una fila de base de datos a una entidad Route del dominio.
        
        Args:
            cursor: Cursor para realizar queries adicionales
            row: Fila de PostgreSQL (diccionario)
            
        Returns:
            Entidad Route
        """
        ruta_id = row['id']
        
        # Obtener los clientes asociados
        cursor.execute("""
            SELECT cliente_id FROM rutas_clientes 
            WHERE ruta_id = %(ruta_id)s 
            ORDER BY orden_visita
        """, {'ruta_id': ruta_id})
        
        client_ids = [str(r['cliente_id']) for r in cursor.fetchall()]
        
        # Convertir día de la semana de número a nombre
        dia_nombre = self._convert_day_number_to_name(row['dia_semana'])
        
        return Route(
            id=row['identificador_unico'],
            name=row['nombre_descriptivo'],
            cedis_id=str(row['cedis_id']),
            day_of_week=dia_nombre,
            client_ids=client_ids,
            is_active=bool(row['activa'])
        )
    
    def _convert_day_name_to_number(self, day_name: str) -> int:
        """
        Convierte nombre de día a número (1-7).
        Acepta tanto nombres en español como en inglés.
        
        Args:
            day_name: Nombre del día en inglés o español
            
        Returns:
            Número del día (1=Lunes, 7=Domingo)
        """
        day_mapping = {
            # Inglés
            'MONDAY': 1, 'TUESDAY': 2, 'WEDNESDAY': 3, 
            'THURSDAY': 4, 'FRIDAY': 5, 'SATURDAY': 6, 'SUNDAY': 7,
            # Español
            'LUNES': 1, 'MARTES': 2, 'MIÉRCOLES': 3, 
            'JUEVES': 4, 'VIERNES': 5, 'SÁBADO': 6, 'DOMINGO': 7
        }
        return day_mapping.get(day_name.upper(), 1)
    
    def _convert_day_number_to_name(self, day_num: int) -> str:
        """
        Convierte número de día a nombre en ESPAÑOL.
        Retorna el formato esperado por el modelo de dominio.
        
        Args:
            day_num: Número del día (1-7)
            
        Returns:
            Nombre del día en español (LUNES, MARTES, etc.)
        """
        day_mapping = {
            1: 'LUNES',
            2: 'MARTES',
            3: 'MIÉRCOLES',
            4: 'JUEVES',
            5: 'VIERNES',
            6: 'SÁBADO',
            7: 'DOMINGO'
        }
        return day_mapping.get(day_num, 'LUNES')
    
    def _get_or_create_cedis(self, cursor: RealDictCursor, cedis_id: str) -> int:
        """
        Obtiene o crea un CEDIS.
        
        Args:
            cursor: Cursor de la BD
            cedis_id: Identificador del CEDIS
            
        Returns:
            ID numérico del CEDIS en la BD
        """
        try:
            # Intentar convertir a número si es posible
            cedis_id_num = int(cedis_id) if isinstance(cedis_id, str) and cedis_id.isdigit() else 0
            
            if cedis_id_num > 0:
                # Verificar si existe
                cursor.execute("SELECT id FROM cedis WHERE id = %(id)s", {'id': cedis_id_num})
                result = cursor.fetchone()
                if result:
                    return cedis_id_num
            
            # Si no existe, obtener el primero como default
            cursor.execute("SELECT id FROM cedis LIMIT 1")
            result = cursor.fetchone()
            if result:
                return result['id']
            
            # Si no hay CEDIS, crear uno
            cursor.execute("""
                INSERT INTO cedis (nombre, ciudad)
                VALUES ('CEDIS Por Defecto', 'Bogotá')
                RETURNING id
            """)
            return cursor.fetchone()['id']
            
        except Exception:
            # En caso de error, usar el primero
            cursor.execute("SELECT id FROM cedis LIMIT 1")
            result = cursor.fetchone()
            return result['id'] if result else 1
    
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
