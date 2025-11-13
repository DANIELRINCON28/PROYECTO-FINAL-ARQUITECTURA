"""
OR-Tools TSP Solver Adapter (Infrastructure Layer)
Adaptador concreto que implementa RouteOptimizationSolverPort usando Google OR-Tools.
"""
from typing import List, Optional
from src.domain.ports.route_optimization_solver_port import (
    RouteOptimizationSolverPort,
    OptimizationResult
)
import logging

logger = logging.getLogger(__name__)

try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    logger.warning("OR-Tools no está instalado. El solucionador TSP no estará disponible.")


class ORToolsTSPSolver(RouteOptimizationSolverPort):
    """
    Adaptador que usa Google OR-Tools para resolver el problema TSP.
    
    Patrón de Diseño: Adapter Pattern (Hexagonal Architecture)
    - Implementa el puerto RouteOptimizationSolverPort
    - Encapsula la lógica específica de OR-Tools
    - Permite cambiar a otro solver sin afectar el dominio
    
    Google OR-Tools es una biblioteca de código abierto para optimización:
    - Problema del viajante (TSP)
    - Problema de ruteo de vehículos (VRP)
    - Programación lineal y entera
    
    Requiere:
    - Biblioteca ortools instalada: pip install ortools
    """
    
    def __init__(self) -> None:
        """Inicializa el solucionador TSP."""
        self._available = ORTOOLS_AVAILABLE
        
        if self._available:
            logger.info("OR-Tools TSP Solver inicializado correctamente")
        else:
            logger.warning("OR-Tools no disponible. Instale con: pip install ortools")
    
    def is_available(self) -> bool:
        """
        Verifica si OR-Tools está disponible.
        
        Returns:
            True si OR-Tools está instalado, False en caso contrario
        """
        return self._available
    
    def solve_tsp(
        self,
        distance_matrix: List[List[float]],
        start_index: int = 0
    ) -> OptimizationResult:
        """
        Resuelve el problema del viajante (TSP) usando OR-Tools.
        
        Args:
            distance_matrix: Matriz NxN donde [i][j] es la distancia del punto i al punto j
            start_index: Índice del punto de inicio (por defecto 0 = CEDIS)
            
        Returns:
            OptimizationResult con el orden óptimo de visita
            
        Raises:
            Exception: Si OR-Tools no está disponible o falla la optimización
        """
        if not self.is_available():
            raise Exception("OR-Tools no está disponible. Instale con: pip install ortools")
        
        if not distance_matrix:
            raise ValueError("La matriz de distancias no puede estar vacía")
        
        n = len(distance_matrix)
        
        # Validar que la matriz es cuadrada
        for row in distance_matrix:
            if len(row) != n:
                raise ValueError("La matriz de distancias debe ser cuadrada (NxN)")
        
        try:
            # Convertir matriz de floats a enteros (OR-Tools trabaja con enteros)
            # Multiplicamos por 1000 para mantener precisión de 3 decimales
            int_matrix = [[int(dist * 1000) for dist in row] for row in distance_matrix]
            
            # Crear el gestor de índices de enrutamiento
            manager = pywrapcp.RoutingIndexManager(n, 1, start_index)
            
            # Crear el modelo de enrutamiento
            routing = pywrapcp.RoutingModel(manager)
            
            # Definir la función de costo (distancia)
            def distance_callback(from_index: int, to_index: int) -> int:
                """Retorna la distancia entre dos nodos."""
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return int_matrix[from_node][to_node]
            
            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
            
            # Configurar parámetros de búsqueda
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
            # Usar búsqueda local para mejorar la solución
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            )
            search_parameters.time_limit.seconds = 30  # Límite de tiempo
            
            # Resolver el problema
            solution = routing.SolveWithParameters(search_parameters)
            
            if not solution:
                raise Exception("No se pudo encontrar una solución al problema TSP")
            
            # Extraer la ruta optimizada
            ordered_indices = []
            total_distance = 0
            
            index = routing.Start(0)
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                ordered_indices.append(node)
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                total_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
            
            # Convertir distancia de vuelta a float (dividir por 1000)
            total_distance_km = total_distance / 1000.0
            
            # Estimar duración (simplificado: 50 km/h promedio)
            total_duration_minutes = (total_distance_km / 50.0) * 60.0
            
            logger.info(
                f"TSP resuelto: {n} puntos, distancia total: {total_distance_km:.2f} km"
            )
            
            return OptimizationResult(
                ordered_indices=ordered_indices,
                total_distance_km=total_distance_km,
                total_duration_minutes=total_duration_minutes
            )
            
        except Exception as e:
            logger.error(f"Error resolviendo TSP con OR-Tools: {str(e)}")
            raise Exception(f"Error al resolver TSP: {str(e)}")
    
    def solve_tsp_with_duration(
        self,
        distance_matrix: List[List[float]],
        duration_matrix: List[List[float]],
        start_index: int = 0,
        optimize_by: str = "distance"
    ) -> OptimizationResult:
        """
        Resuelve el TSP considerando tanto distancia como duración.
        
        Args:
            distance_matrix: Matriz NxN de distancias en km
            duration_matrix: Matriz NxN de duraciones en minutos
            start_index: Índice del punto de inicio
            optimize_by: Criterio de optimización: "distance", "duration" o "balanced"
            
        Returns:
            OptimizationResult con el orden óptimo según el criterio elegido
            
        Raises:
            ValueError: Si las matrices no tienen las mismas dimensiones
            Exception: Si OR-Tools no está disponible o falla la optimización
        """
        if not self.is_available():
            raise Exception("OR-Tools no está disponible. Instale con: pip install ortools")
        
        if not distance_matrix or not duration_matrix:
            raise ValueError("Las matrices de distancia y duración no pueden estar vacías")
        
        n_dist = len(distance_matrix)
        n_dur = len(duration_matrix)
        
        if n_dist != n_dur:
            raise ValueError(
                f"Las matrices deben tener las mismas dimensiones. "
                f"Distancia: {n_dist}x{n_dist}, Duración: {n_dur}x{n_dur}"
            )
        
        try:
            # Seleccionar matriz según criterio de optimización
            if optimize_by == "distance":
                cost_matrix = distance_matrix
            elif optimize_by == "duration":
                cost_matrix = duration_matrix
            elif optimize_by == "balanced":
                # Promedio ponderado: 60% distancia, 40% duración normalizada
                # Normalizar duración a escala de distancia (asumiendo 50 km/h)
                cost_matrix = [
                    [
                        0.6 * distance_matrix[i][j] + 0.4 * (duration_matrix[i][j] / 60.0 * 50.0)
                        for j in range(len(distance_matrix[i]))
                    ]
                    for i in range(len(distance_matrix))
                ]
            else:
                raise ValueError(
                    f"Criterio de optimización inválido: {optimize_by}. "
                    "Use 'distance', 'duration' o 'balanced'."
                )
            
            # Resolver TSP con la matriz de costo elegida
            result = self.solve_tsp(cost_matrix, start_index)
            
            # Recalcular las métricas reales usando ambas matrices
            total_distance = 0.0
            total_duration = 0.0
            
            for i in range(len(result.ordered_indices) - 1):
                from_idx = result.ordered_indices[i]
                to_idx = result.ordered_indices[i + 1]
                total_distance += distance_matrix[from_idx][to_idx]
                total_duration += duration_matrix[from_idx][to_idx]
            
            # Retornar al punto de inicio (cerrar el ciclo)
            if result.ordered_indices:
                last_idx = result.ordered_indices[-1]
                first_idx = result.ordered_indices[0]
                total_distance += distance_matrix[last_idx][first_idx]
                total_duration += duration_matrix[last_idx][first_idx]
            
            logger.info(
                f"TSP resuelto (criterio: {optimize_by}): "
                f"{len(result.ordered_indices)} puntos, "
                f"distancia: {total_distance:.2f} km, "
                f"duración: {total_duration:.2f} min"
            )
            
            return OptimizationResult(
                ordered_indices=result.ordered_indices,
                total_distance_km=total_distance,
                total_duration_minutes=total_duration
            )
            
        except Exception as e:
            logger.error(f"Error resolviendo TSP con duración: {str(e)}")
            raise Exception(f"Error al resolver TSP: {str(e)}")


class NearestNeighborTSPSolver(RouteOptimizationSolverPort):
    """
    Implementación simple del algoritmo Nearest Neighbor para TSP.
    
    Este es un fallback cuando OR-Tools no está disponible.
    No es óptimo pero proporciona una solución razonable rápidamente.
    
    Algoritmo:
    1. Comenzar en el punto de inicio
    2. Visitar el vecino más cercano no visitado
    3. Repetir hasta visitar todos los puntos
    4. Regresar al inicio
    """
    
    def __init__(self) -> None:
        """Inicializa el solucionador simple."""
        logger.info("Nearest Neighbor TSP Solver inicializado (fallback)")
    
    def is_available(self) -> bool:
        """Este solver siempre está disponible (no requiere dependencias)."""
        return True
    
    def solve_tsp(
        self,
        distance_matrix: List[List[float]],
        start_index: int = 0
    ) -> OptimizationResult:
        """
        Resuelve TSP usando el algoritmo Nearest Neighbor (vecino más cercano).
        
        Args:
            distance_matrix: Matriz NxN de distancias
            start_index: Índice del punto de inicio
            
        Returns:
            OptimizationResult con una solución subóptima pero rápida
        """
        if not distance_matrix:
            raise ValueError("La matriz de distancias no puede estar vacía")
        
        n = len(distance_matrix)
        visited = [False] * n
        ordered_indices = [start_index]
        visited[start_index] = True
        
        current = start_index
        total_distance = 0.0
        
        # Visitar todos los puntos
        for _ in range(n - 1):
            nearest_distance = float('inf')
            nearest_index = -1
            
            # Encontrar el vecino más cercano no visitado
            for j in range(n):
                if not visited[j] and distance_matrix[current][j] < nearest_distance:
                    nearest_distance = distance_matrix[current][j]
                    nearest_index = j
            
            if nearest_index == -1:
                break
            
            ordered_indices.append(nearest_index)
            visited[nearest_index] = True
            total_distance += nearest_distance
            current = nearest_index
        
        # Regresar al inicio
        total_distance += distance_matrix[current][start_index]
        
        # Estimar duración
        total_duration_minutes = (total_distance / 50.0) * 60.0
        
        logger.info(
            f"TSP resuelto con Nearest Neighbor: {n} puntos, "
            f"distancia: {total_distance:.2f} km (solución subóptima)"
        )
        
        return OptimizationResult(
            ordered_indices=ordered_indices,
            total_distance_km=total_distance,
            total_duration_minutes=total_duration_minutes
        )
    
    def solve_tsp_with_duration(
        self,
        distance_matrix: List[List[float]],
        duration_matrix: List[List[float]],
        start_index: int = 0,
        optimize_by: str = "distance"
    ) -> OptimizationResult:
        """Resuelve TSP usando Nearest Neighbor con criterio de optimización."""
        # Seleccionar matriz según criterio
        if optimize_by == "duration":
            cost_matrix = duration_matrix
        else:
            cost_matrix = distance_matrix
        
        # Resolver
        result = self.solve_tsp(cost_matrix, start_index)
        
        # Recalcular métricas reales
        total_distance = 0.0
        total_duration = 0.0
        
        for i in range(len(result.ordered_indices) - 1):
            from_idx = result.ordered_indices[i]
            to_idx = result.ordered_indices[i + 1]
            total_distance += distance_matrix[from_idx][to_idx]
            total_duration += duration_matrix[from_idx][to_idx]
        
        # Cerrar ciclo
        if result.ordered_indices:
            last_idx = result.ordered_indices[-1]
            first_idx = result.ordered_indices[0]
            total_distance += distance_matrix[last_idx][first_idx]
            total_duration += duration_matrix[last_idx][first_idx]
        
        return OptimizationResult(
            ordered_indices=result.ordered_indices,
            total_distance_km=total_distance,
            total_duration_minutes=total_duration
        )
