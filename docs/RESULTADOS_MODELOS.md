# Resultados de la experimentacion

La ejecucion reproducible del 17/09/2026 comparo seis configuraciones sobre el mismo holdout estratificado del 20 %, con `random_state=42`.

| Experimento | Familia | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---:|---:|---:|---:|---:|
| logistic_balanced_c1 | Lineal | 0.720 | 0.480 | 0.720 | 0.576 | 0.812 |
| logistic_balanced_c05 | Lineal | 0.720 | 0.480 | 0.720 | 0.576 | 0.812 |
| random_forest_depth_7 | Arbol | 0.731 | 0.493 | 0.696 | 0.577 | 0.802 |
| random_forest_depth_10 | Arbol | 0.759 | 0.538 | 0.626 | 0.579 | 0.804 |
| random_forest_balanced_200 | Arbol | 0.778 | 0.588 | 0.532 | 0.559 | 0.798 |
| dummy_most_frequent | Baseline | 0.736 | 0.000 | 0.000 | 0.000 | 0.500 |

## Modelo candidato

Se selecciono `logistic_balanced_c05`. Alcanzo recall de 0.720 y ROC-AUC de 0.812. Empato en recall con la otra regresion logistica y obtuvo una mejora marginal en ROC-AUC.

La prioridad dada al recall responde al costo de los falsos negativos: un cliente que realmente abandonara puede quedar fuera de una accion de retencion. El umbral de clasificacion todavia puede ajustarse en una etapa posterior con informacion sobre costos de negocio.

Los valores completos, el identificador del run y la version registrada se regeneran mediante `dvc repro` y quedan en `reports/model_comparison.csv`, `reports/selection.json` y MLflow.
