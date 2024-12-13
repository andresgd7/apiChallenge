from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import httpx
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

load_dotenv()

TMDB_BEARER_TOKEN = os.getenv('TMDB_BEARER_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


async def get_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list"
    headers = {
        "Authorization": f"Bearer {TMDB_BEARER_TOKEN}",
        "Content-Type": "application/json;charset=utf-8"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return {genre['id']: genre['name'] for genre in response.json()['genres']}
        return {}


@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")


async def send_to_webhook(data: dict):
    try:
        print(f"Attempting to send data to webhook: {data}")  # Debug log
        async with httpx.AsyncClient() as client:
            response = await client.post(
                WEBHOOK_URL,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Webhook response status: {
                  response.status_code}")  # Debug log
            print(f"Webhook response content: {response.text}")  # Debug log

            return {
                "success": response.status_code == 200,
                "status_code": response.status_code
            }
    except Exception as e:
        print(f"Error sending to webhook: {str(e)}")  # Debug log
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/search_movie/")
async def search_movie(title: str):
    try:
        # Obtener la lista de géneros
        genres_dict = await get_genres()

        # Buscar la película
        url = "https://api.themoviedb.org/3/search/movie"
        headers = {
            "Authorization": f"Bearer {TMDB_BEARER_TOKEN}",
            "Content-Type": "application/json;charset=utf-8"
        }
        params = {
            "query": title,
            "language": "en-US",
            "page": 1
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if data['results']:
                movie = data['results'][0]
                release_date = movie.get('release_date')

                # Convertir IDs de género a nombres
                genre_names = [genres_dict.get(genre_id, "Unknown")
                               for genre_id in movie.get('genre_ids', [])]

                # Crear respuesta con géneros
                response_data = {
                    "title": movie['title'],
                    "release_date": release_date,
                    "genres": genre_names
                }

                if release_date:
                    weather = await get_weather_data(release_date)
                    response_data['weather'] = weather

                # Preparar datos para el webhook
                webhook_data = {
                    "title": movie['title'],
                    "release_date": release_date,
                    "genres": genre_names,
                    "weather": weather if release_date else None,
                    "timestamp": datetime.utcnow().isoformat(),
                    "search_query": title
                }

                # Enviar al webhook y obtener respuesta
                webhook_status = await send_to_webhook(webhook_data)
                print(f"Webhook status: {webhook_status}")  # Debug log

                # Incluir estado del webhook en la respuesta
                response_data['webhook_status'] = webhook_status

                return response_data
            else:
                raise HTTPException(status_code=404, detail="Movie not found")
        else:
            raise HTTPException(status_code=response.status_code,
                                detail="Error fetching movie data")
    except Exception as e:
        print(f"Error in search_movie: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))


async def get_weather_data(release_date: str):
    try:
        date = release_date[:10]
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": 6.2442,
            "longitude": -75.5812,
            "start_date": date,
            "end_date": date,
            "daily": "apparent_temperature_min,apparent_temperature_max",
            "timezone": "America/Bogota"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

        if response.status_code == 200:
            weather_data = response.json()
            if 'daily' in weather_data:
                try:
                    min_temp = weather_data['daily']['apparent_temperature_min'][
                        0] if weather_data['daily']['apparent_temperature_min'] else 'No data'
                    max_temp = weather_data['daily']['apparent_temperature_max'][
                        0] if weather_data['daily']['apparent_temperature_max'] else 'No data'

                    return {
                        "apparent_temperature_min": min_temp,
                        "apparent_temperature_max": max_temp
                    }
                except (IndexError, KeyError):
                    return {"error": "Weather data not available"}
        return {"error": "Weather data not available"}
    except Exception as e:
        return {"error": str(e)}
