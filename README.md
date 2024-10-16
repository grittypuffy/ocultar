# Ocultar

> Offline-first de-identification and sanitization for enhanced privacy

# Features

1. Offline usage
2. Optional web interface
3. Multi-lingual redaction
4. Batch processing
5. Integrated metadata removal

# Philosophy

# Technologies used

## Frontend

1. Vite
2. Alpine.js
3. HTMX
4. Bun

## Backend

1. FastAPI
2. Presidio

## Desktop

1. Tauri

## Deployment and automation

1. Azure
2. GitHub Actions

# Development

## Manual installation

The project is a monorepository containing source code for:
- Frontend
- Backend
- Desktop

## Frontend

``` shell
cd frontend
bun install
```

## Backend

``` shell
cd backend
poetry env use python3.12
source $(poetry env info --path)/bin/activate
poetry install
```

## Desktop

``` shell
cd desktop
bun install
```

For Desktop development, run:
```shell 
bun run tauri dev
```