from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

# In-memory database to store city names
cities = set()

# API endpoints
WORLD_TIME_API = "http://worldtimeapi.org/api/timezone"
WEATHER_API_URL = "https://app.swaggerhub.com/apis/student-73c/Weather/1.0.0"


@app.post("/city/")
def create_city(city: str):
    city = city.strip().lower()
    if city in cities:
        raise HTTPException(status_code=400, detail="City already exists")
    cities.add(city)
    return {"message": "City added successfully", "city": city}


@app.get("/city/{city}")
def get_city(city: str):
    city = city.strip().lower()
    if city not in cities:
        raise HTTPException(status_code=404, detail="City not found")
    return fetch_city_data(city)


@app.delete("/city/{city}")
def delete_city(city: str):
    city = city.strip().lower()
    if city not in cities:
        raise HTTPException(status_code=404, detail="City not found")
    cities.remove(city)
    return {"message": "City deleted successfully"}


@app.get("/cities")
def get_cities():
    if not cities:
        return {"message": "No cities available"}
    return [fetch_city_data(city) for city in cities]


def fetch_city_data(city: str):
    # Get weather data
    weather_response = requests.get(f"{WEATHER_API_URL}/current", params={"query": city})
    if weather_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error fetching weather data")
    weather_data = weather_response.json()
    timezone = weather_data.get("location", {}).get("timezone_id", "Unknown")
    
    # Get world time data
    time_response = requests.get(f"{WORLD_TIME_API}/{timezone}")
    if time_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error fetching time data")
    time_data = time_response.json()
    current_time = time_data.get("datetime", "N/A")
    
    return {
        "city": city,
        "timezone": timezone,
        "current_time": current_time,
        "weather": weather_data.get("current", {})
    }

# To run this API use: uvicorn filename:app --reload
