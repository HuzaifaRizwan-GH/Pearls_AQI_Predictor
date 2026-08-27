import os
import joblib
import requests
import pandas as pd
import hopsworks
from dotenv import load_dotenv
from pathlib import Path

# 1. Resolve .env path
env_path = Path(__file__).resolve().parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"

load_dotenv(dotenv_path=env_path)
os.environ["HOPSWORKS_CLIENT_CERT_FOLDER"] = "E:\\tmp"

# Open-Meteo API Endpoints for Karachi
LATITUDE, LONGITUDE = 24.8607, 67.0011
WEATHER_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,precipitation&timezone=Asia%2FKarachi"
AIR_QUALITY_URL = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LATITUDE}&longitude={LONGITUDE}&current=pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone&timezone=Asia%2FKarachi"

def load_latest_model():
    """Fetches the registered Ridge model from Hopsworks Model Registry."""
    api_key = os.getenv("HOPSWORKS_API_KEY")
    if not api_key:
        raise ValueError(f"HOPSWORKS_API_KEY not found! Checked path: {env_path}")
        
    project = hopsworks.login(
        project="huzzproj10p",
        host="eu-west.cloud.hopsworks.ai",
        api_key_value=api_key
    )
    mr = project.get_model_registry()
    model_meta = mr.get_model("karachi_aqi_72h_forecaster", version=1)
    model_dir = model_meta.download()
    model = joblib.load(os.path.join(model_dir, "aqi_ridge_model.pkl"))
    return model

def fetch_current_features():
    """Fetches live current hour metrics to form an inference row."""
    w_res = requests.get(WEATHER_URL).json()['current']
    aq_res = requests.get(AIR_QUALITY_URL).json()['current']
    
    timestamp = pd.to_datetime(w_res['time'])
    pm2_5_val = float(aq_res.get('pm2_5', 0.0))
    calculated_aqi = int(pm2_5_val * 1.5) if pm2_5_val else 50
    
    live_df = pd.DataFrame([{
        'time': timestamp,
        'pm2_5': pm2_5_val,
        'pm10': float(aq_res.get('pm10', 0.0)),
        'carbon_monoxide': float(aq_res.get('carbon_monoxide', 0.0)),
        'nitrogen_dioxide': float(aq_res.get('nitrogen_dioxide', 0.0)),
        'sulphur_dioxide': float(aq_res.get('sulphur_dioxide', 0.0)),
        'ozone': float(aq_res.get('ozone', 0.0)),
        'temperature_2m': float(w_res.get('temperature_2m', 0.0)),
        'relative_humidity_2m': float(w_curr.get('relative_humidity_2m', 0)) if 'w_curr' in locals() else float(w_res.get('relative_humidity_2m', 0)),
        'surface_pressure': float(w_res.get('surface_pressure', 0.0)),
        'wind_speed_10m': float(w_res.get('wind_speed_10m', 0.0)),
        'precipitation': float(w_res.get('precipitation', 0.0)),
        'hour': int(timestamp.hour),
        'day': int(timestamp.day),
        'month': int(timestamp.month),
        'day_of_week': int(timestamp.dayofweek),
        'pm2_5_change': 0.0,
        'pm10_change': 0.0,
        'pm2_5_change_rate': 0.0,
        'pm10_change_rate': 0.0,
        'aqi': calculated_aqi,
        'aqi_change': 0.0,
        'aqi_change_rate': 0.0
    }])
    return live_df

def generate_forecast():
    # 1. Load model from registry
    model = load_latest_model()
    
    # 2. Get current live features
    df = fetch_current_features()
    
    # Exclude timestamp for feature vector input
    feature_cols = [c for c in df.columns if c not in ['aqi_72h', 'time']]
    latest_features = df[feature_cols]
    
    # Align columns matching model fit time
    if hasattr(model, "feature_names_in_"):
        # Fill missing features (like lag features) with current values to preserve alignment
        for col in model.feature_names_in_:
            if col not in latest_features.columns:
                latest_features[col] = latest_features.get('aqi', 50.0)
        latest_features = latest_features[model.feature_names_in_]
    
    # 3. Predict 72-hour future AQI
    prediction = model.predict(latest_features)[0]
    latest_time = df['time'].iloc[-1]
    forecast_time = latest_time + pd.Timedelta(hours=72)
    
    print("\n==================================================")
    print(f" Current Observation Time : {latest_time}")
    print(f" Target Forecast Time      : {forecast_time}")
    print(f" Predicted 72-Hour AQI     : {prediction:.2f}")
    print("==================================================")
    return prediction, forecast_time

if __name__ == "__main__":
    generate_forecast()