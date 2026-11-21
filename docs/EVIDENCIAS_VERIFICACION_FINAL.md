# Evidencias de verificacion final

Fecha de verificacion local: 20 de noviembre de 2026.

## Suite automatizada

Comando:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado comprobado: **14 tests aprobados**. La suite incluye solicitudes HTTP ASGI a la aplicacion y verifica:

- `200` en salud y prediccion valida.
- `422` por campo faltante y categoria invalida.
- `503` cuando el modelo no esta disponible.
- `500` ante un error controlado de inferencia.
- estructura OpenAPI y carga del modelo.
- generacion e interpretacion del resumen de drift.

El mismo conjunto fue ejecutado por GitHub Actions sobre Ubuntu y el job `test` finalizo correctamente. Esto acredita que la suite no depende del equipo Windows de desarrollo.

## API ejecutada

Se inicio Uvicorn y se hicieron solicitudes reales contra `127.0.0.1`.

- `GET /health/ready`: `200`, estado `ok`, modelo cargado, version `1`.
- `POST /predict`: `200`, prediccion `CHURN`, probabilidad `0.6780069151`, riesgo `MEDIUM`.
- El `request_id` de respuesta coincidio con el header `X-Request-ID`.
- Los logs registraron metodo, ruta, estado, latencia, version y el mismo identificador.

Estos valores son una evidencia puntual; pueden variar si cambia el modelo o el registro de entrada.

## Data drift

Comando:

```powershell
.\.venv\Scripts\dvc.exe repro monitor
```

Resultado comprobado:

- Referencia: 7043 registros.
- Lote actual: 2500 registros.
- Drift detectado en 11 de 19 variables (57,89 %).
- Evidencia detallada: `reports/drift_report.html`.
- Resumen para automatizacion: `reports/drift_summary.json`.

## Docker y despliegue Linux

Verificacion realizada el 21 de noviembre de 2026:

- Host: Ubuntu 26.04.1 LTS sobre WSL2, kernel Linux de Microsoft.
- Docker Engine: 29.10.0.
- Docker Compose: 5.8.0.
- Prueba oficial `hello-world`: correcta.
- Imagen: `ghcr.io/kud-1987/istea-customer-churn-ml:v1.0.0`.
- Estado Compose: `Up (healthy)` y puerto `8000` publicado.
- `GET /health/ready`: HTTP 200, modelo cargado, version `v1.0.0`.
- `POST /predict`: HTTP 200, `CHURN`, probabilidad `0.6780069151`, riesgo `MEDIUM`.
- El `request_id` de la prediccion fue `e5304f02-ae71-4660-9cb6-a1805e1f7def` tanto en JSON como en `X-Request-ID` y logs.
- Latencia registrada: `21.49 ms`.

Directorio operativo Linux: `/home/seven/customer-churn-deploy`.

Este host permite demostrar la operacion completa en Linux y Docker sin depender del entorno virtual Python de desarrollo. Es local a la misma computadora y no expone la API a Internet.

## Donde buscar la evidencia externa

1. GitHub, pestana **Actions**: workflow `CI CD` verde.
2. GitHub, seccion **Packages**: imagen GHCR con tag `v1.0.0` y tag `sha-*`.
3. GitHub, seccion **Releases**: release `v1.0.0` publicada como Latest.
4. Ubuntu: `cd /home/seven/customer-churn-deploy` y luego `docker compose ps`.
5. API: `http://localhost:8000/docs` desde Windows o Ubuntu.
6. Logs: `docker compose logs --tail=50 churn-api`.
7. Video final: demostracion de los puntos anteriores.

