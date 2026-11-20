# Plan de monitoreo e incidentes

## Que se monitorea

| Dimension | Evidencia | Umbral o senal | Accion |
|---|---|---|---|
| Disponibilidad | `/health/live` y `/health/ready` | Respuesta distinta de 200 | Revisar contenedor, logs y carga del modelo |
| Errores | Logs por `status_code` | Aumento de 5xx o 422 | Separar fallas internas de datos de entrada invalidos |
| Latencia | `latency_ms` en logs | Aumento sostenido respecto de la linea base | Revisar recursos, volumen y dependencias |
| Trazabilidad | `request_id` y `model_version` | Campo ausente | Detener despliegue y corregir observabilidad |
| Drift | `reports/drift_summary.json` | Variables por encima del umbral de Evidently | Investigar captura, negocio y distribuciones |
| Performance | Recall, precision, ROC-AUC y calibracion | Caida frente a la version aprobada | Evaluar threshold, recalibracion o reentrenamiento |

## Frecuencia y responsables

- Salud, errores y latencia: revision continua durante la operacion y ante alertas.
- Drift: por lote de datos de produccion o con frecuencia mensual.
- Performance con etiquetas: cuando exista una muestra representativa etiquetada.
- Responsable tecnico: operador del servicio y mantenedor del modelo.
- Responsable de negocio: valida si el cambio observado corresponde a una modificacion real de clientes, productos o campanas.

## Respuesta a incidentes

1. **Detectar:** registrar hora, sintoma, endpoint, version y `request_id`.
2. **Contener:** si hay impacto, detener la version defectuosa o volver al tag anterior.
3. **Diagnosticar:** revisar `docker compose ps`, logs, health checks, recursos y contrato de entrada.
4. **Corregir:** aplicar el cambio en una rama, ejecutar pytest y construir una nueva imagen versionada.
5. **Validar:** comprobar salud, prediccion y logs antes de restablecer trafico.
6. **Aprender:** documentar causa, impacto, correccion y control preventivo.

## Criterio ante drift

El drift no dispara reentrenamiento automatico. Primero se descartan errores de esquema o integracion, se interpreta el cambio con negocio y, cuando existen etiquetas, se mide performance. Solo entonces se decide mantener, recalibrar, ajustar el umbral o reentrenar.

