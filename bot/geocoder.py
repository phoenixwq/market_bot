import requests
from typing import Union, Tuple
nominatim_url = "https://nominatim.openstreetmap.org/"


def search_by_query(q: str) -> Union[Tuple[int, int], None]:
    url = nominatim_url + f"search?q={q}&format=json&addressdetails=1&limit=1"
    data = requests.get(url).json()
    if not data:
        return None
    return data[0]["lat"], data[0]["lon"]


def get_city_by_coords(lat: float, lon: float) -> Union[str, None]:
    url = nominatim_url + f"reverse?lat={lat}&lon={lon}&format=geojson"
    response = requests.get(url=url)
    try:
        city = response.json().get("features")[0].get("properties").get("address").get("city")
    except (AttributeError, KeyError):
        return None
    return city
