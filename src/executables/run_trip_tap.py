import argparse
import os
import typing as T

import dotenv

dotenv.load_dotenv()


def get_secrets() -> T.Dict[str, str]:
    secrets = {
        "google_api_key": os.getenv("GOOGLE_API_KEY", ""),
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    }
    return secrets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the TripTap application")
    parser.add_argument(
        "itinerary_file",
        type=str,
        help="The name of the itinerary file to be processed",
    )
    parser.add_argument(
        "output_file",
        type=str,
        help="The name of the output file to write the processed data",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    secrets = get_secrets()


if __file__ == "__main__":
    main()
