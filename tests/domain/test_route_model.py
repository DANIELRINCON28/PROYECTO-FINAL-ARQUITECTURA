"""
Test básico para el modelo Route del dominio.
Pruebas unitarias de la lógica de negocio.
"""
import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest
from domain.models.route import Route


class TestRouteDomainModel:
    """Tests para el modelo Route."""
    
    def test_create_route_valid(self):
        """Test de creación de ruta válida."""
        route = Route(
            id="route-001",
            name="Ruta Norte 1",
            cedis_id="CEDIS_BOG_01",
            day_of_week="LUNES",
            client_ids=[]
        )
        
        assert route.id == "route-001"
        assert route.name == "Ruta Norte 1"
        assert route.cedis_id == "CEDIS_BOG_01"
        assert route.day_of_week == "LUNES"
        assert route.is_active == True
        assert len(route.client_ids) == 0
    
    def test_create_route_invalid_day(self):
        """Test de validación de día inválido."""
        with pytest.raises(ValueError, match="Día de la semana inválido"):
            Route(
                id="route-001",
                name="Ruta Norte 1",
                cedis_id="CEDIS_BOG_01",
                day_of_week="INVALID_DAY",
                client_ids=[]
            )
    
    def test_add_client_to_route(self):
        """Test de agregar cliente a ruta."""
        route = Route(
            id="route-001",
            name="Ruta Norte 1",
            cedis_id="CEDIS_BOG_01",
            day_of_week="LUNES",
            client_ids=[]
        )
        
        route.add_client("CLI_001")
        route.add_client("CLI_002")
        
        assert len(route.client_ids) == 2
        assert "CLI_001" in route.client_ids
        assert "CLI_002" in route.client_ids
    
    def test_add_duplicate_client_raises_error(self):
        """Test de error al agregar cliente duplicado."""
        route = Route(
            id="route-001",
            name="Ruta Norte 1",
            cedis_id="CEDIS_BOG_01",
            day_of_week="LUNES",
            client_ids=["CLI_001"]
        )
        
        with pytest.raises(ValueError, match="ya está en la ruta"):
            route.add_client("CLI_001")
    
    def test_divide_route(self):
        """Test de división de ruta."""
        route = Route(
            id="route-001",
            name="Ruta Norte",
            cedis_id="CEDIS_BOG_01",
            day_of_week="LUNES",
            client_ids=["CLI_001", "CLI_002", "CLI_003", "CLI_004"]
        )
        
        route_a, route_b = route.divide_route(split_index=2)
        
        # Verificar ruta A
        assert len(route_a.client_ids) == 2
        assert route_a.client_ids == ["CLI_001", "CLI_002"]
        assert route_a.cedis_id == "CEDIS_BOG_01"
        assert route_a.day_of_week == "LUNES"
        
        # Verificar ruta B
        assert len(route_b.client_ids) == 2
        assert route_b.client_ids == ["CLI_003", "CLI_004"]
        assert route_b.cedis_id == "CEDIS_BOG_01"
        assert route_b.day_of_week == "LUNES"
    
    def test_divide_route_invalid_index(self):
        """Test de error al dividir con índice inválido."""
        route = Route(
            id="route-001",
            name="Ruta Norte",
            cedis_id="CEDIS_BOG_01",
            day_of_week="LUNES",
            client_ids=["CLI_001", "CLI_002"]
        )
        
        with pytest.raises(ValueError, match="Índice de división inválido"):
            route.divide_route(split_index=0)
        
        with pytest.raises(ValueError, match="Índice de división inválido"):
            route.divide_route(split_index=2)
    
    def test_merge_routes(self):
        """Test de fusión de rutas."""
        route_a = Route(
            id="route-001",
            name="Ruta A",
            cedis_id="CEDIS_BOG_01",
            day_of_week="LUNES",
            client_ids=["CLI_001", "CLI_002"]
        )
        
        route_b = Route(
            id="route-002",
            name="Ruta B",
            cedis_id="CEDIS_BOG_01",
            day_of_week="LUNES",
            client_ids=["CLI_003", "CLI_004"]
        )
        
        merged = route_a.merge_routes(route_b)
        
        assert len(merged.client_ids) == 4
        assert "CLI_001" in merged.client_ids
        assert "CLI_002" in merged.client_ids
        assert "CLI_003" in merged.client_ids
        assert "CLI_004" in merged.client_ids
        assert merged.cedis_id == "CEDIS_BOG_01"
        assert merged.day_of_week == "LUNES"
    
    def test_merge_routes_different_cedis_fails(self):
        """Test de error al fusionar rutas de diferentes CEDIS."""
        route_a = Route(
            id="route-001",
            name="Ruta A",
            cedis_id="CEDIS_BOG_01",
            day_of_week="LUNES",
            client_ids=["CLI_001"]
        )
        
        route_b = Route(
            id="route-002",
            name="Ruta B",
            cedis_id="CEDIS_MED_01",  # Diferente CEDIS
            day_of_week="LUNES",
            client_ids=["CLI_002"]
        )
        
        with pytest.raises(ValueError, match="mismo CEDIS"):
            route_a.merge_routes(route_b)
    
    def test_merge_routes_different_day_fails(self):
        """Test de error al fusionar rutas de diferentes días."""
        route_a = Route(
            id="route-001",
            name="Ruta A",
            cedis_id="CEDIS_BOG_01",
            day_of_week="LUNES",
            client_ids=["CLI_001"]
        )
        
        route_b = Route(
            id="route-002",
            name="Ruta B",
            cedis_id="CEDIS_BOG_01",
            day_of_week="MARTES",  # Diferente día
            client_ids=["CLI_002"]
        )
        
        with pytest.raises(ValueError, match="mismo día"):
            route_a.merge_routes(route_b)
    
    def test_reorder_clients(self):
        """Test de reordenamiento de clientes."""
        route = Route(
            id="route-001",
            name="Ruta Norte",
            cedis_id="CEDIS_BOG_01",
            day_of_week="LUNES",
            client_ids=["CLI_001", "CLI_002", "CLI_003"]
        )
        
        new_order = ["CLI_003", "CLI_001", "CLI_002"]
        route.reorder_clients(new_order)
        
        assert route.client_ids == new_order
    
    def test_reorder_clients_invalid_list_fails(self):
        """Test de error al reordenar con lista inválida."""
        route = Route(
            id="route-001",
            name="Ruta Norte",
            cedis_id="CEDIS_BOG_01",
            day_of_week="LUNES",
            client_ids=["CLI_001", "CLI_002", "CLI_003"]
        )
        
        # Lista con cliente faltante
        with pytest.raises(ValueError, match="mismos clientes"):
            route.reorder_clients(["CLI_001", "CLI_002"])
        
        # Lista con cliente adicional
        with pytest.raises(ValueError, match="mismos clientes"):
            route.reorder_clients(["CLI_001", "CLI_002", "CLI_003", "CLI_004"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
