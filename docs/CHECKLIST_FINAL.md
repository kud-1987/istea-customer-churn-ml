# Checklist auditado de Entrega Final

Fuente: consigna oficial del proyecto integrador y devolucion docente de la Entrega 2.

## Correcciones de Entrega 2

- [x] Tests HTTP reales con `HTTPX ASGITransport` para `/health` y `/predict`, sin llamadas directas a handlers.
- [x] Codigos 200, 422, 503 y 500 verificados automaticamente.
- [x] Dockerfile con runtime, dependencias, API, modelo, usuario no root y health check.
- [x] `.dockerignore` y `compose.yaml`.
- [x] Build remoto en GitHub Actions y ejecucion Docker verificados en Ubuntu WSL2.

## Definition of Done final

- [x] Codigo, DVC, MLflow, Model Registry, entrenamiento y pipeline reproducible.
- [x] FastAPI, Pydantic, Swagger, health checks y suite pytest.
- [x] Logging con `request_id`, estado, latencia y version del modelo.
- [x] Analisis de drift con Evidently y reporte reproducible.
- [x] Workflow de GitHub Actions con tests como gate, build y GHCR.
- [x] README final y runbook operativo.
- [x] Model Card, plan de monitoreo y procedimiento de incidentes.
- [x] Verificacion local: 14 tests aprobados y API real comprobada con Uvicorn.
- [x] Configurar el secret `DAGSHUB_TOKEN` en GitHub.
- [x] Confirmar workflow verde y paquete versionado en GHCR.
- [x] Crear release/tag `v1.0.0` sobre el commit final.
- [x] Desplegar la imagen en Ubuntu WSL2, separado del entorno Python de desarrollo.
- [x] Verificar `/health`, `/predict`, estado healthy y logs desde Linux.
- [x] Incorporar la indicacion de Clase 15: instrumentar la API con metricas, configurar Prometheus y Grafana, y verificar las consultas con trafico de prueba en Ubuntu WSL2.
- [ ] Grabar y compartir el video tecnico de 12 a 15 minutos, incluyendo las consultas de Prometheus y sus resultados.

El despliegue acreditado usa Ubuntu WSL2 en la misma computadora; demuestra Linux, Docker Engine y Compose, pero no constituye un servidor publico en Internet. La evidencia de Evidently y los logs no reemplazan las metricas solicitadas en Clase 15. El video final sigue requiriendo participacion del alumno.
