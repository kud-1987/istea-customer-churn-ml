# Checklist auditado de Entrega Final

Fuente: consigna oficial del proyecto integrador y devolucion docente de la Entrega 2.

## Correcciones de Entrega 2

- [x] Tests HTTP reales con `HTTPX ASGITransport` para `/health` y `/predict`, sin llamadas directas a handlers.
- [x] Codigos 200, 422, 503 y 500 verificados automaticamente.
- [x] Dockerfile con runtime, dependencias, API, modelo, usuario no root y health check.
- [x] `.dockerignore` y `compose.yaml`.
- [ ] Build y ejecucion Docker verificados en una maquina con Docker instalado.

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
- [ ] Confirmar workflow verde y paquete versionado en GHCR.
- [ ] Crear release/tag `v1.0.0` sobre el commit final.
- [ ] Desplegar la imagen en un host Linux diferente del entorno de desarrollo.
- [ ] Capturar `/health`, `/predict` y logs desde el host Linux.
- [ ] Grabar y compartir el video tecnico de 12 a 15 minutos.

Los puntos pendientes requieren cuentas o infraestructura externa y no pueden acreditarse solamente con archivos locales.
