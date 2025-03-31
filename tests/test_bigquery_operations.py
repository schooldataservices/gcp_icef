# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import pytest
# from unittest.mock import patch, MagicMock
# from bigquery_operations import upload_to_bigquery

# @patch("bigquery_operations.initial_schema_check")
# @patch("bigquery_operations.Create")
# def test_upload_to_bigquery_success(mock_create, mock_initial_schema_check, caplog, tmp_path):
#     # Use pytest's tmp_path fixture to create a temporary directory
#     local_dir = tmp_path / "test_dir"
#     local_dir.mkdir()  # Create the directory

#     # Assert that the directory exists
#     assert local_dir.exists(), f"Directory {local_dir} was not created"

#     # Mock environment variables
#     os.environ["SFTP_FOLDER_NAME"] = "test_folder"
#     os.environ["LOCAL_DIR"] = str(local_dir)
#     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/sam/icef-437920.json"

#     # Mock initial_schema_check return value
#     mock_initial_schema_check.return_value = "processed_folder"

#     # Mock Create instance and process method
#     mock_instance = MagicMock()
#     mock_create.return_value = mock_instance

#     # Call the function
#     upload_to_bigquery()

#     # Assertions
#     mock_initial_schema_check.assert_called_once_with("test_folder")
#     mock_create.assert_called_once_with(
#         project_id="icef-437920",
#         location="us-west1",
#         bucket="processed_folderbucket-icefschools-1",
#         local_dir=str(local_dir),
#         db="processed_folder",
#         append_or_replace="replace",
#     )
#     mock_instance.process.assert_called_once()

#     # Check logs
#     assert "Using Google Application Credentials: /home/sam/icef-437920.json" in caplog.text
#     assert "Processing folder: test_folder" in caplog.text
#     assert "Process has reached the end" in caplog.text


# def test_upload_to_bigquery_missing_env_vars(caplog):
#     # Clear environment variables
#     os.environ.pop("SFTP_FOLDER_NAME", None)
#     os.environ.pop("LOCAL_DIR", None)
#     os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

#     # Call the function
#     upload_to_bigquery()

#     # Check logs for errors
#     assert "Environment variables SFTP_FOLDER_NAME or LOCAL_DIR are not set!" in caplog.text
#     assert "Google application credentials path is not set!" in caplog.text