# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (useful for some packages like numpy, pandas, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt first to leverage Docker caching
COPY requirements.txt /app/

# Install the dependencies inside the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . /app

# Create a logs directory for the pipeline
RUN mkdir -p /app/logs

# Set environment variables (optional: can be used to configure Airflow or other services)
#ENV AIRFLOW_HOME=/app/airflow

# Expose the port that Airflow web server or other services will run on (if needed)
EXPOSE 8080

# Run Airflow or your Python script
CMD ["python", "/app/sftp_operations.py"]


#Command to run
# sudo docker run --network host \
#     -v /home/g2015samtaylor/icef-437920.json:/app/icef-437920.json \
#     -v /home/g2015samtaylor/airflow/git_directory/SFTP_Migrations/logs/sftp_testing.log:/app/logs/sftp_testing.log \
#     sftp_migrations

