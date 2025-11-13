"""
Google Maps Distance Adapter (Infrastructure Layer)
Adaptador concreto que implementa GeoDistanceProviderPort usando Google Maps Distance Matrix API.
"""
from typing import List, Optional
import googlemaps
from src.domain.ports.geo_distance_provider_port import (
    GeoDistanceProviderPort,
    GeoCoordinate,
    DistanceResult
)
import logging

logger = logging.getLogger(__name__)


class GoogleMapsDistanceAdapter(GeoDistanceProviderPort):
    """
    Adaptador que usa Google Maps Distance Matrix API para calcular distancias.
    
    Patrón de Diseño: Adapter Pattern (Hexagonal Architecture)
    - Implementa el puerto GeoDistanceProviderPort
    - Encapsula la lógica específica de Google Maps
    - Permite cambiar a otro proveedor sin afectar el dominio
    
    Requiere:
    - API Key de Google Maps configurada
    - Biblioteca googlemaps instalada: pip install googlemaps
    """
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Inicializa el adaptador con la API key de Google Maps.
        
        Args:
            api_key: Clave de API de Google Maps. Si es None, el servicio no estará disponible.
        """
        self._api_key = api_key
        self._client: Optional[googlemaps.Client] = None
        
        if self._api_key:
            try:
                self._client = googlemaps.Client(key=self._api_key)
                logger.info("Google Maps Distance Adapter inicializado correctamente")
            except Exception as e:
                logger.error(f"Error inicializando cliente de Google Maps: {str(e)}")
                self._client = None
        else:
            logger.warning("Google Maps API Key no configurada. El servicio no estará disponible.")
    
    def is_available(self) -> bool:
        """
        Verifica si el servicio de Google Maps está disponible.
        
        Returns:
            True si hay un cliente configurado, False en caso contrario
        """
        return self._client is not None
    
    def calculate_distance(
        self, 
        origin: GeoCoordinate, 
        destination: GeoCoordinate
    ) -> DistanceResult:
        """
        Calcula la distancia y tiempo entre dos coordenadas usando Google Maps.
        
        Args:
            origin: Coordenada de origen
            destination: Coordenada de destino
            
        Returns:
            DistanceResult con distancia en km y duración en minutos
            
        Raises:
            Exception: Si el servicio no está disponible o falla la consulta
        """
        if not self.is_available():
            raise Exception("Google Maps Distance service no está disponible")
        
        try:
            # Formato esperado por Google Maps: "lat,lng"
            origin_str = f"{origin.latitude},{origin.longitude}"
            destination_str = f"{destination.latitude},{destination.longitude}"
            
            # Llamar a la API de Distance Matrix
            result = self._client.distance_matrix(
                origins=[origin_str],
                destinations=[destination_str],
                mode="driving",  # Modo de transporte
                units="metric"   # Sistema métrico
            )
            
            # Parsear respuesta
            if result['status'] == 'OK':
                element = result['rows'][0]['elements'][0]
                
                if element['status'] == 'OK':
                    distance_m = element['distance']['value']  # Metros
                    duration_s = element['duration']['value']  # Segundos
                    
                    return DistanceResult(
                        distance_km=distance_m / 1000.0,
                        duration_minutes=duration_s / 60.0
                    )
                else:
                    raise Exception(f"No se pudo calcular la ruta: {element['status']}")
            else:
                raise Exception(f"Error en Distance Matrix API: {result['status']}")
                
        except Exception as e:
            logger.error(f"Error calculando distancia: {str(e)}")
            raise Exception(f"Error al calcular distancia con Google Maps: {str(e)}")
    
    def calculate_distance_matrix(
        self, 
        origins: List[GeoCoordinate], 
        destinations: List[GeoCoordinate]
    ) -> List[List[DistanceResult]]:
        """
        Calcula una matriz de distancias entre múltiples orígenes y destinos.
        
        Args:
            origins: Lista de coordenadas de origen
            destinations: Lista de coordenadas de destino
            
        Returns:
            Matriz bidimensional donde [i][j] es la distancia del origen i al destino j
            
        Raises:
            Exception: Si el servicio no está disponible o falla la consulta
        """
        if not self.is_available():
            raise Exception("Google Maps Distance service no está disponible")
        
        if not origins or not destinations:
            raise ValueError("Las listas de orígenes y destinos no pueden estar vacías")
        
        try:
            # Convertir coordenadas a formato de Google Maps
            origins_str = [f"{coord.latitude},{coord.longitude}" for coord in origins]
            destinations_str = [f"{coord.latitude},{coord.longitude}" for coord in destinations]
            
            # Llamar a la API de Distance Matrix
            # Nota: Google Maps tiene límites de 25 orígenes x 25 destinos por request
            # Para matrices más grandes, se necesitaría dividir en múltiples requests
            result = self._client.distance_matrix(
                origins=origins_str,
                destinations=destinations_str,
                mode="driving",
                units="metric"
            )
            
            # Parsear respuesta en matriz
            if result['status'] != 'OK':
                raise Exception(f"Error en Distance Matrix API: {result['status']}")
            
            matrix = []
            for i, row in enumerate(result['rows']):
                matrix_row = []
                for j, element in enumerate(row['elements']):
                    if element['status'] == 'OK':
                        distance_m = element['distance']['value']
                        duration_s = element['duration']['value']
                        
                        matrix_row.append(
                            DistanceResult(
                                distance_km=distance_m / 1000.0,
                                duration_minutes=duration_s / 60.0
                            )
                        )
                    else:
                        # Si no hay ruta disponible, usar distancia euclidiana como fallback
                        logger.warning(
                            f"No hay ruta disponible entre origen {i} y destino {j}. "
                            f"Usando distancia euclidiana."
                        )
                        euclidean_distance = self._calculate_euclidean_distance(
                            origins[i], 
                            destinations[j]
                        )
                        matrix_row.append(
                            DistanceResult(
                                distance_km=euclidean_distance,
                                duration_minutes=euclidean_distance * 2  # Estimación: 30 km/h promedio
                            )
                        )
                
                matrix.append(matrix_row)
            
            return matrix
            
        except Exception as e:
            logger.error(f"Error calculando matriz de distancias: {str(e)}")
            raise Exception(f"Error al calcular matriz con Google Maps: {str(e)}")
    
    def _calculate_euclidean_distance(
        self, 
        coord1: GeoCoordinate, 
        coord2: GeoCoordinate
    ) -> float:
        """
        Calcula la distancia euclidiana aproximada entre dos coordenadas.
        
        Este es un fallback cuando Google Maps no puede calcular una ruta.
        Usa la fórmula de Haversine para distancia sobre la esfera terrestre.
        
        Args:
            coord1: Primera coordenada
            coord2: Segunda coordenada
            
        Returns:
            Distancia aproximada en kilómetros
        """
        import math
        
        # Radio de la Tierra en kilómetros
        R = 6371.0
        
        # Convertir grados a radianes
        lat1 = math.radians(coord1.latitude)
        lon1 = math.radians(coord1.longitude)
        lat2 = math.radians(coord2.latitude)
        lon2 = math.radians(coord2.longitude)
        
        # Diferencias
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        # Fórmula de Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
