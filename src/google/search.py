import concurrent.futures
import json
import threading
import typing as T
from threading import Lock

import googlemaps
import pandas as pd

from constants import DEFAULT_FIELDS
from google.utils import DEFAULT_TYPE, TYPES, Coordinates, get_city_center_coordinates
from llm.defs import DESCRIPTION_COLUMN, LOCATION_COLUMN

ItineraryPlaceDetailsType = T.List[T.Tuple[str, T.Dict[str, T.List[T.Any]]]]
NearbyPlaceDetailsType = T.Dict[str, T.List[T.Dict[str, T.Any]]]


class SearchPlaces:

    def __init__(self, api_key: str, verbose: bool = False):
        self.gmaps = googlemaps.Client(key=api_key)
        self.verbose = verbose
        self.itinerary_place_details: ItineraryPlaceDetailsType = []
        self.nearby_place_details: NearbyPlaceDetailsType = {}

        self.lock = Lock()

    @staticmethod
    def _get_place_details(
        gmaps: googlemaps.Client,
        location_name: str,
        location_description: str,
        city_coordinates: Coordinates,
        store_type: T.Optional[str],
        radius_meters: int,
        itinerary_place_details: ItineraryPlaceDetailsType,
        nearby_place_details: NearbyPlaceDetailsType,
        lock: threading.Lock,
    ) -> None:
        try:
            result = gmaps.places(query=location_name, location=city_coordinates)
        except Exception as exc:
            print(f"Unable to get places info for {location_name}: {exc}")
            return

        if not result or result.get("status") != "OK":
            print(f"Unable to get places info for {location_name}")
            return

        place_result = result["results"][0]
        with lock:
            itinerary_place_details.append((location_name, result["results"]))

        store_type = store_type if store_type else place_result.get("types", [DEFAULT_TYPE])[0]

        print(
            f"Getting nearby places for {location_name} at "
            f"{place_result['geometry']['location']}"
        )
        try:
            nearby_places = gmaps.places_nearby(
                location=place_result["geometry"]["location"],
                radius=radius_meters,
                keyword=location_description if location_description else None,
                type=store_type,
                rank_by="prominence",
            )
        except:  # pylint: disable=bare-except
            print(f"Unable to get nearby places info for {location_name}")
            return

        if not nearby_places or nearby_places.get("status") != "OK":
            print(f"Unable to get nearby places info for {location_name}")
            return

        with lock:
            nearby_place_details[location_name] = nearby_places["results"]

        print(f"Found {len(nearby_places['results'])} nearby places for {location_name}")

    def search(
        self,
        city: str,
        itinerary: T.Dict[str, T.List[str]],
        store_type: T.Optional[str] = None,
        radius_meters: int = 1500,
        write_to_file: bool = False,
    ) -> T.Tuple[
        ItineraryPlaceDetailsType,
        NearbyPlaceDetailsType,
        Coordinates,
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
                    itinerary[LOCATION_COLUMN][index],
                    itinerary[DESCRIPTION_COLUMN][index],
                    city_coordinates,
                    store_type,
                    radius_meters,
                    self.itinerary_place_details,
                    self.nearby_place_details,
                    self.lock,
                )
                for index in range(len(itinerary[LOCATION_COLUMN]))
            ]
            concurrent.futures.wait(futures)

        if write_to_file:
            with open("places.json", "w", encoding="utf-8") as outfile:
                json.dump(
                    {"results": self.itinerary_place_details}, outfile, ensure_ascii=True, indent=4
                )
            with open("nearby_places.json", "w", encoding="utf-8") as outfile:
                json.dump(self.nearby_place_details, outfile, ensure_ascii=True, indent=4)

        return self.itinerary_place_details, self.nearby_place_details, city_coordinates
