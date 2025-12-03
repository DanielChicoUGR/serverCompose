# GEMINI.md

## Project Overview

This project contains the configuration for running a Kestra instance using Docker and Docker Compose. It sets up two main services: the Kestra application itself and a PostgreSQL database.

The setup is designed to be run behind a Traefik reverse proxy, as indicated by the labels in the `compose.yml` file, which configure routing for `kestra.hmbcentral.live`.

## Building and Running

### Prerequisites
- Docker
- Docker Compose
- A running Traefik instance connected to the `nginx_proxy` external network.
- A `.env` file with the required environment variables (see `.env.example`).

### Running the application
1. Create a `.env` file from the `.env.example` and fill in the values for `ADMIN_MAIL` and `ADMIN_PSW`.
2. Start the services using Docker Compose:
```bash
docker-compose up -d
```
3. The Kestra instance will be available at the host configured in `compose.yml` (e.g., `https://kestra.hmbcentral.live`).

### Stopping the application
```bash
docker-compose down
```
