# GEMINI.md

## Project Overview

This directory contains the configuration for running a Psono Enterprise Edition (Combo) instance using Docker and Docker Compose. It includes a PostgreSQL database and the Psono service itself, configured to run behind the central Traefik reverse proxy.

## Architecture

- **Service:** `psono` (Psono Combo)
- **Database:** `psono-db` (PostgreSQL 13)
- **Network:** Connects to `nginx_proxy` for Traefik routing and `psono_backend` for internal database communication.
- **URL:** Configured for `psono.hmbcentral.live`.

## Setup Instructions (IMPORTANT)

**This setup requires manual initialization before it can be started.**

1.  **Environment Variables:**
    Copy `.env.example` to `.env` and set a secure password for the database.
    ```bash
    cp .env.example .env
    # Edit .env and change POSTGRES_PASSWORD
    ```

2.  **Generate Keys & Certificates:**
    Psono requires cryptographic keys to function. You must generate these and update `settings.yaml`.
    
    *   **Secret Key:** Generate a random string.
    *   **Private/Public Keys:** Generate an RSA key pair.
    
    You can typically do this by running a temporary Psono container or using OpenSSL.
    
    Example using OpenSSL:
    ```bash
    openssl genrsa -out private.pem 2048
    openssl rsa -in private.pem -pubout -out public.pem
    ```
    Paste the contents into `settings.yaml` under `PRIVATE_KEY` and `PUBLIC_KEY`.

3.  **Update Configuration:**
    *   Edit `settings.yaml`: Update `POSTGRES_PASSWORD` (must match `.env`), `SECRET_KEY`, `PRIVATE_KEY`, and `PUBLIC_KEY`.
    *   Edit `config.json`: Ensure URLs match your domain (`psono.hmbcentral.live`).

4.  **Database Migration:**
    On the first run, the database might need initialization. The `psono-combo` image typically handles this on startup, but check logs if issues arise.

## Authentik Integration (SAML)

To integrate with Authentik for Single Sign-On (SSO):

1.  **Authentik Setup:**
    *   Create a generic SAML Provider in Authentik.
    *   **ACS URL:** `https://psono.hmbcentral.live/saml/acs/1`
    *   **Issuer:** `https://authentik.hmbcentral.live/application/saml/psono/` (Example)
    *   **Service Provider Binding:** Post
    *   **Audience:** `https://psono.hmbcentral.live/saml/metadata/1`

2.  **Psono Setup:**
    *   Uncomment the `SAML_CONFIGURATIONS` section in `settings.yaml`.
    *   Generate a separate certificate/key pair for the SAML Service Provider (SP) and paste them into `sp.x509cert` and `sp.privateKey`.
    *   Download the Authentik certificate and paste it into `idp.x509cert`.
    *   Update URLs in `settings.yaml` to match your Authentik instance.
    *   Uncomment `'saml'` in `AUTHENTICATION_METHODS` in `settings.yaml`.
    *   Update `config.json` to include `"saml"` in `"authentication_methods"`.

## Running the Service

```bash
docker-compose up -d
```

## Troubleshooting

- Check logs: `docker-compose logs -f`
- If Psono fails to start, verify that the database container is healthy and that all keys in `settings.yaml` are correctly formatted (YAML is whitespace-sensitive).
