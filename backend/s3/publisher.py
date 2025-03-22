import boto3

from dotenv import load_dotenv
import os

load_dotenv()

BUCKET_NAME = "yoga-with-friends.com"


def _get_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("us-east-2"),
    )


def upload_blob_to_s3(blob, file_name):
    s3_client = _get_client()
    try:
        s3_client.put_object(Body=blob, Bucket=BUCKET_NAME, Key=file_name)
        print(f"uploaded: {file_name} to {BUCKET_NAME}/{file_name}")
    except Exception as e:
        print("Noo!!", e)


def upload_file_to_s3(file_name):
    s3_client = _get_client()
    try:
        s3_client.upload_file(file_name, BUCKET_NAME, file_name)
        print(f"uploaded: {file_name} to {BUCKET_NAME}/{file_name}")
    except Exception as e:
        print("Noo!!", e)
