# Customer Churn MLOps

Proyecto individual para la Entrega 1 de Laboratorio de Mineria de Datos. El objetivo es transformar el dataset historico de churn en un flujo de entrenamiento reproducible y trazable con Git, DVC, MLflow y Model Registry.

## Estado de la entrega

La estructura, el EDA, el pipeline de preprocessing y la comparacion de modelos estan implementados. El codigo se publica en GitHub, los datos y artefactos se versionan con DVC en DagsHub, y los seis experimentos y el modelo candidato quedan registrados en MLflow y Model Registry. El cierre formal requiere comprobar la reproduccion desde un clon limpio y crear el tag `entrega-1` sobre el commit presentado.

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
tests/                 pruebas del pipeline
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
