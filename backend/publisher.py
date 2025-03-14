import boto3

from dotenv import load_dotenv
import os

load_dotenv()

BUCKET_NAME = "yoga-with-friends.com"


def upload_to_s3(local_file, s3_file):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("us-east-2"),
    )

    try:
        s3_client.upload_file(local_file, BUCKET_NAME, s3_file)
        print(f"uploaded: {local_file} to {BUCKET_NAME}/{s3_file}")
    except Exception as e:
        print("Noo!!", e)


if __name__ == "__main__":
    upload_to_s3("../frontend/public/yoga.ics", "yoga_1.ics")
