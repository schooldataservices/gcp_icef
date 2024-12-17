import logging
import json
import os
import pysftp
from queue import Queue
from threading import Lock
import re
from .sftp_configs import json_file_path

from airflow.exceptions import AirflowException

def clear_logging_handlers():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

def configure_logging():
    logging.basicConfig(
        filename='logs/SFTP_operations.log',
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%d-%b-%y %H:%M:%S'
    )
    logging.info('\n\n-------------New SFTP Operations Logging Instance')


class SFTPConnection:
    default_cnopts = pysftp.CnOpts()
    default_cnopts.hostkeys = None

    def __init__(self, host, username, password, port=22, max_connections=5, use_pool=True, cnopts=None):
        self.host = host
        self.username = username
        self.password = password
        self.port = port  # Add port
        self.max_connections = max_connections
        self.use_pool = use_pool
        self.cnopts = cnopts or self.default_cnopts
        if use_pool:
            self.pool = Queue(max_connections)
            self.lock = Lock()
            self._initialize_pool()
        else:
            self.pool = None
            self.lock = None

    def _initialize_pool(self):
        for _ in range(self.max_connections):
            self.pool.put(self._create_new_connection())

    def _create_new_connection(self):
        return pysftp.Connection(
            host=self.host,
            username=self.username,
            password=self.password,
            port=self.port,  # Pass the port to the connection
            cnopts=self.cnopts
        )
    
    def close_connection(self, conn):
        try:
            conn.close()
            logging.info('SFTP connection closed')
        except Exception as e:
            logging.error(f"Error closing SFTP connection: {e}")
            raise AirflowException(f"Failed to close SFTP connection: {e}")

    def get_connection(self):
        if self.use_pool:
            with self.lock:
                if self.pool.empty():
                    return self._create_new_connection()
                return self.pool.get()
        else:
            return self._create_new_connection()

    def return_connection(self, conn):
        if self.use_pool:
            with self.lock:
                if self.pool.full():
                    conn.close()
                else:
                    self.pool.put(conn)
        else:
            conn.close()

    def close_all_connections(self):
        if self.use_pool:
            while not self.pool.empty():
                conn = self.pool.get()
                conn.close()
                logging.info('All SFTP connections closed from the pool')

    @classmethod
    def load_credentials(cls):
        """Loads credentials from a JSON file."""
        logging.info(f"JSON file path: {json_file_path}")
        try:
            with open(json_file_path) as json_file:
                credentials = json.load(json_file)
            logging.info("Credentials loaded successfully.")
            return credentials
        except Exception as e:
            logging.error(f"Error loading credentials: {e}")
            raise AirflowException(f"Failed to load credentials: {e}")
    
    @classmethod
    def setup_sftp_connection(cls, type_):
        logging.info(f'\n\n\n\Attempting to setup SFTP connection for {type_}')

        if not type_:
            logging.info("No type provided for SFTP connection. Skipping setup.")
            return None  # Skip connection setup if no type is provided

        creds = cls.load_credentials()
        if creds is None:
            raise AirflowException("Credentials are required to establish SFTP connection.")

        # Build connection details using a dictionary comprehension
        connections = {
            match.group(1): creds[key]
            for key in creds
            if (match := re.match(rf"{type_}_(host|username|password|port)", key))  # Include port in regex
        }

        # Extract port, defaulting to 22 if not present
        port = int(connections.get('port', 22))

        # Validate the connections
        if any(key not in connections for key in ['host', 'username', 'password']):
            logging.error(f'Invalid or incomplete credentials for {type_}: {connections}')
            raise AirflowException("Invalid or incomplete credentials.")

        # Create and return the SFTPConnection instance
        return cls(
            host=connections['host'],
            username=connections['username'],
            password=connections['password'],
            port=port,  # Pass the port
            use_pool=False
        )

        

# dynamic_sftp_file_exchange to inner_dynamic_file_exchange to SFTP_conn_file_exchange
# to replicate_SFTP_file_to_local replicate_BQ_views_to_local needs to all be OOP
#This will reduce the need for passing variables