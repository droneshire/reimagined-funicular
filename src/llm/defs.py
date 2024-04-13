import typing as T

from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# these columns should match the members of the Itinerary class
DAY_COLUMN = "day"
ACTIVITY_TYPE_COLUMN = "activity_type"
LOCATION_COLUMN = "location"
DESCRIPTION_COLUMN = "description"


class Itinerary(BaseModel):
    day: T.List[str] = Field(
        description="a list that indicates the day of the corresponding activity"
    )
    activity_type: T.List[str] = Field(
        description="a list of the activities type of the itinerary like breakfast, dinner etc"
    )
    location: T.List[str] = Field(
        description=(
            "a list of the location that existis in "
            "google places of the corresponding activity type"
        )
    )
    description: T.List[str] = Field(
        description="a brief description of the activity. The description must be 2-3 word phrases"
    )


ITINERARY_PROMPT_TEMPLATE = PromptTemplate(
    template="""Given the user's input below:
Location: {location}
Number of People: {number_of_people}
Date: {date}
Duration (Days): {duration_days}
Tell Us About Your Group: {group_type}
Briefly describe the trip you envision including the groups interests in activities, food etc: {description}

Create an itinerary providing the activities for breakfast, morning activity, lunch, afternoon
activity, dinner and evening activity, the location which must exist in google places and a
brief description of the activity or the place

Make sure to include all the itinerary days""",
    input_variables=[
        "location",
        "number_of_people",
        "date",
        "duration",
        "group_type",
        "description",
    ],
)
