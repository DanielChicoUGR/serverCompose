# 🛡️ Configuración de Fail2Ban para Nginx

Sistema completo de protección contra ataques y abusos en el servidor Nginx usando Fail2Ban.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Jails Configurados](#jails-configurados)
- [Filtros Disponibles](#filtros-disponibles)
- [Uso](#uso)
- [Comandos Útiles](#comandos-útiles)
- [Monitoreo](#monitoreo)
- [Solución de Problemas](#solución-de-problemas)

---

## 📖 Descripción

Este directorio contiene configuraciones de Fail2Ban diseñadas específicamente para proteger el servidor Nginx contra:

- ⚡ **Rate Limiting**: Solicitudes excesivas
- 🔐 **Login Abuse**: Intentos de fuerza bruta en login
- 🔍 **404 Scanning**: Escaneo de directorios
- 🔄 **Proxy Abuse**: Ataques DDoS en upstream

---

## 📂 Estructura del Proyecto

```
fail2ban/
├── README.md                     # Este archivo
├── install-fail2ban.sh          # Script de instalación
├── jail.d/                      # Configuraciones de jails
│   └── nginx-custom.conf        # Jails personalizados para Nginx
└── filter.d/                    # Filtros de detección
    ├── nginx-req-limit.conf     # Filtro para rate limiting
    ├── nginx-login.conf         # Filtro para login abuse
    ├── nginx-404.conf           # Filtro para errores 404
    └── nginx-proxy.conf         # Filtro para errores de proxy
```

---

## 🚀 Instalación

### Paso 1: Instalar Fail2Ban

```bash
sudo apt update
sudo apt install fail2ban -y
```

### Paso 2: Ejecutar el Script de Instalación

```bash
cd /home/daniel/Proyectos/serverCompose/nginx/fail2ban
sudo ./install-fail2ban.sh
```

El script automáticamente:

- ✅ Verifica que Fail2Ban esté instalado
- ✅ Crea hard links de las configuraciones
- ✅ Verifica la configuración
- ✅ Reinicia Fail2Ban
- ✅ Muestra el estado de los jails

### Paso 3: Verificar la Instalación

```bash
sudo fail2ban-client status
```

Deberías ver algo como:

```
Status
|- Number of jail:      4
`- Jail list:   nginx-req-limit, nginx-login-abuse, nginx-404, nginx-proxy
```

---

## 🔒 Jails Configurados

### 1. **nginx-req-limit** - Rate Limiting General

- **Descripción**: Detecta solicitudes excesivas que activan rate limiting
- **Log**: `/home/daniel/Proyectos/serverCompose/nginx/logs/error.log`
- **Máximo de reintentos**: 20
- **Ventana de tiempo**: 60 segundos
- **Tiempo de baneo**: 3600 segundos (1 hora)

**¿Cuándo se activa?**
Cuando Nginx registra mensajes como:

```
limiting requests, excess: 5.000 by zone "general", client: 192.168.1.100
```

### 2. **nginx-login-abuse** - Abuso de Login

- **Descripción**: Protege endpoints de login contra fuerza bruta
- **Log**: `/home/daniel/Proyectos/serverCompose/nginx/logs/access.log`
- **Máximo de reintentos**: 5
- **Ventana de tiempo**: 300 segundos (5 minutos)
- **Tiempo de baneo**: 7200 segundos (2 horas)

**Rutas protegidas**:

- `/web/login` (Odoo)
- `/login`
- `/auth`
- `/signin`
- `/api/login`

### 3. **nginx-404** - Escaneo de Directorios

- **Descripción**: Detecta múltiples errores 404 (posible escaneo)
- **Log**: `/home/daniel/Proyectos/serverCompose/nginx/logs/access.log`
- **Máximo de reintentos**: 50
- **Ventana de tiempo**: 600 segundos (10 minutos)
- **Tiempo de baneo**: 3600 segundos (1 hora)

**Excepciones**: Ignora rutas legítimas como `robots.txt`, `favicon.ico`, `.well-known`

### 4. **nginx-proxy** - Errores de Proxy

- **Descripción**: Detecta problemas con upstream (posible DDoS)
- **Log**: `/home/daniel/Proyectos/serverCompose/nginx/logs/error.log`
- **Máximo de reintentos**: 10
- **Ventana de tiempo**: 300 segundos (5 minutos)
- **Tiempo de baneo**: 1800 segundos (30 minutos)

---

## 🔍 Filtros Disponibles

### nginx-req-limit.conf

Detecta:

```
limiting requests, excess:.*
limiting connections by zone.*
```

### nginx-login.conf

Detecta:

```
POST /web/login HTTP/1.1
POST /login HTTP/1.1
POST /auth HTTP/1.1
```

### nginx-404.conf

Detecta:

```
"GET /admin HTTP/1.1" 404
"POST /wp-admin HTTP/1.1" 404
```

### nginx-proxy.conf

Detecta:

```
upstream timed out
no live upstreams
upstream prematurely closed connection
```

---

## 💻 Uso

### Helper Script Mejorado

El script `../../fail2BanHelper.sh` ha sido mejorado con nuevas funcionalidades:

```bash
# Ver ayuda completa
./fail2BanHelper.sh help

# Banear una IP en Nginx y Fail2Ban
./fail2BanHelper.sh ban 192.168.1.100

# Desbanear una IP
./fail2BanHelper.sh unban 192.168.1.100

# Listar IPs bloqueadas (Nginx + Fail2Ban)
./fail2BanHelper.sh list

# Ver estado de todos los jails
./fail2BanHelper.sh jails

# Ver estado de un jail específico
./fail2BanHelper.sh jail-status nginx-req-limit

# Top 10 IPs con más requests limitados
./fail2BanHelper.sh top-offenders

# Ver logs
./fail2BanHelper.sh logs fail2ban
./fail2BanHelper.sh logs nginx-error
./fail2BanHelper.sh logs nginx-access

# Estadísticas de jails
./fail2BanHelper.sh stats
```

---

## 📊 Comandos Útiles

### Gestión de Jails

```bash
# Estado general
sudo fail2ban-client status

# Estado de un jail específico
sudo fail2ban-client status nginx-req-limit

# Ver IPs baneadas en un jail
sudo fail2ban-client get nginx-req-limit banned

# Banear IP manualmente en un jail
sudo fail2ban-client set nginx-req-limit banip 192.168.1.100

# Desbanear IP de un jail
sudo fail2ban-client set nginx-req-limit unbanip 192.168.1.100
```

### Ver Logs

```bash
# Logs de Fail2Ban
sudo tail -f /var/log/fail2ban.log

# Logs de Nginx (error)
tail -f /home/daniel/Proyectos/serverCompose/nginx/logs/error.log

# Logs de Nginx (access)
tail -f /home/daniel/Proyectos/serverCompose/nginx/logs/access.log

# Buscar baneos recientes
sudo grep "Ban" /var/log/fail2ban.log | tail -20

# Buscar desbaneos
sudo grep "Unban" /var/log/fail2ban.log | tail -20
```

### Reiniciar Servicios

```bash
# Reiniciar Fail2Ban
sudo systemctl restart fail2ban

# Verificar estado de Fail2Ban
sudo systemctl status fail2ban

# Recargar Nginx
docker exec nginx nginx -s reload

# Reiniciar contenedor de Nginx
cd /home/daniel/Proyectos/serverCompose/nginx
docker compose restart nginx
```

---

## 📈 Monitoreo

### Dashboard en Tiempo Real

Crea un script de monitoreo:

```bash
#!/bin/bash
# monitor-fail2ban.sh

watch -n 5 '
echo "=== Estado de Fail2Ban ==="
sudo fail2ban-client status

echo ""
echo "=== IPs Baneadas ==="
for jail in nginx-req-limit nginx-login-abuse nginx-404 nginx-proxy; do
    echo "[$jail]"
    sudo fail2ban-client get $jail banned 2>/dev/null
done

echo ""
echo "=== Últimos Baneos ==="
sudo grep "Ban" /var/log/fail2ban.log | tail -5
'
```

### Alertas por Email (Opcional)

Editar `/etc/fail2ban/jail.local`:

```ini
[DEFAULT]
destemail = tu-email@ejemplo.com
sendername = Fail2Ban
action = %(action_mwl)s
```

---

## 🔧 Solución de Problemas

### Problema: Los jails no se activan

**Verificar configuración**:

```bash
sudo fail2ban-client -t
```

**Revisar logs**:

```bash
sudo tail -50 /var/log/fail2ban.log
```

### Problema: No se detectan ataques

**Verificar rutas de logs**:

```bash
# Asegúrate de que estos archivos existen
ls -la /home/daniel/Proyectos/serverCompose/nginx/logs/
```

**Verificar permisos**:

```bash
# Fail2Ban necesita leer los logs
sudo chmod 644 /home/daniel/Proyectos/serverCompose/nginx/logs/*.log
```

### Problema: IP bloqueada incorrectamente

**Desbanear inmediatamente**:

```bash
./fail2BanHelper.sh unban <IP>
```

**Añadir a lista blanca** en `/etc/fail2ban/jail.local`:

```ini
[DEFAULT]
ignoreip = 127.0.0.1/8 ::1 <TU_IP_CONFIABLE>
```

### Problema: Fail2Ban no se inicia

**Verificar servicio**:

```bash
sudo systemctl status fail2ban
sudo journalctl -u fail2ban -n 50
```

**Reinstalar configuraciones**:

```bash
cd /home/daniel/Proyectos/serverCompose/nginx/fail2ban
sudo ./install-fail2ban.sh
```

---

## 📝 Notas Importantes

### Hard Links vs Symlinks

Este proyecto usa **hard links** en lugar de symlinks porque:

- ✅ Fail2Ban puede tener restricciones de seguridad con symlinks
- ✅ Los hard links son más robustos
- ✅ Cambios en los archivos originales se reflejan automáticamente

### Actualizar Configuraciones

Si modificas algún archivo en `jail.d/` o `filter.d/`:

```bash
# Re-ejecutar instalación
sudo ./install-fail2ban.sh

# O manualmente recargar
sudo fail2ban-client reload
```

### Logs de Nginx

Asegúrate de que el `docker-compose.yml` tiene el volumen de logs:

```yaml
volumes:
  - ./logs:/var/log/nginx
```

---

## 🆘 Soporte

Si encuentras problemas:

1. **Revisar logs**: `sudo tail -f /var/log/fail2ban.log`
2. **Verificar estado**: `sudo fail2ban-client status`
3. **Testear configuración**: `sudo fail2ban-client -t`
4. **Revisar permisos**: `ls -la /etc/fail2ban/jail.d/`

---

## 📜 Licencia

Este proyecto es parte del sistema serverCompose.

**Autor**: Daniel Chico  
**Fecha**: Octubre 2025
