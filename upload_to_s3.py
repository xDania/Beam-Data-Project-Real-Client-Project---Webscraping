import boto3
import sys
import io
import pandas as pd

# Set your AWS credentials
aws_access_key_id = ''
aws_secret_access_key = ''

# Set your S3 bucket name
s3_bucket_name = 'rcp-input'

# Set the key (filename) for your CSV file in S3
s3_key = 'output.csv'

# Read the CSV data from the command line argument
csv_data = sys.argv[1]

# Convert CSV data to DataFrame
csv_buffer = io.StringIO(csv_data)
df = pd.read_csv(csv_buffer)

# Create an S3 client
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Upload the CSV file to S3
s3_client.put_object(
    Bucket=s3_bucket_name,
    Key=s3_key,
    Body=csv_data.encode(),  # Ensure it's encoded as bytes
    ContentType='text/csv'
)

print("CSV file uploaded to S3 successfully.")
