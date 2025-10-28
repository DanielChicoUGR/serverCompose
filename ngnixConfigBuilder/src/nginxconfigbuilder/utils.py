"""
Utilidades para mostrar instrucciones y ayuda en la CLI.
"""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def print_http_instructions(console: Console, domain: str, service_name: str, 
                           config_path: Path, email: str):
    """
    Imprime instrucciones para configurar un servicio HTTP/HTTPS.
    
    Args:
        console: Objeto Console de rich
        domain: Dominio del servicio
        service_name: Nombre del servicio
        config_path: Ruta del archivo de configuración
        email: Email para certificados SSL
    """
    # Crear tabla de pasos
    table = Table(title="📋 Pasos Siguientes", show_header=True, header_style="bold cyan")
    table.add_column("Paso", style="cyan", width=6)
    table.add_column("Descripción", style="white")
    table.add_column("Comando", style="green")
    
    table.add_row(
        "1️⃣",
        "Obtener certificado SSL",
        f"docker exec certbot certbot certonly --webroot \\\n"
        f"    -w /var/www/certbot \\\n"
        f"    -d {domain} \\\n"
        f"    -m {email} \\\n"
        f"    --agree-tos --non-interactive"
    )
    
    table.add_row(
        "2️⃣",
        "Verificar configuración",
        "docker exec nginx nginx -t"
    )
    
    table.add_row(
        "3️⃣",
        "Recargar Nginx",
        "docker exec nginx nginx -s reload"
    )
    
    console.print("\n")
    console.print(table)
    
    # Panel de notas importantes
    notes = f"""
[yellow]⚠️  Notas importantes:[/yellow]

• Asegúrate de que el servicio '[cyan]{service_name}[/cyan]' esté en la red '[cyan]proxy[/cyan]'
• El servicio debe exponer el puerto internamente (usa [cyan]expose[/cyan], no [cyan]ports[/cyan])
• El DNS debe apuntar a tu servidor antes de obtener el certificado SSL
"""
    
    console.print(Panel(notes, border_style="yellow", title="[bold]💡 Información[/bold]"))


def print_stream_instructions(console: Console, service_name: str, ports: list, config_path: Path):
    """
    Imprime instrucciones para configurar un servicio TCP/UDP.
    
    Args:
        console: Objeto Console de rich
        service_name: Nombre del servicio
        ports: Lista de puertos configurados
        config_path: Ruta del archivo de configuración
    """
    # Generar mapeo de puertos para docker-compose
    if len(ports) == 1:
        port_mapping = f'      - "{ports[0]}:{ports[0]}"'
    else:
        port_mapping = f'      - "{ports[0]}-{ports[-1]}:{ports[0]}-{ports[-1]}"'
    
    # Crear tabla de pasos
    table = Table(title="📋 Pasos Siguientes", show_header=True, header_style="bold cyan")
    table.add_column("Paso", style="cyan", width=6)
    table.add_column("Descripción", style="white")
    table.add_column("Comando/Instrucción", style="green")
    
    table.add_row(
        "1️⃣",
        f"Añadir puertos en compose.yml de nginx",
        f"ports:\n{port_mapping}"
    )
    
    table.add_row(
        "2️⃣",
        "Reiniciar Nginx",
        "docker compose up -d"
    )
    
    table.add_row(
        "3️⃣",
        "Verificar configuración",
        "docker exec nginx nginx -t"
    )
    
    table.add_row(
        "4️⃣",
        "Ver logs",
        "docker logs -f nginx"
    )
    
    console.print("\n")
    console.print(table)
    
    # Información de puertos
    ports_info = f"""
[cyan]📊 Puertos configurados:[/cyan] {ports[0]}""" + (f"-{ports[-1]}" if len(ports) > 1 else "") + """

[yellow]⚠️  Notas importantes:[/yellow]

• Asegúrate de que el servicio '[cyan]""" + service_name + """[/cyan]' esté en la red '[cyan]proxy[/cyan]'
• El servicio debe exponer los puertos """ + str(ports[0]) + (f"-{ports[-1]}" if len(ports) > 1 else "") + """ internamente
• Los puertos deben añadirse al compose.yml de nginx para ser accesibles externamente
"""
    
    console.print(Panel(ports_info, border_style="yellow", title="[bold]💡 Información[/bold]"))


def format_docker_compose_snippet(service_name: str, ports: list) -> str:
    """
    Genera un snippet de docker-compose para el servicio.
    
    Args:
        service_name: Nombre del servicio
        ports: Lista de puertos
        
    Returns:
        String con el snippet de docker-compose
    """
    if len(ports) == 1:
        expose_line = f'      - "{ports[0]}"'
    else:
        expose_line = f'      - "{ports[0]}-{ports[-1]}"'
    
    snippet = f"""services:
  {service_name}:
    image: {service_name}:latest
    container_name: {service_name}
    restart: unless-stopped
    networks:
      - proxy
    expose:
{expose_line}

networks:
  proxy:
    external: true
"""
    
    return snippet


def print_static_instructions(console: Console, domain: str, site_name: str, 
                             root_path: str, config_path: Path, email: str):
    """
    Imprime instrucciones para configurar un sitio estático.
    
    Args:
        console: Objeto Console de rich
        domain: Dominio del sitio
        site_name: Nombre del sitio
        root_path: Ruta al directorio con archivos estáticos
        config_path: Ruta del archivo de configuración
        email: Email para certificados SSL
    """
    # Crear tabla de pasos
    table = Table(title="📋 Pasos Siguientes", show_header=True, header_style="bold cyan")
    table.add_column("Paso", style="cyan", width=6)
    table.add_column("Descripción", style="white")
    table.add_column("Comando", style="green")
    
    table.add_row(
        "1️⃣",
        "Colocar archivos estáticos",
        f"Copia tus archivos HTML/CSS/JS a:\n{root_path}"
    )
    
    table.add_row(
        "2️⃣",
        "Obtener certificado SSL",
        f"docker exec certbot certbot certonly --webroot \\\n"
        f"    -w /var/www/certbot \\\n"
        f"    -d {domain} \\\n"
        f"    -m {email} \\\n"
        f"    --agree-tos --non-interactive"
    )
    
    table.add_row(
        "3️⃣",
        "Verificar configuración",
        "docker exec nginx nginx -t"
    )
    
    table.add_row(
        "4️⃣",
        "Recargar Nginx",
        "docker exec nginx nginx -s reload"
    )
    
    console.print("\n")
    console.print(table)
    
    # Panel de notas importantes
    notes = f"""
[yellow]⚠️  Notas importantes:[/yellow]

• Asegúrate de que el directorio '[cyan]{root_path}[/cyan]' exista y contenga tus archivos
• El directorio debe ser accesible por el contenedor de Nginx (considera usar un volumen)
• El DNS debe apuntar a tu servidor antes de obtener el certificado SSL
• Los archivos estáticos serán servidos directamente sin proxy

[cyan]📂 Estructura de ejemplo:[/cyan]

{root_path}/
├── index.html
├── css/
│   └── styles.css
├── js/
│   └── app.js
└── images/
    └── logo.png
"""
    
    console.print(Panel(notes, border_style="yellow", title="[bold]💡 Información[/bold]"))
