"""
Módulo para crear configuraciones de sitios estáticos en Nginx.
"""

from pathlib import Path
from typing import Optional

# Importar la librería nginx del paquete
from .nginx import Conf, Server, Location, Key, Comment


def create_static_service(
    domain: str, 
    root_path: str, 
    index_file: str = 'index.html',
    rate_limit: Optional[str] = None,
    security_headers: bool = True
) -> Conf:
    """
    Crea una configuración de sitio estático HTTP/HTTPS.
    
    Args:
        domain: Dominio del sitio (ej: blog.hmbcentral.live)
        root_path: Ruta al directorio con los archivos estáticos (ej: /var/www/blog)
        index_file: Archivo índice (default: index.html)
        rate_limit: Tipo de rate limiting ('general', 'login', 'api', None)
        security_headers: Añadir headers de seguridad (default: True)
        
    Returns:
        Objeto Conf con la configuración generada
    """
    # Crear configuración
    conf = Conf()
    
    # Server block HTTPS
    server = Server()
    server.add(
        Key('listen', '443 ssl http2'),
        Key('listen', '[::]:443 ssl http2'),
        Key('server_name', domain),
        Comment('SSL certificates'),
        Key('ssl_certificate', f'/etc/letsencrypt/live/{domain}/fullchain.pem'),
        Key('ssl_certificate_key', f'/etc/letsencrypt/live/{domain}/privkey.pem'),
        Comment('Static files configuration'),
        Key('root', root_path),
        Key('index', index_file)
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
    
    # Location block para archivos estáticos
    location = Location('/')
    
    # Rate limiting (opcional, normalmente no necesario para sitios estáticos)
    if rate_limit:
        rate_limit_config = {
            'general': ('general', 'burst=20 nodelay'),
            'login': ('login', 'burst=3 nodelay'),
            'api': ('api', 'burst=50 nodelay')
        }
        
        if rate_limit in rate_limit_config:
            zone, params = rate_limit_config[rate_limit]
            location.add(
                Comment(f'Rate limiting - zone: {zone}'),
                Key('limit_req', f'zone={zone} {params}')
            )
    
    location.add(
        Key('try_files', '$uri $uri/ =404')
    )
    server.add(location)
    
    # Location para assets (cache más agresivo)
    location_assets = Location('~* \\.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$')
    location_assets.add(
        Key('expires', '1y'),
        Key('add_header', 'Cache-Control "public, immutable"')
    )
    server.add(location_assets)
    
    conf.add(server)
    
    return conf


def save_static_config(conf: Conf, service_name: str, config_dir: str = './conf.d') -> Path:
    """
    Guarda la configuración de sitio estático en un archivo.
    
    Args:
        conf: Objeto Conf con la configuración
        service_name: Nombre del sitio
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
