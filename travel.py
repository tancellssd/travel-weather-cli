import requests
import logging
from typing import Any

logging.basicConfig(filename='travel.log', level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

def main() -> None:
    destination = input("Enter the location: ").strip().title()
    if not destination:
        print("Please enter a destination")
        return
    
    location = get_location(destination)

    if not location or not location.get("results"):
        print("Destination not found.")
        return
    
    result = location["results"][0]
    name =  result["name"]
    country = result.get("country", "Unknown")
    country_code = result.get("country_code")
    latitude = result["latitude"]
    longitude = result["longitude"]

    weather = get_weather(latitude, longitude)

    if not weather or "current" not in weather:
        print("Could not retrieve weather information.")
        return
    
    description = get_description(weather["current"].get("weather_code"))
    temperature = weather["current"].get("temperature_2m")

    info = get_info(country_code)

    if not info:
        print("Could not retrieve country information.")
        return

    languages = info.get("languages", [])
    language_names = [language["name"] for language in languages]

    print(f"Destination: {name}, {country}")
    print(f"Region: {info.get('region')}")
    print(f"Longitude: {longitude}")
    print(f"Latitude: {latitude}")
    print(f"Temperature: {temperature}°C")
    print(f"Weather: {description}")
    print(f"Languages: {', '.join(language_names)}")

    logging.info(f"Fetched weather for {name}, {country} ({latitude}, {longitude})")

def get_location(destination: str) -> dict[str, Any] | None:
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    try:
        response = requests.get(geocoding_url, params={"name": destination,
        "count": 1,
        "language": "en",
        "format": "json"}, 
        timeout=10)

        response.raise_for_status()

        data = response.json()

        return data
    
    except requests.exceptions.HTTPError:
        print("The API returned an error")
        logging.error("The API returned an error")
    except requests.exceptions.Timeout:
        print("The request took too long. Please try again.")
        logging.error("The request took too long. Please try again.")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API")
        logging.error("Could not connect to the API")
    except requests.exceptions.RequestException as e:
        print(f"Something went wrong with the request: {e}")
        logging.error(f"Something went wrong with the request: {e}")
    except ValueError:
        print("The API returned invalid JSON.")
        logging.error("The API returned invalid JSON.")

    return None

def get_weather(latitude: float, longitude: float) -> dict[str, Any] | None :
    weather_url =  "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current" : "temperature_2m,weather_code"
    }
    try:
        response = requests.get(weather_url, params=params, timeout=10)

        response.raise_for_status()

        data = response.json()

        return data

    except requests.exceptions.HTTPError:
        print("The weather API returned an error.")
        logging.error("The weather API returned an HTTP error.")
    except requests.exceptions.Timeout:
        print("The weather request took too long")
        logging.error("The weather request took too long.")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the weather API.")
        logging.error("Could not connect to the weather API.")
    except requests.exceptions.RequestException as e:
        print(f"Something went wrong with the weather request: {e}")
        logging.error(f"Weather request error: {e}")
    except ValueError:
        print("The weather API returned invalid JSON.")
        logging.error("The weather API returned invalid JSON.")

    return None
    
def get_description(code: int | None) -> str:
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    if code is None:
        return "Unknown weather condition"
    return descriptions.get(code, "Unknown weather condition")

def get_info(country: str | None) -> dict[ str, Any] | None:
    if not country:
        return None
    try:
        info_url = f"https://countries.dev/alpha/{country}"

        response = requests.get(info_url,params={"fields": "region,languages"}, timeout=10)

        response.raise_for_status()

        data = response.json()

        return data

    except requests.exceptions.HTTPError:
        print("The country information API returned an error.")
        logging.error("The country information API returned an error.")
    except requests.exceptions.Timeout:
        print("The country information request took too long")
        logging.error("The country information request took too long.")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the country information API.")
        logging.error("Could not connect to the country information API.")
    except requests.exceptions.RequestException as e:
        print(f"Something went wrong with the country information request: {e}")
        logging.error(f"Country information request error: {e}")
    except ValueError:
        print("The country information API returned invalid JSON.")
        logging.error("The country information API returned invalid JSON.")

    return None

if __name__ == "__main__":
    main()