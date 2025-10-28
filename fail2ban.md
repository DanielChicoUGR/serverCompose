# Comandos para ver configuración de Fail2Ban

Para ver todos los **jails** (cárceles) configurados en Fail2Ban, usa estos comandos:

## 🔍 Ver Jails Activos

```bash
# Ver todos los jails activos
sudo fail2ban-client status

# Ver estado detallado de un jail específico
sudo fail2ban-client status NOMBRE_JAIL

# Ejemplo:
sudo fail2ban-client status nginx-req-limit
sudo fail2ban-client status sshd
```

## 📋 Listar Configuración de Jails

```bash
# Ver todos los archivos de configuración de jails
ls -la /etc/fail2ban/jail.d/
ls -la /etc/fail2ban/jail.local

# Ver configuración principal de jails
cat /etc/fail2ban/jail.conf

# Ver jails personalizados
cat /etc/fail2ban/jail.d/*.conf
```

## 🔎 Información Detallada de un Jail

```bash
# Ver IPs baneadas en un jail específico
sudo fail2ban-client get NOMBRE_JAIL banned

# Ver número de IPs baneadas
sudo fail2ban-client get NOMBRE_JAIL banip --count

# Ver toda la información de un jail
sudo fail2ban-client get NOMBRE_JAIL actions
sudo fail2ban-client get NOMBRE_JAIL filters
```

## 📊 Ejemplo Completo de Verificación

```bash
#!/bin/bash

# Script para ver estado completo de Fail2Ban

echo "=== Estado General de Fail2Ban ==="
sudo fail2ban-client status

echo -e "\n=== Jails Configurados (archivos) ==="
ls -1 /etc/fail2ban/jail.d/ 2>/dev/null || echo "No hay jails personalizados"

echo -e "\n=== Detalle de Jails Activos ==="
for jail in $(sudo fail2ban-client status | grep "Jail list" | sed 's/.*://; s/,//g'); do
    echo -e "\n--- Jail: $jail ---"
    sudo fail2ban-client status $jail
done

echo -e "\n=== Logs Recientes ==="
sudo tail -20 /var/log/fail2ban.log
```

## 🛠️ Configurar Jails para tu Nginx

Basándome en tu configuración actual de `nginx.conf`, aquí está la configuración recomendada de jails:

````bash
# Crear archivo de configuración personalizado
sudo nano /etc/fail2ban/jail.d/nginx-custom.conf
````

```ini
# Jail para rate limiting general
[nginx-req-limit]
enabled = true
filter = nginx-req-limit
logpath = /home/dachival/serverComposes/nginx/logs/access.log
maxretry = 20
findtime = 60
bantime = 3600
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]

# Jail para intentos de login
[nginx-login-abuse]
enabled = true
filter = nginx-login
logpath = /home/dachival/serverComposes/nginx/logs/access.log
maxretry = 5
findtime = 300
bantime = 7200
action = iptables-multiport[name=LoginAbuse, port="http,https", protocol=tcp]

# Jail para errores 404 (posible escaneo)
[nginx-404]
enabled = true
filter = nginx-404
logpath = /home/dachival/serverComposes/nginx/logs/access.log
maxretry = 50
findtime = 600
bantime = 3600
action = iptables-multiport[name=404Scan, port="http,https", protocol=tcp]

# Jail para errores de proxy (502/503/504)
[nginx-proxy]
enabled = true
filter = nginx-proxy
logpath = /home/dachival/serverComposes/nginx/logs/error.log
maxretry = 10
findtime = 300
bantime = 1800
action = iptables-multiport[name=ProxyAbuse, port="http,https", protocol=tcp]
```

## 🔧 Crear Filtros Correspondientes

````bash
# Filtro para rate limiting (basado en tu nginx.conf actual)
sudo nano /etc/fail2ban/filter.d/nginx-req-limit.conf
````

```ini
[Definition]
failregex = limiting requests, excess:.* by zone.*client: <HOST>
            limiting connections by zone.*client: <HOST>
ignoreregex =
```

````bash
# Filtro para login abuse
sudo nano /etc/fail2ban/filter.d/nginx-login.conf
````

```ini
[Definition]
failregex = ^<HOST> -.*POST.*/web/login.*HTTP.*
            ^<HOST> -.*POST.*/login.*HTTP.*
            ^<HOST> -.*POST.*/auth.*HTTP.*
ignoreregex =
```

````bash
# Filtro para 404 abuse
sudo nano /etc/fail2ban/filter.d/nginx-404.conf
````

```ini
[Definition]
failregex = ^<HOST> -.*"(GET|POST|HEAD).*HTTP.*" 404
ignoreregex = .*(robots.txt|favicon.ico|\.well-known).*
```

````bash
# Filtro para proxy errors
sudo nano /etc/fail2ban/filter.d/nginx-proxy.conf
````

```ini
[Definition]
failregex = upstream timed out.*client: <HOST>
            no live upstreams.*client: <HOST>
            upstream prematurely closed connection.*client: <HOST>
ignoreregex =
```

## 🚀 Aplicar Configuración

```bash
# Reiniciar Fail2Ban para aplicar cambios
sudo systemctl restart fail2ban

# Verificar que los jails están activos
sudo fail2ban-client status

# Ver logs en tiempo real
sudo tail -f /var/log/fail2ban.log
```

## 📈 Monitoreo y Estadísticas

```bash
# Ver IPs baneadas en todos los jails
for jail in $(sudo fail2ban-client status | grep "Jail list" | sed 's/.*://; s/,//g'); do
    echo "=== $jail ==="
    sudo fail2ban-client get $jail banned
done

# Estadísticas de baneos
sudo fail2ban-client status nginx-req-limit | grep "Currently banned"

# Ver logs de baneos recientes
sudo grep "Ban" /var/log/fail2ban.log | tail -20
```

## ⚙️ Actualizar compose.yml de Nginx

Para que Fail2Ban pueda leer los logs, necesitas exponerlos:

```yaml
services:
  nginx:
    # ...existing code...
    volumes:
      # ...existing code...
      - ./logs:/var/log/nginx  # ← Añadir esto para que Fail2Ban lea los logs
```

Luego reinicia Nginx:

```bash
cd /home/dachival/serverComposes/nginx
docker compose up -d
```

## 🔗 Integración con tu script helper

Actualizar `fail2BanHelper.sh` para incluir comandos de Fail2Ban:

```bash
#!/bin/bash

BLOCKED_IPS="$HOME/serverComposes/nginx/conf.d/blocked-ips.conf"

case "$1" in
    ban)
        if [ -z "$2" ]; then
            echo "Uso: $0 ban <IP>"
            exit 1
        fi
        echo "deny $2;" >> "$BLOCKED_IPS"
        sudo fail2ban-client set nginx-req-limit banip "$2"
        echo "IP $2 bloqueada en Nginx y Fail2Ban"
        docker exec nginx nginx -s reload
        ;;
    unban)
        if [ -z "$2" ]; then
            echo "Uso: $0 unban <IP>"
            exit 1
        fi
        sed -i "/deny $2;/d" "$BLOCKED_IPS"
        sudo fail2ban-client set nginx-req-limit unbanip "$2"
        echo "IP $2 desbloqueada de Nginx y Fail2Ban"
        docker exec nginx nginx -s reload
        ;;
    list)
        echo "=== IPs Bloqueadas en Nginx ==="
        grep "deny" "$BLOCKED_IPS" 2>/dev/null || echo "No hay IPs bloqueadas"
        echo -e "\n=== IPs Baneadas por Fail2Ban ==="
        sudo fail2ban-client status nginx-req-limit | grep "Banned IP list"
        ;;
    jails)
        echo "=== Jails Activos de Fail2Ban ==="
        sudo fail2ban-client status
        ;;
    jail-status)
        if [ -z "$2" ]; then
            echo "Uso: $0 jail-status <NOMBRE_JAIL>"
            exit 1
        fi
        sudo fail2ban-client status "$2"
        ;;
    top-offenders)
        echo "=== Top 10 IPs con más requests (Nginx logs) ==="
        docker logs nginx 2>&1 | \
            grep "limiting" | \
            awk '{print $8}' | \
            sort | uniq -c | \
            sort -rn | \
            head -10
        ;;
    *)
        echo "Uso: $0 {ban|unban|list|jails|jail-status|top-offenders} [IP|JAIL]"
        exit 1
        ;;
esac
```

Dar permisos:

```bash
chmod +x /home/dachival/serverComposes/fail2BanHelper.sh
```

Uso:

```bash
# Ver todos los jails
./fail2BanHelper.sh jails

# Ver estado de un jail específico
./fail2BanHelper.sh jail-status nginx-req-limit

# Banear IP en ambos sistemas
./fail2BanHelper.sh ban 192.168.1.100

# Ver IPs bloqueadas
./fail2BanHelper.sh list
```
