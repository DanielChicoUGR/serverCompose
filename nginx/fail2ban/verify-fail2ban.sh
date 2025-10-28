#!/bin/bash
# ==============================================================================
# Script de Verificación Rápida - Fail2Ban + Nginx
# ==============================================================================
# Verifica el estado de Fail2Ban, Nginx y las protecciones configuradas.
#
# Uso:
#   ./verify-fail2ban.sh
# ==============================================================================

# Colores
RED='\e[31m'
GREEN='\e[32m'
YELLOW='\e[33m'
BLUE='\e[34m'
NC='\e[0m' # No Color
print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  $1${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
}

print_success() {
    echo -e "  ${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "  ${RED}✗${NC} $1"
}

print_warning() {
    echo -e "  ${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "  ${BLUE}ℹ${NC} $1"
}

# ==============================================================================
# Verificaciones
# ==============================================================================

echo ""
print_header "     Verificación de Fail2Ban y Nginx     "
echo ""

# 1. Verificar Fail2Ban instalado
print_info "Verificando instalación de Fail2Ban..."
if command -v fail2ban-client &> /dev/null; then
    print_success "Fail2Ban está instalado"
    VERSION=$(fail2ban-client version 2>/dev/null | head -1)
    echo "    Versión: $VERSION"
else
    print_error "Fail2Ban NO está instalado"
    echo ""
    echo "    Instalar con: sudo apt install fail2ban -y"
fi

echo ""

# 2. Verificar servicio activo
print_info "Verificando servicio Fail2Ban..."
if systemctl is-active --quiet fail2ban; then
    print_success "Servicio Fail2Ban activo"
else
    print_error "Servicio Fail2Ban NO está activo"
    echo ""
    echo "    Iniciar con: sudo systemctl start fail2ban"
fi

echo ""

# 3. Verificar jails configurados
print_info "Verificando jails configurados..."
if [[ -f /etc/fail2ban/jail.d/nginx-custom.conf ]]; then
    print_success "Archivo de jails encontrado"
    
    # Verificar que los jails estén activos
    for jail in nginx-req-limit nginx-login-abuse nginx-404 nginx-proxy; do
        if sudo fail2ban-client status "$jail" &> /dev/null; then
            print_success "Jail activo: $jail"
        else
            print_warning "Jail NO activo: $jail"
        fi
    done
else
    print_error "Archivo de jails NO encontrado"
    echo ""
    echo "    Instalar con: cd fail2ban && sudo ./install-fail2ban.sh"
fi

echo ""

# 4. Verificar filtros
print_info "Verificando filtros..."
FILTERS=("nginx-req-limit" "nginx-login" "nginx-404" "nginx-proxy")
for filter in "${FILTERS[@]}"; do
    if [[ -f "/etc/fail2ban/filter.d/${filter}.conf" ]]; then
        print_success "Filtro encontrado: ${filter}.conf"
    else
        print_warning "Filtro NO encontrado: ${filter}.conf"
    fi
done

echo ""

# 5. Verificar logs de Nginx accesibles
print_info "Verificando logs de Nginx..."
print_info $(dirname "$0")
NGINX_LOGS_DIR="$(dirname "$0")/logs"
if [[ -f "$NGINX_LOGS_DIR/error.log" ]]; then
    print_success "Log de error encontrado"
    LINES=$(wc -l < "$NGINX_LOGS_DIR/error.log")
    echo "    Líneas: $LINES"
else
    print_warning "Log de error NO encontrado"
fi

if [[ -f "$NGINX_LOGS_DIR/access.log" ]]; then
    print_success "Log de acceso encontrado"
    LINES=$(wc -l < "$NGINX_LOGS_DIR/access.log")
    echo "    Líneas: $LINES"
else
    print_warning "Log de acceso NO encontrado"
fi

echo ""

# 6. Verificar contenedor Nginx
print_info "Verificando contenedor Nginx..."
if docker ps --format '{{.Names}}' | grep -q "^nginx$"; then
    print_success "Contenedor Nginx corriendo"
    
    # Verificar configuración
    if docker exec nginx nginx -t &> /dev/null; then
        print_success "Configuración de Nginx válida"
    else
        print_error "Configuración de Nginx tiene errores"
        echo ""
        echo "    Verificar con: docker exec nginx nginx -t"
    fi
else
    print_warning "Contenedor Nginx NO está corriendo"
    echo ""
    echo "    Iniciar con: docker compose up -d"
fi

echo ""

# 7. Estadísticas de baneos
if command -v fail2ban-client &> /dev/null && systemctl is-active --quiet fail2ban; then
    print_header "         Estadísticas de Baneos         "
    echo ""
    
    TOTAL_BANNED=0
    for jail in nginx-req-limit nginx-login-abuse nginx-404 nginx-proxy; do
        if sudo fail2ban-client status "$jail" &> /dev/null; then
            BANNED=$(sudo fail2ban-client get "$jail" banned 2>/dev/null | wc -w)
            TOTAL_BANNED=$((TOTAL_BANNED + BANNED))
            echo -e "  ${BLUE}[$jail]${NC} → $BANNED IPs baneadas"
        fi
    done
    
    echo ""
    echo -e "  ${GREEN}Total:${NC} $TOTAL_BANNED IPs baneadas en todos los jails"
    echo ""
fi

# 8. Resumen final
print_header "              Resumen Final              "
echo ""

# Contar estados
OK=0
WARN=0
ERROR=0

# Check Fail2Ban
if command -v fail2ban-client &> /dev/null; then
    ((OK++))
else
    ((ERROR++))
fi

# Check servicio
if systemctl is-active --quiet fail2ban; then
    ((OK++))
else
    ((ERROR++))
fi

# Check jails
if [[ -f /etc/fail2ban/jail.d/nginx-custom.conf ]]; then
    ((OK++))
else
    ((WARN++))
fi

# Check Nginx
if docker ps --format '{{.Names}}' | grep -q "^nginx$"; then
    ((OK++))
else
    ((WARN++))
fi

echo -e "  ${GREEN}✓ Verificaciones exitosas:${NC} $OK"
echo -e "  ${YELLOW}⚠ Advertencias:${NC} $WARN"
echo -e "  ${RED}✗ Errores:${NC} $ERROR"

echo ""

# Comandos útiles
print_header "           Comandos Útiles            "
echo ""
echo "  Ver estado de jails:"
echo -e "    ${BLUE}sudo fail2ban-client status${NC}"
echo ""
echo "  Ver jail específico:"
echo -e "    ${BLUE}sudo fail2ban-client status nginx-req-limit${NC}"
echo ""
echo "  Ver logs de Fail2Ban:"
echo -e "    ${BLUE}sudo tail -f /var/log/fail2ban.log${NC}"
echo ""
echo "  Usar helper script:"
echo -e "    ${BLUE}../fail2BanHelper.sh help${NC}"
echo ""
