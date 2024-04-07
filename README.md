# reimagined-funicular

Upwork client project - OpenAI and Google Places API project

## Project Description

This project is a collaboration between OpenAI and Google Places API to create a tool that generates travel itineraries based on user input. The tool will use OpenAI's GPT-3 to generate the itinerary and Google Places API to provide the relevant information for each location. The goal is to create a user-friendly interface that allows users to input their travel preferences and receive a detailed itinerary with recommendations for accommodations, activities, and dining options.

#### Variables

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

3. Receives the response from the OpenAI API and extracts the relevant information. Specifically, it extracts the names of places for breakfast, morning activity, lunch, afternoon activity, dinner, and evening activity for each day of the trip. This is in the format of `Day 1: Place Name`. From what I can tell, the OpenAI API tends to provide real places, but it's not guaranteed.

4. Uses the Google Places API to search for the details of each place returned by the OpenAI API. It uses this to gather the places id.

5. Uses the Google Places API to get the details of each place using the place id.


## Optimizations

Open AI: [improvements](./docs/OPENAI.md)
Google Places API: [improvements](./docs/GOOGLE_PLACES.md)
