# Runbook de operacion

## Configuracion inicial

1. Instalar Docker Engine y Docker Compose en el host Linux.
2. Crear `.env` a partir de `.env.example`.
3. Definir `IMAGE_NAME=ghcr.io/kud-1987/istea-customer-churn-ml:v1.0.0`.
4. Iniciar sesion sin guardar el token en el repositorio:

```bash
echo "$GHCR_TOKEN" | docker login ghcr.io -u kud-1987 --password-stdin
```

La imagen `v1.0.0` tambien puede descargarse anonimamente. En el host Ubuntu WSL2 utilizado para la evidencia, el directorio operativo es `/home/seven/customer-churn-deploy`.

## Operacion habitual

```bash
docker compose pull
docker compose up -d --no-build
docker compose ps
docker compose logs -f churn-api
curl -fsS http://localhost:8000/health/ready
```

Prediccion:

```bash
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  --data @examples/predict_request_valid.json
```

Actualizacion:

```bash
docker compose pull
docker compose up -d --no-build
docker image prune -f
```

Detencion y rollback:

```bash
docker compose down
# Cambiar IMAGE_NAME en .env a un tag anterior y repetir pull/up.
docker compose pull
docker compose up -d --no-build
```

## Diagnostico

- Servicio caido: `docker compose ps` y `docker compose logs --tail=200 churn-api`.
- Error HTTP: buscar `request_id`, `status_code` y `path` en los logs.
- Latencia: comparar `latency_ms` de las solicitudes y revisar recursos con `docker stats`.
- Modelo no disponible: `/health/ready` devuelve 503 y el contenedor queda unhealthy.
- Drift: abrir `reports/drift_report.html` y revisar `reports/drift_summary.json`.

No se debe reentrenar automaticamente por detectar drift. Primero se investiga el contexto, se consiguen etiquetas cuando corresponda y se evalua performance.
