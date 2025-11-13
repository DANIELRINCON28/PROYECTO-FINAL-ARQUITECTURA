"""
Route Optimization Strategy Pattern
Patrón de Diseño: Strategy

Propósito: Definir una familia de algoritmos de optimización de rutas,
encapsular cada uno de ellos y hacerlos intercambiables. Strategy permite
que el algoritmo varíe independientemente de los clientes que lo usan.

Ventajas:
- Permite cambiar el algoritmo de optimización en tiempo de ejecución
- Facilita agregar nuevos algoritmos sin modificar código existente
- Separa la lógica de optimización del resto del sistema
- Facilita testing de diferentes estrategias

Ubicación: src/domain/strategies/optimization_strategy.py
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from src.domain.models.route import Route


@dataclass
class OptimizationResult:
    """
    Resultado de una optimización de ruta.
    
    Attributes:
        optimized_order: Orden optimizado de los IDs de clientes
        total_distance_km: Distancia total en kilómetros
        total_duration_minutes: Duración total en minutos
        algorithm_used: Nombre del algoritmo utilizado
        metadata: Información adicional del algoritmo
    """
    optimized_order: List[str]
    total_distance_km: float
    total_duration_minutes: float
    algorithm_used: str
    metadata: Dict[str, Any] = None


class RouteOptimizationStrategy(ABC):
    """
    Interfaz abstracta para estrategias de optimización de rutas.
    
    Define el contrato que deben cumplir todas las estrategias de optimización.
    """
    
    @abstractmethod
    def optimize(
        self,
        route: Route,
        client_locations: Dict[str, Tuple[float, float]],
        origin: Tuple[float, float]
    ) -> OptimizationResult:
        """
        Optimiza el orden de los clientes en una ruta.
        
        Args:
            route: Ruta a optimizar
            client_locations: Diccionario {client_id: (lat, lng)}
            origin: Coordenadas de origen (lat, lng)
            
        Returns:
            Resultado de la optimización
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna el nombre de la estrategia."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si la estrategia está disponible para usar."""
        pass


class NearestNeighborStrategy(RouteOptimizationStrategy):
    """
    Estrategia de optimización: Vecino Más Cercano (Greedy).
    
    Algoritmo:
    1. Empieza en el origen
    2. Selecciona el cliente más cercano no visitado
    3. Repite hasta visitar todos los clientes
    
    Ventajas: Rápido, simple
    Desventajas: No garantiza la solución óptima
    """
    
    def optimize(
        self,
        route: Route,
        client_locations: Dict[str, Tuple[float, float]],
        origin: Tuple[float, float]
    ) -> OptimizationResult:
        """Implementa el algoritmo del vecino más cercano."""
        if not route.client_ids:
            return OptimizationResult(
                optimized_order=[],
                total_distance_km=0.0,
                total_duration_minutes=0.0,
                algorithm_used=self.get_name(),
                metadata={'clients_count': 0}
            )
        
        unvisited = set(route.client_ids)
        optimized_order = []
        current_position = origin
        total_distance = 0.0
        
        while unvisited:
            # Encontrar el cliente más cercano
            nearest_client = min(
                unvisited,
                key=lambda c: self._calculate_distance(current_position, client_locations[c])
            )
            
            # Calcular distancia
            distance = self._calculate_distance(current_position, client_locations[nearest_client])
            total_distance += distance
            
            # Actualizar estado
            optimized_order.append(nearest_client)
            unvisited.remove(nearest_client)
            current_position = client_locations[nearest_client]
        
        # Estimar duración (velocidad promedio 40 km/h + 15 min por cliente)
        total_duration = (total_distance / 40.0) * 60 + len(optimized_order) * 15
        
        return OptimizationResult(
            optimized_order=optimized_order,
            total_distance_km=round(total_distance, 2),
            total_duration_minutes=round(total_duration, 0),
            algorithm_used=self.get_name(),
            metadata={
                'clients_count': len(optimized_order),
                'avg_distance_per_client': round(total_distance / len(optimized_order), 2)
            }
        )
    
    def _calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        Calcula la distancia euclidiana aproximada entre dos puntos.
        
        Fórmula de Haversine simplificada para distancias cortas.
        """
        import math
        
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        # Aproximación simple (no exacta, pero suficiente para el algoritmo)
        dlat = abs(lat2 - lat1)
        dlon = abs(lon2 - lon1)
        
        # 1 grado ≈ 111 km
        distance = math.sqrt((dlat * 111) ** 2 + (dlon * 111 * math.cos(math.radians(lat1))) ** 2)
        
        return distance
    
    def get_name(self) -> str:
        """Retorna el nombre de la estrategia."""
        return "Nearest Neighbor (Greedy)"
    
    def is_available(self) -> bool:
        """Siempre disponible."""
        return True


class GoogleMapsStrategy(RouteOptimizationStrategy):
    """
    Estrategia de optimización usando Google Maps API.
    
    Utiliza la API de Google Maps Directions con waypoint optimization
    para obtener la ruta óptima considerando tráfico real y distancias reales.
    
    Ventajas: Muy preciso, considera tráfico real
    Desventajas: Requiere API key, tiene costo
    """
    
    def __init__(self, maps_service):
        """
        Inicializa la estrategia con el servicio de Google Maps.
        
        Args:
            maps_service: Instancia de GoogleMapsService
        """
        self._maps_service = maps_service
    
    def optimize(
        self,
        route: Route,
        client_locations: Dict[str, Tuple[float, float]],
        origin: Tuple[float, float]
    ) -> OptimizationResult:
        """Utiliza Google Maps API para optimizar la ruta."""
        if not route.client_ids:
            return OptimizationResult(
                optimized_order=[],
                total_distance_km=0.0,
                total_duration_minutes=0.0,
                algorithm_used=self.get_name(),
                metadata={'clients_count': 0}
            )
        
        try:
            # Delegar al servicio de Google Maps
            waypoints = [client_locations[client_id] for client_id in route.client_ids]
            result = self._maps_service.optimize_route(origin, waypoints)
            
            # Mapear el resultado al orden de clientes
            optimized_order = [route.client_ids[i] for i in result['waypoint_order']]
            
            return OptimizationResult(
                optimized_order=optimized_order,
                total_distance_km=result['total_distance_km'],
                total_duration_minutes=result['total_duration_minutes'],
                algorithm_used=self.get_name(),
                metadata={
                    'clients_count': len(optimized_order),
                    'google_maps_status': 'OK'
                }
            )
        
        except Exception as e:
            # Fallback: retornar orden original si hay error
            print(f"⚠️ Error en Google Maps API: {e}. Usando orden original.")
            return OptimizationResult(
                optimized_order=route.client_ids,
                total_distance_km=0.0,
                total_duration_minutes=0.0,
                algorithm_used=f"{self.get_name()} (Fallback)",
                metadata={'error': str(e)}
            )
    
    def get_name(self) -> str:
        """Retorna el nombre de la estrategia."""
        return "Google Maps Optimization"
    
    def is_available(self) -> bool:
        """Verifica si el servicio de Google Maps está disponible."""
        return self._maps_service is not None


class TwoOptStrategy(RouteOptimizationStrategy):
    """
    Estrategia de optimización: 2-opt.
    
    Algoritmo:
    1. Empieza con un orden inicial
    2. Intenta intercambiar pares de aristas
    3. Si mejora la distancia, acepta el cambio
    4. Repite hasta que no haya mejoras
    
    Ventajas: Mejora local, mejor que Greedy
    Desventajas: Puede quedar en óptimos locales
    """
    
    def __init__(self, max_iterations: int = 1000):
        """
        Inicializa la estrategia 2-opt.
        
        Args:
            max_iterations: Máximo número de iteraciones
        """
        self._max_iterations = max_iterations
    
    def optimize(
        self,
        route: Route,
        client_locations: Dict[str, Tuple[float, float]],
        origin: Tuple[float, float]
    ) -> OptimizationResult:
        """Implementa el algoritmo 2-opt."""
        if not route.client_ids:
            return OptimizationResult(
                optimized_order=[],
                total_distance_km=0.0,
                total_duration_minutes=0.0,
                algorithm_used=self.get_name(),
                metadata={'clients_count': 0}
            )
        
        # Empezar con orden inicial (puede ser aleatorio o vecino más cercano)
        current_order = route.client_ids.copy()
        improved = True
        iterations = 0
        
        while improved and iterations < self._max_iterations:
            improved = False
            iterations += 1
            
            for i in range(1, len(current_order) - 1):
                for j in range(i + 1, len(current_order)):
                    # Intentar intercambio 2-opt
                    new_order = self._two_opt_swap(current_order, i, j)
                    
                    # Calcular distancias
                    current_distance = self._calculate_total_distance(current_order, client_locations, origin)
                    new_distance = self._calculate_total_distance(new_order, client_locations, origin)
                    
                    # Si mejora, aceptar
                    if new_distance < current_distance:
                        current_order = new_order
                        improved = True
        
        # Calcular métricas finales
        total_distance = self._calculate_total_distance(current_order, client_locations, origin)
        total_duration = (total_distance / 40.0) * 60 + len(current_order) * 15
        
        return OptimizationResult(
            optimized_order=current_order,
            total_distance_km=round(total_distance, 2),
            total_duration_minutes=round(total_duration, 0),
            algorithm_used=self.get_name(),
            metadata={
                'clients_count': len(current_order),
                'iterations': iterations,
                'avg_distance_per_client': round(total_distance / len(current_order), 2)
            }
        )
    
    def _two_opt_swap(self, route: List[str], i: int, j: int) -> List[str]:
        """Realiza un intercambio 2-opt."""
        new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
        return new_route
    
    def _calculate_total_distance(
        self,
        order: List[str],
        locations: Dict[str, Tuple[float, float]],
        origin: Tuple[float, float]
    ) -> float:
        """Calcula la distancia total de una ruta."""
        import math
        
        total = 0.0
        current = origin
        
        for client_id in order:
            next_point = locations[client_id]
            total += self._haversine_distance(current, next_point)
            current = next_point
        
        return total
    
    def _haversine_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calcula la distancia usando la fórmula de Haversine."""
        import math
        
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        R = 6371  # Radio de la Tierra en km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c
        
        return distance
    
    def get_name(self) -> str:
        """Retorna el nombre de la estrategia."""
        return "2-Opt Optimization"
    
    def is_available(self) -> bool:
        """Siempre disponible."""
        return True


class OptimizationContext:
    """
    Contexto para ejecutar estrategias de optimización.
    
    Permite cambiar dinámicamente la estrategia de optimización
    y ejecutarla de manera uniforme.
    """
    
    def __init__(self, strategy: RouteOptimizationStrategy):
        """
        Inicializa el contexto con una estrategia.
        
        Args:
            strategy: Estrategia de optimización a usar
        """
        self._strategy = strategy
    
    def set_strategy(self, strategy: RouteOptimizationStrategy) -> None:
        """
        Cambia la estrategia de optimización.
        
        Args:
            strategy: Nueva estrategia a usar
        """
        self._strategy = strategy
    
    def optimize(
        self,
        route: Route,
        client_locations: Dict[str, Tuple[float, float]],
        origin: Tuple[float, float]
    ) -> OptimizationResult:
        """
        Ejecuta la optimización usando la estrategia actual.
        
        Args:
            route: Ruta a optimizar
            client_locations: Ubicaciones de los clientes
            origin: Punto de origen
            
        Returns:
            Resultado de la optimización
        """
        if not self._strategy.is_available():
            raise RuntimeError(f"Estrategia {self._strategy.get_name()} no disponible")
        
        return self._strategy.optimize(route, client_locations, origin)
    
    def get_current_strategy_name(self) -> str:
        """Retorna el nombre de la estrategia actual."""
        return self._strategy.get_name()
