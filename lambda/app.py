import json
import urllib.request
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=40.7128&longitude=-74.0060"
        "&current=temperature_2m,windspeed_10m,weathercode,relative_humidity_2m"
        "&timezone=auto"
    )

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    response = urllib.request.urlopen(req)
    data = response.read().decode("utf-8")

    weather = json.loads(data)
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": "New York",
        "temperature_c": weather["current"]["temperature_2m"],
        "windspeed_kmh": weather["current"]["windspeed_10m"],
        "humidity": weather["current"]["relative_humidity_2m"],
        "weather_code": weather["current"]["weathercode"]
    }

    s3 = boto3.client("s3")
    bucket = os.environ["BUCKET_NAME"]
    filename = f"weather-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

    s3.put_object(
        Bucket=bucket,
        Key=filename,
        Body=json.dumps(result, indent=2)
    )

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }