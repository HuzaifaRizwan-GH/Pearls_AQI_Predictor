import requests
import pandas as pd
from datetime import date, timedelta


# Karachi coordinates
LATITUDE = 24.8607
LONGITUDE = 67.0011

# Historical period
END_DATE = date.today() - timedelta(days=1)
START_DATE = END_DATE - timedelta(days=89)

# Open-Meteo Historical Weather API
WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"

# Open-Meteo Historical Air Quality API
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def fetch_weather():
    """Fetch historical weather data from Open-Meteo."""

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE.isoformat(),
        "end_date": END_DATE.isoformat(),
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "surface_pressure,"
            "wind_speed_10m,"
            "precipitation"
        ),
        "timezone": "Asia/Karachi",
    }

    response = requests.get(WEATHER_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def fetch_air_quality():
    """Fetch historical pollutant data from Open-Meteo."""

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE.isoformat(),
        "end_date": END_DATE.isoformat(),
        "hourly": (
            "pm2_5,"
            "pm10,"
            "carbon_monoxide,"
            "nitrogen_dioxide,"
            "sulphur_dioxide,"
            "ozone"
        ),
        "timezone": "Asia/Karachi",
    }

    response = requests.get(AIR_QUALITY_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def main():

    print("Starting historical backfill...")
    print(f"Location: Karachi")
    print(f"Start date: {START_DATE}")
    print(f"End date: {END_DATE}")

    # Fetch data
    weather_data = fetch_weather()
    air_data = fetch_air_quality()

    # Convert weather data to DataFrame
    weather_hourly = weather_data["hourly"]

    weather_df = pd.DataFrame(weather_hourly)

    # Convert air-quality data to DataFrame
    air_hourly = air_data["hourly"]

    air_df = pd.DataFrame(air_hourly)

    # Merge using timestamp
    df = pd.merge(
        air_df,
        weather_df,
        on="time",
        how="inner"
    )

    # Sort chronologically
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    # Save historical raw data
    output_file = "data/historical_raw_data.csv"

    df.to_csv(output_file, index=False)

    print("\nHistorical backfill successful!")
    print(f"Rows collected: {len(df)}")
    print(f"Columns collected: {list(df.columns)}")
    print(f"Historical data saved to: {output_file}")


if __name__ == "__main__":
    main()