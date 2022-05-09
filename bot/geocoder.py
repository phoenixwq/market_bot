import requests

base_url = "https://nominatim.openstreetmap.org/"


def search_by_query(q: str):
    url = base_url + f"search?q={q}&format=json&addressdetails=1&limit=1"
    data = requests.get(url).json()
    if not data:
        return None
    data = data[0]

    return {
        "lat": float(data["lat"]),
        "lon": float(data["lon"]),
    }


def get_city_by_coords(lat: float, lon: float):
    url = base_url + f"reverse?lat={lat}&lon={lon}&format=geojson"
    response = requests.get(url=url)
    try:
        city = response.json().get("features")[0].get("properties").get("address").get("city")
    except AttributeError:
        return None
    return city
