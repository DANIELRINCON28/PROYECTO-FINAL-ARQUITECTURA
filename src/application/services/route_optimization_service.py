"""
Route Optimization Application Service
Casos de uso relacionados con optimización de rutas usando servicios externos.
Implementa el algoritmo de ordenamiento inteligente (TSP) para minimizar distancias.
"""
from typing import List, Dict, Optional, Tuple
import logging
from src.domain.ports.route_repository_port import RouteRepositoryPort
from src.domain.ports.route_optimization_port import (
    RouteOptimizationPort,
    ClientLocation,
    RouteOptimizationResult
)
from src.domain.ports.geo_distance_provider_port import (
    GeoDistanceProviderPort,
    GeoCoordinate,
    DistanceResult
)
from src.domain.ports.route_optimization_solver_port import (
    RouteOptimizationSolverPort,
    OptimizationResult
)
from src.domain.models.route import Route
from src.domain.models.client import Client
from src.application.dtos import OptimizeRouteDTO, OptimizedRouteResultDTO

logger = logging.getLogger(__name__)


class RouteOptimizationService:
    """
    Servicio de aplicación para optimización de rutas.
    Coordina entre el repositorio de rutas y el servicio de optimización.
    
    Implementa RF-OPT-01: Ordenamiento Inteligente de Rutas (TSP).
    
    Patrón de Diseño: Service Layer Pattern + Dependency Injection
    - Orquesta múltiples operaciones del dominio
    - Mantiene la lógica de coordinación fuera del dominio
    - Recibe puertos (abstracciones), NO implementaciones concretas
    """
    
    def __init__(
        self,
        route_repository: RouteRepositoryPort,
        optimization_service: RouteOptimizationPort,
        geo_distance_provider: Optional[GeoDistanceProviderPort] = None,
        optimization_solver: Optional[RouteOptimizationSolverPort] = None
    ) -> None:
        """
        Inyección de dependencias: recibe abstracciones (puertos).
        
        Args:
            route_repository: Puerto del repositorio de rutas
            optimization_service: Puerto del servicio de optimización (legacy)
            geo_distance_provider: Puerto del proveedor de distancias geográficas (nuevo)
            optimization_solver: Puerto del solucionador TSP (nuevo)
        """
        self._route_repo = route_repository
        self._optimizer = optimization_service
        self._geo_provider = geo_distance_provider
        self._solver = optimization_solver
    
    def geocode_clients(
        self,
        clients: List[ClientLocation]
    ) -> List[ClientLocation]:
        """
        Geocodifica las direcciones de múltiples clientes.
        
        Args:
            clients: Lista de ubicaciones de clientes
            
        Returns:
            Lista de clientes con coordenadas actualizadas
        """
        geocoded_clients = []
        
        for client in clients:
            if client.latitude is None or client.longitude is None:
                # Geocodificar dirección
                coords = self._optimizer.geocode_address(client.address)
                
                if coords:
                    # Crear nuevo objeto con coordenadas
                    geocoded_client = ClientLocation(
                        client_id=client.client_id,
                        address=client.address,
                        latitude=coords[0],
                        longitude=coords[1]
                    )
                    geocoded_clients.append(geocoded_client)
                else:
                    # Mantener sin coordenadas
                    geocoded_clients.append(client)
            else:
                geocoded_clients.append(client)
        
        return geocoded_clients
    
    def optimize_route_order(
        self,
        route_id: str,
        cedis_location: Tuple[float, float],
        client_locations: List[ClientLocation]
    ) -> RouteOptimizationResult:
        """
        Optimiza el orden de visita de clientes en una ruta.
        
        Args:
            route_id: ID de la ruta a optimizar
            cedis_location: Coordenadas del CEDIS (punto de inicio)
            client_locations: Lista de ubicaciones de clientes
            
        Returns:
            Resultado de optimización con nuevo orden
        """
        # Filtrar solo clientes con coordenadas
        clients_with_coords = [
            c for c in client_locations 
            if c.latitude is not None and c.longitude is not None
        ]
        
        if len(clients_with_coords) == 0:
            raise ValueError("Ningún cliente tiene coordenadas para optimizar")
        
        # Extraer coordenadas
        waypoints = [
            (c.latitude, c.longitude) 
            for c in clients_with_coords
        ]
        
        # Optimizar usando el servicio externo
        result = self._optimizer.optimize_route(
            origin=cedis_location,
            waypoints=waypoints,
            destination=cedis_location  # Regresar al CEDIS
        )
        
        return result
    
    def calculate_route_metrics(
        self,
        cedis_location: Tuple[float, float],
        client_locations: List[ClientLocation]
    ) -> Dict[str, float]:
        """
        Calcula métricas de la ruta (distancia total, tiempo estimado).
        
        Args:
            cedis_location: Coordenadas del CEDIS
            client_locations: Lista de ubicaciones de clientes en orden
            
        Returns:
            Diccionario con métricas calculadas
        """
        clients_with_coords = [
            c for c in client_locations 
            if c.latitude is not None and c.longitude is not None
        ]
        
        if len(clients_with_coords) == 0:
            return {
                'total_distance_km': 0.0,
                'total_duration_minutes': 0.0,
                'clients_count': 0
            }
        
        waypoints = [
            (c.latitude, c.longitude) 
            for c in clients_with_coords
        ]
        
        # Calcular sin optimizar (orden actual)
        all_points = [cedis_location] + waypoints + [cedis_location]
        
        directions = self._optimizer.get_route_directions(all_points)
        
        if directions and 'legs' in directions:
            total_distance_m = sum(leg['distance']['value'] for leg in directions['legs'])
            total_duration_s = sum(leg['duration']['value'] for leg in directions['legs'])
            
            return {
                'total_distance_km': total_distance_m / 1000.0,
                'total_duration_minutes': total_duration_s / 60.0,
                'clients_count': len(clients_with_coords)
            }
        
        return {
            'total_distance_km': 0.0,
            'total_duration_minutes': 0.0,
            'clients_count': len(clients_with_coords)
        }
    
    def suggest_route_split(
        self,
        route_id: str,
        max_distance_km: float,
        max_duration_hours: float,
        cedis_location: Tuple[float, float],
        client_locations: List[ClientLocation]
    ) -> Dict:
        """
        Sugiere si una ruta debería dividirse basándose en métricas reales.
        
        Args:
            route_id: ID de la ruta
            max_distance_km: Distancia máxima permitida
            max_duration_hours: Duración máxima permitida
            cedis_location: Ubicación del CEDIS
            client_locations: Ubicaciones de clientes
            
        Returns:
            Diccionario con sugerencia y punto de división
        """
        metrics = self.calculate_route_metrics(cedis_location, client_locations)
        
        should_split = (
            metrics['total_distance_km'] > max_distance_km or
            metrics['total_duration_minutes'] > max_duration_hours * 60
        )
        
        split_suggestion = {
            'should_split': should_split,
            'reason': [],
            'current_metrics': metrics,
            'suggested_split_point': len(client_locations) // 2 if should_split else None
        }
        
        if metrics['total_distance_km'] > max_distance_km:
            split_suggestion['reason'].append(
                f"Distancia ({metrics['total_distance_km']:.1f} km) excede límite ({max_distance_km} km)"
            )
        
        if metrics['total_duration_minutes'] > max_duration_hours * 60:
            split_suggestion['reason'].append(
                f"Duración ({metrics['total_duration_minutes']:.1f} min) excede límite ({max_duration_hours * 60} min)"
            )
        
        return split_suggestion
    
    def test_optimization_service(self) -> bool:
        """
        Prueba la conexión con el servicio de optimización.
        
        Returns:
            True si el servicio está disponible
        """
        try:
            test_address = "Bogotá, Colombia"
            result = self._optimizer.geocode_address(test_address)
            return result is not None
        except Exception as e:
            print(f"Error probando servicio de optimización: {str(e)}")
            return False
    
    # ==================== NUEVOS MÉTODOS: TSP OPTIMIZATION ====================
    
    def optimize_route_intelligent(
        self, 
        dto: OptimizeRouteDTO,
        clients: List[Client]
    ) -> OptimizedRouteResultDTO:
        """
        RF-OPT-01: Optimiza el orden de visita de clientes usando TSP.
        
        Este es el método principal para el ordenamiento inteligente de rutas.
        Utiliza los nuevos puertos de geo_distance_provider y optimization_solver.
        
        Proceso:
        1. Obtener la ruta y validar que existe
        2. Obtener las coordenadas de todos los clientes
        3. Construir matriz de distancias usando el geo provider
        4. Resolver TSP usando el optimization solver
        5. Actualizar el orden de clientes en la ruta
        6. Persistir cambios
        
        Args:
            dto: Datos de la solicitud de optimización
            clients: Lista de objetos Client con coordenadas
            
        Returns:
            OptimizedRouteResultDTO con el resultado de la optimización
            
        Raises:
            ValueError: Si la ruta no existe o los datos son inválidos
            Exception: Si los servicios de optimización no están disponibles
        """
        logger.info(f"Iniciando optimización inteligente de ruta {dto.route_id}")
        
        # Verificar disponibilidad de servicios
        if self._geo_provider is None or self._solver is None:
            raise Exception(
                "Los servicios de optimización inteligente no están configurados. "
                "Verifique que geo_distance_provider y optimization_solver estén inyectados."
            )
        
        # 1. Obtener y validar la ruta
        route = self._route_repo.find_by_id(dto.route_id)
        if route is None:
            raise ValueError(f"Ruta {dto.route_id} no encontrada")
        
        if not route.client_ids:
            return OptimizedRouteResultDTO(
                route_id=dto.route_id,
                original_client_order=[],
                optimized_client_order=[],
                total_distance_km=0.0,
                total_duration_minutes=0.0,
                distance_saved_km=0.0,
                success=True,
                message="La ruta no tiene clientes asignados"
            )
        
        # 2. Validar que todos los clientes tienen coordenadas
        original_order = route.client_ids.copy()
        clients_dict = {c.id: c for c in clients}
        
        for client_id in route.client_ids:
            if client_id not in clients_dict:
                raise ValueError(f"Cliente {client_id} no encontrado en la lista proporcionada")
            client = clients_dict[client_id]
            if not client.has_coordinates():
                raise ValueError(
                    f"Cliente {client.name} ({client_id}) no tiene coordenadas geográficas. "
                    "Todas las ubicaciones deben tener latitud/longitud para optimizar."
                )
        
        # 3. Construir lista de coordenadas: [CEDIS, Cliente1, Cliente2, ...]
        coordinates = self._build_coordinates_list(dto, route, clients_dict)
        
        # 4. Calcular matriz de distancias
        try:
            distance_matrix, duration_matrix = self._calculate_distance_matrices(coordinates)
        except Exception as e:
            logger.error(f"Error calculando matriz de distancias: {str(e)}")
            return OptimizedRouteResultDTO(
                route_id=dto.route_id,
                original_client_order=original_order,
                optimized_client_order=original_order,
                total_distance_km=0.0,
                total_duration_minutes=0.0,
                distance_saved_km=0.0,
                success=False,
                message=f"Error al calcular distancias: {str(e)}"
            )
        
        # 5. Resolver TSP
        try:
            optimization_result = self._solve_optimization(
                distance_matrix,
                duration_matrix,
                dto.optimization_strategy
            )
        except Exception as e:
            logger.error(f"Error resolviendo TSP: {str(e)}")
            return OptimizedRouteResultDTO(
                route_id=dto.route_id,
                original_client_order=original_order,
                optimized_client_order=original_order,
                total_distance_km=0.0,
                total_duration_minutes=0.0,
                distance_saved_km=0.0,
                success=False,
                message=f"Error al optimizar: {str(e)}"
            )
        
        # 6. Mapear índices optimizados de vuelta a IDs de clientes
        optimized_client_order = self._map_indices_to_client_ids(
            optimization_result.ordered_indices,
            route.client_ids
        )
        
        # 7. Calcular ahorro de distancia (simplificado)
        distance_saved = 0.0  # Requeriría cálculo del orden original
        
        # 8. Actualizar la ruta con el nuevo orden
        try:
            route.reorder_clients(optimized_client_order)
            self._route_repo.update(route)
            self._route_repo.commit_transaction()
            logger.info(f"Ruta {dto.route_id} optimizada exitosamente")
        except Exception as e:
            logger.error(f"Error persistiendo cambios: {str(e)}")
            raise
        
        # 9. Retornar resultado
        return OptimizedRouteResultDTO(
            route_id=dto.route_id,
            original_client_order=original_order,
            optimized_client_order=optimized_client_order,
            total_distance_km=optimization_result.total_distance_km,
            total_duration_minutes=optimization_result.total_duration_minutes,
            distance_saved_km=distance_saved,
            success=True,
            message="Ruta optimizada exitosamente"
        )
    
    def _build_coordinates_list(
        self,
        dto: OptimizeRouteDTO,
        route: Route,
        clients_dict: dict
    ) -> List[GeoCoordinate]:
        """
        Construye la lista de coordenadas: [CEDIS, Cliente1, Cliente2, ...].
        
        Args:
            dto: DTO con coordenadas del CEDIS
            route: Entidad Route con IDs de clientes
            clients_dict: Diccionario de clientes por ID
            
        Returns:
            Lista de GeoCoordinate en el orden actual de la ruta
        """
        coordinates = [
            GeoCoordinate(
                latitude=dto.cedis_latitude,
                longitude=dto.cedis_longitude
            )
        ]
        
        for client_id in route.client_ids:
            client = clients_dict[client_id]
            coordinates.append(
                GeoCoordinate(
                    latitude=client.latitude,
                    longitude=client.longitude
                )
            )
        
        return coordinates
    
    def _calculate_distance_matrices(
        self,
        coordinates: List[GeoCoordinate]
    ) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Calcula las matrices de distancia y duración.
        
        Args:
            coordinates: Lista de coordenadas
            
        Returns:
            Tupla (distance_matrix, duration_matrix)
            
        Raises:
            Exception: Si el proveedor no está disponible o falla el cálculo
        """
        if not self._geo_provider.is_available():
            raise Exception("El proveedor de distancias no está disponible")
        
        # Obtener matriz de resultados
        results_matrix = self._geo_provider.calculate_distance_matrix(
            origins=coordinates,
            destinations=coordinates
        )
        
        # Separar en dos matrices: distancias y duraciones
        n = len(coordinates)
        distance_matrix = [[0.0] * n for _ in range(n)]
        duration_matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                result = results_matrix[i][j]
                distance_matrix[i][j] = result.distance_km
                duration_matrix[i][j] = result.duration_minutes
        
        return distance_matrix, duration_matrix
    
    def _solve_optimization(
        self,
        distance_matrix: List[List[float]],
        duration_matrix: List[List[float]],
        strategy: str
    ) -> OptimizationResult:
        """
        Resuelve el problema de optimización TSP.
        
        Args:
            distance_matrix: Matriz de distancias
            duration_matrix: Matriz de duraciones
            strategy: Estrategia de optimización
            
        Returns:
            OptimizationResult con la solución
            
        Raises:
            Exception: Si el solver no está disponible o falla
        """
        if not self._solver.is_available():
            raise Exception("El solucionador de optimización no está disponible")
        
        # Resolver con el criterio especificado
        return self._solver.solve_tsp_with_duration(
            distance_matrix=distance_matrix,
            duration_matrix=duration_matrix,
            start_index=0,  # CEDIS siempre es el índice 0
            optimize_by=strategy
        )
    
    def _map_indices_to_client_ids(
        self,
        ordered_indices: List[int],
        original_client_ids: List[str]
    ) -> List[str]:
        """
        Mapea los índices optimizados de vuelta a IDs de clientes.
        
        Args:
            ordered_indices: Lista de índices en orden óptimo [0, 3, 1, 2, ...]
            original_client_ids: Lista original de IDs de clientes
            
        Returns:
            Lista de IDs de clientes en el orden optimizado
            
        Note:
            El índice 0 corresponde al CEDIS, así que lo omitimos.
            Los índices 1, 2, 3... corresponden a original_client_ids[0], [1], [2]...
        """
        optimized_ids = []
        
        for index in ordered_indices:
            if index == 0:
                # Es el CEDIS, lo omitimos en el resultado final
                continue
            
            # Convertir índice de la matriz a índice de la lista de clientes
            # índice 1 de la matriz = original_client_ids[0]
            client_index = index - 1
            
            if 0 <= client_index < len(original_client_ids):
                optimized_ids.append(original_client_ids[client_index])
        
        return optimized_ids
    
    def check_optimization_availability(self) -> dict:
        """
        Verifica la disponibilidad de los servicios de optimización inteligente.
        
        Returns:
            Diccionario con el estado de cada servicio
        """
        result = {
            "legacy_optimizer_available": False,
            "geo_distance_provider_available": False,
            "optimization_solver_available": False,
            "intelligent_optimization_available": False
        }
        
        try:
            result["legacy_optimizer_available"] = self.test_optimization_service()
        except:
            pass
        
        if self._geo_provider is not None:
            result["geo_distance_provider_available"] = self._geo_provider.is_available()
        
        if self._solver is not None:
            result["optimization_solver_available"] = self._solver.is_available()
        
        result["intelligent_optimization_available"] = (
            result["geo_distance_provider_available"] and 
            result["optimization_solver_available"]
        )
        
        return result
