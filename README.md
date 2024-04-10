# reimagined-funicular

Upwork client project - OpenAI and Google Places API project

## Project Description

This project is a collaboration between OpenAI and Google Places API to create a tool that generates travel itineraries based on user input. The tool will use OpenAI's GPT-3 to generate the itinerary and Google Places API to provide the relevant information for each location. The goal is to create a user-friendly interface that allows users to input their travel preferences and receive a detailed itinerary with recommendations for accommodations, activities, and dining options.

#### Input Variables for Prompt

- Location: `South Beach Miami, FL (google places location)`
- Number of People: `6`
- Date: `November 2026`
- Duration (Days): `3`
- Tell Us About Your Group: `bachelorette party`
- Briefly describe the trip you envision including the groups interests in activities, food etc.: `boutique hotel with onsite spa, beach clubs with DJs during the day, and high end nightclubs. List at least six restaurant options for dinner That include at least one nice steakhouse and one nice sushi restaurant.`

#### Prompt

The above would become a prompt:

```
Create an itinerary and provide only the names for places listed in google places for breakfast, morning activity, lunch, afternoon activity, dinner and evening activity (return only the day and the name): A “3” day “bachelorette party” to “South Beach Miami, FL” for “6” people in “November 2026” that enjoy “Include high-end boutique hotel options (must be 4 stars or higher) with onsite spa, beach clubs with DJs during the day, and high end nightclubs. List at least six restaurant options for dinner That include at least one nice steakhouse and one nice sushi restaurant.”
```

## Current Implementation

The current implementation does the following:

1. Takes user input for location, number of people, date, duration, and group description.

2. Creates a prompt based on the user input and sends it to the OpenAI API.

3. Receives the response from the OpenAI API and extracts the relevant information. Specifically, it extracts the names of places for breakfast, morning activity, lunch, afternoon activity, dinner, and evening activity for each day of the trip. This is in the format of `Day 1:\n- Activity: Place Name`. From what I can tell, the OpenAI API tends to provide real places, but it's not guaranteed.

4. Uses the Google Maps API to get the place ID for each place returned by the OpenAI API.

5. Uses the Google Maps API to get the details of each place using the place ID (seems to be unused?)

6. Uses the Google Maps API to get location for each item in the places list.

7. Uses the Google Places API to get the nearby places for each location, for example breakfast place, etc.

## Optimizations

### OpenAI API Calls

Most optimizations were just around trying to tweak and modify the prompt to reduce the prompt text length. This is a simple way to reduce costs, but it's not always the best way to optimize. The prompt is already quite concise and removing more details could lead to less accurate results. I was told the OpenAI calls were not the largest source of concern, so I didn't focus on this area too much.

### Google Places API Calls

The Google Places API calls were the main source of concern. The API calls were being made for each place returned by the OpenAI API, which could be up to 6 places per day for each day of the trip. This could result in a large number of API calls, which could be costly. To optimize this, I made the following changes:

1. Remove several of the times where the Google Maps API is used.

2. Use free geocode libraries to get city coordinates instead of use Google Maps API. This is a one-time call per location, so it's not a huge cost, but it's still a cost.

3. Use the Google Places API to get nearby places for each location. This is a more efficient way to get the information needed for each place, as it reduces the number of API calls needed.

### Setup

To setup the notebook, add an `.env` file into the root of the repository. The `.env` file should contain the following variables/secrets:

```
GOOGLE_PLACES_API_KEY=<REDACTED>
OPEN_AI_API_KEY=<REDACTED>
MAPBOX_API_KEY=<REDACTED>
```
After the `.env` is setup, run the following to setup the virtual environment:

```
make init
source ./venv/bin/activate
make install
```

### Notebooks


The notebooks that start with `original*` are the client's original notebooks, and the `experiments.ipynb` is the work product for this project. 
