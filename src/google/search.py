import concurrent.futures
import threading
import typing as T
from threading import Lock

import googlemaps

from constants import DEFAULT_FIELDS, MIN_RATING, MIN_RATING_COUNT
from google.places_api import GoogleMapsAPI, GooglePlacesAPI
from google.utils import DEFAULT_TYPE, Coordinates, get_city_center_coordinates
from llm.defs import LOCATION_COLUMN

ItineraryPlaceDetailsType = T.List[T.Tuple[str, T.Dict[str, T.List[T.Any]]]]
NearbyPlaceDetailsType = T.Dict[str, T.List[T.Dict[str, T.Any]]]


class SearchPlaces:

    def __init__(self, api_key: str, verbose: bool = False):
        self.gmaps = googlemaps.Client(key=api_key)
        self.gmaps_api = GoogleMapsAPI(api_key, verbose)
        self.gplaces_api = GooglePlacesAPI(api_key, verbose)
        self.verbose = verbose
        self.itinerary_place_details: ItineraryPlaceDetailsType = []
        self.nearby_place_details: NearbyPlaceDetailsType = {}
        self.total_api_calls = 0

        self.lock = Lock()

    @staticmethod
    def is_acceptable_location(original: T.Dict[str, T.Any], details: T.Dict[str, T.Any]) -> bool:
        return (
            float(details["rating"]) > MIN_RATING
            and int(details["user_ratings_total"]) > MIN_RATING_COUNT
            and details["business_status"] == "OPERATIONAL"
            and details.get("types", ["New"])[0] == original.get("types", ["Original"])[0]
            and details.get("place_id") != original.get("place_id")
        )

    @staticmethod
    def call_api(gmap_func: T.Callable, *args: T.Any, **kwargs: T.Any) -> T.Any:
        try:
            print(f"Calling Google Maps API {gmap_func} with {args} and {kwargs}")
            result = gmap_func(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Error calling Google Maps API: {exc}")
            return None

        if not result or result.get("status") != "OK" or not result.get("results"):
            if not result:
                print(f"Unable to {gmap_func} to get api info")
            else:
                print(f"Unable to {gmap_func} to get api info status: {result.get('status')}")
            return None

        return result

    @staticmethod
    def _get_place_details(
        gmaps: googlemaps.Client,
        location_name: str,
        location_description: T.Optional[str],
        city_coordinates: Coordinates,
        radius_meters: int,
        itinerary_place_details: ItineraryPlaceDetailsType,
        nearby_place_details: NearbyPlaceDetailsType,
        lock: threading.Lock,
    ) -> int:
        total_api_calls = 0
        result = SearchPlaces.call_api(gmaps.places, query=location_name, location=city_coordinates)

        total_api_calls += 1

        if not result:
            print(f"No places found for {location_name}")
            return total_api_calls

        place_result = result.get("results")[0]

        # Now get the detailed information for the place
        result = SearchPlaces.call_api(
            gmaps.place, place_id=place_result["place_id"], fields=DEFAULT_FIELDS
        )
        total_api_calls += 1

        if not result:
            print(f"Unable to get detailed info for {location_name}")
            return total_api_calls

        with lock:
            itinerary_place_details.append((location_name, result["results"]))

        store_type = place_result.get("types", [DEFAULT_TYPE])[0]
        keyword = location_description if location_description else None

        print(
            f"Getting nearby places for {location_name} at "
            f"{place_result['geometry']['location']} with "
            f"type {store_type} and description {location_description}"
        )

        nearby_places = SearchPlaces.call_api(
            gmaps.places_nearby,
            location=place_result["geometry"]["location"],
            radius=radius_meters,
            keyword=keyword,
            type=store_type,
            rank_by="prominence",
        )
        total_api_calls += 1

        if not nearby_places:
            print(f"Unable to get nearby places for {location_name}")
            return total_api_calls

        for nearby_result in nearby_places["results"]:
            if not SearchPlaces.is_acceptable_location(nearby_result, place_result):
                continue

            with lock:
                nearby_place_details[location_name] = nearby_place_details.get(
                    location_name, []
                ) + [nearby_result]

        print(f"Found {len(nearby_place_details[location_name])} nearby places for {location_name}")

        return total_api_calls

    def search(
        self,
        city: str,
        itinerary: T.Dict[str, T.List[str]],
        radius_meters: int = 1500,
        single_thread: bool = False,
    ) -> T.Tuple[
        ItineraryPlaceDetailsType,
        NearbyPlaceDetailsType,
        Coordinates,
        int,
    ]:
        city_coordinates = get_city_center_coordinates(city)

        if not city_coordinates:
            raise ValueError(f"Unable to get coordinates for city: {city}")

        print(f"{city} coordinates: {city_coordinates}")

        self.total_api_calls = 0

        if single_thread:
            for index in range(len(itinerary[LOCATION_COLUMN])):
                self.total_api_calls += self._get_place_details(
                    self.gmaps,
                    itinerary[LOCATION_COLUMN][index],
                    None,
                    city_coordinates,
                    radius_meters,
                    self.itinerary_place_details,
                    self.nearby_place_details,
                    self.lock,
                )
        else:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        self._get_place_details,
                        self.gmaps,
                        itinerary[LOCATION_COLUMN][index],
                        None,
                        city_coordinates,
                        radius_meters,
                        self.itinerary_place_details,
                        self.nearby_place_details,
                        self.lock,
                    )
                    for index in range(len(itinerary[LOCATION_COLUMN]))
                ]
                concurrent.futures.wait(futures)

                for future in futures:
                    self.total_api_calls += future.result()

        return (
            self.itinerary_place_details,
            self.nearby_place_details,
            city_coordinates,
            self.total_api_calls,
        )
