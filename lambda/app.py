import json
import csv
import io
import urllib.request
import boto3
import os
from datetime import datetime

def fetch_all_capitals():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,capitalInfo"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    response = urllib.request.urlopen(req)
    countries = json.loads(response.read().decode("utf-8"))

    cities = []
    for country in countries:
        try:
            capital = country["capital"][0]
            lat = country["capitalInfo"]["latlng"][0]
            lon = country["capitalInfo"]["latlng"][1]
            cities.append({
                "name": capital,
                "country": country["name"]["common"],
                "latitude": lat,
                "longitude": lon
            })
        except (KeyError, IndexError):
            continue

    return cities

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
        "city": city["name"],
        "country": city["country"],
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "temperature_c": weather["current"]["temperature_2m"],
        "windspeed_kmh": weather["current"]["windspeed_10m"],
        "humidity": weather["current"]["relative_humidity_2m"],
        "weather_code": weather["current"]["weathercode"]
    }

def lambda_handler(event, context):
    cities = fetch_all_capitals()

    results = []
    for city in cities:
        try:
            results.append(fetch_weather(city))
        except Exception as e:
            print(f"Skipping {city['name']}: {str(e)}")
            continue

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
        "body": json.dumps({
            "message": "Weather data saved",
            "total_cities": len(results)
        })
    }