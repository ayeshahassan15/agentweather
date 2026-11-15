# Write the first fetch function
# What it is: a function is a named block of code that does one job, so we can reuse it. 
# This one asks Open-Meteo for hourly weather and gives it back as a table
#  (called a DataFrame in pandas, like an Excel sheet where each row is one hour and each 
# column is one measurement).

import requests
import pandas as pd
import config


def fetch_openmeteo_weather():
    """Ask Open-Meteo for hourly weather and return it as a table."""
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": config.LAT,
            "longitude": config.LON,
            "hourly": (
                "temperature_2m,relative_humidity_2m,precipitation,"
                "precipitation_probability,wind_speed_10m,"
                "wind_direction_10m,uv_index"
            ),
            "wind_speed_unit": "ms",
            "past_days": 1,
            "forecast_days": 1,
            "timezone": config.TIMEZONE,
        },
        timeout=15,
    )
    response.raise_for_status()

    table = pd.DataFrame(response.json()["hourly"])
    table["time"] = pd.to_datetime(table["time"])
    return table


def fetch_openmeteo_air_quality():
    """Ask Open-Meteo for hourly air quality and return it as a table."""
    response = requests.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params={
            "latitude": config.LAT,
            "longitude": config.LON,
            "hourly": (
                "us_aqi,pm2_5,pm10,nitrogen_dioxide,"
                "ozone,sulphur_dioxide,carbon_monoxide"
            ),
            "past_days": 1,
            "forecast_days": 1,
            "timezone": config.TIMEZONE,
        },
        timeout=15,
    )
    response.raise_for_status()

    table = pd.DataFrame(response.json()["hourly"])
    table["time"] = pd.to_datetime(table["time"])
    return table


def _to_local_hour(unix_seconds):
    """Turn OpenWeather's time number into a Karachi time, rounded down to the hour."""
    t = pd.to_datetime(unix_seconds, unit="s", utc=True)
    return t.tz_convert(config.TIMEZONE).tz_localize(None).floor("h")


def fetch_openweather_weather():
    """Ask OpenWeather for the current weather and return it as a one-row table."""
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "lat": config.LAT,
            "lon": config.LON,
            "units": "metric",
            "appid": config.OPENWEATHER_API_KEY,
        },
        timeout=15,
    )
    response.raise_for_status()
    d = response.json()

    row = {
        "time": _to_local_hour(d["dt"]),
        "ow_temperature": d["main"]["temp"],
        "ow_humidity": d["main"]["humidity"],
        "ow_wind_speed": d["wind"]["speed"],
        "ow_wind_direction": d["wind"].get("deg"),
        "ow_rain_mm": d.get("rain", {}).get("1h", 0.0),
    }
    return pd.DataFrame([row])


def fetch_openweather_pollution():
    """Ask OpenWeather for the current air pollution and return it as a one-row table."""
    response = requests.get(
        "http://api.openweathermap.org/data/2.5/air_pollution",
        params={
            "lat": config.LAT,
            "lon": config.LON,
            "appid": config.OPENWEATHER_API_KEY,
        },
        timeout=15,
    )
    response.raise_for_status()
    item = response.json()["list"][0]
    gases = item["components"]

    row = {
        "time": _to_local_hour(item["dt"]),
        "ow_aqi_level": item["main"]["aqi"],  # only a 1 to 5 scale
        "ow_pm2_5": gases["pm2_5"],
        "ow_pm10": gases["pm10"],
        "ow_no2": gases["no2"],
        "ow_o3": gases["o3"],
        "ow_so2": gases["so2"],
        "ow_co": gases["co"],
    }
    return pd.DataFrame([row])




# This part only runs when we run this file directly, as a quick test
if __name__ == "__main__":
    pd.set_option("display.max_columns", None)  # show every column

    weather = fetch_openmeteo_weather()
    print("WEATHER size:", weather.shape)
    print(weather.tail(3))

    air = fetch_openmeteo_air_quality()
    print("\nAIR QUALITY size:", air.shape)
    print(air.tail(3))

    ow = fetch_openweather_weather()
    print("\nOPENWEATHER WEATHER size:", ow.shape)
    print(ow)



    pol = fetch_openweather_pollution()
    print("\nOPENWEATHER POLLUTION size:", pol.shape)
    print(pol)