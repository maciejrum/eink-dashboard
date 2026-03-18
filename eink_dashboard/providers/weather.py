import json

from eink_dashboard.config import AppConfig, WMO_DESCRIPTIONS
from eink_dashboard.http import fetch_bytes


def get_weather(config: AppConfig) -> dict[str, object]:
    location = config.location
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={location.lat}&longitude={location.lon}"
        "&current=temperature_2m,relative_humidity_2m,weather_code"
        f"&timezone={location.timezone}"
    )
    data = json.loads(fetch_bytes(url, user_agent=config.user_agent).decode("utf-8"))
    current = data.get("current", {})
    code = current.get("weather_code")

    return {
        "temp": current.get("temperature_2m"),
        "hum": current.get("relative_humidity_2m"),
        "desc": WMO_DESCRIPTIONS.get(code, f"code {code}"),
    }

