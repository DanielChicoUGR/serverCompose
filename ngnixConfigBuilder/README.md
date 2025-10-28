# Nginx Config Builder 🔧

Herramienta CLI para generar configuraciones de Nginx de forma rápida y sencilla.

## 🚀 Características

- ✅ **Servicios HTTP/HTTPS**: Genera configuraciones de proxy reverso con SSL/TLS
- ✅ **Sitios Estáticos**: Configuración para servir sitios HTML/CSS/JS estáticos
- ✅ **Servicios TCP/UDP (Streams)**: Configura proxies TCP/UDP para servicios no-HTTP
- ✅ **Rate Limiting**: Protección automática contra solicitudes excesivas
- ✅ **Headers de Seguridad**: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
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
# Servicio básico (con rate limiting general por defecto)
nginx-config add-http app.hmbcentral.live myapp:8080

# Con soporte WebSocket
nginx-config add-http ws.hmbcentral.live myws:3000 --websocket

# API con rate limiting más permisivo
nginx-config add-http api.hmbcentral.live api:5000 --rate-limit api

# Login con rate limiting estricto
nginx-config add-http auth.hmbcentral.live auth:8080 --rate-limit login

# Protección triple: general + login + api (RECOMENDADO)
nginx-config add-http app.hmbcentral.live myapp:8080 \
  --login-paths /login \
  --login-paths /auth \
  --api-paths /api/ \
  --rate-limit general

# Solo paths de login con protección especial
nginx-config add-http app.hmbcentral.live myapp:8080 \
  --login-paths /login \
  --login-paths /register \
  --rate-limit general

# Solo paths de API con rate limiting alto
nginx-config add-http app.hmbcentral.live myapp:8080 \
  --api-paths /api/ \
  --api-paths /v1/ \
  --rate-limit general

# Sin rate limiting
nginx-config add-http admin.hmbcentral.live admin:8080 --rate-limit none

# Sin headers de seguridad (no recomendado)
nginx-config add-http legacy.hmbcentral.live legacy:8080 --no-security-headers

# Especificar directorio de salida
nginx-config add-http app.example.com myapp:8080 -o /etc/nginx/conf.d
```

**Opciones:**

- `--websocket, -ws`: Habilitar soporte WebSocket
- `--rate-limit, -rl`: Tipo de rate limiting (`general`, `login`, `api`, `none`) - default: `general`
- `--login-paths, -lp`: Paths de login con rate limiting especial (ej: `/login`, `/auth`) - puede repetirse múltiples veces
- `--api-paths, -ap`: Paths de API con rate limiting especial (ej: `/api/`, `/v1/`) - puede repetirse múltiples veces
- `--no-security-headers`: Deshabilitar headers de seguridad (no recomendado)
- `--output, -o`: Directorio de salida (default: `./conf.d`)
- `--email, -e`: Email para certificados SSL (default: `dachival0007.2@gmail.com`)

**Rate Limiting Zones:**

- `general`: 10 req/s con burst de 20 (uso general)
- `login`: 5 req/min con burst de 3 (endpoints de autenticación)
- `api`: 30 req/s con burst de 50 (APIs REST)
- `none`: Sin rate limiting

**Protección por Capas:**

Cuando usas `--login-paths` y/o `--api-paths` con `--rate-limit general`, obtienes protección multinivel:

```bash
nginx-config add-http app.example.com app:8080 \
  --login-paths /login \
  --api-paths /api/ \
  --rate-limit general
```

Esto genera:

- `/login` → Rate limit: 5 req/min (zona `login`)
- `/api/*` → Rate limit: 30 req/s (zona `api`)
- `/*` → Rate limit: 10 req/s (zona `general`)

### 2.1 Añadir sitio estático

```bash
# Sitio estático básico (sin rate limiting por defecto)
nginx-config add-static blog.hmbcentral.live /var/www/blog

# Con archivo índice personalizado
nginx-config add-static docs.hmbcentral.live /var/www/docs --index index.htm

# Con rate limiting
nginx-config add-static site.hmbcentral.live /var/www/site --rate-limit general

# Sin headers de seguridad
nginx-config add-static old.hmbcentral.live /var/www/old --no-security-headers
```

**Opciones:**

- `--index, -i`: Archivo índice (default: `index.html`)
- `--rate-limit, -rl`: Tipo de rate limiting (`general`, `login`, `api`, `none`) - default: `none`
- `--no-security-headers`: Deshabilitar headers de seguridad
- `--output, -o`: Directorio de salida (default: `./conf.d`)
- `--email, -e`: Email para certificados SSL

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

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    location / {
        # Rate limiting - zone: general
        limit_req zone=general burst=20 nodelay;
        limit_conn addr 10;

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

### 🛡️ Seguridad y Rate Limiting

Este generador incluye protecciones de seguridad por defecto:

#### Headers de Seguridad (habilitados por defecto)

- **X-Frame-Options**: Previene clickjacking
- **X-Content-Type-Options**: Previene MIME sniffing
- **X-XSS-Protection**: Protección contra XSS
- **Referrer-Policy**: Control de información del referrer

#### Rate Limiting

El rate limiting protege contra ataques de fuerza bruta y DDoS. Zonas disponibles:

| Zona      | Rate      | Burst | Uso Recomendado             |
| --------- | --------- | ----- | --------------------------- |
| `general` | 10 req/s  | 20    | Sitios web normales         |
| `login`   | 5 req/min | 3     | Endpoints de autenticación  |
| `api`     | 30 req/s  | 50    | APIs REST                   |
| `none`    | -         | -     | Sin límites (admin/interno) |

**Nota**: Las zonas deben estar configuradas en `nginx.conf`:

```nginx
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;
limit_conn_zone $binary_remote_addr zone=addr:10m;
```

#### Integración con Fail2Ban

Las configuraciones generadas son compatibles con Fail2Ban. Ver:

- `nginx/fail2ban/README.md` - Configuración completa de Fail2Ban
- `FAIL2BAN-QUICK-START.md` - Guía rápida de instalación

### Python API

También puedes usar las funciones programáticamente:

```python
from nginxconfigbuilder import create_http_service, save_http_config

# Crear configuración con rate limiting y seguridad
conf = create_http_service(
    domain='app.example.com',
    upstream_target='myapp:8080',
    enable_websocket=True,
    rate_limit='general',
    security_headers=True
)

# Guardar archivo
config_path = save_http_config(conf, 'myapp', './conf.d')
print(f"Configuración guardada en: {config_path}")
```

**Sitios estáticos:**

```python
from nginxconfigbuilder import create_static_service, save_static_config

conf = create_static_service(
    domain='blog.example.com',
    root_path='/var/www/blog',
    index_file='index.html',
    rate_limit=None,  # Sin rate limiting
    security_headers=True
)

config_path = save_static_config(conf, 'blog', './conf.d')
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
