#!/usr/bin/env python3
"""
CLI principal para nginxconfigbuilder.
Herramienta para generar configuraciones de Nginx.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from pathlib import Path

from .http_service import create_http_service, save_http_config
from .stream_service import create_stream_service, save_stream_config
from .static_service import create_static_service, save_static_config
from .utils import print_http_instructions, print_stream_instructions, print_static_instructions

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    🔧 Nginx Config Builder - Generador de configuraciones Nginx
    
    Herramienta CLI para crear configuraciones de servicios HTTP/HTTPS, TCP/UDP
    y sitios estáticos para Nginx de forma rápida y sencilla.
    """
    pass


@cli.command()
@click.argument('domain')
@click.argument('upstream')
@click.option('--websocket', '-ws', is_flag=True, help='Habilitar soporte WebSocket')
@click.option('--output', '-o', default='./conf.d', help='Directorio de salida para las configuraciones')
@click.option('--email', '-e', default='dachival0007.2@gmail.com', help='Email para certificados SSL')
def add_http(domain, upstream, websocket, output, email):
    """
    Añadir servicio HTTP/HTTPS.
    
    DOMAIN: Dominio del servicio (ej: app.hmbcentral.live)
    
    UPSTREAM: Servicio y puerto (ej: myapp:8080)
    
    Ejemplos:
    
        nginx-config add-http app.hmbcentral.live myapp:8080
        
        nginx-config add-http ws.hmbcentral.live myws:3000 --websocket
    """
    try:
        # Validar formato del upstream
        if ':' not in upstream:
            console.print("[red]❌ Error: El upstream debe tener formato 'servicio:puerto'[/red]")
            raise click.Abort()
        
        service_name = upstream.split(':')[0]
        
        # Crear configuración
        with console.status(f"[bold green]Generando configuración para {service_name}..."):
            conf = create_http_service(domain, upstream, websocket)
        
        # Guardar archivo
        config_path = save_http_config(conf, service_name, output)
        
        # Mostrar configuración generada
        console.print(f"\n[bold green]✅ Configuración creada:[/bold green] {config_path}\n")
        
        # Leer y mostrar contenido con syntax highlighting
        with open(config_path, 'r') as f:
            content = f.read()
            syntax = Syntax(content, "nginx", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"[bold]{config_path.name}[/bold]", border_style="green"))
        
        # Mostrar instrucciones
        print_http_instructions(console, domain, service_name, config_path, email)
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.argument('domain')
@click.argument('root_path')
@click.option('--index', '-i', default='index.html', help='Archivo índice (default: index.html)')
@click.option('--output', '-o', default='./conf.d', help='Directorio de salida para las configuraciones')
@click.option('--email', '-e', default='dachival0007.2@gmail.com', help='Email para certificados SSL')
def add_static(domain, root_path, index, output, email):
    """
    Añadir sitio web estático.
    
    DOMAIN: Dominio del sitio (ej: blog.hmbcentral.live)
    
    ROOT_PATH: Ruta al directorio con archivos estáticos (ej: /var/www/blog)
    
    Ejemplos:
    
        nginx-config add-static blog.hmbcentral.live /var/www/blog
        
        nginx-config add-static docs.hmbcentral.live /var/www/docs --index index.htm
    """
    try:
        # Extraer nombre del sitio del dominio
        site_name = domain.split('.')[0]
        
        # Crear configuración
        with console.status(f"[bold green]Generando configuración para sitio estático {site_name}..."):
            conf = create_static_service(domain, root_path, index)
        
        # Guardar archivo
        config_path = save_static_config(conf, site_name, output)
        
        # Mostrar configuración generada
        console.print(f"\n[bold green]✅ Configuración de sitio estático creada:[/bold green] {config_path}\n")
        
        # Leer y mostrar contenido con syntax highlighting
        with open(config_path, 'r') as f:
            content = f.read()
            syntax = Syntax(content, "nginx", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"[bold]{config_path.name}[/bold]", border_style="magenta"))
        
        # Mostrar instrucciones
        print_static_instructions(console, domain, site_name, root_path, config_path, email)
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.argument('service')
@click.argument('port_start', type=int)
@click.argument('port_end', type=int, required=False)
@click.option('--udp', is_flag=True, help='Usar protocolo UDP en lugar de TCP')
@click.option('--output', '-o', default='./conf.d/streams', help='Directorio de salida para las configuraciones')
def add_stream(service, port_start, port_end, udp, output):
    """
    Añadir servicio TCP/UDP (stream).
    
    SERVICE: Nombre del servicio (ej: croc, mysql)
    
    PORT_START: Puerto inicial
    
    PORT_END: Puerto final (opcional, para rangos)
    
    Ejemplos:
    
        nginx-config add-stream croc 9009 9013
        
        nginx-config add-stream mysql 3306
        
        nginx-config add-stream dns 53 --udp
    """
    try:
        protocol = 'udp' if udp else 'tcp'
        
        # Validar puertos
        if port_end and port_end < port_start:
            console.print("[red]❌ Error: El puerto final debe ser mayor o igual al inicial[/red]")
            raise click.Abort()
        
        # Crear configuración
        with console.status(f"[bold green]Generando configuración stream para {service}..."):
            conf, ports = create_stream_service(service, port_start, port_end, protocol)
        
        # Guardar archivo
        config_path = save_stream_config(conf, service, output)
        
        # Mostrar configuración generada
        console.print(f"\n[bold green]✅ Configuración de stream creada:[/bold green] {config_path}\n")
        
        # Leer y mostrar contenido con syntax highlighting
        with open(config_path, 'r') as f:
            content = f.read()
            syntax = Syntax(content, "nginx", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"[bold]{config_path.name}[/bold]", border_style="blue"))
        
        # Mostrar instrucciones
        print_stream_instructions(console, service, ports, config_path)
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.option('--nginx-dir', '-d', default='./nginx', help='Directorio base de Nginx')
def init(nginx_dir):
    """
    Inicializar estructura de directorios para Nginx.
    
    Crea la estructura necesaria de carpetas y archivos para empezar.
    """
    try:
        base_path = Path(nginx_dir)
        
        # Crear directorios
        directories = [
            base_path / 'conf.d',
            base_path / 'conf.d' / 'streams',
            base_path / 'ssl',
            base_path / 'letsencrypt',
            base_path / 'certbot-webroot',
            base_path / 'www',  # Directorio para sitios estáticos
        ]
        
        console.print("\n[bold cyan]📁 Creando estructura de directorios...[/bold cyan]\n")
        
        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                console.print(f"  [green]✓[/green] {directory}")
            else:
                console.print(f"  [yellow]○[/yellow] {directory} (ya existe)")
        
        console.print("\n[bold green]✅ Estructura inicializada correctamente[/bold green]")
        console.print(f"\n[cyan]📂 Directorio base:[/cyan] {base_path.absolute()}")
        console.print("\n[bold]Siguiente paso:[/bold]")
        console.print("  • Genera certificado SSL por defecto:")
        console.print(f"    cd {base_path.absolute()}")
        console.print("    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\")
        console.print("        -keyout ssl/default.key \\")
        console.print("        -out ssl/default.crt \\")
        console.print('        -subj "/C=ES/ST=State/L=City/O=HMB/CN=localhost"')
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
def show(config_file):
    """
    Mostrar contenido de un archivo de configuración con syntax highlighting.
    
    CONFIG_FILE: Ruta al archivo de configuración de Nginx
    """
    try:
        config_path = Path(config_file)
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        syntax = Syntax(content, "nginx", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"[bold]{config_path.name}[/bold]", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.Abort()


if __name__ == '__main__':
    cli()
