"""
Database Connection Singleton
Patrón de Diseño: Singleton

Propósito: Garantizar que solo exista una única instancia de la conexión a la base de datos
en toda la aplicación, optimizando recursos y evitando múltiples conexiones innecesarias.

Ventajas:
- Control de acceso único a la base de datos
- Reutilización de la conexión existente
- Gestión centralizada de la conexión
- Reducción del overhead de múltiples conexiones

Ubicación: src/infrastructure/database/database_connection.py
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any
from contextlib import contextmanager
import threading


class DatabaseConnection:
    """
    Singleton para gestionar la conexión a PostgreSQL.
    
    Implementa el patrón Singleton Thread-Safe para garantizar
    una única instancia de conexión a la base de datos en toda la aplicación.
    
    Atributos:
        _instance: Instancia única del singleton
        _lock: Lock para thread-safety
        _connection: Conexión activa a PostgreSQL
    """
    
    _instance: Optional['DatabaseConnection'] = None
    _lock: threading.Lock = threading.Lock()
    _connection: Optional[Any] = None
    _connection_params: Optional[Dict[str, Any]] = None
    
    def __new__(cls, connection_params: Optional[Dict[str, Any]] = None):
        """
        Implementación Thread-Safe del Singleton.
        
        Utiliza Double-Checked Locking para optimizar el rendimiento
        mientras mantiene la seguridad en entornos multi-hilo.
        
        Args:
            connection_params: Parámetros de conexión (solo en primera llamada)
            
        Returns:
            Instancia única de DatabaseConnection
        """
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    instance = super().__new__(cls)
                    cls._instance = instance
                    
                    # Inicializar parámetros solo en la primera creación
                    if connection_params:
                        cls._connection_params = connection_params
        
        return cls._instance
    
    def __init__(self, connection_params: Optional[Dict[str, Any]] = None):
        """
        Inicializa la conexión (solo se ejecuta una vez).
        
        Args:
            connection_params: Diccionario con parámetros de conexión PostgreSQL
        """
        # Evitar reinicialización
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        if connection_params:
            self._connection_params = connection_params
        
        if self._connection_params is None:
            raise ValueError("Parámetros de conexión requeridos para inicializar DatabaseConnection")
        
        self._connect()
    
    def _connect(self) -> None:
        """
        Establece la conexión con PostgreSQL.
        
        Raises:
            ConnectionError: Si no se puede establecer la conexión
        """
        try:
            if self._connection is None or self._connection.closed:
                self._connection = psycopg2.connect(**self._connection_params)
                self._connection.autocommit = False
                print(f"✅ Conexión Singleton establecida con PostgreSQL: {self._connection_params.get('database')}")
        except psycopg2.Error as e:
            raise ConnectionError(f"Error al conectar con PostgreSQL: {str(e)}")
    
    def get_connection(self):
        """
        Obtiene la conexión activa (singleton).
        
        Si la conexión está cerrada, la reconecta automáticamente.
        
        Returns:
            Conexión psycopg2 activa
        """
        if self._connection is None or self._connection.closed:
            self._connect()
        return self._connection
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """
        Context manager para obtener un cursor de forma segura.
        
        Args:
            dict_cursor: Si True, usa RealDictCursor para obtener resultados como diccionarios
            
        Yields:
            Cursor de PostgreSQL
            
        Example:
            >>> db = DatabaseConnection.get_instance()
            >>> with db.get_cursor() as cursor:
            >>>     cursor.execute("SELECT * FROM rutas")
            >>>     results = cursor.fetchall()
        """
        connection = self.get_connection()
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = connection.cursor(cursor_factory=cursor_factory)
        
        try:
            yield cursor
        finally:
            cursor.close()
    
    def commit(self) -> None:
        """Confirma la transacción actual."""
        connection = self.get_connection()
        connection.commit()
    
    def rollback(self) -> None:
        """Revierte la transacción actual."""
        connection = self.get_connection()
        connection.rollback()
    
    def close(self) -> None:
        """
        Cierra la conexión.
        
        Nota: Usar con precaución. En aplicaciones con Singleton,
        generalmente la conexión permanece abierta durante toda la vida de la app.
        """
        if self._connection and not self._connection.closed:
            self._connection.close()
            print("🔒 Conexión Singleton cerrada")
    
    @classmethod
    def get_instance(cls, connection_params: Optional[Dict[str, Any]] = None) -> 'DatabaseConnection':
        """
        Método de acceso explícito al Singleton.
        
        Args:
            connection_params: Parámetros de conexión (opcional si ya se inicializó)
            
        Returns:
            Instancia única de DatabaseConnection
            
        Example:
            >>> from config import Config
            >>> params = {
            >>>     'host': Config.DB_HOST,
            >>>     'port': Config.DB_PORT,
            >>>     'database': Config.DB_NAME,
            >>>     'user': Config.DB_USER,
            >>>     'password': Config.DB_PASSWORD
            >>> }
            >>> db = DatabaseConnection.get_instance(params)
        """
        if cls._instance is None:
            return cls(connection_params)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        Resetea el singleton (útil para testing).
        
        ⚠️ ADVERTENCIA: Solo usar en entornos de testing.
        """
        with cls._lock:
            if cls._instance and cls._connection:
                cls._instance.close()
            cls._instance = None
            cls._connection = None
            cls._connection_params = None
    
    def __enter__(self):
        """Soporte para context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del context manager."""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
