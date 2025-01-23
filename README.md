### Documentation for Data Pipeline: Upload to BigQuery (Python & Docker Integration)

### Overview
This Python data pipeline performs the following steps:

1. **SFTP File Fetch**: Fetches files from an SFTP server.
2. **Schema Check**: Validates the schema of the files.
3. **BigQuery Upload**: Uploads the processed files to Google BigQuery using a specified environment and credentials.

The process is packaged into a Docker container to simplify deployment and execution.

---

### Python Code: `bigquery_operations.py`

#### Required Libraries

1. **pysftp**: Used for interacting with the SFTP server.
2. **pandas_gbq**: Used for uploading data to Google BigQuery.
3. **pandas**: For data manipulation.
4. **logging**: For generating logs and tracking execution.

---

#### Core Functionality

##### `upload_to_bigquery()` 

This function performs the following operations:

1. **Reads environment variables**:
   - `SFTP_FOLDER_NAME`: The folder to process from SFTP.
   - `LOCAL_DIR`: The local directory where files will be stored.
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google application credentials JSON file.

2. **Schema Check**:
   - Calls the `initial_schema_check()` function to validate the schema of files fetched from SFTP.

3. **Data Processing and Upload**:
   - Creates an instance of the `Create` class from the `buckets` module to process and upload the data into BigQuery.

4. **Logging**:
   - Logs various stages of the process, including environment variables, credentials, and success/failure messages.

```python
def upload_to_bigquery():
    print("Script execution started!")
  
    logging.info('\n\n-------------New Big Query Logging Instance')

    # Get the environment variables set by the DockerOperator
    SFTP_folder_name = os.environ.get("SFTP_FOLDER_NAME")
    local_dir = os.environ.get("LOCAL_DIR")
    google_application_credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    
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
```

---

### Dockerfile

This Dockerfile sets up a Python-based container to run the `upload_to_bigquery` pipeline. It performs the following:

1. **Base Image**: Uses a `python:3.9-slim` image.
2. **Dependencies**: Installs the dependencies listed in `requirements.txt`.
3. **Environment Variables**: Allows environment variables to be passed into the container using Docker's `-e` flag (e.g., `SFTP_FOLDER_NAME`, `LOCAL_DIR`, `GOOGLE_APPLICATION_CREDENTIALS`).
4. **Volume Mounts**: Mounts local directories and credentials files into the container using Docker's `-v` flag.
5. **Command**: Sets the default command to run the script `bigquery_operations.py`.

#### Dockerfile Example

```dockerfile
# Use a base Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install any required dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code into the container
COPY . .

# Command to run your script (you can customize this as per your needs)
ENTRYPOINT ["python", "bigquery_operations.py"]
```

---

### Running the Docker Container

To run the pipeline in the container, you'll need to specify the appropriate environment variables and mount your local directories and credentials file.

Here’s an example of how to run the Docker container:

```bash
docker run --rm \
  -e SFTP_FOLDER_NAME=illuminate \
  -v /test/dir:/test/dir\
  -v /home/creds.json:/home/creds.json \
  upload-to-bigquery > logs.txt 2>&1
```

This command does the following:
1. `-e SFTP_FOLDER_NAME=illuminate`: Sets the `SFTP_FOLDER_NAME` environment variable.
2. `-v /test/dir`: Mounts the local directory `/test/dir` to the container.
3. `-v /home/creds.json:/home/creds.json`: Mounts the credentials file into the container.
4. Redirects the output of the script to a `logs.txt` file for further inspection.

---

### Dependencies

Ensure the following dependencies are included in the `requirements.txt` file for the Docker container to function correctly:

```
pandas
pandas_gbq
pysftp
google-cloud-storage
google-auth
```

---

### Summary

This pipeline automates the process of fetching data from an SFTP server, checking the schema, and uploading the data to Google BigQuery. The pipeline is fully containerized using Docker, making it easy to deploy and run across different environments while ensuring that the necessary environment variables are provided for authentication and data handling.

### Documentation for Data Pipeline: SFTP Operations

## Overview

This project automates SFTP file exchange operations using **Airflow** to manage tasks and **Docker** to encapsulate the environment. The script handles SFTP file uploads and downloads, logging progress both to the console (for Airflow UI) and to a file inside the container.

## Key Components

### 1. **Airflow DAG** (`sftp_operations.py`)

This Python script defines a script for an Airflow DAG to perform SFTP file exchanges. The key steps involved:

- **Logging**: Logs are captured in both the Airflow UI (stdout) and a log file inside the container (`/app/logs/sftp_testing.log`).
- **SFTP File Exchange**: The script iterates over the `sftp_configs` (which contain configurations for SFTP operations) and calls the `SFTP_conn_file_exchange` function to execute file transfers.
- **SFTP Configurations**: Each configuration contains parameters like SFTP type (upload or download), host, credentials, and directories.


### 2. **SFTP Operations**
For each configuration in `sftp_configs`, the script runs the `SFTP_conn_file_exchange` function to perform the file exchange.

```python
for config in sftp_configs:
    task_id = f"sftp_file_exchange_{config['sftp_type']}"
    logging.info(f"Processing config for task {task_id}: {config}")
    SFTP_conn_file_exchange(**config)
```

- **SFTP Types**: The script supports both file uploads and downloads, with default behavior set to download files.

---

## Docker Setup

### 1. **Dockerfile**

The Dockerfile sets up the environment for the Airflow DAG:

- **Base Image**: Uses the official Python 3.9 slim image.
- **Dependencies**: Installs required Python dependencies from `requirements.txt` and copies the project files into the container.
- **Logs Directory**: Creates a `/logs` directory to store logs inside the container.
- **Airflow Execution**: The default command runs the Python script for Airflow.

### Dockerfile Example:

```dockerfile
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y gcc libssl-dev libffi-dev libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app

# Create logs directory
RUN mkdir -p /app/logs

# Set the command to run the Python script
CMD ["python", "/app/sftp_operations.py"]
```
