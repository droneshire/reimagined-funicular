import typing as T

from geopy.geocoders import Nominatim

METERS_PER_MILE = 1609.34

TYPES = [
    "restaurant",  # default
    "bakery",
    "sandwich_shop",
    "coffee_shop",
    "cafe",
    "fast_food_restaurant",
    "store",
    "food",
    "point_of_interest",
    "establishment",
]

DEFAULT_TYPE = TYPES[0]


def miles_to_meters(miles: float) -> float:
    return miles * METERS_PER_MILE


def get_city_center_coordinates(city_name: str) -> T.Optional[T.Tuple[float, float]]:
    geolocator = Nominatim(user_agent="itinerary-planner")

    location = geolocator.geocode(city_name)

    if not location:
        return None

    return (location.latitude, location.longitude)
