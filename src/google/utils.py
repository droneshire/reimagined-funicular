import typing as T

from geopy.geocoders import Nominatim

METERS_PER_MILE = 1609.34
METERS_PER_KILOMETER = 1000.0

ALL_FIELDS = [
    "places.formattedAddress",
    "places.displayName",
    "places.nationalPhoneNumber",
    "places.location",
    "places.rating",
    "places.googleMapsUri",
    "places.websiteUri",
    "places.regularOpeningHours",
    "places.businessStatus",
    "places.priceLevel",
    "places.userRatingCount",
    "places.takeout",
    "places.delivery",
    "places.dineIn",
    "places.servesBreakfast",
    "places.primaryTypeDisplayName",
    "places.primaryType",
    "places.editorialSummary",
    "places.outdoorSeating",
    "places.servesCoffee",
    "places.paymentOptions",
    "places.accessibilityOptions",
]

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


class Coordinates(T.TypedDict):
    lat: float
    lng: float


class Viewport(T.TypedDict):
    low: Coordinates
    high: Coordinates


class SearchGrid(T.TypedDict):
    center: Coordinates
    viewport: Viewport
    width_meters: float


def meters_to_miles(meters: float) -> float:
    return meters / METERS_PER_MILE


def miles_to_meters(miles: float) -> float:
    return miles * METERS_PER_MILE


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

    print(address)
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


def get_city_center_coordinates(city_name: str) -> T.Optional[Coordinates]:
    # Initialize the Nominatim geocoder
    geolocator = Nominatim(user_agent="tgtg")

    # Use the geocoder to geocode the city name
    location = geolocator.geocode(city_name)

    if not location:
        return None

    return Coordinates(lat=location.latitude, lng=location.longitude)
