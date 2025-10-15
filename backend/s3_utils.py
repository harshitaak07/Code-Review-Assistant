import boto3
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_file(file_path: str, s3_key: str) -> str:
    s3_client.upload_file(file_path, S3_BUCKET, s3_key)
    return s3_key

def download_file(s3_key: str, local_path: str) -> str:
    s3_client.download_file(S3_BUCKET, s3_key, local_path)
    return local_path

def upload_text(text: str, s3_key: str) -> str:
    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=text)
    return s3_key

def download_text(s3_key: str) -> str:
    obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
    return obj['Body'].read().decode('utf-8')
