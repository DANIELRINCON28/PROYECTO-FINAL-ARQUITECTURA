"""
UI Components Library - Componentes Reutilizables
Módulo que proporciona componentes personalizados siguiendo el Design System.
"""
import streamlit as st
from typing import Callable, Optional, List, Dict, Any
from enum import Enum


class AlertType(Enum):
    """Tipos de alertas disponibles."""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


class ButtonStyle(Enum):
    """Estilos de botones disponibles."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    DANGER = "danger"


# ============================================================================
# PALETA DE COLORES
# ============================================================================

COLORS = {
    "primary": "#1F4788",           # Azul Corporativo
    "secondary": "#4A7BA7",         # Azul Claro
    "accent": "#2E8B57",            # Verde Éxito
    "success": "#27AE60",           # Verde (Estados positivos)
    "warning": "#F39C12",           # Naranja (Advertencias)
    "error": "#E74C3C",             # Rojo (Errores)
    "info": "#3498DB",              # Azul (Información)
    "dark": "#2C3E50",              # Gris Oscuro (Texto)
    "medium": "#7F8C8D",            # Gris Medio
    "light": "#F8F9FA",             # Gris Claro (Fondos)
    "border": "#E0E3E8",            # Gris Bordes
    "white": "#FFFFFF",             # Blanco
}


# ============================================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================================

def inject_custom_css() -> None:
    """
    Inyecta estilos CSS personalizados en la aplicación.
    Llamar una única vez al inicio de la app.
    """
    custom_css = f"""
    <style>
        /* Variables CSS */
        :root {{
            --primary: {COLORS['primary']};
            --secondary: {COLORS['secondary']};
            --success: {COLORS['success']};
            --warning: {COLORS['warning']};
            --error: {COLORS['error']};
            --info: {COLORS['info']};
            --dark: {COLORS['dark']};
            --medium: {COLORS['medium']};
            --light: {COLORS['light']};
            --border: {COLORS['border']};
            --radius: 6px;
            --radius-lg: 8px;
            --shadow: 0 2px 8px rgba(0,0,0,0.08);
            --shadow-lg: 0 10px 40px rgba(0,0,0,0.16);
        }}

        /* Estilos Generales */
        body {{
            font-family: "Segoe UI", Arial, sans-serif;
            background-color: {COLORS['light']};
            color: {COLORS['dark']};
        }}

        /* Headers */
        h1 {{
            color: {COLORS['dark']};
            font-weight: 700;
            font-size: 32px;
            margin-bottom: 8px;
        }}

        h2 {{
            color: {COLORS['dark']};
            font-weight: 600;
            font-size: 24px;
            margin-top: 24px;
            margin-bottom: 16px;
        }}

        h3 {{
            color: {COLORS['dark']};
            font-weight: 600;
            font-size: 18px;
            margin-top: 16px;
            margin-bottom: 12px;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {COLORS['light']};
            border-right: 1px solid {COLORS['border']};
        }}

        /* Main Content */
        .main {{
            background-color: {COLORS['light']};
        }}

        /* Dividers */
        hr {{
            border: none;
            border-top: 1px solid {COLORS['border']};
            margin: 24px 0;
        }}

        /* Links */
        a {{
            color: {COLORS['primary']};
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        /* Custom Classes */
        .container-card {{
            background: {COLORS['white']};
            border: 1px solid {COLORS['border']};
            border-radius: var(--radius-lg);
            padding: 20px;
            box-shadow: var(--shadow);
            margin: 16px 0;
        }}

        .text-muted {{
            color: {COLORS['medium']};
            font-size: 12px;
        }}

        .divider-light {{
            border-top: 1px solid {COLORS['border']};
            margin: 16px 0;
        }}

        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
        }}

        .status-active {{
            background: rgba(39, 174, 96, 0.15);
            color: {COLORS['success']};
        }}

        .status-inactive {{
            background: rgba(127, 140, 141, 0.15);
            color: {COLORS['medium']};
        }}

        /* Tablas */
        .dataframe {{
            border-collapse: collapse;
            width: 100%;
        }}

        .dataframe th {{
            background-color: {COLORS['primary']};
            color: {COLORS['white']};
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}

        .dataframe td {{
            padding: 12px;
            border-bottom: 1px solid {COLORS['border']};
        }}

        .dataframe tr:hover {{
            background-color: rgba(31, 71, 136, 0.05);
        }}

        /* Inputs */
        input, textarea, select {{
            border: 1px solid {COLORS['border']} !important;
            border-radius: var(--radius) !important;
            padding: 10px 12px !important;
            font-size: 14px !important;
            font-family: "Segoe UI", Arial, sans-serif !important;
        }}

        input:focus, textarea:focus, select:focus {{
            border-color: {COLORS['primary']} !important;
            box-shadow: 0 0 0 3px rgba(31, 71, 136, 0.1) !important;
        }}

        /* Labels */
        label {{
            color: {COLORS['dark']};
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 8px;
            display: block;
        }}

        /* Botones */
        button {{
            border-radius: var(--radius) !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: all var(--transition) !important;
            cursor: pointer !important;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


# ============================================================================
# COMPONENTES PRINCIPALES
# ============================================================================

def render_header(title: str, subtitle: Optional[str] = None, icon: str = "") -> None:
    """
    Renderiza un header corporativo profesional.
    
    Args:
        title: Título principal
        subtitle: Subtítulo opcional
        icon: Emoji o ícono (opcional)
    """
    if icon:
        st.markdown(f"# {icon} {title}")
    else:
        st.markdown(f"# {title}")
    
    if subtitle:
        st.markdown(f"*{subtitle}*")
    
    st.markdown('<div class="divider-light"></div>', unsafe_allow_html=True)


def render_section_header(title: str, icon: str = "") -> None:
    """
    Renderiza un encabezado de sección.
    
    Args:
        title: Título de la sección
        icon: Emoji o ícono (opcional)
    """
    if icon:
        st.markdown(f"## {icon} {title}")
    else:
        st.markdown(f"## {title}")


def render_subsection_header(title: str) -> None:
    """
    Renderiza un encabezado de subsección.
    
    Args:
        title: Título de la subsección
    """
    st.markdown(f"### {title}")


def alert(
    message: str,
    alert_type: AlertType = AlertType.INFO,
    dismissible: bool = False
) -> None:
    """
    Renderiza una alerta corporativa con estilos personalizados.
    
    Args:
        message: Mensaje de la alerta
        alert_type: Tipo de alerta (SUCCESS, WARNING, ERROR, INFO)
        dismissible: Si es despedible (nota: limitación en Streamlit)
    """
    colors = {
        AlertType.SUCCESS: COLORS['success'],
        AlertType.WARNING: COLORS['warning'],
        AlertType.ERROR: COLORS['error'],
        AlertType.INFO: COLORS['info'],
    }
    
    icons = {
        AlertType.SUCCESS: "✅",
        AlertType.WARNING: "⚠️",
        AlertType.ERROR: "❌",
        AlertType.INFO: "ℹ️",
    }
    
    color = colors[alert_type]
    icon = icons[alert_type]
    
    if alert_type == AlertType.SUCCESS:
        st.success(f"{icon} {message}")
    elif alert_type == AlertType.WARNING:
        st.warning(f"{icon} {message}")
    elif alert_type == AlertType.ERROR:
        st.error(f"{icon} {message}")
    else:
        st.info(f"{icon} {message}")


def card(
    title: str = "",
    content_func: Optional[Callable] = None,
    footer_func: Optional[Callable] = None
) -> None:
    """
    Renderiza una tarjeta (card) corporativa.
    
    Args:
        title: Título de la tarjeta (opcional)
        content_func: Función que renderiza el contenido
        footer_func: Función que renderiza el pie (opcional)
    """
    st.markdown('<div class="container-card">', unsafe_allow_html=True)
    
    if title:
        st.markdown(f"### {title}")
    
    if content_func:
        content_func()
    
    if footer_func:
        st.markdown('<div class="divider-light"></div>', unsafe_allow_html=True)
        footer_func()
    
    st.markdown('</div>', unsafe_allow_html=True)


def statistic_card(label: str, value: str, subtitle: str = "") -> None:
    """
    Renderiza una tarjeta de estadística.
    
    Args:
        label: Etiqueta de la estadística
        value: Valor a mostrar
        subtitle: Subtítulo adicional (opcional)
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="
            background: {COLORS['white']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        ">
            <p style="color: {COLORS['medium']}; font-size: 12px; margin: 0 0 8px 0; font-weight: 600;">
                {label}
            </p>
            <p style="color: {COLORS['primary']}; font-size: 28px; margin: 0; font-weight: 700;">
                {value}
            </p>
            {f'<p style="color: {COLORS["medium"]}; font-size: 12px; margin: 8px 0 0 0;">{subtitle}</p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)


def status_badge(text: str, is_active: bool = True) -> str:
    """
    Crea un badge de estado.
    
    Args:
        text: Texto del badge
        is_active: Si el estado es activo
    
    Returns:
        HTML del badge
    """
    status_class = "status-active" if is_active else "status-inactive"
    return f'<span class="status-badge {status_class}">{text}</span>'


def button_group(
    buttons: List[Dict[str, Any]],
    key_prefix: str = "btn"
) -> Optional[str]:
    """
    Renderiza un grupo de botones horizontales.
    
    Args:
        buttons: Lista de dict con 'label', 'callback' (opcional), 'style' (optional)
        key_prefix: Prefijo para las keys (para evitar conflictos)
    
    Returns:
        Label del botón presionado o None
    
    Ejemplo:
        buttons = [
            {"label": "Guardar", "callback": save_func, "style": ButtonStyle.PRIMARY},
            {"label": "Cancelar", "callback": cancel_func, "style": ButtonStyle.SECONDARY},
        ]
        clicked = button_group(buttons)
    """
    cols = st.columns(len(buttons))
    
    for idx, (col, btn) in enumerate(zip(cols, buttons)):
        with col:
            btn_label = btn.get("label", f"Botón {idx + 1}")
            btn_style = btn.get("style", ButtonStyle.PRIMARY)
            btn_callback = btn.get("callback")
            
            if st.button(
                btn_label,
                key=f"{key_prefix}_{idx}",
                use_container_width=True
            ):
                if btn_callback:
                    btn_callback()
                return btn_label
    
    return None


def form_group(label: str, required: bool = False) -> None:
    """
    Renderiza una etiqueta de formulario con indicador de requerido.
    
    Args:
        label: Etiqueta del campo
        required: Si el campo es requerido
    """
    required_mark = " *" if required else ""
    st.markdown(f"**{label}{required_mark}**")


def divider() -> None:
    """Renderiza un divisor corporativo."""
    st.markdown('<div class="divider-light"></div>', unsafe_allow_html=True)


def info_box(
    title: str,
    description: str,
    icon: str = "ℹ️"
) -> None:
    """
    Renderiza una caja de información destacada.
    
    Args:
        title: Título
        description: Descripción
        icon: Icono (emoji)
    """
    st.markdown(f"""
    <div style="
        background: rgba(52, 152, 219, 0.1);
        border-left: 4px solid {COLORS['info']};
        padding: 12px 16px;
        border-radius: 6px;
        margin: 12px 0;
    ">
        <p style="margin: 0 0 4px 0; font-weight: 600; color: {COLORS['dark']};">
            {icon} {title}
        </p>
        <p style="margin: 0; color: {COLORS['medium']}; font-size: 14px;">
            {description}
        </p>
    </div>
    """, unsafe_allow_html=True)


def success_box(
    title: str,
    description: str,
    icon: str = "✅"
) -> None:
    """Renderiza una caja de éxito."""
    st.markdown(f"""
    <div style="
        background: rgba(39, 174, 96, 0.1);
        border-left: 4px solid {COLORS['success']};
        padding: 12px 16px;
        border-radius: 6px;
        margin: 12px 0;
    ">
        <p style="margin: 0 0 4px 0; font-weight: 600; color: {COLORS['dark']};">
            {icon} {title}
        </p>
        <p style="margin: 0; color: {COLORS['medium']}; font-size: 14px;">
            {description}
        </p>
    </div>
    """, unsafe_allow_html=True)


def warning_box(
    title: str,
    description: str,
    icon: str = "⚠️"
) -> None:
    """Renderiza una caja de advertencia."""
    st.markdown(f"""
    <div style="
        background: rgba(243, 156, 18, 0.1);
        border-left: 4px solid {COLORS['warning']};
        padding: 12px 16px;
        border-radius: 6px;
        margin: 12px 0;
    ">
        <p style="margin: 0 0 4px 0; font-weight: 600; color: {COLORS['dark']};">
            {icon} {title}
        </p>
        <p style="margin: 0; color: {COLORS['medium']}; font-size: 14px;">
            {description}
        </p>
    </div>
    """, unsafe_allow_html=True)


def error_box(
    title: str,
    description: str,
    icon: str = "❌"
) -> None:
    """Renderiza una caja de error."""
    st.markdown(f"""
    <div style="
        background: rgba(231, 76, 60, 0.1);
        border-left: 4px solid {COLORS['error']};
        padding: 12px 16px;
        border-radius: 6px;
        margin: 12px 0;
    ">
        <p style="margin: 0 0 4px 0; font-weight: 600; color: {COLORS['dark']};">
            {icon} {title}
        </p>
        <p style="margin: 0; color: {COLORS['medium']}; font-size: 14px;">
            {description}
        </p>
    </div>
    """, unsafe_allow_html=True)


def metric_row(metrics: List[Dict[str, str]]) -> None:
    """
    Renderiza una fila de métricas.
    
    Args:
        metrics: Lista de dict con 'label' y 'value'
    
    Ejemplo:
        metric_row([
            {"label": "Total Rutas", "value": "12"},
            {"label": "Rutas Activas", "value": "10"},
            {"label": "Clientes", "value": "156"},
        ])
    """
    cols = st.columns(len(metrics))
    
    for col, metric in zip(cols, metrics):
        with col:
            st.metric(metric['label'], metric['value'])


def breadcrumb(items: List[str]) -> None:
    """
    Renderiza un breadcrumb de navegación.
    
    Args:
        items: Lista de items del breadcrumb
    
    Ejemplo:
        breadcrumb(["Inicio", "Rutas", "Crear Ruta"])
    """
    breadcrumb_html = " / ".join(items)
    st.markdown(f"""
    <p style="color: {COLORS['medium']}; font-size: 12px; margin: 0;">
        {breadcrumb_html}
    </p>
    """, unsafe_allow_html=True)


# ============================================================================
# UTILIDADES
# ============================================================================

def get_color(color_name: str) -> str:
    """
    Obtiene un color de la paleta.
    
    Args:
        color_name: Nombre del color
    
    Returns:
        Código HEX del color
    """
    return COLORS.get(color_name, COLORS['dark'])


def responsive_columns(count: int, mobile_count: int = 1) -> List:
    """
    Crea columnas responsivas (nota: Streamlit es mobile-first por default).
    
    Args:
        count: Número de columnas en desktop
        mobile_count: Número de columnas en mobile
    
    Returns:
        Lista de columnas
    """
    return st.columns(count)


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def init_ui() -> None:
    """
    Inicializa la interfaz de usuario con estilos personalizados.
    NOTA: st.set_page_config() debe llamarse ANTES en main.py
    
    Esta función solo inyecta CSS personalizado.
    Llamar al inicio de la aplicación (una sola vez).
    """
    # Inyectar CSS personalizado
    inject_custom_css()
