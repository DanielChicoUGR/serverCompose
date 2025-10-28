#!/bin/bash

BLOCKED_IPS="$HOME/serverComposes/nginx/conf.d/blocked-ips.conf"

case "$1" in
    ban)
        if [ -z "$2" ]; then
            echo "Uso: $0 ban <IP>"
            exit 1
        fi
        echo "deny $2;" >> "$BLOCKED_IPS"
        echo "IP $2 bloqueada"
        docker exec nginx nginx -s reload
        ;;
    unban)
        if [ -z "$2" ]; then
            echo "Uso: $0 unban <IP>"
            exit 1
        fi
        sed -i "/deny $2;/d" "$BLOCKED_IPS"
        echo "IP $2 desbloqueada"
        docker exec nginx nginx -s reload
        ;;
    list)
        echo "=== IPs Bloqueadas ==="
        grep "deny" "$BLOCKED_IPS"
        ;;
    top-offenders)
        echo "=== Top 10 IPs con más requests ==="
        docker logs nginx 2>&1 | \
            grep "limiting" | \
            awk '{print $8}' | \
            sort | uniq -c | \
            sort -rn | \
            head -10
        ;;
    *)
        echo "Uso: $0 {ban|unban|list|top-offenders} [IP]"
        exit 1
        ;;
esac