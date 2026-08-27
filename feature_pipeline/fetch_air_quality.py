import os

import pandas as pd
import requests


# Karachi coordinates
LATITUDE = 24.900002
LONGITUDE = 67.0
TIMEZONE = "Asia/Karachi"

# Open-Meteo Air Quality API
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# Open-Meteo Weather API
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# --------------------------------------------------
# 1. Fetch air-quality data
# --------------------------------------------------

air_quality_params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "hourly": (
        "pm2_5,"
        "pm10,"
        "carbon_monoxide,"
        "nitrogen_dioxide,"
        "sulphur_dioxide,"
        "ozone"
    ),
    "timezone": TIMEZONE,
}

air_response = requests.get(
    AIR_QUALITY_URL,
    params=air_quality_params,
    timeout=30,
)

air_response.raise_for_status()

air_data = air_response.json()

air_df = pd.DataFrame(air_data["hourly"])


# --------------------------------------------------
# 2. Fetch weather data
# --------------------------------------------------

weather_params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "hourly": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "surface_pressure,"
        "wind_speed_10m,"
        "precipitation"
    ),
    "timezone": TIMEZONE,
}

weather_response = requests.get(
    WEATHER_URL,
    params=weather_params,
    timeout=30,
)

weather_response.raise_for_status()

weather_data = weather_response.json()

weather_df = pd.DataFrame(weather_data["hourly"])


# --------------------------------------------------
# 3. Combine air quality + weather
# --------------------------------------------------

df = pd.merge(
    air_df,
    weather_df,
    on="time",
    how="inner",
)


# --------------------------------------------------
# 4. Save combined raw data
# --------------------------------------------------

os.makedirs("data", exist_ok=True)

output_file = "data/raw_data.csv"

df.to_csv(output_file, index=False)


# --------------------------------------------------
# 5. Display result
# --------------------------------------------------

print("Data collection successful!")
print(f"Location: Karachi")
print(f"Timezone: {air_data['timezone']}")
print(f"Rows collected: {len(df)}")
print(f"Columns collected: {list(df.columns)}")
print(f"Raw data saved to: {output_file}")