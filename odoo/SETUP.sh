#!/bin/bash

# Script de configuración inicial para Odoo
# Este script crea los archivos de secretos necesarios

set -e

echo "🔧 Configuración inicial de Odoo"
echo "================================"
echo ""

# Crear directorio de secretos si no existe
if [ ! -d "secrets" ]; then
    echo "📁 Creando directorio de secretos..."
    mkdir -p secrets
fi

# Generar contraseña de base de datos
if [ ! -f "secrets/db_password.txt" ]; then
    echo "🔐 Generando contraseña de base de datos..."
    openssl rand -base64 32 > secrets/db_password.txt
    chmod 600 secrets/db_password.txt
    echo "✅ Contraseña de base de datos generada en: secrets/db_password.txt"
else
    echo "⚠️  El archivo secrets/db_password.txt ya existe. No se sobrescribirá."
fi

# Generar master password de Odoo
if [ ! -f "secrets/odoo_master_password.txt" ]; then
    echo "🔐 Generando master password de Odoo..."
    openssl rand -base64 32 > secrets/odoo_master_password.txt
    chmod 600 secrets/odoo_master_password.txt
    echo "✅ Master password de Odoo generada en: secrets/odoo_master_password.txt"
else
    echo "⚠️  El archivo secrets/odoo_master_password.txt ya existe. No se sobrescribirá."
fi

# Crear directorio de addons si no existe
if [ ! -d "addons" ]; then
    echo "📁 Creando directorio de addons..."
    mkdir -p addons
fi

# Crear directorio de config si no existe
if [ ! -d "config" ]; then
    echo "📁 Creando directorio de config..."
    mkdir -p config
fi

# Copiar odoo.conf al directorio config si no existe
if [ ! -f "config/odoo.conf" ] && [ -f "odoo.conf" ]; then
    echo "📄 Copiando odoo.conf al directorio config..."
    cp odoo.conf config/odoo.conf
fi

echo ""
echo "✅ Configuración completada"
echo ""
echo "📝 Contraseñas generadas:"
echo "   - Base de datos: secrets/db_password.txt"
echo "   - Master password: secrets/odoo_master_password.txt"
echo ""
echo "⚠️  IMPORTANTE: Guarda estas contraseñas en un lugar seguro"
echo "   Puedes verlas con:"
echo "   cat secrets/db_password.txt"
echo "   cat secrets/odoo_master_password.txt"
echo ""
echo "🚀 Para iniciar Odoo, ejecuta:"
echo "   docker compose up -d"
echo ""
echo "🌐 Una vez iniciado, accede a:"
echo "   http://localhost:8069"
echo ""
