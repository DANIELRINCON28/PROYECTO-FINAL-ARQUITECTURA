"""
Service Factory Pattern
Patrón de Diseño: Factory Method / Abstract Factory

Propósito: Proporcionar una interfaz centralizada para crear instancias de servicios
con sus dependencias correctamente configuradas, facilitando la inyección de dependencias
y el testing.

Ventajas:
- Centralización de la creación de objetos complejos
- Facilita el cambio de implementaciones
- Simplifica la configuración de dependencias
- Mejora la testabilidad mediante mocks

Ubicación: src/application/factories/service_factory.py
"""
from typing import Optional

from src.application.services.route_service import RouteService
from src.application.services.route_optimization_service import RouteOptimizationService
from src.domain.ports.route_repository_port import RouteRepositoryPort
from src.domain.ports.route_optimization_port import RouteOptimizationPort
from src.domain.ports.geo_distance_provider_port import GeoDistanceProviderPort
from src.domain.ports.route_optimization_solver_port import RouteOptimizationSolverPort
from src.infrastructure.persistence.postgres_route_repository import PostgresRouteRepository
from src.infrastructure.services.google_maps_service import GoogleMapsService
from src.infrastructure.services.google_maps_distance_adapter import GoogleMapsDistanceAdapter
from src.infrastructure.services.ortools_tsp_solver import ORToolsTSPSolver, NearestNeighborTSPSolver
from src.infrastructure.database.database_connection import DatabaseConnection
from config import Config


class ServiceFactory:
    """
    Factory para crear servicios de aplicación con sus dependencias.
    
    Implementa el patrón Abstract Factory para crear familias de servicios
    relacionados, asegurando que todas las dependencias estén correctamente
    configuradas.
    
    Responsabilidades:
    - Crear instancias de servicios de aplicación
    - Configurar dependencias (repositorios, servicios externos)
    - Gestionar el ciclo de vida de las conexiones
    """
    
    def __init__(self):
        """Inicializa la factory con la configuración por defecto."""
        self._db_connection: Optional[DatabaseConnection] = None
        self._repository: Optional[RouteRepositoryPort] = None
        self._optimization_service: Optional[RouteOptimizationPort] = None
        self._geo_distance_provider: Optional[GeoDistanceProviderPort] = None
        self._tsp_solver: Optional[RouteOptimizationSolverPort] = None
    
    def _get_database_connection(self) -> DatabaseConnection:
        """
        Obtiene la conexión singleton a la base de datos.
        
        Returns:
            Instancia singleton de DatabaseConnection
        """
        if self._db_connection is None:
            connection_params = {
                'host': Config.DB_HOST,
                'port': int(Config.DB_PORT),
                'database': Config.DB_NAME,
                'user': Config.DB_USER,
                'password': Config.DB_PASSWORD
            }
            self._db_connection = DatabaseConnection.get_instance(connection_params)
        
        return self._db_connection
    
    def _create_repository(self) -> RouteRepositoryPort:
        """
        Crea o retorna el repositorio de rutas.
        
        Returns:
            Implementación de RouteRepositoryPort
        """
        if self._repository is None:
            connection_params = {
                'host': Config.DB_HOST,
                'port': int(Config.DB_PORT),
                'database': Config.DB_NAME,
                'user': Config.DB_USER,
                'password': Config.DB_PASSWORD
            }
            self._repository = PostgresRouteRepository(connection_params)
        
        return self._repository
    
    def _create_optimization_service(self) -> Optional[RouteOptimizationPort]:
        """
        Crea o retorna el servicio de optimización (legacy).
        
        Returns:
            Implementación de RouteOptimizationPort o None si no está disponible
        """
        if self._optimization_service is None:
            if Config.GOOGLE_MAPS_API_KEY:
                self._optimization_service = GoogleMapsService(Config.GOOGLE_MAPS_API_KEY)
            else:
                print("⚠️ Warning: Google Maps API Key no configurada. Optimización no disponible.")
        
        return self._optimization_service
    
    def _create_geo_distance_provider(self) -> Optional[GeoDistanceProviderPort]:
        """
        Crea o retorna el proveedor de distancias geográficas.
        
        Returns:
            Implementación de GeoDistanceProviderPort o None si no está disponible
        """
        if self._geo_distance_provider is None:
            if Config.GOOGLE_MAPS_API_KEY:
                self._geo_distance_provider = GoogleMapsDistanceAdapter(Config.GOOGLE_MAPS_API_KEY)
                print("✅ Google Maps Distance Provider configurado")
            else:
                print("⚠️ Warning: Google Maps API Key no configurada. Geo Distance Provider no disponible.")
        
        return self._geo_distance_provider
    
    def _create_tsp_solver(self) -> RouteOptimizationSolverPort:
        """
        Crea o retorna el solucionador TSP.
        
        Intenta usar OR-Tools, si no está disponible usa Nearest Neighbor como fallback.
        
        Returns:
            Implementación de RouteOptimizationSolverPort
        """
        if self._tsp_solver is None:
            # Intentar con OR-Tools primero
            ortools_solver = ORToolsTSPSolver()
            
            if ortools_solver.is_available():
                self._tsp_solver = ortools_solver
                print("✅ OR-Tools TSP Solver configurado")
            else:
                # Fallback a Nearest Neighbor
                self._tsp_solver = NearestNeighborTSPSolver()
                print("⚠️ OR-Tools no disponible. Usando Nearest Neighbor Solver (subóptimo)")
        
        return self._tsp_solver
    
    def create_route_service(self) -> RouteService:
        """
        Crea una instancia de RouteService con todas sus dependencias.
        
        Returns:
            RouteService completamente configurado
            
        Example:
            >>> factory = ServiceFactory()
            >>> route_service = factory.create_route_service()
            >>> routes = route_service.get_all_routes()
        """
        repository = self._create_repository()
        return RouteService(repository)
    
    def create_optimization_service(self) -> Optional[RouteOptimizationService]:
        """
        Crea una instancia de RouteOptimizationService con TODOS los adaptadores.
        
        Incluye tanto los servicios legacy como los nuevos para optimización inteligente.
        
        Returns:
            RouteOptimizationService configurado con todas las capacidades
            
        Example:
            >>> factory = ServiceFactory()
            >>> opt_service = factory.create_optimization_service()
            >>> if opt_service:
            >>>     # Usar optimización inteligente (nuevo)
            >>>     result = opt_service.optimize_route_intelligent(dto, clients)
            >>>     # O usar métodos legacy
            >>>     metrics = opt_service.calculate_route_metrics(cedis, clients)
        """
        repository = self._create_repository()
        optimization_port = self._create_optimization_service()
        geo_provider = self._create_geo_distance_provider()
        tsp_solver = self._create_tsp_solver()
        
        # Crear servicio con todos los adaptadores (legacy + nuevos)
        return RouteOptimizationService(
            route_repository=repository,
            optimization_service=optimization_port,
            geo_distance_provider=geo_provider,
            optimization_solver=tsp_solver
        )
    
    def create_all_services(self) -> tuple[RouteService, Optional[RouteOptimizationService]]:
        """
        Crea todas las instancias de servicios necesarias.
        
        Returns:
            Tupla (RouteService, RouteOptimizationService)
            
        Example:
            >>> factory = ServiceFactory()
            >>> route_service, opt_service = factory.create_all_services()
        """
        route_service = self.create_route_service()
        optimization_service = self.create_optimization_service()
        
        return route_service, optimization_service
    
    @staticmethod
    def create_default() -> 'ServiceFactory':
        """
        Crea una factory con configuración por defecto.
        
        Returns:
            ServiceFactory configurada
            
        Example:
            >>> factory = ServiceFactory.create_default()
            >>> route_service = factory.create_route_service()
        """
        return ServiceFactory()
    
    @staticmethod
    def create_for_testing(
        repository: Optional[RouteRepositoryPort] = None,
        optimization_port: Optional[RouteOptimizationPort] = None
    ) -> 'ServiceFactory':
        """
        Crea una factory para testing con mocks.
        
        Args:
            repository: Mock del repositorio (opcional)
            optimization_port: Mock del servicio de optimización (opcional)
            
        Returns:
            ServiceFactory configurada para testing
            
        Example:
            >>> from unittest.mock import Mock
            >>> mock_repo = Mock(spec=RouteRepositoryPort)
            >>> factory = ServiceFactory.create_for_testing(repository=mock_repo)
            >>> route_service = factory.create_route_service()
        """
        factory = ServiceFactory()
        
        if repository:
            factory._repository = repository
        
        if optimization_port:
            factory._optimization_service = optimization_port
        
        return factory


class FlaskServiceFactory(ServiceFactory):
    """
    Factory especializada para crear servicios para la aplicación Flask.
    
    Extiende ServiceFactory agregando configuraciones específicas
    para el contexto web de Flask.
    """
    
    def __init__(self):
        """Inicializa la factory para Flask."""
        super().__init__()
        self._flask_config = {
            'debug': Config.DEBUG,
            'port': Config.FLASK_PORT
        }
    
    def create_flask_app(self):
        """
        Crea la aplicación Flask con todos sus servicios configurados.
        
        Returns:
            Aplicación Flask configurada
            
        Example:
            >>> factory = FlaskServiceFactory()
            >>> app = factory.create_flask_app()
            >>> app.run()
        """
        from src.infrastructure.ui.flask_app import create_flask_app
        
        route_service = self.create_route_service()
        optimization_service = self.create_optimization_service()
        
        app = create_flask_app(route_service, optimization_service)
        app.config.update(self._flask_config)
        
        return app
    
    @staticmethod
    def create_and_run() -> None:
        """
        Crea y ejecuta la aplicación Flask.
        
        Método de conveniencia para iniciar la aplicación con un solo comando.
        
        Example:
            >>> FlaskServiceFactory.create_and_run()
        """
        factory = FlaskServiceFactory()
        app = factory.create_flask_app()
        
        print(f"🚀 Iniciando aplicación Flask en puerto {Config.FLASK_PORT}")
        app.run(
            host='0.0.0.0',
            port=Config.FLASK_PORT,
            debug=Config.DEBUG
        )


# Singleton global de la factory (opcional, para conveniencia)
_default_factory: Optional[ServiceFactory] = None


def get_default_factory() -> ServiceFactory:
    """
    Obtiene la instancia singleton de la factory por defecto.
    
    Returns:
        Instancia global de ServiceFactory
        
    Example:
        >>> factory = get_default_factory()
        >>> route_service = factory.create_route_service()
    """
    global _default_factory
    
    if _default_factory is None:
        _default_factory = ServiceFactory.create_default()
    
    return _default_factory
