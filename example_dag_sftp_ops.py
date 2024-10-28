import sys
import os
import logging
working_dir = os.path.join(os.environ['AIRFLOW_HOME'], 'git_directory/TN_operations')
sys.path.append(working_dir)

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from modules.sftp_utils import *
from modules.sftp_configs import *
from modules.sftp_ops import *


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Define the DAG
with DAG(
    dag_id='TN_SFTP_operations_dag',
    default_args=default_args,
    description='A DAG to handle SFTP data exchanges dynamically',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
) as dag:


    configure_logging_task = PythonOperator(
    task_id='configure_logging',
    python_callable=configure_logging
    )
    
    # --------------------------------------
    for config in sftp_configs:

        task_id = f"sftp_file_exchange_{config['sftp_type']}"
        logging.info(f"Processing config for task {task_id}: {config}")

        sftp_file_exchange_task = PythonOperator(
            task_id=task_id,
            python_callable=SFTP_conn_file_exchange, #pass in entire dict
            provide_context=True,
            op_kwargs=config
        )

        #Task dependencies
        configure_logging_task >> sftp_file_exchange_task







