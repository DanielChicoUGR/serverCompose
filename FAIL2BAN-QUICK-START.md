# 🛡️ Sistema de Protección Fail2Ban

Sistema completo de protección contra ataques implementado para el servidor Nginx.

## 🚀 Inicio Rápido

### 1. Instalar Fail2Ban

```bash
sudo apt update
sudo apt install fail2ban -y
```

### 2. Instalar Configuraciones

```bash
cd nginx/fail2ban
sudo ./install-fail2ban.sh
```

### 3. Verificar Instalación

```bash
./verify-fail2ban.sh
```

## 📁 Archivos Principales

| Archivo                                            | Descripción                 |
| -------------------------------------------------- | --------------------------- |
| `nginx/fail2ban/`                                  | Configuraciones de Fail2Ban |
| `nginx/conf.d/blocked-ips.conf`                    | IPs bloqueadas manualmente  |
| `fail2BanHelper.sh`                                | Script helper mejorado      |
| `nginx/conf.d/rate-limiting-example.conf.disabled` | Ejemplos de rate limiting   |

## 💻 Comandos Básicos

### Helper Script

```bash
# Ver ayuda completa
./fail2BanHelper.sh help

# Banear IP
./fail2BanHelper.sh ban 192.168.1.100

# Desbanear IP
./fail2BanHelper.sh unban 192.168.1.100

# Ver IPs bloqueadas
./fail2BanHelper.sh list

# Ver jails activos
./fail2BanHelper.sh jails

# Ver estado de jail
./fail2BanHelper.sh jail-status nginx-req-limit

# Top IPs problemáticas
./fail2BanHelper.sh top-offenders

# Ver logs
./fail2BanHelper.sh logs fail2ban
./fail2BanHelper.sh logs nginx-error

# Estadísticas
./fail2BanHelper.sh stats
```

### Fail2Ban Directamente

```bash
# Estado general
sudo fail2ban-client status

# Estado de jail específico
sudo fail2ban-client status nginx-req-limit

# Ver IPs baneadas
sudo fail2ban-client get nginx-req-limit banned

# Banear IP manualmente
sudo fail2ban-client set nginx-req-limit banip 192.168.1.100

# Desbanear IP
sudo fail2ban-client set nginx-req-limit unbanip 192.168.1.100

# Ver logs
sudo tail -f /var/log/fail2ban.log
```

## 🔒 Jails Configurados

1. **nginx-req-limit** - Rate limiting general (20 intentos/60s → ban 1h)
2. **nginx-login-abuse** - Abuso de login (5 intentos/5min → ban 2h)
3. **nginx-404** - Escaneo 404 (50 errores/10min → ban 1h)
4. **nginx-proxy** - Errores de proxy (10 errores/5min → ban 30min)

## 📚 Documentación Completa

Ver archivos de documentación detallada:

- **`nginx/fail2ban/README.md`** - Documentación completa de Fail2Ban
- **`nginx/readme.md`** - Documentación general de Nginx
- **`fail2ban.md`** - Guía original de implementación

## 🔧 Archivos de Configuración

### Jails

- `nginx/fail2ban/jail.d/nginx-custom.conf` - Configuración de 4 jails

### Filtros

- `nginx/fail2ban/filter.d/nginx-req-limit.conf`
- `nginx/fail2ban/filter.d/nginx-login.conf`
- `nginx/fail2ban/filter.d/nginx-404.conf`
- `nginx/fail2ban/filter.d/nginx-proxy.conf`

## ⚙️ Rate Limiting en Nginx

Las zonas de rate limiting ya están configuradas en `nginx/nginx.conf`:

- **general**: 10 req/s
- **login**: 5 req/min
- **api**: 30 req/s

Ver ejemplos de uso en: `nginx/conf.d/rate-limiting-example.conf.disabled`

## 🔍 Monitoreo

### Script de Verificación

```bash
cd nginx/fail2ban
./verify-fail2ban.sh
```

### Logs en Tiempo Real

```bash
# Fail2Ban
sudo tail -f /var/log/fail2ban.log

# Nginx (error)
tail -f nginx/logs/error.log

# Nginx (access)
tail -f nginx/logs/access.log
```

### Estadísticas Rápidas

```bash
./fail2BanHelper.sh stats
```

## 🚨 Solución de Problemas

### IP Bloqueada por Error

```bash
./fail2BanHelper.sh unban <IP>
```

### Jails No Activos

```bash
cd nginx/fail2ban
sudo ./install-fail2ban.sh
```

### Ver Errores de Configuración

```bash
sudo fail2ban-client -t
```

### Reiniciar Todo

```bash
sudo systemctl restart fail2ban
docker compose -f nginx/compose.yml restart nginx
```

## 📞 Ayuda Adicional

Para más información, consulta:

```bash
./fail2BanHelper.sh help
man fail2ban-client
docker exec nginx nginx -h
```

---

**Proyecto**: serverCompose  
**Autor**: Daniel Chico  
**Fecha**: Octubre 2025
