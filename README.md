# Customer Churn MLOps

Proyecto individual de Laboratorio de Mineria de Datos. La Entrega 1 construye un flujo de entrenamiento reproducible y trazable. La Entrega 2 publica el modelo seleccionado como una API REST validada y testeada.

## Estado de la entrega

La Entrega 1 esta completa. Para la opcion administrativa del 03/11/2026, la Entrega 2 incorpora FastAPI, contratos Pydantic, carga unica del artefacto al iniciar, endpoints de salud, prediccion individual, documentacion OpenAPI y pruebas automaticas. Docker y Docker Compose quedan para el alcance completo del 17/11/2026 y para el examen final.

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

La respuesta contiene la clase predicha, probabilidad de churn, nivel de riesgo, version del modelo y un identificador de solicitud. Los umbrales actuales son: bajo menor a 0.4, medio desde 0.4 hasta menos de 0.7 y alto desde 0.7.

Validar la implementacion:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe .\scripts\smoke_test_api_model.py
```

El primer comando prueba contratos, endpoints y logica con dobles controlados. El segundo carga `models/candidate.joblib` y ejecuta una inferencia real sobre el primer registro del lote de scoring.

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
