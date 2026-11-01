# Borrador de correo - Entrega 2

**Para:** diego.mosquera@istea.com.ar

**Asunto:** Laboratorio de Mineria de Datos - Entrega 2 - Emmanuel Escobar

Hola Diego:

Comparto la Entrega 2 del proyecto individual de Customer Churn.

Para el corte del 03/11 implemente la opcion sin Docker: API REST de inferencia con FastAPI, contrato de entrada y salida validado con Pydantic, carga del pipeline serializado, health checks, documentacion OpenAPI y pruebas automatizadas.

La implementacion fue validada localmente desde Swagger/OpenAPI: `GET /health` respondio HTTP 200 con el modelo cargado y la version 1, y `POST /predict` respondio HTTP 200 con la prediccion, probabilidad de churn, nivel de riesgo, version del modelo y un identificador de solicitud. Ademas, la suite cuenta con 10 pruebas aprobadas, incluida la carga del modelo real, y un smoke test adicional con el artefacto real.

GitHub: https://github.com/kud-1987/istea-customer-churn-ml

Version entregada (`entrega-2`): https://github.com/kud-1987/istea-customer-churn-ml/tree/entrega-2

DagsHub: https://dagshub.com/kud-1987/istea-customer-churn-ml

Los pasos de instalacion y ejecucion, el ejemplo de request y la evidencia de cumplimiento se encuentran en el README y en `docs/CHECKLIST_ENTREGA_2.md`. Tambien se incluye `docs/GUIA_CONCEPTUAL_ENTREGA_2.docx`, con la explicacion integral de la arquitectura, el flujo de inferencia, los contratos y las pruebas.

Saludos,

Emmanuel Escobar
