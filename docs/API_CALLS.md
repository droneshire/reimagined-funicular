## OpenAI GPT-3 API

```
ITINERARY_PROMPT_TEMPLATE = PromptTemplate(
    template="""Given the user's input below:
Location: {location}
Number of People: {number_of_people}
Date: {date}
Duration (Days): {duration_days}
Tell Us About Your Group: {group_type}
Briefly describe the trip you envision including the groups interests in activities,
food etc: {description}

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
```

## Obtain the coordinates of the city specified by the user

This is used as a trick to hone in on the place specified by the GPT query. This allows us to use the `searchText` API which is the only one that allows us to specify the fields that we want to return (allowing us to better control API costs)

## Get the details of the itinerary place (from GPT itinerary)

### Query

> `url = https://places.googleapis.com/v1/places:searchText`

> `headers = {'Content-Type': 'application/json', 'X-Goog-Api-Key': 'AIzaSyC721JnEgqgQ6Sanz27wOeTtO_eETybSRs', 'X-Goog-FieldMask': 'places.id,places.formattedAddress,places.displayName,places.location,places.rating,places.googleMapsUri,places.websiteUri,places.businessStatus,places.priceLevel,places.userRatingCount,places.primaryType,places.types,places.editorialSummary,places.goodForChildren'} `

> `data = {'textQuery': 'The Local House in South Beach Miami, FL', 'minRating': 3.5}`

> `params = {} `

### Results

Detailed info for the fields specified

## Get nearby places for the itinerary place:

### Query

> `url = https://places.googleapis.com/v1/places:searchNearby`

> `headers = {'Content-Type': 'application/json', 'X-Goog-Api-Key': 'AIzaSyC721JnEgqgQ6Sanz27wOeTtO_eETybSRs', 'X-Goog-FieldMask': 'places.id,places.formattedAddress,places.displayName,places.location,places.rating,places.googleMapsUri,places.websiteUri,places.businessStatus,places.priceLevel,places.userRatingCount,places.primaryType,places.types,places.editorialSummary,places.goodForChildren'}`

> `params = {}`

> `data = {'locationRestriction': {'circle': {'center': {'latitude': 25.773442, 'longitude': -80.132473}, 'radius': 1500}}, 'minRating': 3.5, 'includedTypes': ['restaurant', 'brunch_restaurant', 'hotel', 'american_restaurant', 'lodging']}`

### Results

Detailed info for the fields specified for 0-20 nearby places

### Filter the nearby places based on the user's preferences:

- Above 3.5 rating
- Above 100 user rating count
- Working status is OPERATIONAL
- Is not the same as the original itinerary place
- The places `types` field matches the itinerary place `types` field

## Detail Fields

```

DEFAULT_FIELDS = [
"places.id",
"places.formattedAddress",
"places.displayName",
"places.location",
"places.rating",
"places.googleMapsUri",
"places.websiteUri",
"places.businessStatus",
"places.priceLevel",
"places.userRatingCount",
"places.primaryType",
"places.types",
"places.editorialSummary",
"places.goodForChildren",
]

```
