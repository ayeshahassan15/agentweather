# Create the settings file
# What it is: one place that stores facts we use everywhere (the city name, coordinates, timezone).
# Instead of typing Karachi’s coordinates in ten different files, every file reads them from here.
# If we ever change something, we change it once.


import os
from dotenv import load_dotenv

# Reads your secret keys from the .env file
load_dotenv()

# Our city
CITY = "Karachi"
LAT = 24.8607
LON = 67.0011
TIMEZONE = "Asia/Karachi"

# Secret key, loaded from .env (never typed here)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


# This part only runs when we run this file directly, as a quick test
if __name__ == "__main__":
    print(CITY, LAT, LON, TIMEZONE)
    print("OpenWeather key loaded:", OPENWEATHER_API_KEY is not None)