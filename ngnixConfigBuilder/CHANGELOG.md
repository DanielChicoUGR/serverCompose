# Changelog - Nginx Config Builder

## [0.3.0] - 2025-10-29

### 🚀 Nuevas Características

#### Protección por Capas (Triple Rate Limiting)

- ✅ **Soporte para `--login-paths`**: Define rutas específicas con rate limiting estricto
  - Rate limit: 5 req/min (zona `login`)
  - Protección contra fuerza bruta en login
  - Se aplica a paths como `/login`, `/auth`, `/register`
- ✅ **Soporte para `--api-paths`**: Define rutas específicas con rate limiting alto
  - Rate limit: 30 req/s (zona `api`)
  - Optimizado para consumo de API
  - Se aplica a paths como `/api/`, `/v1/`
- ✅ **Protección Multinivel**: Combina hasta 3 zonas de rate limiting en un mismo servicio
  - Login paths → zona `login` (5 req/min)
  - API paths → zona `api` (30 req/s)
  - Resto de paths → zona `general` (10 req/s)

### 🔧 Mejoras

#### CLI

- ✅ Nueva opción `--login-paths, -lp` en `add-http`:
  - Se puede usar múltiples veces: `--login-paths /login --login-paths /auth`
  - Genera location blocks específicos con rate limiting estricto
- ✅ Nueva opción `--api-paths, -ap` en `add-http`:
  - Se puede usar múltiples veces: `--api-paths /api/ --api-paths /v1/`
  - Genera location blocks específicos con rate limiting alto

#### API Python

- ✅ `create_http_service()` acepta nuevos parámetros:
  - `login_paths`: Lista de paths para login (Optional[list])
  - `api_paths`: Lista de paths para API (Optional[list])
- ✅ Función helper interna `create_proxy_location()`:
  - Evita duplicación de código
  - Genera location blocks con configuración de proxy consistente

### 📚 Documentación

- ✅ README.md actualizado:
  - Sección "Protección por Capas" explicando el triple rate limiting
  - Ejemplos con `--login-paths` y `--api-paths`
- ✅ EXAMPLES.md actualizado:
  - 4 nuevos ejemplos de uso (6-9)
  - Sección "Protección por Capas (Triple Rate Limiting)"
  - Casos de uso comunes: Aplicación Web Estándar, API Pública, Microservicios
  - Ejemplos de Setup Completo y E-commerce actualizados

### 🎯 Casos de Uso

#### Ejemplo 1: Aplicación con Login

```bash
nginx-config add-http app.example.com app:8080 \
  --login-paths /login \
  --login-paths /auth \
  --rate-limit general
```

#### Ejemplo 2: API con Protección

```bash
nginx-config add-http app.example.com app:8080 \
  --api-paths /api/ \
  --api-paths /v1/ \
  --rate-limit general
```

#### Ejemplo 3: Protección Triple (RECOMENDADO)

```bash
nginx-config add-http app.example.com app:8080 \
  --login-paths /login \
  --api-paths /api/ \
  --rate-limit general
```

### 🔗 Compatibilidad

- ✅ Compatible con v0.2.0 (rate limiting simple)
- ✅ Compatible con v0.1.0 (sin rate limiting)
- ✅ Configuraciones antiguas siguen funcionando

### 📦 Archivos Modificados

- `src/nginxconfigbuilder/http_service.py` - Añadidos parámetros `login_paths` y `api_paths`
- `src/nginxconfigbuilder/cli.py` - Añadidas opciones `--login-paths` y `--api-paths`
- `README.md` - Documentación actualizada con protección por capas
- `EXAMPLES.md` - 4 nuevos ejemplos y sección de protección multinivel
- `CHANGELOG.md` - Este registro de cambios

---

## [0.2.0] - 2025-10-28

### 🚀 Nuevas Características

#### Rate Limiting

- ✅ Añadido soporte para rate limiting en servicios HTTP/HTTPS
- ✅ Añadido soporte para rate limiting en sitios estáticos
- ✅ Tres zonas predefinidas: `general`, `login`, `api`
- ✅ Opción `--rate-limit` en comandos `add-http` y `add-static`
- ✅ Configuración de burst y nodelay automática

#### Headers de Seguridad

- ✅ Headers de seguridad habilitados por defecto:
  - X-Frame-Options: "SAMEORIGIN"
  - X-Content-Type-Options: "nosniff"
  - X-XSS-Protection: "1; mode=block"
  - Referrer-Policy: "strict-origin-when-cross-origin"
- ✅ Opción `--no-security-headers` para deshabilitar

#### Sitios Estáticos

- ✅ Nuevo comando `add-static` para sitios HTML/CSS/JS
- ✅ Caché optimizado para assets (1 año)
- ✅ Soporte para archivos índice personalizados

#### Documentación

- ✅ README.md actualizado con ejemplos de rate limiting
- ✅ Nuevo archivo EXAMPLES.md con casos de uso detallados
- ✅ Instrucciones mejoradas con información de seguridad
- ✅ Integración documentada con Fail2Ban

### 🔧 Mejoras

#### CLI

- ✅ Nuevas opciones en `add-http`:
  - `--rate-limit, -rl`: Tipo de rate limiting
  - `--no-security-headers`: Deshabilitar headers de seguridad
- ✅ Nuevas opciones en `add-static`:
  - `--rate-limit, -rl`: Tipo de rate limiting
  - `--no-security-headers`: Deshabilitar headers de seguridad
- ✅ Comando `init` ahora crea directorio `logs/`

#### Configuraciones Generadas

- ✅ Rate limiting con burst automático según zona
- ✅ Limit connections (10 conexiones por IP)
- ✅ Headers de seguridad en todos los server blocks
- ✅ Comentarios descriptivos en las configuraciones

#### API Python

- ✅ `create_http_service()` acepta parámetros `rate_limit` y `security_headers`
- ✅ `create_static_service()` acepta parámetros `rate_limit` y `security_headers`

### 📚 Documentación

- ✅ Sección de seguridad en README.md
- ✅ Tabla de rate limiting zones
- ✅ Ejemplos de uso extendidos
- ✅ Mejores prácticas documentadas
- ✅ Integración con Fail2Ban documentada

### 🔗 Integración

- ✅ Compatible con configuración de Fail2Ban en `nginx/fail2ban/`
- ✅ Logs configurados para ser leídos por Fail2Ban
- ✅ Zonas de rate limiting alineadas con filtros de Fail2Ban

### 📦 Archivos Nuevos

- `src/nginxconfigbuilder/static_service.py` - Módulo para sitios estáticos
- `EXAMPLES.md` - Ejemplos detallados de uso
- `CHANGELOG.md` - Este archivo

### 🐛 Fixes

- ✅ Corrección en parámetro `add_stream` (udp vs protocol)
- ✅ Permisos de ejecución en scripts de Fail2Ban

---

## [0.1.0] - 2025-10-XX (Versión Inicial)

### Características Iniciales

- ✅ Comando `init` para crear estructura de directorios
- ✅ Comando `add-http` para servicios HTTP/HTTPS
- ✅ Comando `add-stream` para servicios TCP/UDP
- ✅ Comando `show` para visualizar configuraciones
- ✅ Soporte WebSocket con opción `--websocket`
- ✅ Syntax highlighting con Rich
- ✅ Instrucciones interactivas
- ✅ Certificados SSL con Let's Encrypt

---

## Próximas Características (Roadmap)

### v0.3.0 (Planeado)

- [ ] Soporte para múltiples upstreams (load balancing)
- [ ] Configuración de health checks
- [ ] Soporte para HTTP/3 (QUIC)
- [ ] Templates personalizables
- [ ] Comando para validar configuraciones existentes
- [ ] Comando para actualizar configuraciones en lote
- [ ] Soporte para variables de entorno

### v0.4.0 (Planeado)

- [ ] Interfaz web (opcional)
- [ ] Generador de docker-compose.yml
- [ ] Integración con Traefik (migración)
- [ ] Exportar/importar configuraciones
- [ ] Backup automático de configuraciones

---

## Notas de Actualización

### Actualizar de v0.1.0 a v0.2.0

1. **Rate Limiting**: Si actualizas, asegúrate de que `nginx.conf` tenga las zonas configuradas:

   ```nginx
   limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
   limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
   limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;
   limit_conn_zone $binary_remote_addr zone=addr:10m;
   ```

2. **Logs**: Asegúrate de tener el directorio `logs/` mapeado en docker-compose:

   ```yaml
   volumes:
     - ./logs:/var/log/nginx
   ```

3. **Configuraciones Existentes**: Las configuraciones antiguas seguirán funcionando. Para añadir rate limiting y headers de seguridad, regenera las configuraciones.

4. **Fail2Ban**: Si usas Fail2Ban, instala las nuevas configuraciones:
   ```bash
   cd nginx/fail2ban
   sudo ./install-fail2ban.sh
   ```

---

## Contribuciones

Este proyecto es mantenido por Daniel Chico. Las contribuciones son bienvenidas.

## Licencia

GPLv3
