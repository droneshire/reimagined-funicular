import concurrent.futures
import threading
import typing as T
from threading import Lock

import googlemaps

from constants import DEFAULT_FIELDS, MIN_RATING, MIN_RATING_COUNT
from google.places_api import GooglePlacesAPI
from google.utils import Coordinates, get_city_center_coordinates
from llm.defs import LOCATION_COLUMN, DESCRIPTION_COLUMN, ACTIVITY_TYPE_COLUMN

ItineraryPlaceDetailsType = T.List[T.Tuple[str, T.Dict[str, T.List[T.Any]]]]
NearbyPlaceDetailsType = T.Dict[str, T.List[T.Dict[str, T.Any]]]


class SearchPlaces:

    def __init__(self, api_key: str, verbose: bool = False):
        self.api_key = api_key
        self.gmaps_lib = googlemaps.Client(key=api_key)
        self.verbose = verbose
        self.itinerary_place_details: ItineraryPlaceDetailsType = []
        self.nearby_place_details: NearbyPlaceDetailsType = {}
        self.total_api_calls = {
            "places": 0,
            "maps": 0,
        }

        self.lock = Lock()

    @staticmethod
    def is_acceptable_location(
        original: T.Dict[str, T.Any], proposed: T.Dict[str, T.Any], verbose: bool = False
    ) -> bool:
        if float(proposed["rating"]) < MIN_RATING:
            if verbose:
                print(f"Rating is too low: {proposed['rating']}")
            return False

        if int(proposed["userRatingCount"]) < MIN_RATING_COUNT:
            if verbose:
                print(f"Rating count is too low: {proposed['userRatingCount']}")
            return False

        if proposed["businessStatus"] != "OPERATIONAL":
            if verbose:
                print(f"Business status is not operational: {proposed['businessStatus']}")
            return False

        if proposed.get("primaryType") not in original.get("types", []):
            if verbose:
                print(
                    f"Primary type {proposed.get('primaryType')} "
                    f"is not in original types {original.get('types', [])}"
                )
            return False

        if proposed.get("id") == original.get("id"):
            if verbose:
                print(f"ID is the same: {proposed.get('id')}")
            return False

        return True

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
        api_key: str,
        itinerary_info: T.Tuple[str, str, str],
        city_name: str,
        radius_meters: int,
        itinerary_place_details: ItineraryPlaceDetailsType,
        nearby_place_details: NearbyPlaceDetailsType,
        lock: threading.Lock,
        verbose: bool = False,
    ) -> T.Dict[str, int]:
        total_api_calls = {
            "places": 0,
            "maps": 0,
        }

        location_name, description, activity_type = itinerary_info

        for query in [
            f"{location_name} in {city_name}",
            f"{activity_type} at {description} in {city_name}",
        ]:
            gplaces = GooglePlacesAPI(api_key, verbose=True)
            result = gplaces.text_search(
                query=query,
                fields=DEFAULT_FIELDS,
                data={
                    "minRating": MIN_RATING,
                },
            )

            total_api_calls["places"] += 1

            if result and len(result.get("places", [])) > 0:
                break

        if not result or len(result.get("places", [])) == 0:
            print(f"No places found for {location_name}")

        place_result = result["places"][0]
        print(place_result)

        with lock:
            itinerary_place_details.append((location_name, place_result))

        store_types = place_result.get("types", None)
        print(
            f"Getting nearby places for {location_name} at "
            f"{place_result['location']} with types {store_types}"
        )

        nearby_places = gplaces.search_location_radius(
            latitude=place_result["location"]["latitude"],
            longitude=place_result["location"]["longitude"],
            radius_meters=radius_meters,
            query=f"{location_name}",
            fields=DEFAULT_FIELDS,
            data={
                "minRating": MIN_RATING,
            },
        )
        total_api_calls["places"] += 1

        if not nearby_places or len(nearby_places.get("places", [])) == 0:
            print(f"Unable to get nearby places for {location_name}")
            return total_api_calls

        nearby_place_details[location_name] = []
        for nearby_result in nearby_places["places"]:
            print(nearby_result)
            if not SearchPlaces.is_acceptable_location(
                place_result, nearby_result, verbose=verbose
            ):
                print(f"Skipping {nearby_result['displayName']['text']} as it is not acceptable")
                continue

            with lock:
                nearby_place_details[location_name].append(nearby_result)

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

        self.total_api_calls = {
            "places": 0,
            "maps": 0,
        }

        if single_thread:
            for index in range(len(itinerary[LOCATION_COLUMN])):
                itinerary_info = (
                    itinerary[LOCATION_COLUMN][index],
                    itinerary[DESCRIPTION_COLUMN][index],
                    itinerary[ACTIVITY_TYPE_COLUMN][index],
                )
                api_calls = self._get_place_details(
                    self.api_key,
                    itinerary_info,
                    city,
                    radius_meters,
                    self.itinerary_place_details,
                    self.nearby_place_details,
                    self.lock,
                    verbose=self.verbose,
                )
                for key, value in api_calls.items():
                    self.total_api_calls[key] += value
        else:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        self._get_place_details,
                        self.api_key,
                        (
                            itinerary[LOCATION_COLUMN][index],
                            itinerary[DESCRIPTION_COLUMN][index],
                            itinerary[ACTIVITY_TYPE_COLUMN][index],
                        ),
                        city,
                        radius_meters,
                        self.itinerary_place_details,
                        self.nearby_place_details,
                        self.lock,
                    )
                    for index in range(len(itinerary[LOCATION_COLUMN]))
                ]
                concurrent.futures.wait(futures)

                for future in futures:
                    for key, value in future.result().items():
                        self.total_api_calls[key] += value

        return (
            self.itinerary_place_details,
            self.nearby_place_details,
            city_coordinates,
            sum(self.total_api_calls.values()),
        )
