# Guion de video final (12-15 minutos)

## Preparacion

Antes de grabar, abrir:

1. GitHub en la pestana Actions.
2. La release `v1.0.0`.
3. DagsHub/MLflow con los experimentos.
4. `http://localhost:8000/docs`.
5. Una terminal Ubuntu.

En Ubuntu ejecutar:

```bash
cd /home/seven/customer-churn-deploy
docker compose ps
```

Debe aparecer el contenedor `healthy`.

## Recorrido y discurso

1. **0:00-1:00 - Problema.** Explicar churn, target y que un falso negativo es un cliente que se va pero no fue detectado. El objetivo es priorizar retencion, no automatizar decisiones irreversibles.
2. **1:00-2:30 - Arquitectura y datos.** Mostrar el README. Explicar Git para codigo, DVC/DagsHub para datos y artefactos, MLflow para experimentos, FastAPI para inferencia, Docker para entrega y GitHub Actions para CI/CD.
3. **2:30-4:00 - Entrenamiento.** Mostrar los seis Runs de MLflow. Explicar baseline, regresion logistica y Random Forest; la seleccion prioriza recall de churn y usa ROC-AUC y precision como controles.
4. **4:00-5:00 - Trazabilidad.** Relacionar commit, version DVC, Run, modelo candidato y `MODEL_VERSION`. Mostrar la release `v1.0.0`.
5. **5:00-6:30 - API.** Abrir Swagger. Ejecutar `GET /health/ready` y mostrar `status=ok`, `model_loaded=true` y `model_version=v1.0.0`.
6. **6:30-7:30 - Prediccion.** Ejecutar `POST /predict` con el ejemplo de Swagger. Explicar clase, probabilidad, riesgo y `request_id`.
7. **7:30-8:30 - Tests.** Mostrar GitHub Actions y el job `test` verde. Explicar que los 14 tests envian requests HTTP y cubren 200, 422, 500 y 503, corrigiendo la observacion de la Entrega 2.
8. **8:30-9:30 - Docker.** Mostrar `Dockerfile` y `compose.yaml`: usuario no root, health check, variables, puerto y politica de reinicio.
9. **9:30-11:30 - Linux real.** En Ubuntu ejecutar los siguientes comandos.

```bash
cd /home/seven/customer-churn-deploy
docker compose ps
curl -fsS http://127.0.0.1:8000/health/ready
curl -fsS -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  --data @predict_request_valid.json
docker compose logs --tail=20 churn-api
```

Senalar que el contenedor esta `healthy`, la version es `v1.0.0` y el `request_id` de la prediccion aparece tambien en los logs.

10. **11:30-12:30 - CI/CD y GHCR.** Mostrar el workflow verde del tag, la recuperacion DVC, el build Docker, la imagen `ghcr.io/kud-1987/istea-customer-churn-ml:v1.0.0` y la release Latest.
11. **12:30-13:30 - Drift.** Mostrar `docs/RESULTADOS_DRIFT.md` o `reports/drift_report.html`: 11 de 19 variables con drift. Aclarar que drift es una senal para investigar y no implica reentrenamiento automatico.
12. **13:30-15:00 - Cierre.** Resumir observabilidad, rollback, Model Card y limitaciones. Aclarar que WSL2 demuestra Linux, Docker y Compose en un entorno separado, aunque no expone la API publicamente.

## Evidencias que deben quedar visibles

- Workflow del tag `v1.0.0` verde.
- Release `v1.0.0` marcada como Latest.
- Imagen GHCR con tag explicito.
- Contenedor `healthy` en Ubuntu.
- Health check y prediccion reales.
- Mismo `request_id` en respuesta y logs.
- Evidently y explicacion de la accion propuesta.
