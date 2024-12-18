import pandas as pd
import pandas_gbq
import pysftp
import logging
import time
import os
import io
from airflow.exceptions import AirflowException
from .sftp_utils import *
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None


def SFTP_conn_file_exchange(**kwargs):
    conn = None #For loops being as none

    # Access parameters using kwargs.get()
    sftp_type = kwargs.get('sftp_type', None) 
    local_sftp_type = kwargs.get('local_sftp_type', None)
    import_or_export = kwargs.get('import_or_export', None)
    target_sftp_folder_name = kwargs.get('target_sftp_folder_name', None)
    local_sftp_folder_name = kwargs.get('local_sftp_folder_name', None)
    files_to_download = kwargs.get('files_to_download', None)
    use_pool = kwargs.get('use_pool', False)
    naming_dict = kwargs.get('naming_dict', None)
    db = kwargs.get('db', None)
    export_local_bq_replications = kwargs.get('export_local_bq_replications', None)
    project_id = kwargs.get('project_id', None)
    

    # Logging for debugging
    logging.info(f"sftp_type: {sftp_type}")
    logging.info(f"local_sftp_type: {local_sftp_type}")
    logging.info(f"import_or_export: {import_or_export}")
    logging.info(f"target_sftp_folder_name: {target_sftp_folder_name}")
    logging.info(f"local_sftp_folder_name: {local_sftp_folder_name}")
    logging.info(f"files_to_download: {files_to_download}")
    logging.info(f"use_pool: {use_pool}")
    logging.info(f"naming_dict: {naming_dict}")
    logging.info(f"db: {db}")
    logging.info(f"export_local_bq_replications: {export_local_bq_replications}")
    logging.info(f"use_pool: {use_pool}")
    logging.info(f"project_id: {project_id}")


    #specific conns retrieved
    sftp_conn_obj = SFTPConnection.setup_sftp_connection(type_=sftp_type)
    sftp_conn = sftp_conn_obj.get_connection()
    logging.info(f'\n\n\nSFTP singular connection established successfully for {sftp_type}')
  
    sftp_conn_local_obj = SFTPConnection.setup_sftp_connection(type_=local_sftp_type)
    sftp_conn_local = sftp_conn_local_obj.get_connection()
    logging.info(f'\n\n\nSFTP singular connection established successfully for {local_sftp_type}')

                    
    #Bring in local bq replications to local_sftp before sending to vendor
    if export_local_bq_replications:
        logging.info('Attempting to replicate BQ views to local prior to exporting them out')
        replicate_BQ_views_to_local(sftp_conn_local, 
                                    local_sftp_folder_name, 
                                    project_id, 
                                    db, 
                                    naming_dict) 
        
    
            
    # Call the SFTP file transfer function
    SFTP_file_transfer(
        import_or_export=import_or_export,
        sftp_conn=sftp_conn,
        sftp_conn_local=sftp_conn_local,
        sftp_type=sftp_type,
        target_sftp_folder_name=target_sftp_folder_name,
        local_sftp_folder_name=local_sftp_folder_name,
        files_to_download=files_to_download,
        naming_dict=naming_dict
    )

    # finally:
    try:
        sftp_conn_obj.close_connection(sftp_conn)
        logging.info(f'SFTP connection for {sftp_type} closed')
        sftp_conn_local_obj.close_connection(sftp_conn_local)
        logging.info(f'SFTP connection for {local_sftp_type} closed')
    except Exception as e:
        logging.error(f'Unable to close connection for {sftp_type} or {local_sftp_type} due to {e}')

# ---------------------------------------------------------


def ensure_sftp_directory_exists(sftp_conn_destination, local_sftp_folder_name):
    folder_name = local_sftp_folder_name.rstrip('/')  # Remove trailing slash if any
    try:
        sftp_conn_destination.chdir(folder_name)
        logging.info(f'Directory "{folder_name}" already exists on the SFTP server.')
    except IOError:
        logging.info(f'Directory "{folder_name}" does not exist. Attempting to create it.')
        sftp_conn_destination.makedirs(folder_name)
        logging.info(f'Directory "{folder_name}" was created successfully.')





def transfer_file(sftp_conn_source, sftp_conn_destination, source_file_path, destination_file_path):
    """Helper function to transfer a single file."""
    try:
        
        if sftp_conn_source.exists(source_file_path):
            logging.info(f"Path {source_file_path} exists.")
        else:
            logging.error(f"Path {source_file_path} does NOT exist.")
            raise AirflowException(f"Path {source_file_path} does NOT exist.")


        # Validate file being in the path
        source_file_name = os.path.basename(source_file_path) #extract filename form the source file path
        if source_file_name not in sftp_conn_source.listdir():
            logging.error(f'File "{source_file_name}" is invalid or empty in the path {source_file_path}.')
            raise AirflowException(f'File "{source_file_name}" does not exist or is invalid in the {source_file_path}.')

        # Log about opening destination file
        logging.info(f'Opening destination file for writing: "{destination_file_path}".')
        
        # Open the file on the destination SFTP server for writing
        with sftp_conn_destination.open(destination_file_path, 'wb') as destination_file:
            # Download the file from the source and write it to the destination
            sftp_conn_source.getfo(source_file_path, destination_file)
            logging.info(f'File "{source_file_path}" successfully transferred to "{destination_file_path}".')
    
    except FileNotFoundError as fnf_error:
        logging.error(f'File not found error: {fnf_error}')
        raise
    except IOError as io_error:
        logging.error(f'I/O error during file transfer: {io_error}')
        raise
    except Exception as e:
        logging.error(f'An unexpected error occurred during file transfer: {e}', exc_info=True)
        raise
   




def SFTP_file_transfer(import_or_export, sftp_conn, sftp_conn_local, sftp_type, target_sftp_folder_name, local_sftp_folder_name, files_to_download=None, naming_dict=None):


    # Set the source and destination connections based on import_or_export value
    if import_or_export == 'import':
        logging.info(f'Attempting to import SFTP files to local for {sftp_type}')
        sftp_conn_source = sftp_conn                      # Remote SFTP as the source
        sftp_conn_destination = sftp_conn_local           # Local SFTP as the destination
        source_fldr = target_sftp_folder_name
        destination_fldr = local_sftp_folder_name

    elif import_or_export == 'export':
        logging.info(f'Attempting to export SFTP files to remote for {sftp_type}')
        sftp_conn_source = sftp_conn_local                # Local SFTP as the source
        sftp_conn_destination = sftp_conn                 # Remote SFTP as the destination
        source_fldr = local_sftp_folder_name
        destination_fldr = target_sftp_folder_name
    else:
        raise ValueError(f'Invalid value for import_or_export: {import_or_export}')

    logging.info(f'source_fldr: {source_fldr}')
    logging.info(f'destination_fldr: {destination_fldr}')
    
    # Ensure destination directory exists
    ensure_sftp_directory_exists(sftp_conn_destination, destination_fldr)

    try:
        logging.info(f'Navigating to destination folder "{destination_fldr}" for the {import_or_export} on {sftp_type} to ensure landing spot')

        sftp_conn_source.chdir(source_fldr)
        dir_contents = sftp_conn_source.listdir()
        logging.info(f'Dir contents of {source_fldr} for the {import_or_export} of {sftp_type}: {dir_contents}')
        
        if not dir_contents:
            logging.info(f'No files to download in folder for "{source_fldr}".')
            return
        
        # Handle two file transfers
        if files_to_download:
            for file in files_to_download:
                if file in dir_contents:
                    dict_name = naming_dict.get(file)
                    source_file_path = os.path.join(source_fldr, file)
                    destination_file_path = os.path.join(destination_fldr, dict_name)
                    logging.info(f'Starting file transfer: "{file}" -> "{destination_file_path}".')
                    transfer_file(sftp_conn_source, sftp_conn_destination, source_file_path, destination_file_path)
                    logging.info(f'Successfully transferred file "{file}" to "{destination_file_path}".')
                else:
                    logging.error(f'File "{file}" not found in directory "{target_sftp_folder_name}".')
                    raise AirflowException(f'File "{file}" not found.')


        else:
            # Handle batch file transfer
            logging.info(f'No specification for file_to_download variable, assuming all files need to be transferred from {source_fldr}')
            for file_name in dir_contents:
                source_file_path = os.path.join(source_fldr, file_name)
                destination_file_path = os.path.join(destination_fldr, file_name)
                logging.info(f'Transferring file "{file_name}" to "{destination_file_path}".')
                transfer_file(sftp_conn_source, sftp_conn_destination, source_file_path, destination_file_path)
                logging.info(f'Successfully transferred file "{file_name}" to "{destination_file_path}".')

            logging.info(f'All files in folder "{source_fldr}" transferred to destination SFTP.')

    except IOError as e:
        logging.error(f'IOError occurred while accessing "{source_fldr}" or transferring files: {e}')
        raise AirflowException(f'Error during SFTP operation: {e}')

    except Exception as e:
        logging.error(f'An error occurred during file replication {files_to_download} attempt to {destination_fldr}: {e}')
        raise AirflowException
    
    logging.info(f'Finished SFTP file transfer from "{source_fldr}" to "{destination_fldr}')




def replicate_BQ_views_to_local(sftp_conn_local, local_sftp_folder_name, project_id, db, naming_dict):
    
    """
        Function to send BigQuery table data directly to an SFTP server.

        Parameters:
        - conn: pysftp.Connection object for SFTP connection.
        - sftp_folder_name: Remote folder name on the SFTP server.
        - project_id: Google Cloud project ID for BigQuery.
        - db: BigQuery database name.
        - naming_dict: Dictionary mapping BigQuery table names to remote filenames.
    """

    # Iterate over dictionary of table names and filenames
    for table_name, remote_filename in naming_dict.items():

        # Query BigQuery table
        query = f"""SELECT * FROM `{project_id}.{db}.{table_name}`"""
        try:
            # Execute the query and store the result in a DataFrame
            df = pandas_gbq.read_gbq(query, project_id=project_id)
            logging.info(f'Reading {query} from BQ')
        except Exception as e:
            logging.error(f'Error querying table "{table_name}": {str(e)}')
            raise AirflowException

        buffer = io.StringIO()
        try:
            df.to_csv(buffer, index=False) #df in memory
            buffer.seek(0)  #reset buffer position for loop
            logging.info(f"Big Query table - {table_name} written to in-memory buffer.")
        except Exception as e:
            logging.error(f"Failed to write Big Query table - {table_name} to buffer: {str(e)}")
            raise AirflowException
        
        #Ensure directory exists on local SFTP before writing
        ensure_sftp_directory_exists(sftp_conn_local, local_sftp_folder_name)

        # Send the file to the SFTP server
        try:
            remote_path = f"{local_sftp_folder_name}/{remote_filename}"
            with sftp_conn_local.open(remote_path, 'w') as remote_file:
                remote_file.write(buffer.getvalue())  # Write buffer content to SFTP server
            logging.info(f"Successfully replicated Big Query table {remote_filename} to SFTP server at {remote_path}.")
        except Exception as e:
            logging.error(f"Error replicating {remote_filename} Big Query table to SFTP {remote_path}: {str(e)}")
            raise AirflowException


        



