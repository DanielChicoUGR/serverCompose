# GEMINI.md

## Project Overview

This project contains the configuration for running an n8n instance using Docker and Docker Compose. It sets up two main services: the n8n application itself and a PostgreSQL database.

The setup is designed to be run behind a Traefik reverse proxy, as indicated by the labels in the `compose.yml` file, which configure routing for `n8n.hmbcentral.live`.

The directory structure is organized as follows:
- `local-files/`: A directory for local files that can be accessed by n8n workflows.
- `compose.yml`: The Docker Compose file that defines the services.

## Building and Running

### Prerequisites
- Docker
- Docker Compose
- A running Traefik instance connected to the `nginx_proxy` external network.

### Running the application
1. Start the services using Docker Compose:
```bash
docker-compose up -d
```
2. The n8n instance will be available at the host configured in `compose.yml` (e.g., `https://n8n.hmbcentral.live`).

### Stopping the application
```bash
docker-compose down
```

## Development Conventions

- Files that need to be accessed by n8n workflows can be placed in the `local-files/` directory.
- Environment variables for database connections and other settings are managed in the `compose.yml` file.
