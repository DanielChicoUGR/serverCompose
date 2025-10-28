# Nginx Reverse Proxy

Configuración de Nginx como proxy inverso para gestionar servicios Docker mediante archivos de configuración modulares.

## 📁 Estructura de Archivos

```
nginx/
├── compose.yml                    # Docker Compose principal
├── nginx.conf                     # Configuración global de Nginx
├── conf.d/                        # Configuraciones HTTP/HTTPS
│   ├── default.conf              # Servidor por defecto + redirects HTTP→HTTPS
│   ├── blocked-ips.conf          # IPs bloqueadas manualmente
│   ├── rate-limiting-example.conf.disabled  # Ejemplos de rate limiting
│   ├── service1.conf             # Configuración de servicios web
│   └── streams/                  # Configuraciones TCP/UDP
│       └── croc.conf             # Ejemplo: proxy TCP para Croc
├── ssl/                          # Certificados SSL auto-firmados
│   ├── default.crt
│   └── default.key
├── letsencrypt/                  # Certificados Let's Encrypt
│   └── acme.json
├── certbot-webroot/              # Validación ACME para certificados
├── logs/                         # Logs de Nginx (para Fail2Ban)
│   ├── access.log
│   └── error.log
└── fail2ban/                     # Configuraciones de Fail2Ban
    ├── README.md                 # Documentación completa
    ├── install-fail2ban.sh       # Script de instalación
    ├── jail.d/                   # Jails personalizados
    │   └── nginx-custom.conf
    └── filter.d/                 # Filtros de detección
        ├── nginx-req-limit.conf
        ├── nginx-login.conf
        ├── nginx-404.conf
        └── nginx-proxy.conf
```

## 🚀 Inicio Rápido

### 1. Preparar el entorno

```bash
cd /home/daniel/Proyectos/serverComposes/nginx

# Crear estructura de directorios
mkdir -p conf.d/streams ssl letsencrypt certbot-webroot

# Generar certificado SSL auto-firmado por defecto
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/default.key \
    -out ssl/default.crt \
    -subj "/C=ES/ST=State/L=City/O=HMB/CN=localhost"

chmod 600 ssl/default.key
chmod 644 ssl/default.crt
```

### 2. Iniciar servicios

```bash
# Levantar Nginx y Certbot
docker compose up -d

# Verificar que están corriendo
docker ps | grep -E "nginx|certbot"

# Ver logs en tiempo real
docker logs -f nginx
```

### 3. Verificar configuración

```bash
# Probar sintaxis de configuración
docker exec nginx nginx -t

# Recargar configuración (sin downtime)
docker exec nginx nginx -s reload

# Reiniciar servicio completo
docker restart nginx
```

## 📝 Añadir Nuevos Servicios

### Servicios HTTP/HTTPS

Crear archivo en `conf.d/` con el siguiente formato:

```nginx
upstream myservice {
    server myservice:8080;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name app.hmbcentral.live;

    ssl_certificate /etc/letsencrypt/live/app.hmbcentral.live/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.hmbcentral.live/privkey.pem;

    location / {
        proxy_pass http://myservice;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

**Pasos:**

1. **Obtener certificado SSL:**

```bash
docker exec certbot certbot certonly --webroot \
    -w /var/www/certbot \
    -d app.hmbcentral.live \
    -m dachival0007.2@gmail.com \
    --agree-tos
```

2. **Crear configuración del servicio** (ver ejemplo arriba)

3. **Recargar Nginx:**

```bash
docker exec nginx nginx -t && docker exec nginx nginx -s reload
```

### Servicios TCP/UDP (Streams)

Para servicios que usan puertos TCP/UDP (como Croc, SSH, bases de datos):

```nginx
upstream tcp_service {
    server service:9000;
}

server {
    listen 9000;
    proxy_pass tcp_service;
    proxy_timeout 30s;
    proxy_connect_timeout 5s;
}
```

**Importante:**

- Añadir el puerto en compose.yml:

```yaml
ports:
  - "9000:9000" # Nuevo puerto TCP
```

- Reiniciar el contenedor: `docker compose up -d`

## 🔧 Configuraciones Comunes

### Archivos grandes (uploads)

Ya configurado en nginx.conf:

```nginx
client_max_body_size 600M;
client_body_buffer_size 600M;
```

Para cambiar:

1. Editar nginx.conf
2. Recargar: `docker exec nginx nginx -s reload`

### Compresión Gzip

Habilitada por defecto para:

- HTML, CSS, JavaScript
- JSON, XML
- Fuentes (TTF, OTF, WOFF)
- SVG

### Headers de seguridad

Añadir en configuración de servicio:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

## 🔐 Gestión de Certificados SSL

### Renovación automática

Certbot revisa cada 12 horas y renueva certificados próximos a expirar automáticamente.

### Renovación manual

```bash
# Renovar todos los certificados
docker exec certbot certbot renew

# Renovar certificado específico
docker exec certbot certbot renew --cert-name app.hmbcentral.live

# Verificar expiración
docker exec certbot certbot certificates
```

### Nuevo certificado

```bash
docker exec certbot certbot certonly --webroot \
    -w /var/www/certbot \
    -d nuevo.hmbcentral.live \
    -m dachival0007.2@gmail.com \
    --agree-tos --non-interactive
```

## 🐛 Troubleshooting

### Ver logs

```bash
# Logs de Nginx
docker logs nginx

# Logs en tiempo real
docker logs -f nginx

# Logs de Certbot
docker logs certbot

# Ver últimas 50 líneas
docker logs --tail 50 nginx
```

### Errores comunes

**"502 Bad Gateway"**

- El servicio backend no está corriendo
- Verificar: `docker ps | grep nombre-servicio`
- El servicio no está en la red `proxy`

**"Certificate not found"**

- Ejecutar certbot para obtener certificado
- Verificar ruta en configuración del servicio

**"Address already in use"**

- Otro servicio usa el puerto (ej: Traefik)
- Detener el otro servicio primero

### Debug de configuración

```bash
# Verificar sintaxis
docker exec nginx nginx -t

# Ver configuración completa
docker exec nginx nginx -T

# Verificar puertos abiertos
docker exec nginx netstat -tlnp

# Probar conectividad al backend
docker exec nginx ping -c 3 nombre-servicio
```

## 🔄 Migración desde Traefik

Si estás migrando desde Traefik:

1. **Mantener ambos activos temporalmente:**

```bash
# Traefik en puertos actuales
# Nginx en puertos alternativos para pruebas
```

2. **Migrar servicio por servicio:**

   - Crear configuración en Nginx
   - Probar con dominio de prueba
   - Cambiar DNS cuando funcione

3. **Detener Traefik:**

```bash
cd /home/daniel/Proyectos/serverComposes/traefik
docker compose down
```

## 📊 Monitoreo

### Estado de servicios

```bash
# Ver todos los servicios en la red proxy
docker network inspect proxy

# Estado de Nginx
docker exec nginx nginx -s status

# Conexiones activas
docker exec nginx ss -tunlp
```

### Acceso a logs

Los logs se almacenan en:

- Access log: `/var/log/nginx/access.log`
- Error log: `/var/log/nginx/error.log`

Ver dentro del contenedor:

```bash
docker exec nginx tail -f /var/log/nginx/access.log
docker exec nginx tail -f /var/log/nginx/error.log
```

## 🔗 Servicios Backend

Para que un servicio sea accesible a través de Nginx:

1. **Debe estar en la red `proxy`:**

```yaml
networks:
  - proxy
```

2. **NO debe exponer puertos públicamente:**

```yaml
expose:
  - "8080" # Solo interno, no 'ports:'
```

3. **Ejemplo completo:**

```yaml
services:
  myapp:
    image: myapp:latest
    container_name: myapp
    networks:
      - proxy
    expose:
      - "8080"

networks:
  proxy:
    external: true
```

## 📚 Referencias

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Certbot Documentation](https://eff-certbot.readthedocs.io/)

---

## 🛡️ Protección con Fail2Ban

Este proyecto incluye configuraciones completas de Fail2Ban para proteger contra:

- ⚡ Rate limiting abuse
- 🔐 Ataques de fuerza bruta en login
- 🔍 Escaneo de directorios (404)
- 🔄 Ataques DDoS en proxies

### Instalación Rápida

```bash
# 1. Instalar Fail2Ban
sudo apt update && sudo apt install fail2ban -y

# 2. Instalar configuraciones
cd fail2ban
sudo ./install-fail2ban.sh

# 3. Verificar
sudo fail2ban-client status
```

### Helper Script

Gestiona IPs bloqueadas fácilmente:

```bash
# Ver ayuda
../fail2BanHelper.sh help

# Banear una IP
../fail2BanHelper.sh ban 192.168.1.100

# Ver IPs bloqueadas
../fail2BanHelper.sh list

# Ver jails activos
../fail2BanHelper.sh jails

# Ver top IPs problemáticas
../fail2BanHelper.sh top-offenders
```

### Documentación Completa

Ver `fail2ban/README.md` para documentación detallada, incluyendo:

- Configuración de jails
- Filtros disponibles
- Monitoreo y estadísticas
- Solución de problemas

```

```
