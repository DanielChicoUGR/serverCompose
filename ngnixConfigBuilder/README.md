# Nginx Config Builder 🔧

Herramienta CLI para generar configuraciones de Nginx de forma rápida y sencilla.

## 🚀 Características

- ✅ **Servicios HTTP/HTTPS**: Genera configuraciones de proxy reverso con SSL/TLS
- ✅ **Servicios TCP/UDP (Streams)**: Configura proxies TCP/UDP para servicios no-HTTP
- ✅ **Soporte WebSocket**: Configura automáticamente headers para WebSockets
- ✅ **Syntax Highlighting**: Visualiza las configuraciones generadas con colores
- ✅ **Instrucciones interactivas**: Te guía paso a paso en la configuración

## 📦 Instalación

Este proyecto usa `uv` como gestor de paquetes. Para instalar:

```bash
cd /home/daniel/Proyectos/serverComposes/buildNginxConfig

# Sincronizar dependencias
uv sync

# Instalar en modo desarrollo
uv pip install -e .
```

## 🎯 Uso

### Comandos disponibles

```bash
nginx-config --help
```

### 1. Inicializar estructura

Crea la estructura de directorios necesaria para Nginx:

```bash
nginx-config init --nginx-dir ./nginx
```

Esto crea:

```
nginx/
├── conf.d/
│   └── streams/
├── ssl/
├── letsencrypt/
└── certbot-webroot/
```

### 2. Añadir servicio HTTP/HTTPS

```bash
# Servicio básico
nginx-config add-http app.hmbcentral.live myapp:8080

# Con soporte WebSocket
nginx-config add-http ws.hmbcentral.live myws:3000 --websocket

# Especificar directorio de salida
nginx-config add-http app.example.com myapp:8080 -o /etc/nginx/conf.d
```

**Opciones:**

- `--websocket, -ws`: Habilitar soporte WebSocket
- `--output, -o`: Directorio de salida (default: `./conf.d`)
- `--email, -e`: Email para certificados SSL (default: `dachival0007.2@gmail.com`)

### 3. Añadir servicio TCP/UDP (Stream)

```bash
# Puerto único
nginx-config add-stream mysql 3306

# Rango de puertos
nginx-config add-stream croc 9009 9013

# Servicio UDP
nginx-config add-stream dns 53 --udp

# Especificar directorio de salida
nginx-config add-stream redis 6379 -o /etc/nginx/conf.d/streams
```

**Opciones:**

- `--udp`: Usar protocolo UDP en lugar de TCP
- `--output, -o`: Directorio de salida (default: `./conf.d/streams`)

### 4. Ver configuración

Muestra el contenido de un archivo de configuración con syntax highlighting:

```bash
nginx-config show ./conf.d/myapp.conf
```

## 📝 Ejemplos Completos

### Ejemplo 1: Aplicación web con SSL

```bash
# 1. Inicializar estructura
nginx-config init

# 2. Crear configuración
nginx-config add-http nextcloud.hmbcentral.live nextcloud:80

# 3. Obtener certificado SSL (seguir las instrucciones mostradas)
docker exec certbot certbot certonly --webroot \
    -w /var/www/certbot \
    -d nextcloud.hmbcentral.live \
    -m dachival0007.2@gmail.com \
    --agree-tos --non-interactive

# 4. Recargar Nginx
docker exec nginx nginx -t && docker exec nginx nginx -s reload
```

### Ejemplo 2: Servicio WebSocket

```bash
nginx-config add-http chat.hmbcentral.live chatapp:3000 --websocket
```

### Ejemplo 3: Servicio TCP (Base de datos)

```bash
# PostgreSQL
nginx-config add-stream postgres 5432

# MySQL
nginx-config add-stream mysql 3306

# Redis
nginx-config add-stream redis 6379
```

### Ejemplo 4: Múltiples puertos (Croc)

```bash
# Genera configuración para puertos 9009-9013
nginx-config add-stream croc 9009 9013
```

## 🏗️ Estructura de Archivos Generados

### Configuración HTTP

```nginx
upstream myapp {
    server myapp:8080;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name app.hmbcentral.live;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/app.hmbcentral.live/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.hmbcentral.live/privkey.pem;

    location / {
        proxy_pass http://myapp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### Configuración Stream (TCP/UDP)

```nginx
# Croc service TCP streams (puertos 9009-9013)
upstream croc_9009 {
    server croc:9009;
}

server {
    listen 9009;
    proxy_pass croc_9009;
    proxy_timeout 30s;
    proxy_connect_timeout 5s;
}

# ... más servidores para cada puerto
```

## 🔧 Desarrollo

### Estructura del proyecto

```
buildNginxConfig/
├── pyproject.toml           # Configuración del proyecto
├── README.md               # Este archivo
├── src/
│   ├── nginx.py           # Librería python-nginx
│   └── nginxconfigbuilder/
│       ├── __init__.py    # Exports del paquete
│       ├── cli.py         # CLI principal con Click
│       ├── http_service.py    # Generador de configs HTTP
│       ├── stream_service.py  # Generador de configs Stream
│       └── utils.py       # Utilidades y formateo
```

### Ejecutar en modo desarrollo

```bash
# Con uv
uv run nginx-config --help

# Directamente
python -m nginxconfigbuilder.cli --help
```

### Agregar nuevas dependencias

```bash
uv add nombre-paquete
```

## 🐛 Troubleshooting

### Error: Comando no encontrado

Asegúrate de haber instalado el paquete:

```bash
uv pip install -e .
```

### Error: ModuleNotFoundError

Reinstala las dependencias:

```bash
uv sync
```

### Ver versión instalada

```bash
nginx-config --version
```

## 📚 Documentación

### Python API

También puedes usar las funciones programáticamente:

```python
from nginxconfigbuilder import create_http_service, save_http_config

# Crear configuración
conf = create_http_service(
    domain='app.example.com',
    upstream_target='myapp:8080',
    enable_websocket=True
)

# Guardar archivo
config_path = save_http_config(conf, 'myapp', './conf.d')
print(f"Configuración guardada en: {config_path}")
```

## 🤝 Contribuir

Este es un proyecto personal, pero las contribuciones son bienvenidas.

## 📄 Licencia

GPLv3 - Basado en python-nginx (c) 2016 Jacob Cook

## 👤 Autor

**Daniel Chico**

- Email: dachival@correo.ugr

## 🔗 Recursos

- [Documentación de Nginx](https://nginx.org/en/docs/)
- [python-nginx (librería base)](https://github.com/peakwinter/python-nginx)
- [Click (framework CLI)](https://click.palletsprojects.com/)
- [Rich (terminal formatting)](https://rich.readthedocs.io/)
