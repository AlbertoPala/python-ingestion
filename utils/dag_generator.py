import os
import glob
import yaml
import sys
from jinja2 import Template
from google.cloud import storage

# Template definition
# Note: Project ID and Bucket are now baked in at generation time from Env Vars
DAG_TEMPLATE = """
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocDeleteClusterOperator,
    DataprocSubmitJobOperator,
)
from datetime import timedelta
import pendulum

# Configuration generated from YAML and Environment
DAG_ID = "{{ dag_id }}"
SCHEDULE = "{{ schedule }}"
REGION = "{{ region }}"
SCRIPT_PATH = "{{ script_path }}" # Relative path e.g. scripts/myscript.py
PIP_PACKAGES = "{{ pip_packages }}" # Space separated string

# Environment constants baked in during generation
PROJECT_ID = "{{ project_id }}"
BUCKET_NAME = "{{ bucket_name }}"

# Note: Dataproc cluster names must be lowercase, no underscores, max 51 chars.
# We replace underscores with hyphens and truncate the DAG ID if necessary.
CLUSTER_NAME = "{{ dag_id.replace('_', '-')[:25] }}-cluster-{{ '{{' }} ts_nodash {{ '}}' }}"


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.today('UTC').add(days=-1),
    'email_on_failure': False,
    'retries': 0,
}

with DAG(
    DAG_ID,
    default_args=default_args,
    schedule=SCHEDULE,
    catchup=False,
    tags=['generated', 'agile-factory'],
) as dag:

    # 1. Create Dataproc Cluster
    create_cluster = DataprocCreateClusterOperator(
        task_id="create_cluster",
        project_id=PROJECT_ID,
        cluster_name=CLUSTER_NAME,
        region=REGION,
        cluster_config={
            "master_config": {
                "num_instances": 1,
                "machine_type_uri": "{{ master_machine_type }}",
                "disk_config": {"boot_disk_size_gb": 30},
            },
            "worker_config": {
                "num_instances": {{ num_workers }},
                "machine_type_uri": "{{ worker_machine_type }}",
                "disk_config": {"boot_disk_size_gb": 30},
            },
            "software_config": {
                "image_version": "{{ image_version }}",
            },
            "gce_cluster_config": {
                "metadata": {
                    "pip-install": PIP_PACKAGES
                },
                "internal_ip_only": True
            },
            "initialization_actions": [
                {
                    "executable_file": f"gs://{BUCKET_NAME}/utils/install_deps.sh"
                }
            ],
        },
    )

    # 2. Submit Job
    submit_job = DataprocSubmitJobOperator(
        task_id="run_processing_logic",
        job={
            "placement": {"cluster_name": CLUSTER_NAME},
            "pyspark_job": {
                "main_python_file_uri": f"gs://{BUCKET_NAME}/{SCRIPT_PATH}",
            },
        },
        region=REGION,
        project_id=PROJECT_ID,
    )

    # 3. Delete Cluster
    delete_cluster = DataprocDeleteClusterOperator(
        task_id="delete_cluster",
        project_id=PROJECT_ID,
        cluster_name=CLUSTER_NAME,
        region=REGION,
        trigger_rule="all_done",
    )

    create_cluster >> submit_job >> delete_cluster
"""

def generate_and_upload_dags(config_dir, project_id, bucket_name):
    """
    Reads YAML configs, renders DAGs with Env vars, and uploads to GCS.
    """
    if not os.path.exists(config_dir):
        print(f"Config directory {config_dir} not found.")
        sys.exit(1)

    # Initialize GCS Client
    try:
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)

    except Exception as e:
        print(f"Failed to connect to GCS bucket {bucket_name}: {e}")
        sys.exit(1)
    
    yaml_files = glob.glob(os.path.join(config_dir, "*.yaml"))
    print(f"Found {len(yaml_files)} config files in {config_dir}")

    for filename in yaml_files:
        try:
            with open(filename, 'r') as f:
                config = yaml.safe_load(f)
                
            dag_id = config.get('dag_id')
            if not dag_id:
                print(f"Skipping {filename}: Missing dag_id")
                continue

            cluster_conf = config.get('cluster_config', {})
            
            # Context now includes Project/Bucket from Environment
            context = {
                'dag_id': dag_id,
                'schedule': config.get('schedule', '@daily'),
                'region': cluster_conf.get('region', 'us-central1'),
                'master_machine_type': cluster_conf.get('master_machine_type', 'n1-standard-2'),
                'worker_machine_type': cluster_conf.get('worker_machine_type', 'n1-standard-2'),
                'num_workers': cluster_conf.get('num_workers', 2),
                'image_version': cluster_conf.get('image_version', '2.1-debian11'),
                'script_path': config.get('script_path', '').replace('\\', '/'),
                'pip_packages': " ".join(config.get('dependencies') or []),
                'project_id': project_id,
                'bucket_name': bucket_name
            }
            
            # Render
            template = Template(DAG_TEMPLATE)
            rendered_dag = template.render(context)
            
            # Upload to GCS
            blob_name = f"dags/{dag_id}.py"
            blob = bucket.blob(blob_name)
            blob.upload_from_string(rendered_dag, content_type='application/x-python')
            
            print(f"Uploaded: gs://{bucket_name}/{blob_name}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Fetch Multi-Env variables
    project_id = os.environ.get('GCP_PROJECT_ID')
    bucket_name = os.environ.get('GCP_COMPOSER_BUCKET')

    if not project_id or not bucket_name:
        print("Error: GCP_PROJECT_ID and GCP_COMPOSER_BUCKET must be set.")
        sys.exit(1)

    base_dir = os.getcwd()
    config_directory = os.path.join(base_dir, "config")
    
    if not os.path.exists(config_directory) and os.path.exists("../config"):
        config_directory = "../config"

    generate_and_upload_dags(config_directory, project_id, bucket_name)
