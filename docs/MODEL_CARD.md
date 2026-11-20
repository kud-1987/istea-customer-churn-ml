# Model Card: Customer Churn

## Proposito

El modelo estima la probabilidad de baja de un cliente de telecomunicaciones. Su salida sirve para priorizar acciones de retencion; no decide automaticamente la baja, el precio ni el acceso a un servicio.

## Version y artefacto

- Artefacto de inferencia: `models/candidate.joblib`.
- Tipo: pipeline serializado de scikit-learn, con transformaciones y clasificador en un unico objeto.
- Version operativa: variable `MODEL_VERSION`, expuesta en `/health` y `/predict`.
- Trazabilidad: parametros y metricas en MLflow, seleccion en `reports/selection.json` y datos versionados con DVC.

## Datos

- Fuente de entrenamiento: `data/raw/customer_churn_historical.csv`.
- Unidad de analisis: un cliente.
- Target: `Churn`.
- Variables: datos demograficos, antiguedad, servicios contratados, contrato, facturacion y cargos.
- La columna `customerID` no se usa para predecir.

## Seleccion del modelo

Se compararon un baseline, regresion logistica y Random Forest. La seleccion prioriza recall de churn, con ROC-AUC y precision como metricas complementarias, porque no detectar a un cliente que se dara de baja tiene costo comercial.

## Uso esperado

1. Enviar un registro que cumpla el contrato Pydantic de `/predict`.
2. Recibir clase, probabilidad y nivel de riesgo.
3. Usar el resultado como apoyo para priorizar revision o contacto humano.

## Limitaciones y riesgos

- La probabilidad no es una certeza ni una explicacion causal.
- El modelo refleja la poblacion y el periodo de los datos historicos.
- Drift, cambios comerciales o cambios de captura pueden degradar su utilidad.
- Deben revisarse metricas por segmentos relevantes antes de tomar decisiones sensibles.
- No se autoriza el uso para decisiones discriminatorias ni para acciones irreversibles sin revision humana.

## Controles

- Validacion de entrada con Pydantic.
- Health checks de vida y disponibilidad del modelo.
- Logs con `request_id`, latencia, codigo HTTP y version.
- Tests del contrato HTTP para respuestas 200, 422, 500 y 503.
- Monitoreo de drift con Evidently.
- Versionado explicito de la imagen y procedimiento de rollback.

