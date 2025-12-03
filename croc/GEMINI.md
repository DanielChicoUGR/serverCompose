# GEMINI.md

## Project Overview

This project contains the configuration for running a Croc relay server using Docker and Docker Compose. Croc is a tool that allows you to securely transfer files and folders between two computers.

The setup is designed to be run behind a Traefik reverse proxy, as indicated by the labels in the `compose.yml` file, which configure TCP routing for the Croc relay.

## Building and Running

### Prerequisites
- Docker
- Docker Compose
- A running Traefik instance with TCP entrypoints for ports 9009-9013.

### Running the application
1. Create a `.env` file with the `CROC_PASS` variable (e.g., `CROC_PASS=yourpassword`).
2. Start the service using Docker Compose:
```bash
docker-compose up -d
```
3. The Croc relay will be running and accessible through the configured Traefik TCP entrypoints.

### Usage
To use the relay, you can use the `croc` command-line tool and specify the relay address and port. For example:
```bash
croc --relay your-server-address:9009 send my-file.txt
```

## Configuration

- The `compose.yml` file defines the Croc service and its Traefik configuration.
- The `CROC_PASS` environment variable is used to set the password for the relay.
