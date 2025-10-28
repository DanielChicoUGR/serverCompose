"""
Nginx Config Builder - Herramienta CLI para generar configuraciones de Nginx.

Este paquete proporciona una interfaz de línea de comandos para crear
configuraciones de servicios HTTP/HTTPS, TCP/UDP (streams) y sitios estáticos para Nginx.
"""

__version__ = "0.1.0"
__author__ = "Daniel Chico"
__email__ = "dachival@correo.ugr"

from .cli import cli
from .http_service import create_http_service, save_http_config
from .stream_service import create_stream_service, save_stream_config
from .static_service import create_static_service, save_static_config

__all__ = [
    'cli',
    'create_http_service',
    'save_http_config',
    'create_stream_service',
    'save_stream_config',
    'create_static_service',
    'save_static_config',
]
