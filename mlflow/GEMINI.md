# Project Overview

This directory contains a Docker Compose setup for running MLflow locally. It uses a PostgreSQL database as the backend store for MLflow's metadata and a MinIO server for artifact storage. This setup is intended for local development and evaluation of MLflow.

The main components are:
- **MLflow Tracking Server:** The main MLflow server, accessible on `http://localhost:5000` by default.
- **PostgreSQL:** A PostgreSQL database for persisting MLflow's metadata, such as experiments, runs, parameters, and metrics.
- **MinIO:** An S3-compatible object storage server for storing run artifacts.

## Building and Running

### Prerequisites
- Docker
- Docker Compose

### 1. Configure Environment
Before launching the stack, you need to create a `.env` file. You can do this by copying the example file:
```bash
cp .env.dev.example .env
```
The `.env` file contains all the configuration variables for the services, such as ports, credentials, and storage settings. You can modify this file to suit your needs.

### 2. Launch the Stack
To start all the services, run the following command:
```bash
docker-compose up -d
```
This command will build or pull the necessary Docker images, create a network, and start the `postgres`, `minio`, and `mlflow` containers in the background.

You can check the status of the containers using:
```bash
docker-compose ps
```

### 3. Access MLflow
Once the stack is running, you can access the MLflow UI in your web browser at:
[http://localhost:5000](http://localhost:5000)

### 4. Shutdown
To stop and remove the containers and network, run:
```bash
docker-compose down
```
If you also want to remove the data volumes, which is an irreversible action, use the `-v` flag:
```bash
docker-compose down -v
```

## Development Conventions

The project uses a `.env` file for configuration, which is a common practice for Docker-based applications. The `docker-compose.yml` file is well-structured and uses environment variables to make it easily configurable.

The services are designed to work together on a shared network, and the MLflow service depends on the PostgreSQL and MinIO services being healthy before it starts. This ensures a proper startup order.

The MLflow server is configured to use the PostgreSQL database for its backend store and the MinIO server for artifact storage. The `create-bucket` service is a one-off job that creates the necessary bucket in MinIO before the MLflow server starts.
