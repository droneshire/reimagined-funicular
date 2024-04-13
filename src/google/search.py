import concurrent.futures
import threading
import typing as T
from threading import Lock

import googlemaps
import pandas as pd

from constants import DEFAULT_FIELDS
from google.utils import DEFAULT_TYPE, TYPES, get_city_center_coordinates
from llm.defs import LOCATION_COLUMN


class SearchPlaces:

    def __init__(self, api_key: str, verbose: bool = False):
        self.gmaps = googlemaps.Client(key=api_key)
        self.verbose = verbose
        self.itinerary_place_details: T.List[T.Tuple[str, T.Dict[str, T.Any]]] = []
        self.nearby_place_details: T.Dict[str, T.List[T.Dict[str, T.Any]]] = {}

        self.lock = Lock()

    @staticmethod
    def _get_place_details(
        gmaps: googlemaps.Client,
        place_name: str,
        city_coordinates: T.Tuple[float, float],
        store_type: T.Optional[str],
        keyword: T.Optional[str],
        radius_meters: int,
        itinerary_place_details: T.List[T.Tuple[str, T.Dict[str, T.Any]]],
        nearby_place_details: T.Dict[str, T.List[T.Dict[str, T.Any]]],
        lock: threading.Lock,
    ) -> None:
        try:
            result = gmaps.places(
                query=place_name, location=city_coordinates, fields=DEFAULT_FIELDS
            )
        except:  # pylint: disable=bare-except
            print(f"Unable to get places info for {place_name}")
            return

        if not result or result.get("status") != "OK":
            print(f"Unable to get places info for {place_name}")
            return

        place_result = result["results"][0]
        with lock:
            itinerary_place_details.append((place_name, place_result))

        store_type = store_type if store_type else place_result.get("types", [DEFAULT_TYPE])[0]

        print(
            f"Getting nearby places for {place_name} at " f"{place_result['geometry']['location']}"
        )
        try:
            nearby_places = gmaps.places_nearby(
                location=place_result["geometry"]["location"],
                radius=radius_meters,
                keyword=keyword if keyword else None,
                type=store_type,
            )
        except:  # pylint: disable=bare-except
            print(f"Unable to get nearby places info for {place_name}")
            return

        if not nearby_places or nearby_places.get("status") != "OK":
            print(f"Unable to get nearby places info for {place_name}")
            return

        with lock:
            nearby_place_details[place_name] = nearby_places["results"]

        print(f"Found {len(nearby_places['results'])} nearby places for {place_name}")

    def search(
        self,
        city: str,
        itinerary: pd.DataFrame,
        store_type: T.Optional[str] = None,
        keyword: T.Optional[str] = None,
        radius_meters: int = 1500,
    ) -> T.Tuple[
        T.List[T.Tuple[str, T.Dict[str, T.Any]]],
        T.Dict[str, T.List[T.Dict[str, T.Any]]],
        T.Tuple[float, float],
    ]:
        city_coordinates = get_city_center_coordinates(city)

        if not city_coordinates:
            raise ValueError(f"Unable to get coordinates for city: {city}")

        print(f"{city} coordinates: {city_coordinates}")

        if store_type:
            assert (
                store_type in TYPES
            ), f"Invalid store type: {store_type}, must be one of {','.join(TYPES)}"

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    self._get_place_details,
                    self.gmaps,
                    row[LOCATION_COLUMN],
                    city_coordinates,
                    store_type,
                    keyword,
                    radius_meters,
                    self.itinerary_place_details,
                    self.nearby_place_details,
                    self.lock,
                )
                for _, row in itinerary.iterrows()
            ]
            concurrent.futures.wait(futures)

        return self.itinerary_place_details, self.nearby_place_details, city_coordinates
