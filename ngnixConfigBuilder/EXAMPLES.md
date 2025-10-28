# Ejemplos de Uso - Nginx Config Builder

Este archivo contiene ejemplos de uso del generador de configuraciones con las nuevas características de rate limiting y seguridad.

## 🔧 Configuraciones HTTP/HTTPS

### Ejemplo 1: Aplicación Web Normal (con rate limiting general)

```bash
nginx-config add-http app.hmbcentral.live myapp:8080
```

Genera configuración con:

- ✅ Rate limiting: 10 req/s (zona general)
- ✅ Headers de seguridad habilitados
- ✅ SSL/HTTPS

### Ejemplo 2: Endpoint de Login (rate limiting estricto)

```bash
nginx-config add-http auth.hmbcentral.live auth:8080 --rate-limit login
```

Genera configuración con:

- ✅ Rate limiting: 5 req/min (zona login)
- ✅ Protección contra fuerza bruta
- ✅ Headers de seguridad

### Ejemplo 3: API REST (rate limiting permisivo)

```bash
nginx-config add-http api.hmbcentral.live api:5000 --rate-limit api
```

Genera configuración con:

- ✅ Rate limiting: 30 req/s (zona api)
- ✅ Mayor throughput para APIs
- ✅ Headers de seguridad

### Ejemplo 4: Panel de Administración (sin rate limiting)

```bash
nginx-config add-http admin.hmbcentral.live admin:8080 --rate-limit none
```

Genera configuración con:

- ❌ Sin rate limiting
- ✅ Headers de seguridad
- ⚠️ Solo para servicios internos/admin

### Ejemplo 5: WebSocket con Rate Limiting

```bash
nginx-config add-http ws.hmbcentral.live websocket:3000 --websocket --rate-limit general
```

Genera configuración con:

- ✅ Soporte WebSocket completo
- ✅ Rate limiting: 10 req/s
- ✅ Headers de seguridad

### Ejemplo 6: Aplicación con Paths de Login Específicos

```bash
nginx-config add-http app.hmbcentral.live myapp:8080 \
  --login-paths /login \
  --login-paths /auth \
  --login-paths /register \
  --rate-limit general
```

Genera configuración con:

- ✅ Rate limiting estricto (5 req/min) para `/login`, `/auth`, `/register`
- ✅ Rate limiting general (10 req/s) para el resto de paths
- ✅ Protección contra fuerza bruta en rutas de autenticación
- ✅ Headers de seguridad

### Ejemplo 7: API con Paths de API Específicos

```bash
nginx-config add-http app.hmbcentral.live myapp:8080 \
  --api-paths /api/ \
  --api-paths /v1/ \
  --rate-limit general
```

Genera configuración con:

- ✅ Rate limiting alto (30 req/s) para `/api/` y `/v1/`
- ✅ Rate limiting general (10 req/s) para el resto de paths
- ✅ Optimizado para consumo de API
- ✅ Headers de seguridad

### Ejemplo 8: Configuración Triple (General + Login + API)

```bash
nginx-config add-http app.hmbcentral.live myapp:8080 \
  --login-paths /login \
  --login-paths /auth \
  --api-paths /api/ \
  --api-paths /v1/api/ \
  --rate-limit general
```

Genera configuración con:

- ✅ Rate limiting estricto (5 req/min) para `/login`, `/auth`
- ✅ Rate limiting alto (30 req/s) para `/api/`, `/v1/api/`
- ✅ Rate limiting general (10 req/s) para el resto
- ✅ Máxima flexibilidad y protección
- ✅ Headers de seguridad

### Ejemplo 9: Aplicación Legacy (sin headers de seguridad)

```bash
nginx-config add-http legacy.hmbcentral.live legacy:8080 --no-security-headers --rate-limit none
```

Genera configuración con:

- ❌ Sin rate limiting
- ❌ Sin headers de seguridad
- ⚠️ Solo para compatibilidad con sistemas antiguos

## 📄 Sitios Estáticos

### Ejemplo 10: Blog Estático (sin rate limiting por defecto)

```bash
nginx-config add-static blog.hmbcentral.live /var/www/blog
```

Genera configuración con:

- ❌ Sin rate limiting (normal para sitios estáticos)
- ✅ Headers de seguridad
- ✅ Caché optimizado para assets

### Ejemplo 11: Sitio Estático con Rate Limiting

```bash
nginx-config add-static docs.hmbcentral.live /var/www/docs --rate-limit general
```

Genera configuración con:

- ✅ Rate limiting: 10 req/s
- ✅ Headers de seguridad
- ✅ Útil si el sitio tiene formularios o se espera tráfico alto

### Ejemplo 12: Sitio con Índice Personalizado

```bash
nginx-config add-static portfolio.hmbcentral.live /var/www/portfolio --index index.htm
```

## 🌊 Servicios Stream (TCP/UDP)

### Ejemplo 13: Base de Datos PostgreSQL

```bash
nginx-config add-stream postgres 5432
```

### Ejemplo 14: Rango de Puertos (Croc)

```bash
nginx-config add-stream croc 9009 9013
```

### Ejemplo 15: Servicio UDP (DNS)

```bash
nginx-config add-stream dns 53 --udp
```

## 🔗 Combinaciones Comunes

### Setup Completo de Aplicación

```bash
# 1. Inicializar estructura
nginx-config init

# 2. Frontend estático
nginx-config add-static app.hmbcentral.live /var/www/app

# 3. API backend con paths específicos
nginx-config add-http api.hmbcentral.live api:5000 \
  --api-paths /api/ \
  --api-paths /v1/ \
  --rate-limit general

# 4. Servicio de autenticación con login paths
nginx-config add-http auth.hmbcentral.live auth:8080 \
  --login-paths /login \
  --login-paths /auth \
  --login-paths /register \
  --rate-limit general

# 5. WebSocket para tiempo real
nginx-config add-http ws.hmbcentral.live ws:3000 --websocket --rate-limit general

# 6. Base de datos (stream)
nginx-config add-stream postgres 5432
```

### E-commerce con Protección

```bash
# Frontend
nginx-config add-http shop.hmbcentral.live frontend:3000 --rate-limit general

# API de productos con triple protección
nginx-config add-http api.shop.hmbcentral.live api:5000 \
  --login-paths /login \
  --api-paths /api/ \
  --rate-limit general

# Panel admin (sin límites)
nginx-config add-http admin.shop.hmbcentral.live admin:8080 --rate-limit none
```

### Aplicación Moderna (Separación de Concerns)

```bash
# SPA Frontend
nginx-config add-static www.hmbcentral.live /var/www/spa

# Backend principal con protección triple
nginx-config add-http backend.hmbcentral.live app:8080 \
  --login-paths /auth/login \
  --login-paths /auth/register \
  --api-paths /api/ \
  --rate-limit general

# Microservicio de pagos (solo API)
nginx-config add-http payments.hmbcentral.live payments:5000 \
  --api-paths /v1/payments/ \
  --rate-limit api

# WebSocket para notificaciones
nginx-config add-http ws.hmbcentral.live notifications:3000 --websocket
```

## 📊 Comparación de Rate Limiting

| Tipo      | Rate      | Burst | Casos de Uso                                |
| --------- | --------- | ----- | ------------------------------------------- |
| `general` | 10 req/s  | 20    | Sitios web, blogs, aplicaciones normales    |
| `login`   | 5 req/min | 3     | Login, registro, recuperación de contraseña |
| `api`     | 30 req/s  | 50    | APIs REST, microservicios                   |
| `none`    | ∞         | ∞     | Admin, servicios internos, desarrollo       |

### Protección por Capas (Triple Rate Limiting)

Cuando usas `--login-paths` y `--api-paths` simultáneamente con `--rate-limit general`, obtienes **tres niveles de protección**:

```bash
nginx-config add-http app.example.com app:8080 \
  --login-paths /login \
  --api-paths /api/ \
  --rate-limit general
```

**Resultado:**

| Path     | Rate Limit | Zona      | Protege Contra        |
| -------- | ---------- | --------- | --------------------- |
| `/login` | 5 req/min  | `login`   | Fuerza bruta en login |
| `/api/*` | 30 req/s   | `api`     | Abuso de API          |
| `/*`     | 10 req/s   | `general` | Tráfico normal        |

**Ventajas:**

- ✅ Protección específica para cada tipo de endpoint
- ✅ No penaliza el tráfico legítimo de API
- ✅ Máxima seguridad en rutas de autenticación
- ✅ Flexibilidad para diferentes casos de uso

## 🛡️ Mejores Prácticas

### ✅ Recomendado

```bash
# Aplicación pública con rate limiting
nginx-config add-http app.example.com app:8080 --rate-limit general

# Aplicación con protección triple (RECOMENDADO)
nginx-config add-http app.example.com app:8080 \
  --login-paths /login \
  --login-paths /auth \
  --api-paths /api/ \
  --rate-limit general

# API con rate limit alto
nginx-config add-http api.example.com api:5000 \
  --api-paths /v1/ \
  --rate-limit general
```

### ⚠️ Usar con Precaución

```bash
# Sin rate limiting (solo para admin/interno)
nginx-config add-http admin.example.com admin:8080 --rate-limit none

# Sin headers de seguridad (solo si es necesario)
nginx-config add-http legacy.example.com app:8080 --no-security-headers
```

### ❌ No Recomendado

```bash
# Servicio público sin protecciones
nginx-config add-http public.example.com app:8080 --rate-limit none --no-security-headers
```

## 💡 Casos de Uso Comunes

### Aplicación Web Estándar

```bash
# Backend con protección de login
nginx-config add-http app.example.com backend:8080 \
  --login-paths /login \
  --login-paths /register \
  --login-paths /reset-password \
  --rate-limit general
```

### Aplicación con API Pública

```bash
# Frontend + API en un solo servicio
nginx-config add-http app.example.com fullstack:8080 \
  --login-paths /auth/login \
  --api-paths /api/ \
  --rate-limit general
```

### Microservicios

```bash
# Gateway público
nginx-config add-http gateway.example.com gateway:8080 \
  --api-paths /api/ \
  --rate-limit general

# Auth service (solo login)
nginx-config add-http auth.example.com auth:8080 \
  --login-paths /login \
  --login-paths /register \
  --rate-limit general

# Service interno (sin límites)
nginx-config add-http internal.example.com service:8080 --rate-limit none
```

## 🔍 Verificar Configuraciones

Después de generar configuraciones:

```bash
# Ver la configuración generada
nginx-config show ./conf.d/myapp.conf

# Probar configuración en Nginx
docker exec nginx nginx -t

# Recargar Nginx
docker exec nginx nginx -s reload

# Ver logs en tiempo real
tail -f nginx/logs/error.log
```

## 📝 Notas Importantes

1. **Rate Limiting Zones**: Las zonas deben estar configuradas en `nginx.conf`:

   ```nginx
   limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
   limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
   limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;
   limit_conn_zone $binary_remote_addr zone=addr:10m;
   ```

2. **Fail2Ban**: Para protección adicional, instala Fail2Ban:

   ```bash
   cd nginx/fail2ban
   sudo ./install-fail2ban.sh
   ```

3. **Headers de Seguridad**: Están habilitados por defecto. Solo deshabilítalos si tienes una razón específica.

4. **Logs**: Asegúrate de que los logs estén accesibles en `nginx/logs/` para que Fail2Ban pueda leerlos.

## 🔗 Recursos

- [README.md](README.md) - Documentación completa
- [nginx/fail2ban/README.md](../nginx/fail2ban/README.md) - Configuración de Fail2Ban
- [FAIL2BAN-QUICK-START.md](../FAIL2BAN-QUICK-START.md) - Guía rápida de Fail2Ban
