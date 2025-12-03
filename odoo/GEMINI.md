# GEMINI.md

## Project Overview

This project contains the configuration for running an Odoo 18 instance using Docker and Docker Compose. It sets up two main services: the Odoo application itself and a PostgreSQL database.

The setup is designed to be run behind a Traefik reverse proxy, as indicated by the labels in the `compose.yml` file, which configure routing for `erp.hmbcentral.live`.

The directory structure is organized as follows:
- `addons/`: For custom Odoo modules.
- `config/`: Contains the `odoo.conf` file for Odoo's server configuration.
- `odoo-db-data/`: Persists the PostgreSQL database data.
- `odoo-web-data/`: Persists Odoo's application data.

## Building and Running

### Prerequisites
- Docker
- Docker Compose
- A running Traefik instance connected to the `nginx_proxy` external network.
- A `.env` file with the required environment variables (see `.env.example`).

### Running the application
1. Create a `.env` file from the `.env.example` and fill in the values, especially `ADMIN_PASSWD`.
2. Start the services using Docker Compose:
```bash
docker-compose up -d
```
3. The Odoo instance will be available at the host configured in `compose.yml` (e.g., `http://erp.hmbcentral.live`).

### Stopping the application
```bash
docker-compose down
```

## Development Conventions

- Custom Odoo modules should be placed in the `addons/` directory. They will be automatically mounted into the Odoo container.
- Odoo's server configuration can be modified in `config/odoo.conf`.
- Environment variables for database connections and other secrets are managed in the `compose.yml` and `.env` file.