import sys
import os
import logging
from datetime import timedelta, datetime
# working_dir = os.path.join(os.environ['AIRFLOW_HOME'], 'git_directory/SFTP_Migrations')
# sys.path.append(working_dir)

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from modules.sftp_utils import *
from modules.sftp_configs import *
from modules.sftp_ops import *

# Ensure proper logging setup
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging to both stdout (for Airflow UI) and a file inside the container
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to Airflow UI via stdout
    ]
)

logging.info('\n\n-------------New Logging Instance')


# --------------------------------------
for config in sftp_configs:

    task_id = f"sftp_file_exchange_{config['sftp_type']}"
    logging.info(f"Processing config for task {task_id}: {config}")


    SFTP_conn_file_exchange(**config)


#Defauted to downloading all files
#The files_to_download variable is being passed down as None not sure why