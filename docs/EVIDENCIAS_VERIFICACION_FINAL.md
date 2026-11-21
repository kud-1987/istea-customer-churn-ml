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

## Docker y despliegue

El `Dockerfile`, `compose.yaml`, health check y runbook estan incluidos. La computadora de desarrollo usada para esta verificacion no tiene Docker instalado; por lo tanto, el build de imagen y el despliegue Linux deben acreditarse con el workflow de GitHub y el host final.

## Donde buscar la evidencia externa

1. GitHub, pestana **Actions**: workflow `CI CD` verde.
2. GitHub, seccion **Packages**: imagen GHCR con tag `v1.0.0` y tag `sha-*`.
3. GitHub, seccion **Releases**: release `v1.0.0`.
4. Host Linux: salida de `docker compose ps`, `/health/ready`, `/predict` y `docker compose logs`.
5. Video final: demostracion de los cuatro puntos anteriores.

