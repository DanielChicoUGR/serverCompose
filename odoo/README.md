# Odoo 19 con PostgreSQL 18

Configuración de Docker Compose para ejecutar Odoo 19 con PostgreSQL 18, utilizando Docker secrets para gestionar las contraseñas de forma segura.

## 📋 Requisitos

- Docker Engine 20.10+
- Docker Compose v2.0+

## 🔐 Configuración de Secretos

Antes de iniciar los contenedores, debes crear los archivos de secretos:

### 1. Crear el directorio de secretos

```bash
mkdir -p secrets
```

### 2. Crear el archivo de contraseña de la base de datos

```bash
# Generar una contraseña segura aleatoria
openssl rand -base64 32 > secrets/db_password.txt

# O establecer una contraseña manualmente
echo "tu_contraseña_db_segura" > secrets/db_password.txt
```

### 3. Crear el archivo de master password de Odoo

```bash
# Generar una contraseña segura aleatoria
openssl rand -base64 32 > secrets/odoo_master_password.txt

# O establecer una contraseña manualmente
echo "tu_contraseña_maestra_odoo" > secrets/odoo_master_password.txt
```

### 4. Proteger los archivos de secretos

```bash
chmod 600 secrets/*.txt
```

## 🚀 Uso

### Iniciar los servicios

```bash
docker compose up -d
```

### Ver logs

```bash
# Todos los servicios
docker compose logs -f

# Solo Odoo
docker compose logs -f odoo

# Solo PostgreSQL
docker compose logs -f db
```

### Detener los servicios

```bash
docker compose down
```

### Detener y eliminar volúmenes (⚠️ elimina todos los datos)

```bash
docker compose down -v
```

## 🌐 Acceso

Una vez iniciados los servicios, Odoo estará disponible en:

- **URL**: http://localhost:8069
- **Usuario inicial**: admin
- **Contraseña inicial**: admin (cambiar en el primer acceso)

### Primera configuración

1. Accede a http://localhost:8069
2. Crea una nueva base de datos:
   - **Nombre de la base de datos**: Elige un nombre (ej: `odoo_prod`)
   - **Email**: Tu correo electrónico (será el usuario admin)
   - **Contraseña**: Contraseña para el usuario admin
   - **Master Password**: Usa la contraseña del archivo `secrets/odoo_master_password.txt`

## 📁 Estructura de Directorios

```
odoo/
├── compose.yml                    # Configuración de Docker Compose
├── odoo.conf                      # Configuración de Odoo
├── .env.example                   # Ejemplo de variables de entorno
├── .gitignore                     # Archivos a ignorar en git
├── README.md                      # Este archivo
├── secrets/                       # Contraseñas (NO commitear)
│   ├── db_password.txt           # Contraseña de PostgreSQL
│   └── odoo_master_password.txt  # Master password de Odoo
├── config/                        # Configuraciones adicionales
│   └── odoo.conf                 # Enlace simbólico o copia
└── addons/                        # Módulos personalizados de Odoo
    └── .gitkeep
```

## 🔧 Configuración

### Archivo odoo.conf

El archivo `odoo.conf` contiene la configuración principal de Odoo. Puedes ajustar:

- **Workers**: Número de workers (recomendado: CPU \* 2 + 1)
- **Timeouts**: Límites de tiempo de ejecución
- **Memoria**: Límites de memoria
- **Logging**: Nivel de log y destino
- **Proxy**: Configuración para proxy inverso

### Variables de entorno

Puedes crear un archivo `.env` basado en `.env.example` para personalizar:

- Puertos de exposición
- Número de workers
- Otras configuraciones

## 📦 Volúmenes

- `odoo-web-data`: Datos de Odoo (filestore, sessions, etc.)
- `odoo-db-data`: Datos de PostgreSQL
- `./config`: Archivos de configuración montados
- `./addons`: Módulos personalizados de Odoo

## 🔄 Actualización

Para actualizar a una nueva versión de Odoo:

```bash
# Detener los servicios
docker compose down

# Hacer backup de los datos
docker run --rm -v odoo-db-data:/data -v $(pwd)/backup:/backup ubuntu tar czf /backup/db-backup-$(date +%Y%m%d).tar.gz /data

# Actualizar la imagen en compose.yml (cambiar versión)
# Después ejecutar:
docker compose pull
docker compose up -d
```

## 🐛 Troubleshooting

### El contenedor de Odoo no inicia

```bash
# Verificar logs
docker compose logs odoo

# Verificar que PostgreSQL esté healthy
docker compose ps
```

### Error de conexión a la base de datos

```bash
# Verificar que el archivo de secreto existe y tiene contenido
cat secrets/db_password.txt

# Verificar que PostgreSQL esté ejecutándose
docker compose exec db pg_isready -U odoo
```

### Cambiar la master password

1. Detener Odoo: `docker compose stop odoo`
2. Modificar el archivo: `echo "nueva_contraseña" > secrets/odoo_master_password.txt`
3. Iniciar Odoo: `docker compose start odoo`

## 🔒 Seguridad

- ⚠️ **NUNCA** commitees los archivos de `secrets/` a git
- ⚠️ Cambia la contraseña del usuario admin después del primer acceso
- ⚠️ Usa contraseñas fuertes y únicas
- 📝 Considera usar un gestor de secretos en producción (Vault, AWS Secrets Manager, etc.)
- 🔥 En producción, usa un proxy inverso (nginx) con HTTPS
- 🛡️ Configura `list_db = False` en `odoo.conf` para ocultar el listado de bases de datos

## 📚 Recursos

- [Documentación oficial de Odoo](https://www.odoo.com/documentation/19.0/)
- [Odoo en Docker Hub](https://hub.docker.com/_/odoo)
- [PostgreSQL 18 Documentation](https://www.postgresql.org/docs/18/)

## 🆘 Comandos útiles

```bash
# Acceder al contenedor de Odoo
docker compose exec odoo bash

# Acceder a PostgreSQL
docker compose exec db psql -U odoo

# Ver bases de datos en PostgreSQL
docker compose exec db psql -U odoo -c "\l"

# Backup de una base de datos específica
docker compose exec db pg_dump -U odoo nombre_base > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker compose exec -T db psql -U odoo nombre_base < backup.sql

# Ver uso de recursos
docker stats odoo_app odoo_db
```
