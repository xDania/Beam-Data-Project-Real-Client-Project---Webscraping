# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the required files into the container
COPY run.py .
COPY config_file.toml .
COPY init.sh .
COPY requirements.txt .
COPY upload_to_s3.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Specify the command to run when the container starts
CMD ["python", "run.py"]