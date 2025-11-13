"""
Flask Application - UI Adapter (Driving Adapter)
Aplicación web profesional para Yedistribuciones usando Flask.
Mantiene la arquitectura hexagonal - capa de infraestructura.

RNF-RUT-01: Interface de usuario simple, intuitiva y profesional.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from typing import Optional, Dict
import json
from functools import wraps

from src.application.services.route_service import RouteService
from src.application.services.route_optimization_service import RouteOptimizationService
from src.application.dtos import CreateRouteDTO
from src.domain.ports.route_optimization_port import ClientLocation


# ========================================================================
# UTILIDADES Y HELPERS
# ========================================================================

def get_cedis_display_name(cedis_id: str) -> str:
    """
    Convierte el ID del CEDIS en un nombre amigable para mostrar.
    Intenta obtener el nombre real de la BD, si no está disponible usa fallbacks.
    
    Args:
        cedis_id: ID del CEDIS (puede ser string de ID numérico o identificador)
    
    Returns:
        Nombre amigable del CEDIS
    """
    try:
        # Intentar obtener el nombre real de la BD
        import psycopg2
        from config import Config
        
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=int(Config.DB_PORT),
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Intentar búsqueda por ID numérico
        try:
            cedis_id_int = int(cedis_id)
            cursor.execute("SELECT nombre FROM cedis WHERE id = %s", (cedis_id_int,))
        except (ValueError, TypeError):
            # Si no es numérico, búsqueda por nombre/identificador
            cursor.execute("SELECT nombre FROM cedis WHERE nombre LIKE %s OR id::text = %s", 
                         (f"%{cedis_id}%", cedis_id))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return row[0]
        
    except Exception as e:
        # Si hay error de conexión, usar fallback
        print(f"⚠️ Warning: No se pudo obtener nombre de CEDIS {cedis_id} desde BD: {e}")
        pass
    
    # Fallback: mapeo hardcodeado para compatibilidad
    cedis_names = {
        'CEDIS_BOGOTA': 'CEDIS Bogotá',
        'CEDIS_MEDELLIN': 'CEDIS Medellín',
        'CEDIS_CALI': 'CEDIS Cali',
        'CEDIS_BARRANQUILLA': 'CEDIS Barranquilla',
        'CEDIS_CARTAGENA': 'CEDIS Cartagena',
        '13': 'CEDIS Bogotá (13)',
        '14': 'CEDIS Medellín (14)',
        '15': 'CEDIS Cali (15)',
        '16': 'CEDIS Barranquilla (16)',
        '17': 'CEDIS Cartagena (17)',
    }
    return cedis_names.get(str(cedis_id), f'CEDIS {cedis_id}')


def create_flask_app(
    route_service: RouteService,
    optimization_service: Optional[RouteOptimizationService] = None
) -> Flask:
    """
    Factory function para crear y configurar la aplicación Flask.
    
    Args:
        route_service: Servicio de aplicación de rutas (inyectado)
        optimization_service: Servicio de optimización (opcional)
        
    Returns:
        Instancia configurada de Flask
    """
    app = Flask(__name__)
    app.secret_key = 'yedistribuciones-secret-key-change-in-production'
    
    # Inyectar servicios en el contexto de la app
    app.config['ROUTE_SERVICE'] = route_service
    app.config['OPTIMIZATION_SERVICE'] = optimization_service
    
    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================
    
    def get_route_service() -> RouteService:
        """Obtener el servicio de rutas del contexto."""
        return app.config['ROUTE_SERVICE']
    
    def get_optimization_service() -> Optional[RouteOptimizationService]:
        """Obtener el servicio de optimización del contexto."""
        return app.config['OPTIMIZATION_SERVICE']
    
    def handle_service_error(func):
        """Decorador para manejar errores de servicios."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                print(f"❌ ValueError en {func.__name__}: {str(e)}")
                return jsonify({'success': False, 'error': str(e)}), 400
            except Exception as e:
                import traceback
                print(f"❌ Error en {func.__name__}: {str(e)}")
                print(traceback.format_exc())
                return jsonify({'success': False, 'error': f'Error interno: {str(e)}'}), 500
        return wrapper
    
    # ========================================================================
    # ROUTES - PÁGINAS WEB
    # ========================================================================
    
    @app.route('/')
    def index():
        """Dashboard principal."""
        service = get_route_service()
        opt_service = get_optimization_service()
        
        try:
            all_routes = service.get_all_routes(include_inactive=False)
            total_clients = sum(r.client_count for r in all_routes) if all_routes else 0
            total_routes = len(all_routes) if all_routes else 0
            avg_clients = round(total_clients / total_routes) if total_routes > 0 else 0
            
            # Distribución por CEDIS con nombres amigables
            cedis_distribution = {}
            cedis_distribution_display = {}
            for route in all_routes:
                cedis = route.cedis_id
                if cedis not in cedis_distribution:
                    cedis_distribution[cedis] = 0
                cedis_distribution[cedis] += 1
            
            # Convertir a nombres amigables para el gráfico
            for cedis_id, count in cedis_distribution.items():
                display_name = get_cedis_display_name(cedis_id)
                cedis_distribution_display[display_name] = count
            
            return render_template(
                'dashboard.html',
                total_routes=total_routes,
                total_clients=total_clients,
                avg_clients=avg_clients,
                cedis_distribution=cedis_distribution_display,
                recent_routes=all_routes[:5] if all_routes else [],
                optimization_enabled=opt_service is not None,
                get_cedis_name=get_cedis_display_name
            )
        except Exception as e:
            flash(f'Error al cargar dashboard: {str(e)}', 'error')
            return render_template('dashboard.html', error=str(e))
    
    @app.route('/routes')
    def routes_list():
        """Vista de todas las rutas."""
        service = get_route_service()
        
        try:
            # Filtros
            cedis_filter = request.args.get('cedis', None)
            day_filter = request.args.get('day', None)
            
            all_routes = service.get_all_routes(include_inactive=False)
            
            # Aplicar filtros
            if cedis_filter:
                all_routes = [r for r in all_routes if r.cedis_id == cedis_filter]
            if day_filter:
                all_routes = [r for r in all_routes if r.day_of_week == day_filter]
            
            # Obtener lista de CEDIS directamente de la BD con nombres reales
            cedis_list = []
            try:
                import psycopg2
                from config import Config
                
                conn = psycopg2.connect(
                    host=Config.DB_HOST,
                    port=int(Config.DB_PORT),
                    database=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD
                )
                
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM cedis ORDER BY nombre")
                cedis_list = [(str(row[0]), row[1]) for row in cursor.fetchall()]
                cursor.close()
                conn.close()
                
            except Exception as e:
                print(f"⚠️ Warning: No se pudo cargar lista de CEDIS: {e}")
                # Fallback: obtener de las rutas existentes
                cedis_list_ids = sorted(set(r.cedis_id for r in service.get_all_routes(include_inactive=False)))
                cedis_list = [(cedis_id, get_cedis_display_name(cedis_id)) for cedis_id in cedis_list_ids]
            
            days_list = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
            
            return render_template(
                'routes_list.html',
                routes=all_routes,
                cedis_list=cedis_list,
                days_list=days_list,
                selected_cedis=cedis_filter,
                selected_day=day_filter,
                get_cedis_name=get_cedis_display_name
            )
        except Exception as e:
            flash(f'Error al cargar rutas: {str(e)}', 'error')
            return render_template('routes_list.html', routes=[])
    
    @app.route('/routes/create', methods=['GET', 'POST'])
    def create_route():
        """Crear nueva ruta."""
        if request.method == 'POST':
            service = get_route_service()
            
            try:
                name = request.form.get('name', '').strip()
                cedis_id = request.form.get('cedis_id', '').strip()
                day_of_week = request.form.get('day_of_week', '').strip()
                
                if not name or not cedis_id or not day_of_week:
                    flash('Todos los campos son obligatorios', 'error')
                    return redirect(url_for('create_route'))
                
                dto = CreateRouteDTO(
                    name=name,
                    cedis_id=cedis_id,
                    day_of_week=day_of_week.upper()
                )
                
                route = service.create_route(dto)
                flash(f'Ruta "{route.name}" creada exitosamente', 'success')
                return redirect(url_for('route_detail', route_id=route.id))
                
            except Exception as e:
                flash(f'Error al crear ruta: {str(e)}', 'error')
                return redirect(url_for('create_route'))
        
        # GET request
        cedis_list_ids = ['CEDIS_BOGOTA', 'CEDIS_MEDELLIN', 'CEDIS_CALI', 'CEDIS_BARRANQUILLA']
        cedis_list = [(cedis_id, get_cedis_display_name(cedis_id)) for cedis_id in cedis_list_ids]
        days_list = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
        
        return render_template(
            'create_route.html',
            cedis_list=cedis_list,
            days_list=days_list
        )
    
    @app.route('/routes/<route_id>')
    def route_detail(route_id: str):
        """Detalle de una ruta específica."""
        service = get_route_service()
        opt_service = get_optimization_service()
        
        try:
            route = service.get_route_by_id(route_id)
            if not route:
                flash('Ruta no encontrada', 'error')
                return redirect(url_for('routes_list'))
            
            return render_template(
                'route_detail.html', 
                route=route,
                get_cedis_name=get_cedis_display_name,
                optimization_enabled=opt_service is not None
            )
        except Exception as e:
            flash(f'Error al cargar ruta: {str(e)}', 'error')
            return redirect(url_for('routes_list'))
    
    @app.route('/routes/<route_id>/clients')
    def manage_clients(route_id: str):
        """Gestión de clientes de una ruta."""
        service = get_route_service()
        
        try:
            route = service.get_route_by_id(route_id)
            if not route:
                flash('Ruta no encontrada', 'error')
                return redirect(url_for('routes_list'))
            
            # Obtener todos los clientes disponibles
            all_clients = service.get_available_clients()
            print(f"📊 DEBUG: Total clientes disponibles cargados: {len(all_clients)}")
            
            # Obtener información detallada de los clientes en la ruta
            route_clients_info = []
            for client_id in route.client_ids:
                client_info = service.get_client_info(client_id)
                route_clients_info.append(client_info)
            
            print(f"📊 DEBUG: Clientes en ruta: {len(route_clients_info)}")
            print(f"📊 DEBUG: IDs en ruta: {route.client_ids}")
            
            return render_template(
                'manage_clients.html',
                route=route,
                available_clients=all_clients,
                route_clients_info=route_clients_info,
                get_cedis_name=get_cedis_display_name
            )
        except Exception as e:
            flash(f'Error al cargar clientes: {str(e)}', 'error')
            return redirect(url_for('route_detail', route_id=route_id))
    
    @app.route('/routes/divide')
    def divide_route_page():
        """Página para dividir rutas."""
        service = get_route_service()
        
        try:
            all_routes = service.get_all_routes(include_inactive=False)
            return render_template('divide_route.html', routes=all_routes)
        except Exception as e:
            flash(f'Error al cargar rutas: {str(e)}', 'error')
            return render_template('divide_route.html', routes=[])
    
    @app.route('/routes/merge')
    def merge_routes_page():
        """Página para fusionar rutas."""
        service = get_route_service()
        
        try:
            all_routes = service.get_all_routes(include_inactive=False)
            return render_template('merge_routes.html', routes=all_routes)
        except Exception as e:
            flash(f'Error al cargar rutas: {str(e)}', 'error')
            return render_template('merge_routes.html', routes=[])
    
    @app.route('/routes/<route_id>/optimize')
    def optimize_route_page(route_id: str):
        """Página de optimización de ruta."""
        service = get_route_service()
        opt_service = get_optimization_service()
        
        if not opt_service:
            flash('Servicio de optimización no disponible', 'warning')
            return redirect(url_for('route_detail', route_id=route_id))
        
        try:
            route = service.get_route_by_id(route_id)
            if not route:
                flash('Ruta no encontrada', 'error')
                return redirect(url_for('routes_list'))
            
            return render_template('optimize_route.html', route=route)
        except Exception as e:
            flash(f'Error al cargar ruta: {str(e)}', 'error')
            return redirect(url_for('routes_list'))
    
    # ========================================================================
    # API REST - ENDPOINTS JSON
    # ========================================================================
    
    @app.route('/api/routes', methods=['GET'])
    @handle_service_error
    def api_get_routes():
        """API: Obtener todas las rutas."""
        service = get_route_service()
        routes = service.get_all_routes(include_inactive=False)
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': r.id,
                    'name': r.name,
                    'cedis_id': r.cedis_id,
                    'day_of_week': r.day_of_week,
                    'client_count': r.client_count,
                    'is_active': r.is_active
                }
                for r in routes
            ]
        })
    
    @app.route('/api/routes/<route_id>', methods=['GET'])
    @handle_service_error
    def api_get_route(route_id: str):
        """API: Obtener una ruta específica."""
        service = get_route_service()
        route = service.get_route_by_id(route_id)
        
        if not route:
            return jsonify({'success': False, 'error': 'Ruta no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': route.id,
                'name': route.name,
                'cedis_id': route.cedis_id,
                'day_of_week': route.day_of_week,
                'client_ids': route.client_ids,
                'client_count': route.client_count,
                'is_active': route.is_active
            }
        })
    
    @app.route('/api/routes/<route_id>/clients', methods=['POST'])
    @handle_service_error
    def api_add_client(route_id: str):
        """API: Añadir cliente a una ruta."""
        service = get_route_service()
        data = request.get_json()
        
        client_id = data.get('client_id')
        if not client_id:
            return jsonify({'success': False, 'error': 'client_id requerido'}), 400
        
        route = service.assign_client_to_route(route_id, client_id)
        
        return jsonify({
            'success': True,
            'message': f'Cliente {client_id} añadido a la ruta',
            'data': {
                'id': route.id,
                'name': route.name,
                'client_count': route.client_count
            }
        })
    
    @app.route('/api/routes/<route_id>/clients/<client_id>', methods=['DELETE'])
    @handle_service_error
    def api_remove_client(route_id: str, client_id: str):
        """API: Eliminar cliente de una ruta."""
        service = get_route_service()
        route = service.remove_client_from_route(route_id, client_id)
        
        return jsonify({
            'success': True,
            'message': f'Cliente {client_id} eliminado de la ruta',
            'data': {
                'id': route.id,
                'name': route.name,
                'client_count': route.client_count
            }
        })
    
    @app.route('/api/routes/<route_id>/reorder', methods=['POST'])
    @handle_service_error
    def api_reorder_clients(route_id: str):
        """API: Reordenar clientes en una ruta."""
        service = get_route_service()
        data = request.get_json()
        
        ordered_client_ids = data.get('client_ids', [])
        if not ordered_client_ids:
            return jsonify({'success': False, 'error': 'client_ids requerido'}), 400
        
        route = service.reorder_clients_in_route(route_id, ordered_client_ids)
        
        return jsonify({
            'success': True,
            'message': 'Clientes reordenados exitosamente',
            'data': {
                'id': route.id,
                'name': route.name,
                'client_ids': route.client_ids
            }
        })
    
    @app.route('/api/routes/divide', methods=['POST'])
    @handle_service_error
    def api_divide_route():
        """API: Dividir una ruta en dos."""
        service = get_route_service()
        data = request.get_json()
        
        route_id = data.get('route_id')
        split_point = data.get('split_point')
        name_a = data.get('name_a')
        name_b = data.get('name_b')
        
        if not all([route_id, split_point is not None, name_a, name_b]):
            return jsonify({'success': False, 'error': 'Faltan parámetros requeridos'}), 400
        
        route_a, route_b = service.divide_route_use_case(
            route_id, split_point, name_a, name_b
        )
        
        return jsonify({
            'success': True,
            'message': 'Ruta dividida exitosamente',
            'data': {
                'route_a': {
                    'id': route_a.id,
                    'name': route_a.name,
                    'client_count': route_a.client_count
                },
                'route_b': {
                    'id': route_b.id,
                    'name': route_b.name,
                    'client_count': route_b.client_count
                }
            }
        })
    
    @app.route('/api/routes/merge', methods=['POST'])
    @handle_service_error
    def api_merge_routes():
        """API: Fusionar dos rutas."""
        service = get_route_service()
        data = request.get_json()
        
        route_a_id = data.get('route_a_id')
        route_b_id = data.get('route_b_id')
        new_name = data.get('new_name')
        
        if not all([route_a_id, route_b_id, new_name]):
            return jsonify({'success': False, 'error': 'Faltan parámetros requeridos'}), 400
        
        merged_route = service.merge_routes_use_case(route_a_id, route_b_id, new_name)
        
        return jsonify({
            'success': True,
            'message': 'Rutas fusionadas exitosamente',
            'data': {
                'id': merged_route.id,
                'name': merged_route.name,
                'client_count': merged_route.client_count
            }
        })
    
    @app.route('/api/routes/<route_id>/optimize', methods=['POST'])
    @handle_service_error
    def api_optimize_route(route_id: str):
        """API: Optimizar una ruta."""
        service = get_route_service()
        opt_service = get_optimization_service()
        
        if not opt_service:
            return jsonify({'success': False, 'error': 'Optimización no disponible'}), 503
        
        data = request.get_json()
        clients_data = data.get('clients', [])
        origin = data.get('origin')
        
        if not clients_data or not origin:
            return jsonify({'success': False, 'error': 'Faltan parámetros requeridos'}), 400
        
        # Convertir a ClientLocation
        client_locations = [
            ClientLocation(
                client_id=c['id'],
                address=c['address'],
                latitude=c.get('latitude'),
                longitude=c.get('longitude')
            )
            for c in clients_data
        ]
        
        result = opt_service.optimize_route(route_id, client_locations, origin)
        
        return jsonify({
            'success': True,
            'message': 'Ruta optimizada exitosamente',
            'data': {
                'original_distance_km': result.original_distance_km,
                'optimized_distance_km': result.optimized_distance_km,
                'distance_saved_km': result.distance_saved_km,
                'time_saved_minutes': result.time_saved_minutes,
                'optimized_order': result.optimized_order
            }
        })
    
    @app.route('/api/clients', methods=['GET'])
    @handle_service_error
    def api_get_clients():
        """API: Obtener todos los clientes disponibles."""
        service = get_route_service()
        clients = service.get_available_clients()
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': c.id,
                    'name': c.name,
                    'address': c.address,
                    'phone': c.phone
                }
                for c in clients
            ]
        })
    
    # ========================================================================
    # ERROR HANDLERS
    # ========================================================================
    
    @app.errorhandler(404)
    def not_found(e):
        """Página no encontrada."""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        """Error interno del servidor."""
        return render_template('500.html'), 500
    
    return app


def run_flask_app(
    route_service: RouteService,
    optimization_service: Optional[RouteOptimizationService] = None,
    debug: bool = True,
    port: int = 5000
) -> None:
    """
    Función para ejecutar la aplicación Flask.
    
    Args:
        route_service: Servicio de rutas
        optimization_service: Servicio de optimización (opcional)
        debug: Modo debug
        port: Puerto de la aplicación
    """
    app = create_flask_app(route_service, optimization_service)
    app.run(debug=debug, port=port, host='0.0.0.0')
