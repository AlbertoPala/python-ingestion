# Agile DAG Factory (Dev Focus)

Este repositorio implementa una orquestación ligera y ágil para entornos de desarrollo.
Al hacer push a la rama principal, el código se despliega automáticamente al entorno **Development** configurado en GitHub Environments.

## Filosofía "Agile"
- **Zero Local Config**: No necesitas configurar variables Airflow. El pipeline "hornea" (`bakes`) las variables de entorno (`Project ID`, `Bucket`) directamente en los DAGs generados.
- **Direct Upload**: Los DAGs se generan en memoria en el runner y se suben directamente a la nube.
- **Environment Isolation**: Usa GitHub Environments para separar Dev de Prod.

## Estructura
- `config/`: YAMLs de definición.
- `scripts/`: Lógica pura en Python.
- `utils/`: Herramientas del "Factory".
- `.github/workflows/`: Pipeline apuntando a `environment: development`.

## Prerrequisitos (GitHub Environment: development)
Asegúrese de crear el Environment `development` en GitHub y configurar los siguientes secretos:


1. `GCP_WIF_PROVIDER`: ID del Provider de Workload Identity (incluyendo la ruta completa).
2. `GCP_PROJECT_ID`: ID del proyecto GCP.
3. `GCP_COMPOSER_BUCKET`: Nombre del bucket de Composer.
4. `GCP_WIF_POOL`: ID del Pool de Identidad (si se requiere para referencia).


## Cómo Escalar a Producción
Dado que el generador utiliza variables de entorno inyectadas por el pipeline:
1. Cree un Environment `production` en GitHub.
2. Clone los secretos con los valores de Producción.
3. Actualice el pipeline o cree uno nuevo que apunte a `environment: production`. 
   - No se requiere cambiar una sola línea de código en los scripts o YAMLs.
