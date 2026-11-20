# Resultados del analisis de Data Drift

## Comparacion

- Referencia: `data/raw/customer_churn_historical.csv`, sin `customerID` ni target.
- Produccion simulada: `data/production/customer_churn_current.csv`, sin `customerID`.
- Herramienta: Evidently 0.7.19, preset `DataDriftPreset`.
- Filas de referencia: 7043.
- Filas actuales: 2500.

## Resultado

Evidently detecto drift de dataset: 11 de 19 variables, equivalentes al 57,89 %, superaron el umbral configurado por el preset.

Variables con evidencia de drift:

- `tenure` (0,4768)
- `MonthlyCharges` (0,4858)
- `TotalCharges` (0,1702)
- `InternetService` (0,1155)
- `OnlineSecurity` (0,1184)
- `OnlineBackup` (0,1009)
- `DeviceProtection` (0,1021)
- `TechSupport` (0,1123)
- `StreamingTV` (0,1192)
- `StreamingMovies` (0,1154)
- `Contract` (0,1062)

Para estas variables Evidently uso distancia de Wasserstein normalizada en numericas y distancia Jensen-Shannon en categoricas, con umbral 0,1.

## Interpretacion y accion

El lote actual difiere de la poblacion historica, especialmente en cargos y antiguedad. Esto puede cambiar la distribucion de probabilidades y el volumen de clientes clasificados como riesgo alto. Sin etiquetas actuales no se puede afirmar que recall o ROC-AUC hayan caido.

Accion propuesta:

1. Verificar que no exista un cambio de captura, esquema o integracion.
2. Analizar las distribuciones de `MonthlyCharges`, `tenure` y variables de servicios.
3. Obtener una muestra etiquetada del periodo actual.
4. Medir recall, precision, calibracion y matriz de confusion por segmento.
5. Recalibrar, ajustar el threshold o reentrenar solamente si la evidencia de performance y negocio lo justifica.

La evidencia completa queda en `reports/drift_report.html` y el resumen estructurado en `reports/drift_summary.json`.
