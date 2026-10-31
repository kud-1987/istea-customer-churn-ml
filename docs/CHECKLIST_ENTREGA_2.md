# Checklist de Entrega 2

## Alcance elegido

Opcion administrativa del 03/11/2026: aplicacion de inferencia con contrato REST y pruebas automatizadas, sin Docker. Segun la aclaracion de clase, el porcentaje de Docker se redistribuye entre los demas criterios. El proyecto completo con Docker y Docker Compose queda pendiente para el 17/11/2026 y para el examen final.

## Cumplimiento funcional

- [x] Reutilizar el pipeline serializado completo de la Entrega 1.
- [x] Cargar `models/candidate.joblib` una sola vez durante el inicio de FastAPI.
- [x] Exponer `POST /predict`.
- [x] Exponer health checks de vida y disponibilidad.
- [x] Validar las 19 variables mediante Pydantic y rechazar campos extra.
- [x] Mantener el mismo orden de columnas usado durante el entrenamiento.
- [x] Obtener la clase positiva desde `model.classes_` sin asumir una posicion fija.
- [x] Devolver prediccion, probabilidad, nivel de riesgo, version y `request_id`.
- [x] Publicar la documentacion interactiva OpenAPI en `/docs`.
- [x] Responder `422` ante contratos invalidos, `400` ante errores controlados, `503` si falta el modelo y `500` ante fallas inesperadas.

## Pruebas y evidencia

- [x] Health check con modelo disponible.
- [x] Prediccion valida y contrato de respuesta.
- [x] Campo obligatorio faltante.
- [x] Categoria desconocida.
- [x] Documentacion OpenAPI generada.
- [x] Indice de clase positiva aunque `classes_` este invertido.
- [x] Limites de los niveles de riesgo.
- [x] Smoke test con el artefacto real.
- [x] Suite completa: 9 pruebas aprobadas.

## Como demostrarlo

1. Ejecutar `.\.venv\Scripts\python.exe -m pytest -q` y mostrar el resultado.
2. Ejecutar `.\.venv\Scripts\python.exe .\scripts\smoke_test_api_model.py`.
3. Iniciar Uvicorn con `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
4. Abrir `http://127.0.0.1:8000/docs`.
5. Ejecutar `GET /health` y luego `POST /predict` con el ejemplo del README.
6. Probar una categoria invalida y mostrar la respuesta de validacion `422`.

## Pendiente antes del envio

- [ ] Revisar la fecha y modalidad definitiva indicadas por el profesor.
- [ ] Confirmar que GitHub y DagsHub contienen el ultimo commit.
- [ ] Crear y publicar el tag `entrega-2` cuando la version sea definitiva.
- [ ] Enviar el correo con enlaces y una sintesis de cumplimiento.
