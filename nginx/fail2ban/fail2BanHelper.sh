#!/bin/bash
# ==============================================================================
# Fail2Ban Helper Script
# ==============================================================================
# Script mejorado para gestionar IPs bloqueadas en Nginx y Fail2Ban
#
# Uso:
#   ./fail2BanHelper.sh {ban|unban|list|jails|jail-status|top-offenders} [ARGS]
#
# Ejemplos:
#   ./fail2BanHelper.sh ban 192.168.1.100
#   ./fail2BanHelper.sh list
#   ./fail2BanHelper.sh jails
#   ./fail2BanHelper.sh jail-status nginx-req-limit
#   ./fail2BanHelper.sh top-offenders
# ==============================================================================

# Configuración
BLOCKED_IPS="$HOME/Proyectos/serverCompose/nginx/conf.d/blocked-ips.conf"
NGINX_CONTAINER="nginx"

# Colores
RED='\e[31m'
GREEN='\e[32m'
YELLOW='\e[33m'
BLUE='\e[34m'
NC='\e[0m' # No Color

# ==============================================================================
# Funciones auxiliares
# ==============================================================================

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

check_fail2ban() {
    if ! command -v fail2ban-client &> /dev/null; then
        print_error "Fail2Ban no está instalado"
        return 1
    fi
    return 0
}

# ==============================================================================
# Comandos principales
# ==============================================================================

cmd_ban() {
    local ip="$1"
    
    if [[ -z "$ip" ]]; then
        print_error "Uso: $0 ban <IP>"
        exit 1
    fi
    
    print_info "Bloqueando IP: $ip"
    echo ""
    
    # Añadir a Nginx
    echo "deny $ip;" >> "$BLOCKED_IPS"
    print_success "IP añadida a Nginx: $BLOCKED_IPS"
    
    # Añadir a Fail2Ban si está disponible
    if check_fail2ban; then
        for jail in nginx-req-limit nginx-login-abuse nginx-404 nginx-proxy; do
            if sudo fail2ban-client status "$jail" &> /dev/null; then
                sudo fail2ban-client set "$jail" banip "$ip" &> /dev/null
                print_success "IP baneada en jail: $jail"
            fi
        done
    fi
    
    # Recargar Nginx
    docker exec "$NGINX_CONTAINER" nginx -s reload &> /dev/null
    print_success "Nginx recargado"
    
    echo ""
    print_success "IP $ip bloqueada completamente"
}

cmd_unban() {
    local ip="$1"
    
    if [[ -z "$ip" ]]; then
        print_error "Uso: $0 unban <IP>"
        exit 1
    fi
    
    print_info "Desbloqueando IP: $ip"
    echo ""
    
    # Remover de Nginx
    sed -i "/deny $ip;/d" "$BLOCKED_IPS"
    print_success "IP removida de Nginx"
    
    # Remover de Fail2Ban si está disponible
    if check_fail2ban; then
        for jail in nginx-req-limit nginx-login-abuse nginx-404 nginx-proxy; do
            if sudo fail2ban-client status "$jail" &> /dev/null; then
                sudo fail2ban-client set "$jail" unbanip "$ip" &> /dev/null
                print_success "IP desbaneada de jail: $jail"
            fi
        done
    fi
    
    # Recargar Nginx
    docker exec "$NGINX_CONTAINER" nginx -s reload &> /dev/null
    print_success "Nginx recargado"
    
    echo ""
    print_success "IP $ip desbloqueada completamente"
}

cmd_list() {
    print_header "IPs Bloqueadas"
    echo ""
    
    # Listar IPs en Nginx
    echo -e "${YELLOW}📋 IPs bloqueadas en Nginx:${NC}"
    if [[ -f "$BLOCKED_IPS" ]] && grep -q "deny" "$BLOCKED_IPS" 2>/dev/null; then
        grep "deny" "$BLOCKED_IPS" | sed 's/deny //;s/;//' | while read -r ip; do
            echo "  • $ip"
        done
    else
        echo "  (ninguna)"
    fi
    
    echo ""
    
    # Listar IPs baneadas por Fail2Ban
    if check_fail2ban; then
        echo -e "${YELLOW}🛡️  IPs baneadas por Fail2Ban:${NC}"
        for jail in nginx-req-limit nginx-login-abuse nginx-404 nginx-proxy; do
            if sudo fail2ban-client status "$jail" &> /dev/null; then
                banned=$(sudo fail2ban-client get "$jail" banned 2>/dev/null)
                if [[ -n "$banned" ]]; then
                    echo "  [$jail]"
                    echo "    $banned" | sed 's/ / \n    /g'
                fi
            fi
        done
    fi
    
    echo ""
}

cmd_jails() {
    if ! check_fail2ban; then
        exit 1
    fi
    
    print_header "Estado de Fail2Ban"
    echo ""
    
    sudo fail2ban-client status
    
    echo ""
}

cmd_jail_status() {
    local jail="$1"
    
    if ! check_fail2ban; then
        exit 1
    fi
    
    if [[ -z "$jail" ]]; then
        print_error "Uso: $0 jail-status <NOMBRE_JAIL>"
        echo ""
        echo "Jails disponibles:"
        echo "  • nginx-req-limit"
        echo "  • nginx-login-abuse"
        echo "  • nginx-404"
        echo "  • nginx-proxy"
        exit 1
    fi
    
    print_header "Estado del Jail: $jail"
    echo ""
    
    sudo fail2ban-client status "$jail"
    
    echo ""
}

cmd_top_offenders() {
    print_header "Top 10 IPs con más Requests Limitados"
    echo ""
    
    if docker logs "$NGINX_CONTAINER" 2>&1 | grep -q "limiting"; then
        docker logs "$NGINX_CONTAINER" 2>&1 | \
            grep "limiting" | \
            grep -oP 'client: \K[0-9.]+' | \
            sort | uniq -c | \
            sort -rn | \
            head -10 | \
            while read -r count ip; do
                echo "  $count requests → $ip"
            done
    else
        echo "  No se encontraron requests limitados"
    fi
    
    echo ""
}

cmd_logs() {
    local log_type="${1:-fail2ban}"
    
    case "$log_type" in
        fail2ban|f2b)
            print_info "Mostrando logs de Fail2Ban (últimas 50 líneas)"
            echo ""
            sudo tail -50 /var/log/fail2ban.log
            ;;
        nginx-error|error)
            print_info "Mostrando logs de error de Nginx (últimas 50 líneas)"
            echo ""
            tail -50 "$HOME/Proyectos/serverCompose/nginx/logs/error.log"
            ;;
        nginx-access|access)
            print_info "Mostrando logs de acceso de Nginx (últimas 50 líneas)"
            echo ""
            tail -50 "$HOME/Proyectos/serverCompose/nginx/logs/access.log"
            ;;
        *)
            print_error "Tipo de log desconocido: $log_type"
            echo "Tipos disponibles: fail2ban, nginx-error, nginx-access"
            exit 1
            ;;
    esac
}

cmd_stats() {
    print_header "Estadísticas de Fail2Ban"
    echo ""
    
    if ! check_fail2ban; then
        exit 1
    fi
    
    for jail in nginx-req-limit nginx-login-abuse nginx-404 nginx-proxy; do
        if sudo fail2ban-client status "$jail" &> /dev/null; then
            total=$(sudo fail2ban-client status "$jail" | grep "Currently banned" | awk '{print $4}')
            echo -e "${BLUE}[$jail]${NC}"
            echo "  IPs baneadas actualmente: $total"
            
            # Obtener fecha del último baneo
            if [[ -f /var/log/fail2ban.log ]]; then
                last_ban=$(sudo grep "Ban $jail" /var/log/fail2ban.log | tail -1)
                if [[ -n "$last_ban" ]]; then
                    echo "  Último baneo: $(echo "$last_ban" | awk '{print $1, $2}')"
                fi
            fi
            
            echo ""
        fi
    done
}

show_help() {
    echo -e "
${BLUE}╔══════════════════════════════════════════════════════════╗${NC}
${BLUE}║          Fail2Ban Helper - Sistema de Ayuda              ║${NC}
${BLUE}╚══════════════════════════════════════════════════════════╝${NC}

${YELLOW}Comandos disponibles:${NC}

  ${GREEN}ban${NC} <IP>
    Bloquea una IP en Nginx y Fail2Ban
    Ejemplo: $0 ban 192.168.1.100

  ${GREEN}unban${NC} <IP>
    Desbloquea una IP de Nginx y Fail2Ban
    Ejemplo: $0 unban 192.168.1.100

  ${GREEN}list${NC}
    Muestra todas las IPs bloqueadas

  ${GREEN}jails${NC}
    Muestra el estado de todos los jails de Fail2Ban

  ${GREEN}jail-status${NC} <NOMBRE_JAIL>
    Muestra el estado detallado de un jail específico
    Ejemplo: $0 jail-status nginx-req-limit

  ${GREEN}top-offenders${NC}
    Muestra las 10 IPs con más requests limitados

  ${GREEN}logs${NC} [tipo]
    Muestra logs recientes
    Tipos: fail2ban, nginx-error, nginx-access
    Ejemplo: $0 logs fail2ban

  ${GREEN}stats${NC}
    Muestra estadísticas de todos los jails

  ${GREEN}help${NC}
    Muestra esta ayuda

${YELLOW}Jails disponibles:${NC}
  • nginx-req-limit     (Rate limiting general)
  • nginx-login-abuse   (Abuso de login)
  • nginx-404           (Escaneo 404)
  • nginx-proxy         (Errores de proxy)
"
}

# ==============================================================================
# Main
# ==============================================================================

case "$1" in
    ban)
        cmd_ban "$2"
        ;;
    unban)
        cmd_unban "$2"
        ;;
    list)
        cmd_list
        ;;
    jails)
        cmd_jails
        ;;
    jail-status)
        cmd_jail_status "$2"
        ;;
    top-offenders)
        cmd_top_offenders
        ;;
    logs)
        cmd_logs "$2"
        ;;
    stats)
        cmd_stats
        ;;
    help|--help|-h)
    
        show_help
        ;;
    *)
        print_error "Comando desconocido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac