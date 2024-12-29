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
    SFTP_folder_name = os.environ.get("SFTP_FOLDER_NAME")
    local_dir = os.environ.get("LOCAL_DIR")
     # Get the GOOGLE_APPLICATION_CREDENTIALS environment variable from the container
    google_application_credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    print(f'Here is the google_application_credentials_path {google_application_credentials_path}')
    
    if not SFTP_folder_name or not local_dir:
        logging.error("Environment variables SFTP_FOLDER_NAME or LOCAL_DIR are not set!")
        print("Environment variables SFTP_FOLDER_NAME or LOCAL_DIR are not set!")
        return
    
    if not google_application_credentials_path:
        logging.error("Google application credentials path is not set!")
        print("Google application credentials path is not set!")
        return

    logging.info(f"Using Google Application Credentials: {google_application_credentials_path}")
    logging.info(f"Processing folder: {SFTP_folder_name}")
    logging.info(f"Local directory: {local_dir}")

    # Call the initial schema check
    SFTP_folder_name = initial_schema_check(SFTP_folder_name)
    logging.info(f"Processing folder: {SFTP_folder_name}")

    # Create instance for BigQuery operation
    instance = Create(
                project_id='icef-437920',
                location='us-west1',
                bucket=f'{SFTP_folder_name}bucket-icefschools-1',
                local_dir=local_dir,
                db=SFTP_folder_name,
                append_or_replace='replace',
                )
    
    instance.process()  # Pass SFTP files into Bucket & then into BigQuery tables
    logging.info('Process has reached the end\n\n')


#Will run locally by bringing in os.environ and mounting json file and local path
# os.environ["SFTP_FOLDER_NAME"] = "illuminate"
# os.environ["LOCAL_DIR"] = '/home/g2015samtaylor/illuminate'
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/g2015samtaylor/icef-437920.json"

# docker run --rm \
#   -e SFTP_FOLDER_NAME=illuminate \
#   -v /home/icef/illuminate:/home/g2015samtaylor/illuminate \
#   -v /home/g2015samtaylor/icef-437920.json:/home/g2015samtaylor/icef-437920.json \
#   upload-to-bigquery > logs.txt 2>&1
    
    
# Call the function
upload_to_bigquery()

