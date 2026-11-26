# Customer Churn MLOps

Proyecto individual de Laboratorio de Mineria de Datos. La solucion recorre el ciclo completo: datos versionados, experimentacion trazable, modelo registrado, API REST, testing HTTP, contenedores, CI/CD, publicacion versionada, deployment y monitoreo de drift.

## Estado de la entrega

El repositorio contiene la implementacion acumulativa de las tres entregas. Las observaciones docentes de la Entrega 2 fueron incorporadas: la suite valida el contrato HTTP real con `TestClient`, y se agregaron Dockerfile y Docker Compose. La entrega final suma logging operativo, Evidently, GitHub Actions, GHCR y runbook para Linux.

## Problema de negocio

Se busca estimar la probabilidad de abandono de clientes de telecomunicaciones. Un falso negativo representa un cliente que abandonara y que el modelo considera estable; por eso se prioriza `recall` de la clase churn, manteniendo ROC-AUC como control de capacidad discriminante.

## Datos

- `data/raw/customer_churn_historical.csv`: 7043 registros con target `Churn`. Se usa para entrenamiento y evaluacion.
- `data/production/customer_churn_current.csv`: lote actual sin target. Se reserva para monitoreo y drift.
- `data/scoring/scoring_batch.csv`: lote sin target para pruebas futuras de inferencia.
- `customerID` se conserva para trazabilidad, pero se excluye de los predictores.

Los CSV no deben versionarse directamente con Git. DVC conserva sus archivos de seguimiento y almacena el contenido en el remote configurado.

## Estructura

```text
data/                 datasets administrados por DVC
metadata/             esquema, diccionario y manifiesto
src/churn_ml/          carga, preprocessing, modelos y evaluacion
scripts/               puntos de entrada ejecutables
reports/               EDA, metricas y comparacion de modelos
models/                modelo candidato generado
app/                   API REST, contratos y logica de inferencia
tests/                 pruebas del pipeline, contratos e inferencia
monitoring/scripts     analisis reproducible de drift
.github/workflows/     CI/CD, build y publicacion en GHCR
Dockerfile             imagen reproducible de la API
compose.yaml           ejecucion y operacion declarativa
dvc.yaml               pipeline reproducible
params.yaml            parametros versionados
```

## Instalacion

Requiere Python 3.11 o compatible.

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Ejecucion local

Sin DVC:

```bash
python scripts/run_eda.py
python scripts/run_training.py
pytest
```

Con DVC:

```bash
dvc pull
dvc repro
dvc metrics show
```

En una carpeta sincronizada por OneDrive, DVC puede fallar al mover archivos de su cache de ejecuciones. En ese caso usar `dvc repro --no-run-cache`; el resultado del pipeline y `dvc.lock` se conservan igualmente.

La ejecucion de entrenamiento registra seis runs razonados: baseline, dos regresiones logisticas y tres bosques aleatorios. El run elegido se registra como `customer-churn-candidate`.

La comparacion obtenida en la ejecucion validada se resume en [docs/RESULTADOS_MODELOS.md](docs/RESULTADOS_MODELOS.md).

## Entrega 2: API de inferencia

Iniciar la API desde la raiz del repositorio:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000/docs` para usar Swagger. El endpoint principal es `POST /predict`; los endpoints `GET /health`, `GET /health/live` y `GET /health/ready` permiten comprobar el estado del servicio y del modelo.

Ejemplo de entrada:

```json
{
  "gender": "Female",
  "SeniorCitizen": 0,
  "Partner": "Yes",
  "Dependents": "No",
  "tenure": 1,
  "PhoneService": "No",
  "MultipleLines": "No phone service",
  "InternetService": "DSL",
  "OnlineSecurity": "No",
  "OnlineBackup": "Yes",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "No",
  "StreamingMovies": "No",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 29.85,
  "TotalCharges": 29.85
}
```

La respuesta contiene la clase predicha (`CHURN` o `NO_CHURN`), probabilidad de churn, nivel de riesgo, version del modelo y un identificador de solicitud. Los umbrales actuales son: `LOW` menor a 0.4, `MEDIUM` desde 0.4 hasta menos de 0.7 y `HIGH` desde 0.7.

Validar la implementacion:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe .\scripts\smoke_test_api_model.py
```

El primer comando envia requests HTTP reales en memoria mediante `HTTPX ASGITransport` y verifica respuestas `200`, `422`, `503` y `500`, ademas de la logica de ML. Es la misma frontera HTTP que valida `TestClient`, sin invocar directamente los handlers. El segundo carga `models/candidate.joblib` y ejecuta una inferencia real sobre el primer registro del lote de scoring.

La explicacion conceptual completa, el flujo de una prediccion y la auditoria contra la consigna y las clases se encuentran en [docs/GUIA_CONCEPTUAL_ENTREGA_2.docx](docs/GUIA_CONCEPTUAL_ENTREGA_2.docx).

## Docker y Docker Compose

Antes del build, recuperar el modelo administrado por DVC:

```powershell
.\.venv\Scripts\dvc.exe pull models/candidate.joblib
docker build -t customer-churn-api:local .
docker compose up -d --build
docker compose ps
docker compose logs -f churn-api
```

La API queda en `http://localhost:8000`. El contenedor ejecuta como usuario no root e incluye un health check sobre `/health/ready`.

```powershell
Invoke-RestMethod http://localhost:8000/health/ready
Invoke-RestMethod -Method Post -Uri http://localhost:8000/predict -ContentType 'application/json' -InFile .\examples\predict_request_valid.json
```

Detener con `docker compose down`. La operacion completa en Linux se encuentra en [docs/RUNBOOK.md](docs/RUNBOOK.md).

## Observabilidad y Data Drift

La configuracion opcional de [Prometheus y Grafana](docs/MONITOREO_CLASE_15.md) incluye un tablero, las consultas y el procedimiento de verificacion.

Cada request recibe un `request_id`, devuelto tambien en el header `X-Request-ID`. Los logs incluyen metodo, ruta, codigo HTTP, latencia en milisegundos y version del modelo. Esto permite relacionar una respuesta con su evidencia operativa.

Generar el analisis de drift:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_data_drift.py
```

Resultados:

- `reports/drift_report.html`: reporte visual interactivo de Evidently.
- `reports/drift_summary.json`: resumen verificable para la entrega.
- [docs/RESULTADOS_DRIFT.md](docs/RESULTADOS_DRIFT.md): interpretacion tecnica y plan de accion.

El dataset historico sin target se usa como referencia y `data/production/customer_churn_current.csv` como lote observado. Detectar drift abre una investigacion; no dispara reentrenamiento automatico.

## CI/CD y GHCR

El workflow `.github/workflows/ci-cd.yml` ejecuta pytest como quality gate. En pushes a `main`, tags `v*` o ejecucion manual, recupera el modelo con DVC, construye la imagen y la publica en `ghcr.io/kud-1987/istea-customer-churn-ml` con tag de version y tag de commit.

Configurar en GitHub `Settings > Secrets and variables > Actions`:

- `DAGSHUB_TOKEN`: Default Access Token de DagsHub. El workflow lo usa como usuario Basic; la contrasena tecnica solo fuerza el encabezado requerido por DVC.

`GITHUB_TOKEN` es provisto automaticamente por GitHub Actions. No se guardan credenciales en Git ni dentro de la imagen.

Para cerrar la version final:

```bash
git tag -a v1.0.0 -m "Entrega final"
git push origin main
git push origin v1.0.0
```

Luego crear la release `v1.0.0` en GitHub y comprobar la imagen con tags `v1.0.0` y `sha-...` en Packages.

## Evidencias de entrega final

La verificacion ejecutada, sus resultados y la ubicacion de cada evidencia se documentan en [`docs/EVIDENCIAS_VERIFICACION_FINAL.md`](docs/EVIDENCIAS_VERIFICACION_FINAL.md). La ficha de uso y limitaciones del modelo esta en [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md), y el plan operativo en [`docs/MONITORING_AND_INCIDENTS.md`](docs/MONITORING_AND_INCIDENTS.md).

La auditoria actualizada esta en [docs/CHECKLIST_FINAL.md](docs/CHECKLIST_FINAL.md) y el recorrido sugerido para el video en [docs/GUION_VIDEO_FINAL.md](docs/GUION_VIDEO_FINAL.md). Las evidencias externas que deben capturarse son:

1. workflow verde en GitHub Actions;
2. paquete GHCR con tag explicito;
3. release `v1.0.0`;
4. `docker compose ps`, `/health/ready`, `/predict` y logs en Linux;
5. reporte HTML y resumen de drift;
6. video tecnico de 12 a 15 minutos.

## Configuracion de DagsHub

No guardar tokens en el repositorio. Configurar el remote DVC cuando exista el proyecto:

```bash
dvc remote add -d origin <URL_DEL_REMOTE_DVC>
dvc remote modify origin --local auth basic
dvc remote modify origin --local user <USUARIO>
dvc remote modify origin --local password <TOKEN>
dvc push
```

Para MLflow, iniciar sesion mediante OAuth y activar DagsHub para la ejecucion:

```powershell
dagshub login
$env:DAGSHUB_OWNER='kud-1987'
$env:DAGSHUB_REPO='istea-customer-churn-ml'
python scripts/run_training.py
```

El login abre una autorizacion en el navegador y evita escribir el token en el comando o almacenarlo en el repositorio.

Si no se define un servidor remoto, MLflow usa `./mlruns` mediante una URI absoluta y permite verificar todo el flujo localmente.

## Criterio de seleccion

Se prioriza el mayor recall de churn entre modelos con ROC-AUC igual o superior al minimo configurado. Este criterio reduce falsos negativos sin aceptar un modelo con discriminacion insuficiente. Los resultados quedan en `reports/model_comparison.csv` y la decision completa en `reports/selection.json`.

## Cierre de la Entrega 1

1. Ejecutar `dvc push` y confirmar que el remote este actualizado.
2. Ejecutar `pytest` y revisar `reports/model_comparison.csv`.
3. Confirmar que un clon limpio puede ejecutar `dvc pull` y `dvc repro`.
4. Verificar los seis runs y la version `1` de `customer-churn-candidate` en DagsHub.
5. Crear el tag con `git tag entrega-1` y publicar con `git push origin entrega-1`.
6. Verificar permisos de GitHub, DagsHub, MLflow y Model Registry antes de enviar el correo.

## Limitaciones

La seleccion se realiza con un unico holdout estratificado. Para una version productiva convendria incorporar validacion cruzada, ajuste de threshold basado en costos y validacion temporal cuando exista una dimension de tiempo confiable.
