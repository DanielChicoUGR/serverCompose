"""
Módulo para crear configuraciones de servicios TCP/UDP (streams) en Nginx.
"""

from pathlib import Path
from typing import Tuple, List

# Importar la librería nginx del paquete
from .nginx import Upstream, Server, Key, Comment


def create_stream_service(service_name: str, port_start: int, 
                          port_end: int = None, protocol: str = 'tcp') -> Tuple[List, List[int]]:
    """
    Crea una configuración de stream TCP/UDP.
    
    Args:
        service_name: Nombre del servicio (ej: croc, mysql)
        port_start: Puerto de inicio
        port_end: Puerto final (para rangos), None para puerto único
        protocol: Protocolo (tcp o udp)
        
    Returns:
        Tupla con (lista de objetos de configuración, lista de puertos)
    """
    # Si no hay rango, usar el mismo puerto
    if port_end is None:
        port_end = port_start
    
    # Lista para almacenar todos los elementos de configuración
    config_elements = []
    ports = []
    
    # Añadir comentario al inicio
    config_elements.append(
        Comment(f'{service_name.capitalize()} service {protocol.upper()} streams (puertos {port_start}' + 
                (f'-{port_end}' if port_end != port_start else '') + ')')
    )
    
    # Crear upstream y server para cada puerto
    for port in range(port_start, port_end + 1):
        # Upstream block
        upstream_name = f'{service_name}_{port}'
        upstream = Upstream(upstream_name)
        upstream.add(
            Key('server', f'{service_name}:{port}')
        )
        config_elements.append(upstream)
        
        # Server block
        server = Server()
        listen_directive = str(port)
        if protocol == 'udp':
            listen_directive += ' udp'
        
        server.add(
            Key('listen', listen_directive),
            Key('proxy_pass', upstream_name),
            Key('proxy_timeout', '30s'),
            Key('proxy_connect_timeout', '5s')
        )
        config_elements.append(server)
        ports.append(port)
    
    return config_elements, ports


def save_stream_config(config_elements: List, service_name: str, 
                       streams_dir: str = './conf.d/streams') -> Path:
    """
    Guarda la configuración de stream en un archivo.
    
    Args:
        config_elements: Lista de objetos de configuración
        service_name: Nombre del servicio
        streams_dir: Directorio donde guardar la configuración
        
    Returns:
        Path del archivo creado
    """
    config_path = Path(streams_dir) / f'{service_name}.conf'
    
    # Crear directorio si no existe
    Path(streams_dir).mkdir(parents=True, exist_ok=True)
    
    # Construir el contenido del archivo
    content_parts = []
    for element in config_elements:
        if isinstance(element, Comment):
            content_parts.append(element.as_strings)
        else:
            content_parts.extend(element.as_strings)
    
    # Guardar configuración
    with open(config_path, 'w') as f:
        f.write(''.join(content_parts))
    
    return config_path
