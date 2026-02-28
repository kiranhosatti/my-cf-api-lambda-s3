import json
import urllib.request
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    url = "https://api.github.com"

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    response = urllib.request.urlopen(req)
    data = response.read().decode("utf-8")

    s3 = boto3.client("s3")
    bucket = os.environ["BUCKET_NAME"]

    filename = f"api-data-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

    s3.put_object(
        Bucket=bucket,
        Key=filename,
        Body=data
    )

    return {
        "statusCode": 200,
        "body": "Data saved to S3"
    }