import math
import typing as T

from geopy.geocoders import Nominatim

METERS_PER_MILE = 1609.34
METERS_PER_KILOMETER = 1000.0


class Coordinates(T.TypedDict):
    latitude: float
    longitude: float


class Viewport(T.TypedDict):
    low: Coordinates
    high: Coordinates


class SearchGrid(T.TypedDict):
    center: Coordinates
    viewport: Viewport
    width_meters: float


def extract_city(address: str) -> T.Optional[str]:
    """
    Given an address, extract the city from it.
    The address is expected to be a comma-separated string.
    Example:
        1340, Saint Nicholas Avenue, Washington Heights, Manhattan Community Board 12,
        Manhattan, City of New York, New York County, New York, 10033, United States
    """
    parts = address.split(",")
    city = None
    zip_code_index: T.Optional[int] = None

    for i, part in enumerate(parts):
        part = part.strip()
        if "City of " in part:
            city = part[len("City of ") :].strip()
            break
        if part.isnumeric() and len(part) == 5 and i > 1:
            zip_code_index = i

    if not city and zip_code_index:
        # If none of the recognizable keywords are found,
        # assume city is 3 parts before the zip code
        city = parts[zip_code_index - 3].strip() if zip_code_index - 3 >= 0 else None

        if city is None:
            return None

        if "County" in city:
            return None

        if any(char.isdigit() for char in city):
            return None

    return city


def meters_to_miles(meters: float) -> float:
    return meters / METERS_PER_MILE


def miles_to_meters(miles: float) -> float:
    return miles * METERS_PER_MILE


def get_city_center_coordinates(city_name: str) -> T.Optional[T.Tuple[float, float]]:
    geolocator = Nominatim(user_agent="tgtg")

    location = geolocator.geocode(city_name)

    if not location:
        return None

    return (location.latitude, location.longitude)


def meters_to_degrees_latitude(meters: float) -> float:
    """Convert miles to degrees latitude."""
    return meters / 111139.0


def meters_to_degrees_longitude(meters: float, latitude: float) -> float:
    """Convert miles to degrees longitude at a given latitude."""
    earth_radius_meters = 6378137.0
    radians_latitude = math.radians(latitude)
    # Calculate the radius of a circle at the given latitude
    meters_per_degree = (
        math.cos(radians_latitude) * math.pi * earth_radius_meters / 180.0
    )
    return meters / meters_per_degree


def meters_to_degress(meters: float, center_lat: float) -> T.Tuple[float, float]:
    """
    Given a distance in meters and a center latitude, calculate the number of degrees
    in latitude and longitude that correspond to the radius.
    """
    lat_adjustment = meters_to_degrees_latitude(meters)
    lon_adjustment = meters_to_degrees_longitude(meters, center_lat)
    return lat_adjustment, lon_adjustment


def get_viewport(
    center_lat: float, center_lon: float, radius_meters: float
) -> Viewport:
    """
    Given a center (lat, lon) and radius in meters, calculate a viewport.
    Where the low is the bottom left corner and the high is the top right corner.
    """
    lat_adjustment, lon_adjustment = meters_to_degress(radius_meters, center_lat)

    low_lat = max(-90, center_lat - lat_adjustment)
    high_lat = min(90, center_lat + lat_adjustment)
    low_lon = center_lon - lon_adjustment
    high_lon = center_lon + lon_adjustment

    # Handle longitude wraparound
    if low_lon < -180:
        low_lon += 360
    if high_lon > 180:
        high_lon -= 360

    return {
        "low": {"latitude": low_lat, "longitude": low_lon},
        "high": {"latitude": high_lat, "longitude": high_lon},
    }
