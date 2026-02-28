import json
import csv
import io
import urllib.request
import boto3
import os
from datetime import datetime

def fetch_weather(city):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={city['latitude']}&longitude={city['longitude']}"
        f"&current=temperature_2m,windspeed_10m,weathercode,relative_humidity_2m"
        f"&timezone=auto"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    response = urllib.request.urlopen(req)
    weather = json.loads(response.read().decode("utf-8"))

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": city["name"],
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "temperature_c": weather["current"]["temperature_2m"],
        "windspeed_kmh": weather["current"]["windspeed_10m"],
        "humidity": weather["current"]["relative_humidity_2m"],
        "weather_code": weather["current"]["weathercode"]
    }

def lambda_handler(event, context):
    cities = event.get("cities", [])

    if not cities:
        return {
            "statusCode": 400,
            "body": "No cities provided. Pass cities in the event."
        }

    results = [fetch_weather(city) for city in cities]

    s3 = boto3.client("s3")
    bucket = os.environ["BUCKET_NAME"]
    date_prefix = datetime.now().strftime("%Y%m%d%H%M%S")

    # Save JSON
    s3.put_object(
        Bucket=bucket,
        Key=f"weather-{date_prefix}.json",
        Body=json.dumps(results, indent=2)
    )

    # Save CSV
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

    s3.put_object(
        Bucket=bucket,
        Key=f"weather-{date_prefix}.csv",
        Body=csv_buffer.getvalue()
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Weather data saved", "cities": len(results)})
    }