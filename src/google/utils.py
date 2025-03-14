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

TABLE_A_TYPES = [
    "car_dealer",
    "car_rental",
    "car_repair",
    "car_wash",
    "electric_vehicle_charging_station",
    "gas_station",
    "parking",
    "rest_stop",
    "farm",
    "art_gallery",
    "museum",
    "performing_arts_theater",
    "library",
    "preschool",
    "primary_school	school",
    "secondary_school",
    "university",
    "amusement_center",
    "amusement_park",
    "aquarium",
    "banquet_hall",
    "bowling_alley",
    "casino",
    "community_center",
    "convention_center",
    "cultural_center",
    "dog_park",
    "event_venue",
    "hiking_area",
    "historical_landmark",
    "marina",
    "movie_rental",
    "movie_theater",
    "national_park",
    "night_club",
    "park",
    "tourist_attraction",
    "visitor_center",
    "wedding_venue",
    "zoo",
    "accounting",
    "atm",
    "bank",
    "american_restaurant",
    "bakery",
    "bar",
    "barbecue_restaurant",
    "brazilian_restaurant",
    "breakfast_restaurant",
    "brunch_restaurant",
    "cafe",
    "chinese_restaurant",
    "coffee_shop",
    "fast_food_restaurant",
    "french_restaurant",
    "greek_restaurant",
    "hamburger_restaurant",
    "ice_cream_shop",
    "indian_restaurant",
    "indonesian_restaurant",
    "italian_restaurant",
    "japanese_restaurant",
    "korean_restaurant	lebanese_restaurant",
    "meal_delivery",
    "meal_takeaway",
    "mediterranean_restaurant",
    "mexican_restaurant",
    "middle_eastern_restaurant",
    "pizza_restaurant",
    "ramen_restaurant",
    "restaurant",
    "sandwich_shop",
    "seafood_restaurant",
    "spanish_restaurant",
    "steak_house",
    "sushi_restaurant",
    "thai_restaurant",
    "turkish_restaurant",
    "vegan_restaurant",
    "vegetarian_restaurant",
    "vietnamese_restaurant",
    "administrative_area_level_1",
    "administrative_area_level_2",
    "country	locality",
    "postal_code",
    "school_district",
    "city_hall",
    "courthouse",
    "embassy",
    "fire_station	",
    "local_government_office",
    "police",
    "post_office",
    "dental_clinic",
    "dentist",
    "doctor",
    "drugstore",
    "hospital	medical_lab",
    "pharmacy",
    "physiotherapist",
    "spa",
    "bed_and_breakfast",
    "campground",
    "camping_cabin",
    "cottage",
    "extended_stay_hotel",
    "farmstay",
    "guest_house	hostel",
    "hotel",
    "lodging",
    "motel",
    "private_guest_room",
    "resort_hotel",
    "rv_park",
    "church",
    "hindu_temple",
    "mosque",
    "synagogue",
    "barber_shop",
    "beauty_salon",
    "cemetery",
    "child_care_agency",
    "consultant",
    "courier_service",
    "electrician",
    "florist",
    "funeral_home",
    "hair_care",
    "hair_salon",
    "insurance_agency	",
    "laundry",
    "lawyer",
    "locksmith",
    "moving_company",
    "painter",
    "plumber",
    "real_estate_agency",
    "roofing_contractor",
    "storage",
    "tailor",
    "telecommunications_service_provider",
    "travel_agency",
    "veterinary_care",
    "auto_parts_store",
    "bicycle_store",
    "book_store",
    "cell_phone_store",
    "clothing_store",
    "convenience_store",
    "department_store",
    "discount_store",
    "electronics_store",
    "furniture_store",
    "gift_shop",
    "grocery_store",
    "hardware_store",
    "home_goods_store	home_improvement_store",
    "jewelry_store",
    "liquor_store",
    "market",
    "pet_store",
    "shoe_store",
    "shopping_mall",
    "sporting_goods_store",
    "store",
    "supermarket",
    "wholesaler",
    "athletic_field",
    "fitness_center",
    "golf_course",
    "gym",
    "playground",
    "ski_resort",
    "sports_club",
    "sports_complex",
    "stadium",
    "swimming_pool",
    "airport",
    "bus_station",
    "bus_stop",
    "ferry_terminal",
    "heliport",
    "light_rail_station",
    "park_and_ride	subway_station",
    "taxi_stand",
    "train_station",
    "transit_depot",
    "transit_station",
    "truck_stop",
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
