import concurrent.futures
import json
import threading
import typing as T
from threading import Lock

import googlemaps

from constants import DEFAULT_FIELDS, MIN_RATING, MIN_RATING_COUNT
from google.utils import DEFAULT_TYPE, Coordinates, get_city_center_coordinates
from llm.defs import LOCATION_COLUMN

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
    def is_acceptable_location(details: T.Dict[str, T.Any]) -> bool:
        return (
            float(details["rating"]) > MIN_RATING
            and int(details["user_ratings_total"]) > MIN_RATING_COUNT
            and details["business_status"] == "OPERATIONAL"
        )

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
    ) -> None:
        try:
            result = gmaps.places(query=location_name, location=city_coordinates)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Unable to get places info for {location_name}: {exc}")
            return

        if not result or result.get("status") != "OK":
            if not result:
                print(f"Unable to get places info for {location_name}")
            else:
                print(
                    f"Unable to get places info for {location_name}, status: {result.get('status')}"
                )
            return

        place_result = result["results"][0]
        with lock:
            itinerary_place_details.append((location_name, result["results"]))

        store_type = place_result.get("types", [DEFAULT_TYPE])[0]
        keyword = location_description if location_description else None

        print(
            f"Getting nearby places for {location_name} at "
            f"{place_result['geometry']['location']} with "
            f"type {store_type} and description {location_description}"
        )
        try:
            nearby_places = gmaps.places_nearby(
                location=place_result["geometry"]["location"],
                radius=radius_meters,
                keyword=keyword,
                type=store_type,
                rank_by="prominence",
            )
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Unable to get nearby places info for {location_name}: {exc}")
            return

        if not nearby_places or nearby_places.get("status") != "OK":
            print(f"Unable to get nearby places info for {location_name}")
            return

        for nearby_result in nearby_places["results"]:
            if nearby_result["place_id"] == place_result["place_id"]:
                continue

            if not SearchPlaces.is_acceptable_location(nearby_result):
                continue

            with lock:
                nearby_place_details[location_name] = nearby_place_details.get(
                    location_name, []
                ) + [nearby_result]

        print(f"Found {len(nearby_place_details[location_name])} nearby places for {location_name}")

    def search(
        self,
        city: str,
        itinerary: T.Dict[str, T.List[str]],
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

        if write_to_file:
            with open("places.json", "w", encoding="utf-8") as outfile:
                json.dump(
                    {"results": self.itinerary_place_details}, outfile, ensure_ascii=True, indent=4
                )
            with open("nearby_places.json", "w", encoding="utf-8") as outfile:
                json.dump(self.nearby_place_details, outfile, ensure_ascii=True, indent=4)

        return self.itinerary_place_details, self.nearby_place_details, city_coordinates
