"""
Route Optimization Solver Port (Domain Layer)
Puerto abstracto para resolver problemas de optimización de rutas (TSP - Traveling Salesman Problem).
NO depende de ninguna biblioteca específica (OR-Tools, algoritmos propios, etc.)
"""
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class OptimizationResult:
    """Value Object que representa el resultado de una optimización de ruta."""
    ordered_indices: List[int]  # Orden óptimo de los índices (basado en la matriz de entrada)
    total_distance_km: float    # Distancia total de la ruta optimizada
    total_duration_minutes: float  # Duración total de la ruta optimizada
    
    def __post_init__(self) -> None:
        """Validaciones del resultado."""
        if not self.ordered_indices:
            raise ValueError("La lista de índices ordenados no puede estar vacía")
        if self.total_distance_km < 0:
            raise ValueError("La distancia total no puede ser negativa")
        if self.total_duration_minutes < 0:
            raise ValueError("La duración total no puede ser negativa")


class RouteOptimizationSolverPort(ABC):
    """
    Puerto abstracto para solucionadores de optimización de rutas.
    
    Patrón de Diseño: Port (Hexagonal Architecture)
    - Permite múltiples implementaciones: OR-Tools, algoritmos propios, servicios externos, etc.
    - El dominio no conoce los detalles de implementación
    
    El problema TSP (Traveling Salesman Problem):
    - Dado un conjunto de puntos y las distancias entre ellos
    - Encontrar el orden de visita que minimice la distancia total
    - Debe partir desde un punto específico (CEDIS) y visitar todos los demás
    """
    
    @abstractmethod
    def solve_tsp(
        self,
        distance_matrix: List[List[float]],
        start_index: int = 0
    ) -> OptimizationResult:
        """
        Resuelve el problema del viajante (TSP) dado una matriz de distancias.
        
        Args:
            distance_matrix: Matriz NxN donde [i][j] es la distancia del punto i al punto j
            start_index: Índice del punto de inicio (por defecto 0 = CEDIS)
            
        Returns:
            OptimizationResult con el orden óptimo de visita
            
        Raises:
            ValueError: Si la matriz es inválida o vacía
            Exception: Si no se puede resolver el problema
            
        Example:
            >>> # Matriz 3x3: CEDIS (0), Cliente A (1), Cliente B (2)
            >>> matrix = [
            ...     [0, 10, 15],  # Distancias desde CEDIS
            ...     [10, 0, 5],   # Distancias desde Cliente A
            ...     [15, 5, 0]    # Distancias desde Cliente B
            ... ]
            >>> result = solver.solve_tsp(matrix, start_index=0)
            >>> # result.ordered_indices podría ser [0, 1, 2] o [0, 2, 1]
        """
        pass
    
    @abstractmethod
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
            Exception: Si no se puede resolver el problema
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica si el solucionador está disponible y funcional.
        
        Returns:
            True si el solucionador está listo para usar, False en caso contrario
        """
        pass
