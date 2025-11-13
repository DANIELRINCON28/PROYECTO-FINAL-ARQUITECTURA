/**
 * Yedistribuciones - Main JavaScript
 * Funcionalidades comunes y utilidades
 */

// ============================================================================
// CONFIGURACIÓN GLOBAL
// ============================================================================

const CONFIG = {
    API_BASE_URL: '/api',
    TOAST_DURATION: 3000
};

// ============================================================================
// FUNCIONES DE UTILIDAD
// ============================================================================

/**
 * Muestra un mensaje toast (notificación)
 */
function showToast(message, type = 'info') {
    const colors = {
        success: '#27AE60',
        error: '#E74C3C',
        warning: '#F39C12',
        info: '#3498DB'
    };

    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, CONFIG.TOAST_DURATION);
}

/**
 * Realiza una petición fetch con manejo de errores
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error en la petición');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Muestra un spinner de carga
 */
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="spinner-container">
                <div class="spinner-border spinner-border-lg text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
            </div>
        `;
    }
}

/**
 * Confirma una acción con el usuario
 */
function confirmAction(message, onConfirm) {
    if (confirm(message)) {
        onConfirm();
    }
}

// ============================================================================
// FUNCIONES DE API - RUTAS
// ============================================================================

/**
 * Obtiene todas las rutas
 */
async function getAllRoutes() {
    try {
        const data = await apiRequest(`${CONFIG.API_BASE_URL}/routes`);
        return data.data;
    } catch (error) {
        showToast('Error al obtener rutas: ' + error.message, 'error');
        return [];
    }
}

/**
 * Obtiene una ruta por ID
 */
async function getRouteById(routeId) {
    try {
        const data = await apiRequest(`${CONFIG.API_BASE_URL}/routes/${routeId}`);
        return data.data;
    } catch (error) {
        showToast('Error al obtener ruta: ' + error.message, 'error');
        return null;
    }
}

/**
 * Añade un cliente a una ruta
 */
async function addClientToRoute(routeId, clientId) {
    try {
        const data = await apiRequest(`${CONFIG.API_BASE_URL}/routes/${routeId}/clients`, {
            method: 'POST',
            body: JSON.stringify({ client_id: clientId })
        });
        showToast('Cliente añadido exitosamente', 'success');
        return data.data;
    } catch (error) {
        showToast('Error al añadir cliente: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Elimina un cliente de una ruta
 */
async function removeClientFromRoute(routeId, clientId) {
    try {
        const data = await apiRequest(
            `${CONFIG.API_BASE_URL}/routes/${routeId}/clients/${clientId}`,
            { method: 'DELETE' }
        );
        showToast('Cliente eliminado exitosamente', 'success');
        return data.data;
    } catch (error) {
        showToast('Error al eliminar cliente: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Reordena los clientes en una ruta
 */
async function reorderClients(routeId, clientIds) {
    try {
        const data = await apiRequest(`${CONFIG.API_BASE_URL}/routes/${routeId}/reorder`, {
            method: 'POST',
            body: JSON.stringify({ client_ids: clientIds })
        });
        showToast('Clientes reordenados exitosamente', 'success');
        return data.data;
    } catch (error) {
        showToast('Error al reordenar clientes: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Divide una ruta en dos
 */
async function divideRoute(routeId, splitPoint, nameA, nameB) {
    try {
        const data = await apiRequest(`${CONFIG.API_BASE_URL}/routes/divide`, {
            method: 'POST',
            body: JSON.stringify({
                route_id: routeId,
                split_point: splitPoint,
                name_a: nameA,
                name_b: nameB
            })
        });
        showToast('Ruta dividida exitosamente', 'success');
        return data.data;
    } catch (error) {
        showToast('Error al dividir ruta: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Fusiona dos rutas
 */
async function mergeRoutes(routeAId, routeBId, newName) {
    try {
        const data = await apiRequest(`${CONFIG.API_BASE_URL}/routes/merge`, {
            method: 'POST',
            body: JSON.stringify({
                route_a_id: routeAId,
                route_b_id: routeBId,
                new_name: newName
            })
        });
        showToast('Rutas fusionadas exitosamente', 'success');
        return data.data;
    } catch (error) {
        showToast('Error al fusionar rutas: ' + error.message, 'error');
        throw error;
    }
}

// ============================================================================
// FUNCIONES DE API - CLIENTES
// ============================================================================

/**
 * Obtiene todos los clientes
 */
async function getAllClients() {
    try {
        const data = await apiRequest(`${CONFIG.API_BASE_URL}/clients`);
        return data.data;
    } catch (error) {
        showToast('Error al obtener clientes: ' + error.message, 'error');
        return [];
    }
}

// ============================================================================
// VALIDACIÓN DE FORMULARIOS
// ============================================================================

/**
 * Valida un formulario
 */
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return false;
    }

    return true;
}

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers de Bootstrap
    var popoverTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="popover"]')
    );
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-ocultar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-permanent')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });

    console.log('✅ Yedistribuciones - Sistema inicializado');
});

// ============================================================================
// EXPORTAR FUNCIONES GLOBALES
// ============================================================================

window.YediAPI = {
    getAllRoutes,
    getRouteById,
    addClientToRoute,
    removeClientFromRoute,
    reorderClients,
    divideRoute,
    mergeRoutes,
    getAllClients,
    showToast,
    confirmAction,
    validateForm
};
