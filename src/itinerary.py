import re
import typing as T

from llm.defs import ACTIVITY_TYPE_COLUMN, DAY_COLUMN, LOCATION_COLUMN


class Itinerary:

    def __init__(
        self,
        location: str,
        number_of_people: str,
        date: str,
        duration_days: str,
        group_type: str,
        description: str,
    ):
        self.location = location
        self.number_of_people = number_of_people
        self.date = date
        self.duration_days = duration_days
        self.group_type = group_type
        self.description = description

    def parse_itenerary_day(self, lines: T.List[str]) -> T.List[T.Tuple[str, str]]:
        day_plan = []
        # This pattern is designed to capture two groups separated by various delimiters
        pattern = re.compile(r"\-?\s*([\w\s]+?)\s*(?::|at|-)\s*([\w\s'&]+)")

        for line in lines:
            match = pattern.match(line)
            if match:
                activity_type, place = match.groups()
                activity_type = activity_type.strip()
                place = place.split("(")[0].strip()  # Removes anything within parentheses
                day_plan.append((activity_type, place))
            else:
                print(f"Could not parse line: {line}")

        return day_plan

    def parse_itinerary_content(self, content: str) -> T.List[T.Dict[str, str]]:
        """Split the content into days and activities"""
        days = content.split("\n\n")
        data = []
        for day in days:
            lines = day.split("\n")
            day_number = lines[0].split(" ")[1]
            day_plan = self.parse_itenerary_day(lines[1:])
            for activity_type, place in day_plan:
                data.append(
                    {
                        DAY_COLUMN: day_number,
                        ACTIVITY_TYPE_COLUMN: activity_type,
                        LOCATION_COLUMN: place,
                    }
                )

        return data
