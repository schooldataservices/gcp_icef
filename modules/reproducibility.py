import pandas as pd
import re
import logging


def read_file(file_path):
    try:
        # Get the file extension
        file_extension = file_path.split('.')[-1].lower()

        # Read the file based on its extension
        if file_extension == 'csv':
            try:
                df = pd.read_csv(file_path, low_memory=False)
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="ISO-8859-1", low_memory=False)

        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(file_path)
        elif file_extension == 'json':
            df = pd.read_json(file_path)
        elif file_extension == 'txt':
            # Example: tab-separated text file
            df = pd.read_csv(file_path, sep='\t', low_memory=False)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        return df

    except Exception as e:
        # Raise a custom error with details
        raise RuntimeError(f"Error reading file {file_path}: {e}") from e


def pre_processing(df):
    # Remove parentheses and content inside
    cleaned_cols = [re.sub(r'\(.*?\)', '', col) for col in df.columns]
    
    # Replace all characters except letters, numbers, and underscores with underscores
    cleaned_cols = [
        re.sub(r'[^A-Za-z0-9_]', '_', col) for col in cleaned_cols
    ]
    
    # Optionally, lowercase and strip leading/trailing underscores
    cleaned_cols = [col.lower().strip('_') for col in cleaned_cols]
    
    df.columns = cleaned_cols

    logging.info(f'Here are the cleaned column names {cleaned_cols}')

    return df

# ----------------------------------------------------

# Bucket names can only contain lowercase letters, numeric characters, 
# dashes ( - ), underscores ( _ ), and dots ( . ). Spaces are not allowed.

# Table names can contain letters (uppercase and lowercase), numbers, and underscores (_). 
# Table names must start with a letter or underscore.

def initial_schema_check(SFTP_folder_name):

    SFTP_folder_name = SFTP_folder_name.lower()
  
    return(SFTP_folder_name)


# ---------------------------------------------------------

def remove_extension_from_file(file_name):

    parts = file_name.split('.')  # Split the filename by dot
    if len(parts) > 1:  # Check if there is an extension
        return '.'.join(parts[:-1])  # Join all parts except the last one
    else:
        return file_name  # If there's no extension, return the original filename



