# GEMINI.md

## Project Overview

This repository contains a collection of Docker Compose projects that are managed by a central Traefik reverse proxy. Each subdirectory represents a distinct service or application that is containerized and configured to be accessible through the Traefik proxy.

The main components are:
- **Traefik:** The reverse proxy that routes traffic to the various services based on hostname.
- **Odoo:** An Odoo 18 instance with a PostgreSQL database.
- **Nginx:** An Nginx server for hosting static websites.
- **MLflow:** A platform for the machine learning lifecycle.
- **Other services:** The repository also contains configurations for `croc` and `n8n`.

## Architecture

The services are connected through a Docker network named `nginx_proxy`. Traefik is configured to watch this network and automatically discover and route traffic to the services that have the appropriate labels in their `compose.yml` files.

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Running the services
Each service can be started individually by running `docker-compose up -d` in its respective directory.

**1. Start Traefik:**
```bash
cd traefik
docker-compose up -d
```

**2. Start other services:**
For example, to start the Odoo service:
```bash
cd odoo19
docker-compose up -d
```
The same process applies to the other services in this repository.

## Services

### Traefik
- **Directory:** `traefik/`
- **Configuration:** `traefik/compose.yml` and `traefik/config.yml`
- **Dashboard:** Accessible at `traefik.hmbcentral.live` (with basic auth).

### Odoo
- **Directory:** `odoo19/`
- **Description:** An Odoo 18 instance.

### Nginx
- **Directory:** `nginx/`
- **Description:** An Nginx server for static content. The personal website (`dachival`) is hosted here.
- **Configuration:** `nginx/compose.yml` and `nginx/nginx.conf`.
- **Content:** The static files are located in the `nginx/webs` directory.

### MLflow
- **Directory:** `mlflow/`
- **Description:** A platform for the machine learning lifecycle.
- **Details:** See `mlflow/GEMINI.md` for more information.

### Other Services
- **`croc/`**: Configuration for the `croc` file transfer service.
- **`n8n/`**: Configuration for the `n8n` workflow automation tool.
