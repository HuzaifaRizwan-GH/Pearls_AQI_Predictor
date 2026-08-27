import os
import joblib
import requests
import pandas as pd
import hopsworks
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI, HTTPException

# Resolve .env path
env_path = Path(__file__).resolve().parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"

load_dotenv(dotenv_path=env_path)
os.environ["HOPSWORKS_CLIENT_CERT_FOLDER"] = "E:\\tmp"

app = FastAPI(title="Karachi AQI Prediction Service", version="1.0")

# Open-Meteo Endpoints for Karachi
LATITUDE, LONGITUDE = 24.8607, 67.0011
WEATHER_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,precipitation&timezone=Asia%2FKarachi"
AIR_QUALITY_URL = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LATITUDE}&longitude={LONGITUDE}&current=pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone&timezone=Asia%2FKarachi"

model_cache = None

def get_model():
    global model_cache
    if model_cache is None:
        api_key = os.getenv("HOPSWORKS_API_KEY")
        if not api_key:
            raise ValueError("HOPSWORKS_API_KEY missing in .env")
            
        project = hopsworks.login(
            project="huzzproj10p",
            host="eu-west.cloud.hopsworks.ai",
            api_key_value=api_key
        )
        mr = project.get_model_registry()
        model_meta = mr.get_model("karachi_aqi_72h_forecaster", version=1)
        model_dir = model_meta.download()
        model_cache = joblib.load(os.path.join(model_dir, "aqi_ridge_model.pkl"))
    return model_cache

def get_live_features():
    w_res = requests.get(WEATHER_URL).json()['current']
    aq_res = requests.get(AIR_QUALITY_URL).json()['current']
    
    timestamp = pd.to_datetime(w_res['time'])
    pm2_5_val = float(aq_res.get('pm2_5', 0.0))
    calculated_aqi = int(pm2_5_val * 1.5) if pm2_5_val else 50
    
    df = pd.DataFrame([{
        'time': timestamp,
        'pm2_5': pm2_5_val,
        'pm10': float(aq_res.get('pm10', 0.0)),
        'carbon_monoxide': float(aq_res.get('carbon_monoxide', 0.0)),
        'nitrogen_dioxide': float(aq_res.get('nitrogen_dioxide', 0.0)),
        'sulphur_dioxide': float(aq_res.get('sulphur_dioxide', 0.0)),
        'ozone': float(aq_res.get('ozone', 0.0)),
        'temperature_2m': float(w_res.get('temperature_2m', 0.0)),
        'relative_humidity_2m': float(w_res.get('relative_humidity_2m', 0)),
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
    return df

@app.get("/")
def home():
    return {"message": "Karachi 72-Hour AQI Forecasting API is running!"}

@app.get("/predict")
def predict():
    try:
        model = get_model()
        df = get_live_features()
        
        feature_cols = [c for c in df.columns if c not in ['aqi_72h', 'time']]
        latest_features = df[feature_cols]
        
        if hasattr(model, "feature_names_in_"):
            for col in model.feature_names_in_:
                if col not in latest_features.columns:
                    latest_features[col] = latest_features.get('aqi', 50.0)
            latest_features = latest_features[model.feature_names_in_]
            
        pred_72h = float(model.predict(latest_features)[0])
        curr_aqi = float(df['aqi'].iloc[0])
        
        pred_24h = curr_aqi + (pred_72h - curr_aqi) * (24 / 72)
        pred_48h = curr_aqi + (pred_72h - curr_aqi) * (48 / 72)
        
        return {
            "status": "success",
            "observation_time": str(df['time'].iloc[0]),
            "current_aqi": round(curr_aqi, 2),
            "forecast_24h": round(pred_24h, 2),
            "forecast_48h": round(pred_48h, 2),
            "forecast_72h": round(pred_72h, 2),
            "weather": {
                "temperature": df['temperature_2m'].iloc[0],
                "humidity": df['relative_humidity_2m'].iloc[0],
                "wind_speed": df['wind_speed_10m'].iloc[0]
            },
            "pollutants": {
                "pm2_5": df['pm2_5'].iloc[0],
                "pm10": df['pm10'].iloc[0],
                "ozone": df['ozone'].iloc[0],
                "no2": df['nitrogen_dioxide'].iloc[0],
                "so2": df['sulphur_dioxide'].iloc[0]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))