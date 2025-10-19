import requests

# Geocode Utility to find lat/lon from address using OpenStreetMap Nominatim API

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def geocode_address(address):
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }

    try:
        response = requests.get(NOMINATIM_URL, params=params, headers={'User-Agent': 'JeevanDharaApp'})
        response.raise_for_status()
        data = response.json()
        if not data:
            return None

        return {
            "latitude": float(data[0]["lat"]),
            "longitude": float(data[0]["lon"]),
            "display_name": data[0]["display_name"]
        }
    except requests.RequestException as e:
        print(f"Geocoding failed: {e}")
        return None
