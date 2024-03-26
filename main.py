# main.py
from _datetime import datetime

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import time
from utils import KelvinToCelsius, TimeDiffText
from weather import get_weather, get_forecast

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World", "date": datetime.now()}


class WeatherPayload(BaseModel):
    lat: float
    lon: float
    pump_flow_rate_per_min: int
    area_in_sq_meter: int


@app.post("/weather")
async def create_item(item: WeatherPayload):
    api_key = '6bb9fd6e797f57d46d315f6d1683ff65'

    forecast_data = get_forecast(api_key, item.lat, item.lon)
    weather_data = get_weather(api_key, item.lat, item.lon)

    if forecast_data is None:
        raise HTTPException(status_code=503, detail="Weather data not available")

    # Extract precipitation data and calculate total water
    total_rain_hour = 0
    total_water_rate = 0
    crop_water_requirement = 1  # TODO . Will replace with proper value

    for forecast in forecast_data['list']:
        if 'rain' in forecast:
            if '3h' in forecast['rain']:
                total_water_rate += forecast['rain']['3h']
                total_rain_hour += 3  # cause , 3hours forecast

    total_water_requirement = crop_water_requirement * item.area_in_sq_meter * 1000
    total_rain_water = round(total_water_rate * item.area_in_sq_meter * total_rain_hour,0)
    total_water_need = round(total_water_requirement - total_rain_water,0)
    total_pump_time = TimeDiffText(total_water_need / item.pump_flow_rate_per_min)

    message = ""
    if total_water_need == 0 and total_rain_water > 0:
        message = "No need to irrigate.It will be raining"
    elif total_water_need > 0 and total_rain_water == 0:
        message = "Need to irrigate.It won't be raining"
    elif total_water_need > 0 and total_rain_water > 0:
        message = "Need to irrigate just sometime.Cause,It will be raining too"
    elif total_water_need < 0:
        message = "Need to irrigate.Also,It will be raining more than need"

    return {
        "message": message,
        "location": forecast_data['city']['name'],
        "current_temperature": round(KelvinToCelsius(weather_data['main']['temp']), 2),
        "temperature_unit": "celsius",
        "last_update": TimeDiffText(time.time() - weather_data['dt']),
        "sunrise": datetime.fromtimestamp(forecast_data['city']['sunrise']),
        "sunset": datetime.fromtimestamp(forecast_data['city']['sunset']),
        "water_unit": "liters",
        "total_water_requirement": total_water_requirement,
        "total_rain_water": round(total_rain_water, 2),
        "total_water_need": total_water_need,
        "total_pump_time": total_pump_time
    }
