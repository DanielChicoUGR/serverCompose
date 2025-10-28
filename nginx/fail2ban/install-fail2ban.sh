#!/bin/bash
# ==============================================================================
# Script de Instalación de Configuraciones Fail2Ban para Nginx
# ==============================================================================
# Este script crea hard links de las configuraciones de Fail2Ban desde este
# directorio hacia las rutas del sistema (/etc/fail2ban/).
#
# Los hard links permiten que Fail2Ban lea las configuraciones mientras
# mantienes el control de versiones en tu repositorio.
#
# Uso:
#   sudo ./install-fail2ban.sh
#
# Requisitos:
#   - Fail2Ban instalado (apt install fail2ban)
#   - Permisos de root (sudo)
# ==============================================================================

set -e  # Salir si hay errores

# Colores para output
# Colores
RED='\e[31m'
GREEN='\e[32m'
YELLOW='\e[33m'
BLUE='\e[34m'
NC='\e[0m' # No Color

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JAIL_SOURCE_DIR="$SCRIPT_DIR/jail.d"
FILTER_SOURCE_DIR="$SCRIPT_DIR/filter.d"
FAIL2BAN_JAIL_DIR="/etc/fail2ban/jail.d"
FAIL2BAN_FILTER_DIR="/etc/fail2ban/filter.d"

# ==============================================================================
# Funciones de utilidad
# ==============================================================================

print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                          ║${NC}"
    echo -e "${BLUE}║   🛡️  Instalador de Configuración Fail2Ban para Nginx    ║${NC}"
    echo -e "${BLUE}║                                                          ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# ==============================================================================
# Verificaciones previas
# ==============================================================================

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Este script debe ejecutarse con sudo"
        echo "Uso: sudo ./install-fail2ban.sh"
        exit 1
    fi
    print_success "Permisos de root verificados"
}

check_fail2ban_installed() {
    if ! command -v fail2ban-client &> /dev/null; then
        print_error "Fail2Ban no está instalado"
        echo ""
        echo "Instálalo con:"
        echo "  sudo apt update"
        echo "  sudo apt install fail2ban -y"
        exit 1
    fi
    print_success "Fail2Ban está instalado"
}

check_directories_exist() {
    if [[ ! -d "$FAIL2BAN_JAIL_DIR" ]]; then
        print_error "Directorio $FAIL2BAN_JAIL_DIR no existe"
        exit 1
    fi
    
    if [[ ! -d "$FAIL2BAN_FILTER_DIR" ]]; then
        print_error "Directorio $FAIL2BAN_FILTER_DIR no existe"
        exit 1
    fi
    
    print_success "Directorios de Fail2Ban verificados"
}

# ==============================================================================
# Funciones de instalación
# ==============================================================================

remove_old_links() {
    print_info "Eliminando configuraciones antiguas..."
    
    # Eliminar jails antiguos
    if [[ -f "$FAIL2BAN_JAIL_DIR/nginx-custom.conf" ]]; then
        rm -f "$FAIL2BAN_JAIL_DIR/nginx-custom.conf"
        print_success "Jail anterior eliminado"
    fi
    
    # Eliminar filtros antiguos
    for filter in nginx-req-limit nginx-login nginx-404 nginx-proxy; do
        if [[ -f "$FAIL2BAN_FILTER_DIR/${filter}.conf" ]]; then
            rm -f "$FAIL2BAN_FILTER_DIR/${filter}.conf"
            print_success "Filtro $filter anterior eliminado"
        fi
    done
}

create_hard_links() {
    print_info "Creando hard links de configuraciones..."
    echo ""
    
    # Crear hard link del jail
    local jail_file="$JAIL_SOURCE_DIR/nginx-custom.conf"
    if [[ -f "$jail_file" ]]; then
        ln -f "$jail_file" "$FAIL2BAN_JAIL_DIR/nginx-custom.conf"
        chmod 644 "$FAIL2BAN_JAIL_DIR/nginx-custom.conf"
        print_success "Jail creado: $FAIL2BAN_JAIL_DIR/nginx-custom.conf"
    else
        print_error "No se encontró $jail_file"
        exit 1
    fi
    
    echo ""
    
    # Crear hard links de los filtros
    for filter in nginx-req-limit nginx-login nginx-404 nginx-proxy; do
        local filter_file="$FILTER_SOURCE_DIR/${filter}.conf"
        if [[ -f "$filter_file" ]]; then
            ln -f "$filter_file" "$FAIL2BAN_FILTER_DIR/${filter}.conf"
            chmod 644 "$FAIL2BAN_FILTER_DIR/${filter}.conf"
            print_success "Filtro creado: $FAIL2BAN_FILTER_DIR/${filter}.conf"
        else
            print_warning "No se encontró $filter_file"
        fi
    done
}

test_configuration() {
    print_info "Verificando configuración de Fail2Ban..."
    
    if fail2ban-client -t &> /dev/null; then
        print_success "Configuración válida"
        return 0
    else
        print_error "La configuración tiene errores"
        echo ""
        echo "Ejecuta esto para ver detalles:"
        echo "  sudo fail2ban-client -t"
        return 1
    fi
}

restart_fail2ban() {
    print_info "Reiniciando Fail2Ban..."
    
    if systemctl restart fail2ban; then
        print_success "Fail2Ban reiniciado correctamente"
        sleep 2  # Esperar a que se inicialicen los jails
    else
        print_error "Error al reiniciar Fail2Ban"
        exit 1
    fi
}

show_status() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                   Estado de Jails                        ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    fail2ban-client status
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ Instalación completada exitosamente${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

show_next_steps() {
    echo -e "${YELLOW}📋 Próximos pasos:${NC}"
    echo ""
    echo "1. Verificar estado de un jail específico:"
    echo "   ${BLUE}sudo fail2ban-client status nginx-req-limit${NC}"
    echo ""
    echo "2. Ver IPs baneadas:"
    echo "   ${BLUE}sudo fail2ban-client get nginx-req-limit banned${NC}"
    echo ""
    echo "3. Monitorear logs en tiempo real:"
    echo "   ${BLUE}sudo tail -f /var/log/fail2ban.log${NC}"
    echo ""
    echo "4. Ver logs de Nginx:"
    echo "   ${BLUE}tail -f $SCRIPT_DIR/../logs/error.log${NC}"
    echo "   ${BLUE}tail -f $SCRIPT_DIR/../logs/access.log${NC}"
    echo ""
    echo "5. Usar el helper script mejorado:"
    echo "   ${BLUE}./fail2BanHelper.sh jails${NC}"
    echo "   ${BLUE}./fail2BanHelper.sh jail-status nginx-req-limit${NC}"
    echo ""
}

# ==============================================================================
# Main
# ==============================================================================

main() {
    print_header
    
    # Verificaciones
    check_root
    check_fail2ban_installed
    check_directories_exist
    
    echo ""
    
    # Instalación
    remove_old_links
    echo ""
    create_hard_links
    echo ""
    
    # Verificación
    if ! test_configuration; then
        exit 1
    fi
    
    echo ""
    
    # Reiniciar servicio
    restart_fail2ban
    
    # Mostrar estado
    show_status
    
    # Próximos pasos
    show_next_steps
}

# Ejecutar script principal
main "$@"
