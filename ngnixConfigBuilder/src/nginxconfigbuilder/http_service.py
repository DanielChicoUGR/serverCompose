"""
Módulo para crear configuraciones de servicios HTTP/HTTPS en Nginx.
"""

from pathlib import Path
from typing import Optional

# Importar la librería nginx del paquete
from .nginx import Conf, Upstream, Server, Location, Key, Comment


def create_http_service(
    domain: str, 
    upstream_target: str, 
    enable_websocket: bool = False,
    rate_limit: Optional[str] = None,
    security_headers: bool = True,
    login_paths: Optional[list] = None,
    api_paths: Optional[list] = None
) -> Conf:
    """
    Crea una configuración de servicio HTTP/HTTPS.
    
    Args:
        domain: Dominio del servicio (ej: app.hmbcentral.live)
        upstream_target: Target del upstream (ej: myapp:8080)
        enable_websocket: Habilitar soporte WebSocket
        rate_limit: Tipo de rate limiting global ('general', 'login', 'api', None)
        security_headers: Añadir headers de seguridad (default: True)
        login_paths: Lista de paths para login con rate limiting especial (ej: ['/login', '/auth'])
        api_paths: Lista de paths para API con rate limiting especial (ej: ['/api/', '/v1/'])
        
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
    
    # Security headers
    if security_headers:
        server.add(
            Comment('Security headers'),
            Key('add_header', 'X-Frame-Options "SAMEORIGIN" always'),
            Key('add_header', 'X-Content-Type-Options "nosniff" always'),
            Key('add_header', 'X-XSS-Protection "1; mode=block" always'),
            Key('add_header', 'Referrer-Policy "strict-origin-when-cross-origin" always')
        )
    
    # Helper function para crear location blocks con proxy
    def create_proxy_location(path: str, rate_zone: Optional[str] = None):
        loc = Location(path)
        
        # Rate limiting si se especifica
        if rate_zone:
            rate_limit_config = {
                'general': ('general', 'burst=20 nodelay'),
                'login': ('login', 'burst=3 nodelay'),
                'api': ('api', 'burst=50 nodelay')
            }
            
            if rate_zone in rate_limit_config:
                zone, params = rate_limit_config[rate_zone]
                loc.add(
                    Comment(f'Rate limiting - zone: {zone}'),
                    Key('limit_req', f'zone={zone} {params}'),
                    Key('limit_conn', 'addr 10')
                )
        
        # Proxy configuration
        loc.add(
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
            loc.add(
                Comment('WebSocket support'),
                Key('proxy_http_version', '1.1'),
                Key('proxy_set_header', 'Upgrade $http_upgrade'),
                Key('proxy_set_header', 'Connection "upgrade"')
            )
        
        return loc
    
    # Location blocks - orden de prioridad:
    # 1. Login paths (rate limiting más restrictivo)
    if login_paths:
        for login_path in login_paths:
            server.add(create_proxy_location(login_path, 'login'))
    
    # 2. API paths (rate limiting moderado)
    if api_paths:
        for api_path in api_paths:
            server.add(create_proxy_location(api_path, 'api'))
    
    # 3. Location general (rate limiting configurado o ninguno)
    server.add(create_proxy_location('/', rate_limit))
    
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
