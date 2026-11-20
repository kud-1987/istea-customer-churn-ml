# Checklist auditado de Entrega 2

Auditoria realizada contra la consigna oficial del proyecto, la nota administrativa de Classroom y los contenidos de testing y serving desarrollados en clase.

## Estado posterior a la devolucion docente

La devolucion otorgo 6/10. Los dos faltantes principales fueron: pruebas que invocaban funciones Python sin verificar el contrato HTTP real, y ausencia de Docker/Compose. Ambos puntos fueron corregidos para la entrega final.

## Cumplimiento funcional

- [x] Reutilizar el pipeline serializado completo de la Entrega 1.
- [x] Cargar `models/candidate.joblib` una sola vez durante el inicio de FastAPI.
- [x] Exponer `POST /predict`.
- [x] Exponer health checks de vida y disponibilidad.
- [x] Validar las 19 variables mediante Pydantic y rechazar campos extra.
- [x] Mantener el mismo orden de columnas usado durante el entrenamiento.
- [x] Obtener la clase positiva desde `model.classes_` sin asumir una posicion fija.
- [x] Devolver prediccion, probabilidad, nivel de riesgo, version y `request_id`.
- [x] Publicar la documentacion interactiva OpenAPI en `/docs`.
- [x] Responder `422` ante contratos invalidos, `400` ante errores controlados, `503` si falta el modelo y `500` ante fallas inesperadas.

## Matriz contra la consigna oficial

| Requisito | Estado | Evidencia |
|---|---|---|
| `GET /health` operativo e identificacion de version | Cumplido | `app/main.py`; validacion manual HTTP 200, modelo cargado, version 1. |
| `POST /predict` con pipeline completo | Cumplido | `app/main.py`, `app/inference.py`; validacion manual HTTP 200. |
| `prediction`, `probability`, `risk_level`, `model_version` | Cumplido | `PredictionResponse`; clases `CHURN`/`NO_CHURN` y riesgos `LOW`/`MEDIUM`/`HIGH`. |
| Contratos de entrada y salida con Pydantic | Cumplido | `app/schemas.py`; 19 variables, campos extra prohibidos, tipos, rangos y categorias. |
| OpenAPI/Swagger accesible | Cumplido | `/docs` validado manualmente. |
| Test de carga del modelo o pipeline | Cumplido | `tests/test_model_loader.py`. |
| Test de prediccion valida | Cumplido | `tests/test_api.py` y smoke test con el artefacto real. |
| Test de estructura y tipos de respuesta | Cumplido | `tests/test_api.py`. |
| Tests de `/health` y `/predict` | Cumplido y corregido | Requests HTTP en memoria con HTTPX ASGITransport; codigos 200, 422, 503 y 500. |
| Entradas invalidas y errores esperados | Cumplido | Casos de campo faltante y categoria desconocida; FastAPI documenta respuesta 422. |
| Dockerfile, `.dockerignore`, imagen y puerto | Implementado | Dockerfile, usuario no root, puerto 8000 y health check. Build pendiente de verificar en un host con Docker. |
| `compose.yaml` y `docker compose up` | Implementado | Servicio declarativo, variables, puerto, restart y health check. Ejecucion pendiente de un host con Docker. |
| Tag `entrega-2` sobre el commit presentado | Cumplido | El tag se actualiza al commit definitivo de esta auditoria antes del envio. |

## Matriz contra los contenidos de clase

| Concepto trabajado | Estado | Implementacion |
|---|---|---|
| Separar training de serving | Cumplido | La API carga un artefacto ya entrenado; no ejecuta `fit`. |
| Servir el pipeline serializado completo | Cumplido | `models/candidate.joblib` contiene preprocessing y estimador. |
| Validar en la frontera antes de inferir | Cumplido | Pydantic valida presencia, tipos, rangos y categorias. |
| Adaptar el request a estructura tabular | Cumplido | `request_to_frame` crea una fila con el orden de features del modelo. |
| Usar `predict` y `predict_proba` | Cumplido | La respuesta combina clase y probabilidad de churn. |
| No asumir la posicion de la clase positiva | Cumplido | Se obtiene el indice de la clase `1` desde `model.classes_`. |
| Cargar el modelo una vez al iniciar | Cumplido | FastAPI `lifespan` guarda el modelo en `app.state`. |
| Incluir version y `request_id` | Cumplido | Ambos forman parte de `PredictionResponse`. |
| Health check y readiness | Cumplido | `/health`, `/health/live` y `/health/ready`. |
| Suite pequena pero significativa | Cumplido | Tests de esquema, inferencia, thresholds, OpenAPI y carga real. |
| Smoke test de inferencia | Cumplido | `scripts/smoke_test_api_model.py`. |

## Pruebas y evidencia

- [x] Health check con modelo disponible.
- [x] Prediccion valida y contrato de respuesta.
- [x] Campo obligatorio faltante.
- [x] Categoria desconocida.
- [x] Documentacion OpenAPI generada.
- [x] Indice de clase positiva aunque `classes_` este invertido.
- [x] Limites de los niveles de riesgo.
- [x] Smoke test con el artefacto real.
- [x] Suite completa posterior a la correccion: 14 pruebas aprobadas.
- [x] Validacion manual en Swagger: `GET /health` respondio HTTP 200 con `model_loaded: true` y `model_version: "1"`.
- [x] Validacion manual en Swagger: `POST /predict` respondio HTTP 200 con el contrato completo.

## Como demostrarlo

1. Ejecutar `.\.venv\Scripts\python.exe -m pytest -q` y mostrar el resultado.
2. Ejecutar `.\.venv\Scripts\python.exe .\scripts\smoke_test_api_model.py`.
3. Iniciar Uvicorn con `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
4. Abrir `http://127.0.0.1:8000/docs`.
5. Ejecutar `GET /health` y luego `POST /predict` con el ejemplo del README.
6. Probar una categoria invalida y mostrar la respuesta de validacion `422`.

## Pendiente antes del envio

- [x] Revisar la fecha y modalidad administrativa: opcion del 03/11/2026 sin Docker.
- [x] Confirmar que GitHub contiene la version definitiva de la Entrega 2.
- [x] Crear y publicar el tag `entrega-2` sobre la version definitiva.
- [ ] Enviar el correo con enlaces y una sintesis de cumplimiento.
