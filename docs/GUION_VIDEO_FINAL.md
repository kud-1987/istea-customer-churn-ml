# Guion de video final (12-15 minutos)

1. **0:00-1:00 - Contexto:** churn, target, falso negativo y arquitectura.
2. **1:00-2:30 - Datos:** DVC, dataset historico, current, preprocessing y split.
3. **2:30-4:00 - Experimentos:** seis Runs, metricas, criterio y candidato registrado.
4. **4:00-5:30 - Trazabilidad:** commit, DVC, Run, Registry, version de modelo.
5. **5:30-7:00 - API y tests:** Swagger, pytest HTTP, `/health`, `/predict`, 422 y 503.
6. **7:00-8:30 - Docker:** Dockerfile, Compose, health check y logs.
7. **8:30-10:00 - CI/CD:** workflow verde, tag explicito e imagen GHCR.
8. **10:00-12:00 - Linux:** `docker compose up -d`, health y prediccion real.
9. **12:00-13:30 - Observabilidad:** `request_id`, latencia, logs y reporte Evidently.
10. **13:30-15:00 - Cierre:** limitaciones, drift no equivale a retraining y proximos pasos.

La demostracion debe mostrar una prediccion real contra el host Linux, el mismo `request_id` en la respuesta y en los logs, un workflow exitoso y una imagen GHCR con tag explicito.
