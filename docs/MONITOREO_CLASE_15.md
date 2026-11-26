# Monitoreo de la API

Prometheus recoge `/metrics` cada 5 segundos. Grafana consulta esas series y carga el tablero Customer Churn API. Los logs conservan el detalle por solicitud y Evidently compara distribuciones entre lotes.

Con los artefactos DVC recuperados, iniciar desde la raiz en Linux:

```bash
API_PORT=8015 MODEL_VERSION=monitoring-local docker compose -p churn-monitoring -f compose.yaml -f compose.monitoring.yaml up -d --build
curl -fsS http://localhost:8015/health/ready
curl -fsS http://localhost:8015/metrics
python3 scripts/verify_monitoring.py
```

Abrir Swagger en http://localhost:8015/docs, probar `/predict` con el JSON de `examples/predict_request_valid.json` y con un objeto vacio. Verificar el target en http://localhost:9090/targets y abrir http://localhost:3000/d/churn-api. Esperar varios scrapes y repetir ambas solicitudes para observar:

```promql
sum(rate(churn_prediction_requests_total[1m]))
sum(rate(churn_prediction_requests_total{outcome!="success"}[1m])) / sum(rate(churn_prediction_requests_total[1m]))
histogram_quantile(0.95, sum by (le) (rate(churn_prediction_duration_seconds_bucket[1m])))
```

Las consultas miden solicitudes por segundo, proporcion de errores de cliente y servidor, y p95 de respuestas exitosas. El p95 no es el promedio: estima el tiempo que no supera el 95 % de las predicciones exitosas. Sin peticiones recientes, los dos ultimos indicadores pueden quedar sin valor.

Para el video, mostrar el target UP, un 200 y un 422, el tablero y el reporte de Evidently. El visor anonimo de Grafana se limita al uso local; Prometheus y Grafana publican sus puertos solo en loopback. La instrumentacion supone un proceso de API por contenedor.

## Evidencia del ensayo local

El 26/11/2026, en Ubuntu WSL2, `verify_monitoring.py` verifico el modelo cargado, el target UP y el tablero provisionado. Envio 12 solicitudes validas (200) y 12 invalidas (422) y obtuvo 0.404 solicitudes/s, 50 % de errores deliberados y p95 de 24.25 ms para respuestas exitosas. Son valores de un ensayo puntual, no una medicion de produccion. La suite local paso los 15 tests.
