import pysftp
import os
import pandas_gbq
import pandas as pd
from modules.buckets import *
from modules.reproducibility import *
from modules.sftp_ops import *
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)

# Flush after each log statement
class FlushableStreamHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

logging.getLogger().handlers = [FlushableStreamHandler(sys.stdout)]


# ----------------------------------------------------------

# Function to execute your existing code
def upload_to_bigquery():

    print("Script execution started!")

  
    logging.info('\n\n-------------New Big Query Logging Instance')

    # Get the environment variables set by the DockerOperator
    dataset_name = os.environ.get("dataset_name")
    local_dir = os.environ.get("LOCAL_DIR")
    google_application_credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    logging.info(f"ENV VARS:\n"
             f"GOOGLE_APPLICATION_CREDENTIALS={google_application_credentials_path}\n"
             f"dataset_name={dataset_name}\n"
             f"LOCAL_DIR={local_dir}")

    if not dataset_name:
        logging.error("Environment variables dataset_name is not set!")
        print("Environment variables dataset_name is not set!")
        return
    
    if not google_application_credentials_path:
        logging.error("Google application credentials path is not set!")
        print("Google application credentials path is not set!")
        return

    logging.info(f"Using Google Application Credentials: {google_application_credentials_path}")
    logging.info(f"Processing folder: {dataset_name}")
    logging.info(f"Local directory: {local_dir}")

    # Call the initial schema check
    dataset_name = initial_schema_check(dataset_name)
    logging.info(f"Processing folder: {dataset_name}")

    # Create instance for BigQuery operation
    instance = Create(
                project_id='icef-437920',
                location='us-west1',
                bucket=f'{dataset_name}bucket-icefschools-1',
                local_dir=local_dir,
                dataset_name=dataset_name,
                append_or_replace='replace',
                )
    
    instance.process()  # Pass SFTP files into Bucket & then into BigQuery tables
    logging.info('Process has reached the end\n\n')

    
# Call the function
upload_to_bigquery()


#function upload_all_files_to_bucket needs to become optional within the class. Only if local_dir has a value then that should run 