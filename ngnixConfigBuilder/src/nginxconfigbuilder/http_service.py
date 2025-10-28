"""
Módulo para crear configuraciones de servicios HTTP/HTTPS en Nginx.
"""

from pathlib import Path

# Importar la librería nginx del paquete
from .nginx import Conf, Upstream, Server, Location, Key, Comment


def create_http_service(domain: str, upstream_target: str, enable_websocket: bool = False) -> Conf:
    """
    Crea una configuración de servicio HTTP/HTTPS.
    
    Args:
        domain: Dominio del servicio (ej: app.hmbcentral.live)
        upstream_target: Target del upstream (ej: myapp:8080)
        enable_websocket: Habilitar soporte WebSocket
        
    Returns:
        Objeto Conf con la configuración generada
    """
    service_name = upstream_target.split(':')[0]
    
    # Crear configuración
    conf = Conf()
    
    # Upstream block
    upstream = Upstream(service_name)
    upstream.add(
        Key('server', upstream_target)
    )
    conf.add(upstream)
    
    # Server block HTTPS
    server = Server()
    server.add(
        Key('listen', '443 ssl http2'),
        Key('listen', '[::]:443 ssl http2'),
        Key('server_name', domain),
        Comment('SSL certificates'),
        Key('ssl_certificate', f'/etc/letsencrypt/live/{domain}/fullchain.pem'),
        Key('ssl_certificate_key', f'/etc/letsencrypt/live/{domain}/privkey.pem')
    )
    
    # Location block
    location = Location('/')
    location.add(
        Key('proxy_pass', f'http://{service_name}'),
        Key('proxy_set_header', 'Host $host'),
        Key('proxy_set_header', 'X-Real-IP $remote_addr'),
        Key('proxy_set_header', 'X-Forwarded-For $proxy_add_x_forwarded_for'),
        Key('proxy_set_header', 'X-Forwarded-Proto $scheme'),
        Comment('Timeouts'),
        Key('proxy_connect_timeout', '60s'),
        Key('proxy_send_timeout', '60s'),
        Key('proxy_read_timeout', '60s')
    )
    
    # WebSocket support
    if enable_websocket:
        location.add(
            Comment('WebSocket support'),
            Key('proxy_http_version', '1.1'),
            Key('proxy_set_header', 'Upgrade $http_upgrade'),
            Key('proxy_set_header', 'Connection "upgrade"')
        )
    
    server.add(location)
    conf.add(server)
    
    return conf


def save_http_config(conf: Conf, service_name: str, config_dir: str = './conf.d') -> Path:
    """
    Guarda la configuración HTTP en un archivo.
    
    Args:
        conf: Objeto Conf con la configuración
        service_name: Nombre del servicio
        config_dir: Directorio donde guardar la configuración
        
    Returns:
        Path del archivo creado
    """
    config_path = Path(config_dir) / f'{service_name}.conf'
    
    # Crear directorio si no existe
    Path(config_dir).mkdir(parents=True, exist_ok=True)
    
    # Guardar configuración
    with open(config_path, 'w') as f:
        f.write(''.join(conf.as_strings))
    
    return config_path
