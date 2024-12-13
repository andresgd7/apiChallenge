# Movie Weather App

This application allows users to search for movies and retrieve both movie information and historical weather data for the movie's release date. It uses The Movie Database (TMDB) API for movie data and Open-Meteo for historical weather information.

## Features

- Search movies by title
- Display movie release date and genres
- Show historical weather data for the movie's release date
- Send search data to a webhook for tracking
- Error handling with modal displays

## Prerequisites

- Python 3.8 or higher
- FastAPI
- HTTPX
- A TMDB API Bearer Token

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd movie-weather-app
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn httpx python-dotenv
```

4. Create a `.env` file in the root directory with your TMDB API token:
```
TMDB_BEARER_TOKEN=your_tmdb_token_here
```

## Running the Application

1. Start the server:
```bash
uvicorn main:app --reload
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

## How to Use

1. Enter a movie title in the search box
2. Click the "Search" button or press Enter
3. The application will display:
   - Movie title
   - Release date
   - Movie genres
   - Historical weather data for the release date (temperature in Medellín, Colombia)

## API Endpoints

- `GET /`: Serves the main application page
- `GET /search_movie/?title={movie_title}`: Searches for a movie and returns movie and weather data

## Data Flow

1. User enters a movie title
2. Application queries TMDB API for movie information
3. If a movie is found, it retrieves historical weather data for the release date
4. Data is displayed in a modal window
5. Search data is sent to a webhook for tracking

## Error Handling

- Displays error messages in a modal for:
  - Movie not found
  - API connection issues
  - Invalid responses

## Technical Details

- Frontend: HTML, CSS, JavaScript
- Backend: Python with FastAPI
- APIs Used:
  - TMDB API for movie data
  - Open-Meteo API for historical weather data
- Webhook integration for data tracking

## Notes

- Weather data is specific to Medellín, Colombia (coordinates: 6.2442, -75.5812)
- The application uses modern async/await patterns for API calls
- CORS is enabled for all origins
