# Agile DAG Factory (Dev Focus)

This repository implements a lightweight and agile orchestration for development environments.
Upon pushing to the main branch, code is automatically deployed to the **Development** environment configured in GitHub Environments.

## "Agile" Philosophy
- **Zero Local Config**: No need to configure Airflow variables. The pipeline "bakes" environment variables (`Project ID`, `Bucket`) directly into the generated DAGs.
- **Direct Upload**: DAGs are generated in-memory within the runner and uploaded directly to the cloud.
- **Environment Isolation**: Uses GitHub Environments to separate Dev from Prod.

## Structure
- `config/`: Definition YAMLs.
- `scripts/`: Pure Python logic.
- `utils/`: "Factory" tools.
- `.github/workflows/`: Pipeline targeting `environment: development`.

## Prerequisites (GitHub Environment: development)
Ensure you create the `development` Environment in GitHub and configure the following secrets:

1. `GCP_WIF_PROVIDER`: Workload Identity Provider ID (including the full path).
2. `GCP_SERVICE_ACCOUNT`: GCP Service Account Email (Required for impersonation).
3. `GCP_PROJECT_ID`: GCP Project ID.
4. `GCP_COMPOSER_BUCKET`: Composer bucket name.

## How to Scale to Production
Since the generator uses environment variables injected by the pipeline:
1. Create a `production` Environment in GitHub.
2. Clone the secrets with Production values.
3. Update the pipeline or create a new one targeting `environment: production`.
   - No code changes are required in scripts or YAMLs.
