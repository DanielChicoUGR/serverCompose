# Guía Rápida - Nginx Config Builder

## 🚀 Comandos Rápidos

### Generar configuraciones desde este directorio

```bash
# Servicios HTTP/HTTPS
uv run --project ../buildNginxConfig nginx-config add-http DOMINIO SERVICIO:PUERTO

# Servicios TCP/UDP
uv run --project ../buildNginxConfig nginx-config add-stream SERVICIO PUERTO_INICIO [PUERTO_FIN]
```

## 📝 Ejemplos

### Servicios HTTP/HTTPS

```bash
# Aplicación web básica
uv run --project ../buildNginxConfig nginx-config add-http app.hmbcentral.live myapp:8080

# Con soporte WebSocket
uv run --project ../buildNginxConfig nginx-config add-http chat.hmbcentral.live chatapp:3000 --websocket

# API backend
uv run --project ../buildNginxConfig nginx-config add-http api.hmbcentral.live backend:5000
```

### Servicios TCP/UDP (Streams)

```bash
# Croc (rango de puertos)
uv run --project ../buildNginxConfig nginx-config add-stream croc 9009 9013

# MySQL
uv run --project ../buildNginxConfig nginx-config add-stream mysql 3306

# PostgreSQL
uv run --project ../buildNginxConfig nginx-config add-stream postgres 5432

# Redis
uv run --project ../buildNginxConfig nginx-config add-stream redis 6379

# DNS (UDP)
uv run --project ../buildNginxConfig nginx-config add-stream dns 53 --udp
```

## 🔄 Workflow Completo

### 1. Añadir servicio HTTP

```bash
# Generar configuración
uv run --project ../buildNginxConfig nginx-config add-http nextcloud.hmbcentral.live nextcloud:80

# Verificar y recargar Nginx para habilitar el endpoint ACME
docker exec nginx nginx -t
docker exec nginx nginx -s reload

# Obtener certificado SSL (ahora sí funcionará)
docker exec certbot certbot certonly --webroot \
    -w /var/www/certbot \
    -d nextcloud.hmbcentral.live \
    -m dachival0007.2@gmail.com \
    --agree-tos --non-interactive

# Verificar que el certificado se obtuvo correctamente
docker exec certbot certbot certificates

# Recargar Nginx para usar el nuevo certificado
docker exec nginx nginx -s reload
```

### 2. Añadir servicio TCP

```bash
# Generar configuración
uv run --project ../buildNginxConfig nginx-config add-stream redis 6379

# Añadir puerto en compose.yml (hacer manualmente):
# ports:
#   - "6379:6379"

# Reiniciar Nginx
docker compose up -d

# Verificar
docker exec nginx nginx -t
docker logs -f nginx
```

## 🎨 Ver configuración generada

```bash
# Con syntax highlighting
uv run --project ../buildNginxConfig nginx-config show conf.d/myapp.conf

# O simplemente con cat
cat conf.d/myapp.conf
cat conf.d/streams/croc.conf
```

## 🔍 Verificar y debugear

```bash
# Verificar sintaxis de Nginx
docker exec nginx nginx -t

# Ver configuración completa cargada
docker exec nginx nginx -T

# Ver logs
docker logs nginx
docker logs -f nginx

# Ver últimas 50 líneas
docker logs --tail 50 nginx

# Recargar configuración (sin downtime)
docker exec nginx nginx -s reload

# Reiniciar contenedor
docker restart nginx
```

## 🔐 Gestión de Certificados SSL

```bash
# Obtener nuevo certificado
docker exec certbot certbot certonly --webroot \
    -w /var/www/certbot \
    -d DOMINIO \
    -m dachival0007.2@gmail.com \
    --agree-tos --non-interactive

# Ver certificados instalados
docker exec certbot certbot certificates

# Renovar todos los certificados
docker exec certbot certbot renew

# Renovar certificado específico
docker exec certbot certbot renew --cert-name DOMINIO
```

## 📊 Comandos útiles Docker

```bash
# Ver servicios en la red proxy
docker network inspect proxy

# Ver puertos expuestos por Nginx
docker port nginx

# Ver procesos dentro de Nginx
docker exec nginx ps aux

# Acceder al shell de Nginx
docker exec -it nginx sh

# Ver configuración dentro del contenedor
docker exec nginx cat /etc/nginx/nginx.conf
docker exec nginx ls -la /etc/nginx/conf.d/
```

## 🗂️ Estructura de archivos

```
nginx/
├── compose.yml                    # Docker Compose
├── nginx.conf                     # Configuración principal
├── conf.d/                        # Configuraciones HTTP/HTTPS
│   ├── default.conf              # Servidor por defecto
│   ├── testapp.conf              # ← Generado con add-http
│   └── streams/                  # Configuraciones TCP/UDP
│       └── croc.conf             # ← Generado con add-stream
├── ssl/                          # Certificados auto-firmados
├── letsencrypt/                  # Certificados Let's Encrypt
└── certbot-webroot/              # Validación ACME
```

## 💡 Tips

1. **Siempre verifica** la configuración antes de recargar:

   ```bash
   docker exec nginx nginx -t && docker exec nginx nginx -s reload
   ```

2. **Servicios backend** deben estar en la red `proxy`:

   ```yaml
   networks:
     - proxy
   ```

3. **No expongas puertos** en servicios HTTP (usa `expose` en lugar de `ports`)

4. **Para streams TCP/UDP** sí debes exponer los puertos en el compose de Nginx

5. **DNS debe apuntar** al servidor antes de obtener certificados SSL

## 🆘 Problemas comunes

### 502 Bad Gateway

- Verifica que el servicio backend esté corriendo
- Verifica que esté en la red `proxy`
- Comprueba el nombre del servicio

### Certificate not found

- Ejecuta certbot para obtener el certificado
- Verifica la ruta en la configuración

### Address already in use

- Otro servicio está usando el puerto (probablemente Traefik)
- Detén el otro servicio primero

### Connection refused

- El servicio backend no está escuchando en el puerto correcto
- Verifica con: `docker exec SERVICIO netstat -tlnp`
