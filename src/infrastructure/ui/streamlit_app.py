"""
Streamlit Application - UI Adapter (Driving Adapter)
Interface web para administradores del sistema Yedistribuciones.
RNF-RUT-01: Interface de usuario simple e intuitiva.
"""
import streamlit as st
from typing import Optional
from src.application.services.route_service import RouteService
from src.application.dtos import CreateRouteDTO


def run_ui(route_service: RouteService) -> None:
    """
    Función principal de la aplicación Streamlit.
    
    Args:
        route_service: Servicio de aplicación de rutas (inyectado)
    """
    st.set_page_config(
        page_title="Yedistribuciones - Gestión de Rutas",
        page_icon="🚚",
        layout="wide"
    )
    
    st.title("🚚 Yedistribuciones - Sistema de Gestión de Rutas")
    st.markdown("---")
    
    # Menú lateral
    menu = st.sidebar.selectbox(
        "Menú Principal",
        [
            "📋 Ver Todas las Rutas",
            "➕ Crear Nueva Ruta",
            "✏️ Gestionar Clientes en Ruta",
            "✂️ Dividir Ruta",
            "🔗 Fusionar Rutas",
            "🔍 Buscar Ruta por CEDIS/Día"
        ]
    )
    
    # Enrutamiento de vistas
    if menu == "📋 Ver Todas las Rutas":
        view_all_routes(route_service)
    elif menu == "➕ Crear Nueva Ruta":
        create_route_view(route_service)
    elif menu == "✏️ Gestionar Clientes en Ruta":
        manage_clients_view(route_service)
    elif menu == "✂️ Dividir Ruta":
        divide_route_view(route_service)
    elif menu == "🔗 Fusionar Rutas":
        merge_routes_view(route_service)
    elif menu == "🔍 Buscar Ruta por CEDIS/Día":
        search_routes_view(route_service)


def view_all_routes(service: RouteService) -> None:
    """
    RF-RUT-04: Visualizar todas las rutas.
    """
    st.header("📋 Todas las Rutas")
    
    # Opción para incluir inactivas
    include_inactive = st.checkbox("Mostrar rutas inactivas", value=False)
    
    try:
        routes = service.get_all_routes(include_inactive=include_inactive)
        
        if not routes:
            st.info("No hay rutas registradas en el sistema.")
            return
        
        # Mostrar en tabla
        st.subheader(f"Total de rutas: {len(routes)}")
        
        # Preparar datos para la tabla
        data = []
        for route in routes:
            data.append({
                "ID": route.id[:8] + "...",  # Mostrar solo parte del ID
                "Nombre": route.name,
                "CEDIS": route.cedis_id,
                "Día": route.day_of_week,
                "Clientes": route.client_count,
                "Estado": "✅ Activa" if route.is_active else "❌ Inactiva"
            })
        
        st.dataframe(data, use_container_width=True)
        
        # Opciones de gestión
        st.markdown("---")
        st.subheader("Gestionar Ruta")
        
        route_ids = {f"{r.name} ({r.id[:8]}...)": r.id for r in routes}
        selected_route = st.selectbox("Seleccionar ruta:", list(route_ids.keys()))
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Activar/Desactivar"):
                route_id = route_ids[selected_route]
                route = service.get_route_by_id(route_id)
                if route:
                    if route.is_active:
                        service.deactivate_route(route_id)
                        st.success(f"Ruta '{route.name}' desactivada")
                    else:
                        service.activate_route(route_id)
                        st.success(f"Ruta '{route.name}' activada")
                    st.rerun()
        
        with col2:
            if st.button("🔍 Ver Detalles"):
                route_id = route_ids[selected_route]
                route = service.get_route_by_id(route_id)
                if route:
                    st.json({
                        "ID": route.id,
                        "Nombre": route.name,
                        "CEDIS": route.cedis_id,
                        "Día": route.day_of_week,
                        "Clientes": route.client_ids,
                        "Total Clientes": route.client_count,
                        "Activa": route.is_active
                    })
    
    except Exception as e:
        st.error(f"Error al cargar rutas: {str(e)}")


def create_route_view(service: RouteService) -> None:
    """
    RF-RUT-01: Crear una nueva ruta.
    """
    st.header("➕ Crear Nueva Ruta")
    
    with st.form("create_route_form"):
        st.subheader("Información de la Ruta")
        
        route_name = st.text_input("Nombre de la Ruta *", placeholder="Ej: Ruta Norte 1")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cedis = st.text_input("CEDIS *", placeholder="Ej: CEDIS_BOG_01")
        
        with col2:
            day = st.selectbox(
                "Día de la Semana *",
                ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
            )
        
        st.markdown("*Campos obligatorios*")
        
        submitted = st.form_submit_button("✅ Crear Ruta", use_container_width=True)
        
        if submitted:
            if not route_name or not cedis:
                st.error("Por favor complete todos los campos obligatorios")
            else:
                try:
                    dto = CreateRouteDTO(
                        name=route_name,
                        cedis_id=cedis,
                        day_of_week=day
                    )
                    
                    created_route = service.create_route(dto)
                    st.success(f"✅ Ruta '{created_route.name}' creada exitosamente!")
                    st.info(f"ID de la ruta: {created_route.id}")
                    
                except ValueError as e:
                    st.error(f"Error de validación: {str(e)}")
                except Exception as e:
                    st.error(f"Error al crear ruta: {str(e)}")


def manage_clients_view(service: RouteService) -> None:
    """
    RF-RUT-02: Asignar clientes a rutas.
    RF-RUT-03: Reordenar clientes en rutas.
    """
    st.header("✏️ Gestionar Clientes en Ruta")
    
    try:
        routes = service.get_all_routes(include_inactive=False)
        
        if not routes:
            st.warning("No hay rutas activas. Cree una ruta primero.")
            return
        
        route_options = {f"{r.name} - {r.day_of_week}": r.id for r in routes}
        selected_route_name = st.selectbox("Seleccionar Ruta:", list(route_options.keys()))
        
        if selected_route_name:
            route_id = route_options[selected_route_name]
            route = service.get_route_by_id(route_id)
            
            if route:
                st.subheader(f"Ruta: {route.name}")
                st.info(f"CEDIS: {route.cedis_id} | Día: {route.day_of_week}")
                
                # Mostrar clientes actuales
                st.markdown("### Clientes en la Ruta (en orden):")
                if route.client_ids:
                    for idx, client_id in enumerate(route.client_ids, 1):
                        st.write(f"{idx}. {client_id}")
                else:
                    st.write("*No hay clientes asignados*")
                
                st.markdown("---")
                
                # Agregar cliente
                with st.form("add_client_form"):
                    st.subheader("➕ Agregar Cliente")
                    new_client_id = st.text_input("ID del Cliente", placeholder="Ej: CLI_001")
                    add_submitted = st.form_submit_button("Agregar Cliente")
                    
                    if add_submitted and new_client_id:
                        try:
                            service.assign_client_to_route(route_id, new_client_id)
                            st.success(f"Cliente {new_client_id} agregado!")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                
                # Eliminar cliente
                if route.client_ids:
                    st.markdown("---")
                    with st.form("remove_client_form"):
                        st.subheader("➖ Eliminar Cliente")
                        client_to_remove = st.selectbox("Cliente a eliminar:", route.client_ids)
                        remove_submitted = st.form_submit_button("Eliminar Cliente")
                        
                        if remove_submitted:
                            try:
                                service.remove_client_from_route(route_id, client_to_remove)
                                st.success(f"Cliente {client_to_remove} eliminado!")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                
                # Reordenar clientes
                if len(route.client_ids) > 1:
                    st.markdown("---")
                    with st.form("reorder_clients_form"):
                        st.subheader("🔄 Reordenar Clientes")
                        st.info("Ingrese los IDs de clientes en el orden deseado, separados por comas")
                        
                        current_order = ", ".join(route.client_ids)
                        new_order_input = st.text_area(
                            "Nuevo Orden:",
                            value=current_order,
                            height=100
                        )
                        
                        reorder_submitted = st.form_submit_button("Aplicar Nuevo Orden")
                        
                        if reorder_submitted:
                            try:
                                new_order = [c.strip() for c in new_order_input.split(",")]
                                service.reorder_clients_in_route(route_id, new_order)
                                st.success("Orden de clientes actualizado!")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
    
    except Exception as e:
        st.error(f"Error: {str(e)}")


def divide_route_view(service: RouteService) -> None:
    """
    RF-RUT-06: Dividir una ruta en dos.
    """
    st.header("✂️ Dividir Ruta")
    
    try:
        routes = service.get_all_routes(include_inactive=False)
        
        if not routes:
            st.warning("No hay rutas activas para dividir.")
            return
        
        # Filtrar rutas con al menos 2 clientes
        dividable_routes = [r for r in routes if r.client_count >= 2]
        
        if not dividable_routes:
            st.warning("No hay rutas con suficientes clientes (mínimo 2) para dividir.")
            return
        
        with st.form("divide_route_form"):
            route_options = {f"{r.name} ({r.client_count} clientes)": r.id for r in dividable_routes}
            selected_route = st.selectbox("Seleccionar Ruta a Dividir:", list(route_options.keys()))
            
            if selected_route:
                route_id = route_options[selected_route]
                route = service.get_route_by_id(route_id)
                
                if route:
                    st.info(f"Clientes actuales: {', '.join(route.client_ids)}")
                    
                    split_point = st.slider(
                        "Punto de División (índice)",
                        min_value=1,
                        max_value=route.client_count - 1,
                        value=route.client_count // 2
                    )
                    
                    st.markdown(f"**Ruta A tendrá:** {split_point} clientes")
                    st.markdown(f"**Ruta B tendrá:** {route.client_count - split_point} clientes")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name_a = st.text_input("Nombre Ruta A *", value=f"{route.name}_A")
                    
                    with col2:
                        name_b = st.text_input("Nombre Ruta B *", value=f"{route.name}_B")
                    
                    submitted = st.form_submit_button("✂️ Dividir Ruta", use_container_width=True)
                    
                    if submitted:
                        try:
                            route_a, route_b = service.divide_route_use_case(
                                route_id_to_split=route_id,
                                split_point=split_point,
                                new_route_name_a=name_a,
                                new_route_name_b=name_b
                            )
                            
                            st.success("✅ Ruta dividida exitosamente!")
                            st.info(f"**Ruta A:** {route_a.name} con {route_a.client_count} clientes")
                            st.info(f"**Ruta B:** {route_b.name} con {route_b.client_count} clientes")
                            st.warning(f"La ruta original '{route.name}' ha sido desactivada")
                            
                        except ValueError as e:
                            st.error(f"Error: {str(e)}")
                        except Exception as e:
                            st.error(f"Error inesperado: {str(e)}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")


def merge_routes_view(service: RouteService) -> None:
    """
    RF-RUT-07: Fusionar dos rutas en una.
    """
    st.header("🔗 Fusionar Rutas")
    
    try:
        routes = service.get_all_routes(include_inactive=False)
        
        if len(routes) < 2:
            st.warning("Se necesitan al menos 2 rutas activas para fusionar.")
            return
        
        with st.form("merge_routes_form"):
            route_options = {f"{r.name} - {r.cedis_id} - {r.day_of_week}": r.id for r in routes}
            
            col1, col2 = st.columns(2)
            
            with col1:
                route_a_name = st.selectbox("Primera Ruta:", list(route_options.keys()), key="route_a")
            
            with col2:
                route_b_name = st.selectbox("Segunda Ruta:", list(route_options.keys()), key="route_b")
            
            merged_name = st.text_input("Nombre de la Ruta Fusionada *", placeholder="Ej: Ruta Fusionada Norte")
            
            if route_a_name and route_b_name:
                route_a_id = route_options[route_a_name]
                route_b_id = route_options[route_b_name]
                
                route_a = service.get_route_by_id(route_a_id)
                route_b = service.get_route_by_id(route_b_id)
                
                if route_a and route_b:
                    st.info(f"**Ruta A:** {route_a.client_count} clientes")
                    st.info(f"**Ruta B:** {route_b.client_count} clientes")
                    st.info(f"**Total estimado:** ~{route_a.client_count + route_b.client_count} clientes (sin duplicados)")
            
            submitted = st.form_submit_button("🔗 Fusionar Rutas", use_container_width=True)
            
            if submitted:
                if not merged_name:
                    st.error("Por favor ingrese un nombre para la ruta fusionada")
                elif route_a_name == route_b_name:
                    st.error("Debe seleccionar dos rutas diferentes")
                else:
                    try:
                        merged_route = service.merge_routes_use_case(
                            route_id_a=route_options[route_a_name],
                            route_id_b=route_options[route_b_name],
                            new_merged_route_name=merged_name
                        )
                        
                        st.success("✅ Rutas fusionadas exitosamente!")
                        st.info(f"**Nueva Ruta:** {merged_route.name}")
                        st.info(f"**Total de clientes:** {merged_route.client_count}")
                        st.warning("Las rutas originales han sido desactivadas")
                        
                    except ValueError as e:
                        st.error(f"Error de validación: {str(e)}")
                    except Exception as e:
                        st.error(f"Error inesperado: {str(e)}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")


def search_routes_view(service: RouteService) -> None:
    """
    Buscar rutas por CEDIS y día de la semana.
    """
    st.header("🔍 Buscar Rutas por CEDIS y Día")
    
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            cedis_search = st.text_input("CEDIS", placeholder="Ej: CEDIS_BOG_01")
        
        with col2:
            day_search = st.selectbox(
                "Día de la Semana",
                ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
            )
        
        submitted = st.form_submit_button("🔍 Buscar", use_container_width=True)
        
        if submitted:
            if not cedis_search:
                st.error("Por favor ingrese un CEDIS")
            else:
                try:
                    results = service.get_routes_by_cedis_and_day(cedis_search, day_search)
                    
                    if not results:
                        st.info(f"No se encontraron rutas para {cedis_search} en {day_search}")
                    else:
                        st.success(f"Se encontraron {len(results)} ruta(s)")
                        
                        data = []
                        for route in results:
                            data.append({
                                "Nombre": route.name,
                                "CEDIS": route.cedis_id,
                                "Día": route.day_of_week,
                                "Clientes": route.client_count,
                                "Estado": "✅ Activa" if route.is_active else "❌ Inactiva"
                            })
                        
                        st.dataframe(data, use_container_width=True)
                
                except Exception as e:
                    st.error(f"Error en la búsqueda: {str(e)}")
