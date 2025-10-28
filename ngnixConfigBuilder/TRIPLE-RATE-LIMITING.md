# Triple Rate Limiting - Guía de Uso

## 🎯 Descripción

La funcionalidad de **Triple Rate Limiting** permite aplicar diferentes niveles de protección en un mismo servicio HTTP/HTTPS, según el tipo de endpoint:

- **Login paths**: Protección estricta (5 req/min) para rutas de autenticación
- **API paths**: Rate limiting alto (30 req/s) para endpoints de API
- **General paths**: Rate limiting estándar (10 req/s) para el resto

## 🔧 Sintaxis

```bash
nginx-config add-http <domain> <upstream> \
  --login-paths <path1> \
  --login-paths <path2> \
  --api-paths <path3> \
  --api-paths <path4> \
  --rate-limit general
```

## 📊 Niveles de Protección

| Zona      | Rate Limit | Burst | Ubicación en Nginx         |
| --------- | ---------- | ----- | -------------------------- |
| `login`   | 5 req/min  | 3     | Login paths específicos    |
| `api`     | 30 req/s   | 50    | API paths específicos      |
| `general` | 10 req/s   | 20    | Catch-all (resto de paths) |

## ✅ Ejemplos de Uso

### Ejemplo 1: Solo Login Paths

Proteger rutas de autenticación con rate limiting estricto:

```bash
nginx-config add-http app.example.com backend:8080 \
  --login-paths /login \
  --login-paths /auth \
  --login-paths /register \
  --rate-limit general
```

**Resultado:**

- `/login`, `/auth`, `/register` → 5 req/min (zona `login`)
- `/*` (resto) → 10 req/s (zona `general`)

### Ejemplo 2: Solo API Paths

Permitir mayor throughput para endpoints de API:

```bash
nginx-config add-http api.example.com backend:8080 \
  --api-paths /api/ \
  --api-paths /v1/ \
  --api-paths /v2/ \
  --rate-limit general
```

**Resultado:**

- `/api/*`, `/v1/*`, `/v2/*` → 30 req/s (zona `api`)
- `/*` (resto) → 10 req/s (zona `general`)

### Ejemplo 3: Triple Protección (RECOMENDADO)

Combinar login paths + API paths + general:

```bash
nginx-config add-http app.example.com backend:8080 \
  --login-paths /login \
  --login-paths /auth \
  --api-paths /api/ \
  --api-paths /v1/api/ \
  --rate-limit general
```

**Resultado:**

- `/login`, `/auth` → 5 req/min (zona `login`)
- `/api/*`, `/v1/api/*` → 30 req/s (zona `api`)
- `/*` (resto) → 10 req/s (zona `general`)

### Ejemplo 4: Aplicación Moderna (SPA + API)

```bash
nginx-config add-http app.example.com fullstack:8080 \
  --login-paths /auth/login \
  --login-paths /auth/register \
  --login-paths /auth/reset-password \
  --api-paths /api/v1/ \
  --api-paths /graphql \
  --rate-limit general
```

**Resultado:**

- `/auth/login`, `/auth/register`, `/auth/reset-password` → 5 req/min
- `/api/v1/*`, `/graphql` → 30 req/s
- `/*` (frontend, assets, etc.) → 10 req/s

### Ejemplo 5: E-commerce

```bash
nginx-config add-http shop.example.com shop:8080 \
  --login-paths /customer/login \
  --login-paths /customer/register \
  --api-paths /api/products/ \
  --api-paths /api/cart/ \
  --api-paths /api/checkout/ \
  --rate-limit general
```

## 🛡️ Ventajas

### 1. Protección Específica

Cada tipo de endpoint recibe el nivel de protección adecuado:

- **Login**: Máxima protección contra fuerza bruta
- **API**: Alto throughput para integraciones legítimas
- **General**: Protección estándar sin impactar UX

### 2. Flexibilidad

Puedes usar solo `--login-paths`, solo `--api-paths`, o ambas simultáneamente:

```bash
# Solo login
--login-paths /login --rate-limit general

# Solo API
--api-paths /api/ --rate-limit general

# Ambas
--login-paths /login --api-paths /api/ --rate-limit general
```

### 3. Sin Impacto en Tráfico Legítimo

- Los usuarios normales no se ven afectados por el rate limiting de login
- Las APIs pueden recibir más requests sin penalizar el sitio web
- Los atacantes son bloqueados específicamente en las rutas vulnerables

### 4. Compatibilidad con Fail2Ban

Las zonas de rate limiting se integran perfectamente con Fail2Ban:

```bash
# Ver jails configuradas
sudo fail2ban-client status

# Ver estadísticas de rate limiting
sudo ./fail2BanHelper.sh jail-status nginx-req-limit
```

## 🔍 Verificación

### 1. Ver la Configuración Generada

```bash
nginx-config show ./conf.d/myapp.conf
```

### 2. Validar Sintaxis de Nginx

```bash
docker exec nginx nginx -t
```

### 3. Probar Rate Limiting

```bash
# Probar login path (debe bloquearse después de 5 req/min)
for i in {1..10}; do curl -X POST https://app.example.com/login; sleep 1; done

# Probar API path (debe permitir 30 req/s)
ab -n 100 -c 10 https://app.example.com/api/users

# Probar path general (debe permitir 10 req/s)
ab -n 50 -c 5 https://app.example.com/
```

## 📋 Configuración Requerida

Asegúrate de que `nginx.conf` tenga las zonas configuradas:

```nginx
http {
    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;
    limit_conn_zone $binary_remote_addr zone=addr:10m;

    # ... resto de configuración
}
```

## 🐛 Troubleshooting

### Error: "limit_req_zone not found"

**Problema**: Nginx no encuentra las zonas de rate limiting

**Solución**: Verifica que `nginx.conf` tenga las definiciones de zonas

```bash
docker exec nginx cat /etc/nginx/nginx.conf | grep limit_req_zone
```

### Rate Limiting No Funciona

**Problema**: Los requests no se están limitando

**Solución**:

1. Verifica que los paths coincidan exactamente (case-sensitive)
2. Revisa logs: `tail -f nginx/logs/error.log`
3. Verifica la sintaxis: `docker exec nginx nginx -t`

### 503 Service Unavailable

**Problema**: Demasiados requests llegando al burst limit

**Solución**: Ajusta los valores de burst en `http_service.py`:

```python
rate_limit_config = {
    'general': ('general', 'burst=20 nodelay'),    # Aumentar a 30
    'login': ('login', 'burst=3 nodelay'),         # Aumentar a 5
    'api': ('api', 'burst=50 nodelay')             # Aumentar a 100
}
```

## 📚 Recursos

- [README.md](README.md) - Documentación completa
- [EXAMPLES.md](EXAMPLES.md) - Más ejemplos de uso
- [CHANGELOG.md](CHANGELOG.md) - Historial de cambios
- [nginx/fail2ban/README.md](../nginx/fail2ban/README.md) - Integración con Fail2Ban

## 🎓 Casos de Uso Recomendados

| Tipo de Aplicación | Login Paths          | API Paths        | Rate Limit General |
| ------------------ | -------------------- | ---------------- | ------------------ |
| Blog/CMS           | ✅ `/admin/login`    | ❌               | ✅ `general`       |
| SPA + REST API     | ✅ `/auth/*`         | ✅ `/api/*`      | ✅ `general`       |
| E-commerce         | ✅ `/customer/login` | ✅ `/api/cart/*` | ✅ `general`       |
| Microservicio API  | ❌                   | ✅ `/v1/*`       | ✅ `general`       |
| Panel Admin        | ✅ `/login`          | ❌               | ❌ `none`          |

## 💡 Mejores Prácticas

1. **Siempre usa `--login-paths`** para rutas de autenticación
2. **Usa `--api-paths`** solo si tu API necesita alto throughput
3. **Combina ambas** cuando tu aplicación tenga login + API pública
4. **No uses `--rate-limit none`** en servicios públicos
5. **Monitorea logs** para ajustar límites según tráfico real
6. **Instala Fail2Ban** para protección adicional

## 🔗 Referencias

- [Nginx Rate Limiting](http://nginx.org/en/docs/http/ngx_http_limit_req_module.html)
- [Fail2Ban Documentation](https://www.fail2ban.org/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
