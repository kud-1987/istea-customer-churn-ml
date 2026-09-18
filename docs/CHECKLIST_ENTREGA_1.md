# Checklist de Entrega 1

Fecha limite: 22/09/2026 a las 19:00.

## Preparado localmente

- [x] Estructura del proyecto y dependencias.
- [x] EDA reproducible.
- [x] Particion estratificada con seed.
- [x] Preprocessing dentro de un Pipeline de scikit-learn.
- [x] Baseline, modelos lineales y modelos de arbol.
- [x] Seis configuraciones de experimento.
- [x] Metricas mas alla de accuracy.
- [x] Regla de seleccion orientada a reducir falsos negativos.
- [x] Registro del modelo candidato en MLflow Model Registry.
- [x] Pipeline DVC y parametros versionados.
- [x] Pruebas minimas del tratamiento de datos y pipeline.

## Requiere GitHub y DagsHub

- [x] Crear repositorio de GitHub.
- [x] Inicializar Git y agregar el remote de GitHub.
- [x] Inicializar DVC y ejecutar `dvc add` sobre los tres CSV.
- [x] Crear proyecto en DagsHub.
- [x] Configurar y probar el remote DVC.
- [x] Configurar MLflow para que los seis runs queden visibles en DagsHub.
- [x] Confirmar que el modelo aparezca en Model Registry y conserve el run de origen.
- [x] Probar un clon limpio con `dvc pull` y `dvc repro`.
- [x] Crear y publicar el tag `entrega-1`.
- [x] Verificar permisos de todos los enlaces.
- [ ] Enviar el correo antes de las 19:00.
